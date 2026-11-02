import code as code_module
import io
import json
import sys
import threading
import time

from runner import DEFAULT_TIMEOUT, EXEC_LOCK, SandboxTimeout, _Watchdog, _truncate

# B1: how long a single REPL statement may run before it is force-interrupted.
# Mirrors runner.DEFAULT_TIMEOUT so the desktop/Android behaviour is identical.
REPL_TIMEOUT = DEFAULT_TIMEOUT

_console = None
# E3: REPL 会话是进程内单例（跨 push 保持状态），用锁保证 start/reset/push
# 的原子性，避免 UI 线程与后台线程并发访问同一个 console 导致串台。
# 复用 runner.EXEC_LOCK：REPL 同样会改写进程级 sys.stdout/sys.stderr，
# 必须与 run_code / check_exercise 互斥，否则终端与课程页并发执行会互相劫持输出。
_console_lock = EXEC_LOCK


class NeonConsole(code_module.InteractiveConsole):
    def __init__(self):
        super().__init__(locals={"__name__": "__neon_console__", "__doc__": None})
        self.capture = io.StringIO()
        # Per-statement execution budget; updated by push() for each call.
        self._timeout = REPL_TIMEOUT

    def write(self, data):
        self.capture.write(data)

    def runcode(self, code):
        # B1: every executable statement runs inside a daemon thread guarded by
        # the same settrace watchdog runner uses, so a dead loop / slow statement
        # is interrupted instead of hanging the calling (UI) thread forever.
        capture = self.capture
        state = {"finished": False}
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        deadline = time.perf_counter() + self._timeout

        def target():
            try:
                sys.stdout = capture
                sys.stderr = capture
                sys.settrace(_Watchdog(deadline))
                try:
                    exec(code, self.locals)
                finally:
                    sys.settrace(None)
            except SystemExit:
                raise
            except SandboxTimeout:
                self.write("运行超时：代码疑似死循环，已被强制中断。\n")
            except BaseException:
                self.showtraceback()
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                state["finished"] = True

        worker = threading.Thread(target=target, daemon=True)
        worker.start()
        # Wait for the budget plus a safety margin for the watchdog to fire.
        worker.join(self._timeout + 1.5)
        if not state["finished"]:
            self.write("运行超时：代码疑似死循环，已被强制中断。\n")


def _active_console() -> NeonConsole:
    global _console
    with _console_lock:
        if _console is None:
            _console = NeonConsole()
        return _console


def start():
    global _console
    with _console_lock:
        _console = NeonConsole()
    return json.dumps({"ok": True})


def reset():
    # 说明：重建 InteractiveConsole 会清空 locals（变量/函数定义）；
    # 模块级副作用（import 过的模块、改过的 builtins 等）不会因重建而回滚，
    # 这是 CPython 会话的固有行为，教学场景可接受。
    return start()


def push(line, timeout=None):
    console = _active_console()
    with _console_lock:
        # Honour an optional per-call budget (used by tests); defaults to REPL_TIMEOUT.
        console._timeout = REPL_TIMEOUT if timeout is None else float(timeout)
        console.capture.seek(0)
        console.capture.truncate(0)
        more = console.push(line)
        return json.dumps(
            {"more": bool(more), "output": _truncate(console.capture.getvalue())},
            ensure_ascii=False,
        )
