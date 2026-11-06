#!/usr/bin/env python3
"""JavaScript 三包课程 · 真实执行验证。

用法：
    python tools/verify_js_packs.py            # 验证并输出摘要
    python tools/verify_js_packs.py -v         # 逐讲输出

验证内容：
  1. 三个 JSON 可 json.load，每包 10 讲，id/order 连续，无重复 id
  2. 每讲的代码块数量、quiz、table/diagram、tip/warn、exercise 字段
  3. 每个 runnable 代码块在 node vm 中真实执行，捕获 stdout 并与紧随其后的
     output 块逐字符比对（换行统一为 LF，忽略末尾空行）
  4. exercise.solution + 每条 tests 在同一作用域执行，全部通过
  5. exercise.starterCode + 同样的 tests 必须至少失败一条（防止空壳通过）
  6. 静态扫描禁用语法：class / 展开运算符 / 默认参数 / async-await /
     可选链 / 空值合并 / import / require / process / setTimeout / fetch /
     document / window

退出码 0 表示全部通过；任何失败打印明细并返回 1。脚本可重复运行。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS = [
    ("js-basics", 21, "JavaScript · 基础篇", 300),
    ("js-core", 22, "JavaScript · 核心篇", 310),
    ("js-advanced", 23, "JavaScript · 进阶篇", 320),
]

HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const task = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function makeSandbox() {
  const out = [];
  const sandbox = {
    print: function () {
      out.push(Array.prototype.slice.call(arguments).map(String).join(' '));
    },
    input: function () { throw new Error('InputError: 运行台不支持交互式输入'); },
    assert: function (cond, msg) {
      if (!cond) throw new Error('AssertionError: ' + (msg || '断言未通过'));
    }
  };
  sandbox.console = {
    log: sandbox.print,
    info: sandbox.print,
    warn: sandbox.print,
    error: sandbox.print
  };
  return { sandbox: sandbox, out: out };
}

function runScript(src, sandbox, timeout) {
  vm.runInContext(src, sandbox, { timeout: timeout || 5000 });
}

// Rhino 每次 evaluateString 结束后会清空微任务队列；node vm 不会。
// 显式让出一轮事件循环，复现真实运行时「脚本结束后回调才执行」的时序。
function flush() {
  return new Promise(function (resolve) { setImmediate(resolve); });
}

const result = {
  parse: [],
  blocks: [],
  practices: [],
  judge: { ok: false, failures: [], output: '' },
  starter: { failedAsExpected: false, failures: [], error: '', output: '' }
};

(async function () {
  const sources = task.blocks.map(function (b) { return b.code; })
    .concat([task.solution, task.starter])
    .concat(task.tests);
  sources.forEach(function (src, i) {
    try { new Function(src); }
    catch (e) { result.parse.push({ index: i, error: String((e && e.message) || e) }); }
  });

  for (let i = 0; i < task.blocks.length; i++) {
    const sb = makeSandbox();
    vm.createContext(sb.sandbox);
    try {
      runScript(task.blocks[i].code, sb.sandbox, 5000);
      await flush();
      result.blocks.push({ index: i, ok: true, output: sb.out.join('\n'), error: '' });
    } catch (e) {
      result.blocks.push({
        index: i, ok: false, output: sb.out.join('\n'),
        error: String((e && e.message) || e)
      });
    }
  }

  for (let i = 0; i < task.practices.length; i++) {
    const sb = makeSandbox();
    vm.createContext(sb.sandbox);
    try {
      runScript(task.practices[i].code, sb.sandbox, 5000);
      await flush();
      result.practices.push({ index: i, ok: true, output: sb.out.join('\n'), error: '' });
    } catch (e) {
      result.practices.push({ index: i, ok: false, output: sb.out.join('\n'), error: String((e && e.message) || e) });
    }
  }

  try {
    const sb = makeSandbox();
    vm.createContext(sb.sandbox);
    runScript(task.solution, sb.sandbox, 5000);
    await flush();
    for (let i = 0; i < task.tests.length; i++) {
      try { runScript(task.tests[i], sb.sandbox, 2000); }
      catch (e) { result.judge.failures.push({ index: i + 1, reason: String((e && e.message) || e) }); }
      await flush();
    }
    result.judge.output = sb.out.join('\n');
    result.judge.ok = result.judge.failures.length === 0;
  } catch (e) {
    result.judge.failures.push({ index: 0, reason: 'solution: ' + String((e && e.message) || e) });
  }

  try {
    const sb = makeSandbox();
    vm.createContext(sb.sandbox);
    runScript(task.starter, sb.sandbox, 5000);
    await flush();
    for (let i = 0; i < task.tests.length; i++) {
      try { runScript(task.tests[i], sb.sandbox, 2000); }
      catch (e) { result.starter.failures.push({ index: i + 1, reason: String((e && e.message) || e) }); }
      await flush();
    }
    result.starter.output = sb.out.join('\n');
    result.starter.failedAsExpected = result.starter.failures.length > 0;
  } catch (e) {
    result.starter.error = String((e && e.message) || e);
    result.starter.failedAsExpected = true;
  }

  process.stdout.write(JSON.stringify(result));
})();
"""

FORBIDDEN = [
    (r"\bclass\s+[A-Za-z_$]", "class 语法"),
    (r"\.\.\.", "展开/rest 解构之外的 ... 语法"),
    (r"function\s*\([^)]*=[^)]*\)", "函数默认参数"),
    (r"function\s+[A-Za-z_$][\w$]*\s*\([^)]*=", "函数默认参数"),
    (r"\basync\b", "async 语法"),
    (r"\bawait\b", "await 语法"),
    (r"\?\.", "可选链"),
    (r"\?\?", "空值合并"),
    (r"\bimport\s", "import 语法"),
    (r"\brequire\s*\(", "require 调用"),
    (r"\bprocess\b", "process 对象"),
    (r"\bsetTimeout\s*\(", "setTimeout"),
    (r"\bsetInterval\s*\(", "setInterval"),
    (r"\bfetch\s*\(", "fetch"),
    (r"\bdocument\b", "document 对象"),
    (r"\bwindow\b", "window 对象"),
]

def strip_strings_and_comments(src: str) -> str:
    """粗略去掉字符串与注释，避免误报（课程文本里会有 class 等词）。"""
    out = []
    i = 0
    n = len(src)
    while i < n:
        ch = src[i]
        if ch in ("'", '"', "`"):
            quote = ch
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                    continue
                if src[i] == quote:
                    i += 1
                    break
                i += 1
            out.append(" ")
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                i += 1
            out.append(" ")
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "*":
            i += 2
            while i + 1 < n and not (src[i] == "*" and src[i + 1] == "/"):
                i += 1
            i += 2
            out.append(" ")
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def check_forbidden(lesson_id, where, src):
    problems = []
    cleaned = strip_strings_and_comments(src)
    for pattern, label in FORBIDDEN:
        if pattern == r"\.\.\.":
            # 允许给 rest 参数：函数形参里的 ...name
            for m in re.finditer(r"\.\.\.", cleaned):
                tail = cleaned[m.end():]
                if re.match(r"[A-Za-z_$][\w$]*", tail) and "function" in cleaned[: m.start()][-80:]:
                    continue
                if re.match(r"[A-Za-z_$][\w$]*", tail) and re.match(
                    r"\s*(?:var|let|const)\s*\[[^\]]*$", cleaned[: m.start()]
                ):
                    continue
                problems.append(f"{lesson_id}: {where} 使用了 {label}")
                break
            continue
        if re.search(pattern, cleaned):
            problems.append(f"{lesson_id}: {where} 使用了 {label}")
    return problems


def normalise(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    while lines and lines[-1] == "":
        lines.pop()
    while lines and lines[0] == "":
        lines.pop(0)
    return "\n".join(line.rstrip() for line in lines)


def find_node():
    found = shutil.which("node")
    if found:
        return found
    for candidate in (r"C:\Program Files\nodejs\node.exe",):
        if os.path.exists(candidate):
            return candidate
    return None


NODE = find_node()
VERBOSE = False


def load_pack(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def check_structure(pack_id, chapter, chapter_name, base_order, lessons):
    problems = []
    if len(lessons) != 10:
        problems.append(f"{pack_id}: 应为 10 讲，实际 {len(lessons)}")
    ids = [l.get("id") for l in lessons]
    if len(set(ids)) != len(ids):
        problems.append(f"{pack_id}: 包内 id 重复")
    for i, lesson in enumerate(lessons):
        lid = lesson.get("id")
        expected_id = f"{pack_id.split('-')[0]}{base_order - 299 + i:02d}"
        # js-basics -> js01 .. js10，js-core -> js11 .. js20，js-advanced -> js21 .. js30
        if lid != expected_id:
            problems.append(f"{pack_id}: 第 {i+1} 讲 id 应为 {expected_id}，实际 {lid}")
        if lesson.get("order") != base_order + i:
            problems.append(f"{lid}: order 应为 {base_order + i}，实际 {lesson.get('order')}")
        if lesson.get("chapter") != chapter:
            problems.append(f"{lid}: chapter 应为 {chapter}")
        if lesson.get("chapterName") != chapter_name:
            problems.append(f"{lid}: chapterName 不一致")
        if lesson.get("lang") != "javascript":
            problems.append(f"{lid}: lang 应为 javascript")

        blocks = lesson.get("blocks") or []
        types = [b.get("type") for b in blocks]
        if types.count("heading") != 1:
            problems.append(f"{lid}: 应有且仅有 1 个 heading，实际 {types.count('heading')}")
        if types.count("text") < 2:
            problems.append(f"{lid}: text 少于 2 段")
        if types.count("code") < 2:
            problems.append(f"{lid}: 代码块少于 2 个")
        if types.count("code") != types.count("output"):
            problems.append(f"{lid}: code 与 output 数量不匹配")
        if not any(t in ("table", "diagram") for t in types):
            problems.append(f"{lid}: 缺少 table 或 diagram")
        if not any(t in ("tip", "warn") for t in types):
            problems.append(f"{lid}: 缺少 tip 或 warn")
        if "quiz" not in types:
            problems.append(f"{lid}: 缺少 quiz")
        if len(blocks) < 8:
            problems.append(f"{lid}: 内容块少于 8 个")

        for block in blocks:
            if block.get("type") == "quiz":
                options = block.get("options") or []
                if len(options) != 4:
                    problems.append(f"{lid}: quiz 应有 4 个选项")
                if not (isinstance(block.get("answer"), int) and 0 <= block["answer"] < len(options)):
                    problems.append(f"{lid}: quiz answer 越界")
            if block.get("type") == "code" and not block.get("runnable"):
                problems.append(f"{lid}: 代码块必须显式 runnable")
            if block.get("type") == "table":
                width = len(block.get("headers") or [])
                for row in block.get("rows") or []:
                    if len(row) != width:
                        problems.append(f"{lid}: 表格列数不一致")
            if block.get("type") == "fill":
                if "____" not in block.get("code", ""):
                    problems.append(f"{lid}: fill 缺少空格占位")

        ex = lesson.get("exercise") or {}
        for key in ("title", "brief", "starterCode", "hint", "tests", "stdin", "xp", "solution"):
            if key not in ex:
                problems.append(f"{lid}: exercise 缺少 {key}")
        tests = ex.get("tests") or []
        if not (3 <= len(tests) <= 5):
            problems.append(f"{lid}: tests 应为 3-5 条，实际 {len(tests)}")
        if not str(ex.get("starterCode", "")).strip():
            problems.append(f"{lid}: starterCode 为空")
        if not str(ex.get("solution", "")).strip():
            problems.append(f"{lid}: solution 为空")

        for block in blocks:
            if block.get("type") == "code":
                problems.extend(check_forbidden(lid, "代码块", block["code"]))
            if block.get("type") == "practice":
                problems.extend(check_forbidden(lid, "practice", block["code"]))
        problems.extend(check_forbidden(lid, "starterCode", ex.get("starterCode", "")))
        problems.extend(check_forbidden(lid, "solution", ex.get("solution", "")))
        for t in tests:
            problems.extend(check_forbidden(lid, "test", t))
    return problems


def run_lesson(node, harness_path, work_dir, lesson):
    blocks = [b for b in lesson["blocks"] if b.get("type") == "code"]
    outputs = [b for b in lesson["blocks"] if b.get("type") == "output"]
    task = {
        "blocks": [{"code": b["code"], "runnable": b.get("runnable", False)} for b in blocks],
        "starter": lesson["exercise"]["starterCode"],
        "solution": lesson["exercise"]["solution"],
        "tests": lesson["exercise"]["tests"],
        "practices": [
            {"code": b["code"], "output": b["output"]}
            for b in lesson["blocks"] if b.get("type") == "practice"
        ],
    }
    task_path = Path(work_dir) / f"{lesson['id']}.json"
    task_path.write_text(json.dumps(task, ensure_ascii=False), encoding="utf-8")
    proc = subprocess.run(
        [node, str(harness_path), str(task_path)],
        capture_output=True,
        text=True,
        timeout=90,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        return None, f"node 执行失败: {proc.stderr.strip()[:500]}"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError:
        return None, f"harness 输出无法解析: {proc.stdout[:300]}"


def verify_lesson(node, harness_path, work_dir, lesson):
    failures = []
    result, err = run_lesson(node, harness_path, work_dir, lesson)
    if err:
        return [f"{lesson['id']}: {err}"]

    parse = result.get("parse") or []
    if parse:
        failures.append(f"{lesson['id']}: 存在语法错误 {[p.get('error') for p in parse]}")

    code_blocks = [b for b in lesson["blocks"] if b.get("type") == "code"]
    output_blocks = [b for b in lesson["blocks"] if b.get("type") == "output"]
    block_results = result.get("blocks") or []
    if len(block_results) != len(code_blocks):
        failures.append(f"{lesson['id']}: 代码块执行结果数量不匹配")
    for i, br in enumerate(block_results):
        if not br.get("ok"):
            failures.append(f"{lesson['id']}: 代码块 #{i+1} 抛错 {br.get('error')}")
            continue
        if i < len(output_blocks):
            actual = normalise(br.get("output", ""))
            expected = normalise(output_blocks[i].get("text", ""))
            if actual != expected:
                failures.append(
                    f"{lesson['id']}: 代码块 #{i+1} 输出不一致\n"
                    f"    期望: {expected!r}\n    实际: {actual!r}"
                )
        else:
            failures.append(f"{lesson['id']}: 代码块 #{i+1} 缺少 output 块")

    practice_blocks = [b for b in lesson["blocks"] if b.get("type") == "practice"]
    practice_results = result.get("practices") or []
    for i, pr in enumerate(practice_results):
        if not pr.get("ok"):
            failures.append(f"{lesson['id']}: practice #{i+1} 抛错 {pr.get('error')}")
        elif i < len(practice_blocks):
            actual = normalise(pr.get("output", ""))
            expected = normalise(practice_blocks[i].get("output", ""))
            if actual != expected:
                failures.append(
                    f"{lesson['id']}: practice #{i+1} 输出不一致\n"
                    f"    期望: {expected!r}\n    实际: {actual!r}"
                )

    judge = result.get("judge") or {}
    if not judge.get("ok"):
        items = judge.get("failures") or []
        detail = "; ".join(f"#{f.get('index')} {f.get('reason')}" for f in items[:4])
        failures.append(f"{lesson['id']}: solution 未通过全部判题 {detail}")

    starter = result.get("starter") or {}
    if not starter.get("failedAsExpected"):
        failures.append(f"{lesson['id']}: starterCode 不应通过判题（空壳实现必须失败）")

    return failures


def main():
    global VERBOSE
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    VERBOSE = args.verbose

    if not NODE:
        print("FAIL: 未找到 node，无法执行真实运行验证", file=sys.stderr)
        return 2

    problems = []
    total_lessons = 0
    passed_lessons = 0
    total_blocks = 0
    total_tests = 0
    seen_ids = set()
    seen_orders = set()

    with tempfile.TemporaryDirectory(prefix="js_pack_verify_") as work_dir:
        harness_path = Path(work_dir) / "harness.js"
        harness_path.write_text(HARNESS, encoding="utf-8")

        for pack_id, chapter, chapter_name, base_order in PACKS:
            path = ROOT / "content_packs" / f"{pack_id}.json"
            if not path.exists():
                problems.append(f"{pack_id}: 缺少文件 {path.name}")
                continue
            try:
                lessons = load_pack(path)
            except json.JSONDecodeError as exc:
                problems.append(f"{pack_id}: JSON 解析失败 {exc}")
                continue
            if not isinstance(lessons, list):
                problems.append(f"{pack_id}: 顶层应为数组")
                continue

            pack_problems = check_structure(pack_id, chapter, chapter_name, base_order, lessons)
            problems.extend(pack_problems)

            for lesson in lessons:
                lid = lesson.get("id")
                if lid in seen_ids:
                    problems.append(f"重复 id: {lid}")
                seen_ids.add(lid)
                if lesson.get("order") in seen_orders:
                    problems.append(f"重复 order: {lesson.get('order')}")
                seen_orders.add(lesson.get("order"))

            total_lessons += len(lessons)
            pack_passed = 0
            for lesson in lessons:
                failures = verify_lesson(NODE, harness_path, work_dir, lesson)
                total_blocks += len([b for b in lesson["blocks"] if b.get("type") == "code"])
                total_tests += len(lesson["exercise"]["tests"])
                if failures:
                    problems.extend(failures)
                else:
                    passed_lessons += 1
                    pack_passed += 1
                if VERBOSE:
                    status = "PASS" if not failures else "FAIL"
                    print(f"[{status}] {lesson['id']} {lesson['title']}")
            print(f"{pack_id}: {pack_passed}/{len(lessons)} 讲通过")

    print()
    print(f"包数={len(PACKS)} 讲数={total_lessons} 通过讲数={passed_lessons}")
    print(f"代码块={total_blocks} 判题用例={total_tests}")
    if problems:
        print(f"失败项={len(problems)}")
        for p in problems:
            print("FAIL:", p)
        return 1
    print("结果=全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
