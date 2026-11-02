"""并发执行回归测试：进程级 stdout/builtins 不得被另一次运行劫持。

背景（2026-11 实测缺陷）：
    `runner._run_protected` 直接改写进程级的 `sys.stdout` / `sys.stderr` /
    `builtins.input`，而 `run_code` 本身没有互斥。课程详情页每个代码块各自
    `scope.launch`，同一屏连点两个「▶ 运行」就会并发进入引擎：
        两个线程各打印 50 行 → A 只剩 3 行自己的输出，其余 47 行被写进 B。
    修复方式：`runner.EXEC_LOCK`（RLock）串行化 run_code / check_exercise，
    并让 `repl.push` 复用同一把锁。

本文件锁定该行为：任何一次运行的结果里都不得出现另一路运行的输出。
"""
import json
import os
import sys
import threading
import unittest

sys.path.insert(
    0, os.path.join(os.path.dirname(__file__), "..", "app", "src", "main", "python")
)

import repl
import runner

SLEEP_LINES = (
    "import time\n"
    "for i in range(30):\n"
    "    print({tag!r}, i)\n"
    "    time.sleep(0.002)\n"
)


def _run_tagged(tag, results, errors):
    try:
        results[tag] = runner.run_code(SLEEP_LINES.format(tag=tag), timeout=8.0)
    except BaseException as exc:  # noqa: BLE001 - 失败要原样带回主线程断言
        errors[tag] = exc


def _own_and_foreign(stdout, tag):
    lines = [ln for ln in stdout.splitlines() if ln.strip()]
    own = [ln for ln in lines if ln.startswith(tag + " ")]
    foreign = [ln for ln in lines if not ln.startswith(tag + " ")]
    return own, foreign


class ConcurrentRunTests(unittest.TestCase):
    def test_concurrent_run_code_does_not_cross_talk(self):
        """两路 run_code 并发：各自输出必须完整且互不掺入。"""
        results = {}
        errors = {}
        threads = [
            threading.Thread(target=_run_tagged, args=(tag, results, errors))
            for tag in ("AAA", "BBB")
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join(30)

        self.assertEqual(errors, {}, f"并发执行抛出异常: {errors}")
        for tag in ("AAA", "BBB"):
            with self.subTest(tag=tag):
                own, foreign = _own_and_foreign(results[tag]["stdout"], tag)
                self.assertEqual(foreign, [], f"{tag} 的输出混入了其他运行的输出: {foreign[:3]}")
                self.assertEqual(
                    len(own), 30, f"{tag} 自身输出丢失：只收到 {len(own)}/30 行"
                )

    def test_concurrent_check_exercise_keeps_results_isolated(self):
        """run_code 与 check_exercise 并发：判题结论与输出都不得被污染。"""

        def judge():
            code = "import time\ndef add(a, b):\n    time.sleep(0.002)\n    return a + b"
            out["result"] = runner.check_exercise(code, ["assert add(1, 2) == 3"])

        out = {}
        results = {}
        errors = {}

        t_judge = threading.Thread(target=judge)
        t_run = threading.Thread(target=_run_tagged, args=("RUN", results, errors))
        t_judge.start()
        t_run.start()
        t_judge.join(30)
        t_run.join(30)

        self.assertEqual(errors, {}, f"并发执行抛出异常: {errors}")
        self.assertTrue(out["result"]["passed"], out["result"]["error"])
        own, foreign = _own_and_foreign(results["RUN"]["stdout"], "RUN")
        self.assertEqual(foreign, [], f"运行输出混入判题输出: {foreign[:3]}")
        self.assertEqual(len(own), 30)


class ReplLockSharingTests(unittest.TestCase):
    def test_repl_push_shares_exec_lock(self):
        """REPL 与引擎必须共用同一把锁，否则终端与课程页并发会互相劫持。"""
        self.assertIs(
            repl._console_lock,
            runner.EXEC_LOCK,
            "repl.py 必须复用 runner.EXEC_LOCK，不能自带一把独立的锁",
        )

    def test_repl_push_does_not_leak_into_run_code(self):
        """REPL push 与 run_code 并发时，两者的输出互不污染。"""
        repl.start()
        results = {}
        errors = {}
        repl_out = {}

        def do_repl():
            try:
                lines = []
                for i in range(20):
                    payload = json.loads(repl.push("print('REPL', %d)" % i))
                    lines.append(payload["output"])
                repl_out["text"] = "".join(lines)
            except BaseException as exc:  # noqa: BLE001
                errors["repl"] = exc

        t_repl = threading.Thread(target=do_repl)
        t_run = threading.Thread(target=_run_tagged, args=("PY", results, errors))
        t_repl.start()
        t_run.start()
        t_repl.join(30)
        t_run.join(30)

        self.assertEqual(errors, {}, f"并发执行抛出异常: {errors}")
        own, foreign = _own_and_foreign(results["PY"]["stdout"], "PY")
        self.assertEqual(foreign, [], f"run_code 输出混入 REPL 输出: {foreign[:3]}")
        self.assertEqual(len(own), 30)
        self.assertNotIn("PY 0", repl_out["text"], "REPL 输出混入了 run_code 的输出")


if __name__ == "__main__":
    unittest.main(verbosity=2)
