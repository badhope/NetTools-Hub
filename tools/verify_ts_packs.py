#!/usr/bin/env python3
"""TypeScript 课程包验证器。

两层验证：
  1) 结构校验：JSON 可解析、讲数/id/order/chapter、块类型与字段、exercise 字段齐全、
     正文汉字数、代码块可运行标记、quiz 答案下标。
  2) 逻辑校验：把 TS 按 TypeScriptTranspiler 的简化规则擦除成等价 JS（不含复杂
     类型语法），再用 Node 真跑 solution + tests；同时确认 starter 单独跑不通过。

擦除器只做减法，不试图实现完整 TypeScript：
  - 删 interface / type 别名 / declare 整段
  - 删函数名后的泛型参数表
  - 删变量、参数、返回值的类型标注（含对象字面量键的区分）
  - 删 as 断言、非空断言
  - enum 转 Object.freeze 对象
它只保证「课程里实际出现的类型写法」能被正确擦掉，超出范围会直接报错而不是猜。

用法：
  python tools/verify_ts_packs.py            # 全部校验
  python tools/verify_ts_packs.py --no-node  # 只做结构校验
"""

import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS = ["ts-basics.json", "ts-core.json", "ts-advanced.json"]

EXPECTED = {
    "ts-basics.json": ("ts", 600, 61, "TypeScript · 基础篇"),
    "ts-core.json": ("ts", 610, 62, "TypeScript · 核心篇"),
    "ts-advanced.json": ("ts", 620, 63, "TypeScript · 进阶篇"),
}

ALLOWED_BLOCKS = {
    "heading", "text", "code", "output", "table", "diagram", "tip", "warn",
    "quiz", "practice", "steps", "task", "fill", "order", "compare", "visualize",
}

CJK = re.compile(r"[\u4e00-\u9fff]")


class VerifyError(Exception):
    pass


# ---------------------------------------------------------------- 结构校验

def check_lesson_schema(lesson, pack_name, index):
    where = f"{pack_name}#{index}"

    def need(cond, msg):
        if not cond:
            raise VerifyError(f"[{where}] {msg}")

    for key in ("id", "order", "chapter", "chapterName", "lang", "title", "subtitle",
                "xp", "blocks", "exercise"):
        need(key in lesson, f"缺少字段 {key}")
    need(lesson["lang"] == "typescript", "lang 必须是 typescript")
    need(isinstance(lesson["xp"], int) and lesson["xp"] > 0, "xp 必须是正整数")

    blocks = lesson["blocks"]
    need(isinstance(blocks, list) and len(blocks) >= 8, f"内容块应至少 8 个，实际 {len(blocks)}")

    kinds = [b.get("type") for b in blocks]
    for k in kinds:
        need(k in ALLOWED_BLOCKS, f"未知块类型 {k}")
    need(kinds.count("heading") >= 1, "至少一个 heading")
    need(kinds.count("text") >= 2, "至少两个 text")
    need(kinds.count("code") >= 1, "至少一个 code")
    need(kinds.count("output") >= 1, "至少一个 output")
    need(kinds.count("quiz") >= 1, "至少一个 quiz")
    need(kinds.count("table") + kinds.count("diagram") >= 1, "至少一个 table 或 diagram")
    need(kinds.count("tip") + kinds.count("warn") >= 1, "至少一个 tip 或 warn")

    runnable = 0
    for i, b in enumerate(blocks):
        t = b["type"]
        if t in ("heading", "text", "tip", "warn", "task", "output"):
            need(isinstance(b.get("text"), str) and b["text"].strip(), f"块 {i}({t}) 缺 text")
        elif t == "code":
            need(isinstance(b.get("code"), str) and b["code"].strip(), f"块 {i}(code) 缺 code")
            if b.get("runnable", True):
                runnable += 1
        elif t == "table":
            need(isinstance(b.get("headers"), list) and len(b["headers"]) >= 2, f"块 {i}(table) headers 不合法")
            need(isinstance(b.get("rows"), list) and b["rows"], f"块 {i}(table) rows 为空")
            for row in b["rows"]:
                need(len(row) == len(b["headers"]), f"块 {i}(table) 行列数不匹配")
        elif t == "diagram":
            need(isinstance(b.get("text"), str) and b["text"].strip(), f"块 {i}(diagram) 缺 text")
        elif t == "quiz":
            opts = b.get("options")
            need(isinstance(opts, list) and len(opts) >= 2, f"块 {i}(quiz) options 不足")
            need(isinstance(b.get("answer"), int) and 0 <= b["answer"] < len(opts), f"块 {i}(quiz) answer 越界")
        elif t == "practice":
            for key in ("title", "code", "output", "hint"):
                need(isinstance(b.get(key), str) and b[key].strip(), f"块 {i}(practice) 缺 {key}")
        elif t == "fill":
            for key in ("goal", "code", "answer", "explain"):
                need(isinstance(b.get(key), str) and b[key].strip(), f"块 {i}(fill) 缺 {key}")
        elif t == "steps":
            need(isinstance(b.get("items"), list) and len(b["items"]) >= 2, f"块 {i}(steps) items 不足")
        elif t == "order":
            need(isinstance(b.get("lines"), list) and len(b["lines"]) >= 2, f"块 {i}(order) lines 不足")
        elif t == "compare":
            cols = b.get("columns")
            need(isinstance(cols, list) and len(cols) >= 2, f"块 {i}(compare) columns 不足")

    need(runnable >= 1, "至少一个可运行代码块")

    ex = lesson["exercise"]
    for key in ("title", "brief", "starterCode", "hint", "tests", "stdin", "xp", "solution"):
        need(key in ex, f"exercise 缺少 {key}")
    need(isinstance(ex["tests"], list) and 3 <= len(ex["tests"]) <= 5, "tests 应为 3-5 条")
    for t in ex["tests"]:
        need("assert(" in t, f"测试用例必须使用 assert：{t[:40]}")
    need(isinstance(ex["solution"], str) and ex["solution"].strip(), "solution 为空")
    need(isinstance(ex["starterCode"], str) and ex["starterCode"].strip(), "starterCode 为空")
    need(isinstance(ex["xp"], int) and ex["xp"] > 0, "exercise xp 必须是正整数")


def count_cjk(lesson):
    """正文汉字数：只统计 text 块的讲解文字，不含标题、代码与练习说明。"""
    return sum(len(CJK.findall(b.get("text", ""))) for b in lesson["blocks"] if b["type"] == "text")


def check_structure():
    all_ids = []
    total_cases = 0
    report = []

    for pack_name in PACKS:
        path = ROOT / "content_packs" / pack_name
        if not path.exists():
            raise VerifyError(f"缺少文件 {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise VerifyError(f"{pack_name} JSON 解析失败：{e}")
        if not isinstance(data, list):
            raise VerifyError(f"{pack_name} 顶层必须是数组")
        if len(data) != 10:
            raise VerifyError(f"{pack_name} 应有 10 讲，实际 {len(data)}")

        _prefix, base_order, chapter, chapter_name = EXPECTED[pack_name]
        for i, lesson in enumerate(data):
            check_lesson_schema(lesson, pack_name, i)
            lid = lesson["id"]
            if not re.fullmatch(r"ts\d{2}", lid):
                raise VerifyError(f"{pack_name}#{i} id 格式不合法：{lid}")
            all_ids.append(lid)
            if lesson["order"] != base_order + i:
                raise VerifyError(f"{pack_name}#{i} order 应为 {base_order + i}，实际 {lesson['order']}")
            if lesson["chapter"] != chapter:
                raise VerifyError(f"{pack_name}#{i} chapter 应为 {chapter}")
            if lesson["chapterName"] != chapter_name:
                raise VerifyError(f"{pack_name}#{i} chapterName 应为 {chapter_name}")
            prose = count_cjk(lesson)
            if not 900 <= prose <= 1600:
                raise VerifyError(f"{pack_name}#{i} {lid} 正文汉字数 {prose} 不在 900-1600")
            total_cases += len(lesson["exercise"]["tests"])
            report.append((pack_name, lid, len(lesson["blocks"]), prose, len(lesson["exercise"]["tests"])))

    if len(set(all_ids)) != len(all_ids):
        dup = [x for x in set(all_ids) if all_ids.count(x) > 1]
        raise VerifyError(f"存在重复 id：{dup}")
    expected_ids = [f"ts{i:02d}" for i in range(1, 31)]
    if sorted(all_ids) != expected_ids:
        raise VerifyError(f"id 集合不完整，缺少 {sorted(set(expected_ids) - set(all_ids))}")

    return report, total_cases


# ---------------------------------------------------------------- 简化擦除

# 这些关键字开头的是表达式，不是类型标注
VALUE_KEYWORDS = {
    "true", "false", "this", "new", "typeof", "in", "instanceof",
    "void", "delete", "yield", "await", "function", "return",
}


def strip_comments_and_strings(src):
    """返回掩码：字符串与注释内容替换成空格，长度不变，便于定位。"""
    out = list(src)
    i = 0
    n = len(src)
    while i < n:
        ch = src[i]
        if ch in "'\"`":
            quote = ch
            out[i] = " "
            i += 1
            while i < n:
                if src[i] == "\\":
                    out[i] = " "
                    if i + 1 < n:
                        out[i + 1] = " "
                    i += 2
                    continue
                if src[i] == quote:
                    out[i] = " "
                    i += 1
                    break
                out[i] = " "
                i += 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                out[i] = " "
                i += 1
            continue
        if ch == "/" and i + 1 < n and src[i + 1] == "*":
            out[i] = out[i + 1] = " "
            i += 2
            while i + 1 < n and not (src[i] == "*" and src[i + 1] == "/"):
                out[i] = " "
                i += 1
            if i + 1 < n:
                out[i] = out[i + 1] = " "
                i += 2
            continue
        i += 1
    return "".join(out)


def strip_interfaces(src):
    out = []
    i = 0
    while True:
        m = re.search(r"\binterface\s+\w+(?:\s*<[^<>{}]*>)?(?:\s+extends\s+[^{]+)?\s*\{", src[i:])
        if not m:
            out.append(src[i:])
            break
        start = i + m.start()
        out.append(src[i:start])
        j = i + m.end() - 1  # 指向 '{'
        depth = 0
        while j < len(src):
            if src[j] == "{":
                depth += 1
            elif src[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        end = j + 1
        while end < len(src) and src[end] in " \t\r\n":
            end += 1
        out.append("\n")
        i = end
    return "".join(out)


def strip_type_aliases(src):
    lines = src.split("\n")
    result = []
    i = 0
    while i < len(lines):
        trimmed = lines[i].lstrip()
        if re.match(r"type\s+\w+(\s*<[^>]*>)?\s*=", trimmed):
            depth = lines[i].count("{") - lines[i].count("}")
            j = i
            while depth > 0 and j + 1 < len(lines):
                j += 1
                depth += lines[j].count("{") - lines[j].count("}")
            result.append("")
            i = j + 1
            continue
        result.append(lines[i])
        i += 1
    return "\n".join(result)


def strip_declare(src):
    return "\n".join("" if line.lstrip().startswith("declare ") else line for line in src.split("\n"))


def convert_enums(src):
    def repl(m):
        name = m.group(1)
        body = m.group(2)
        next_val = 0
        entries = []
        for raw in body.split(","):
            item = raw.strip()
            if not item:
                continue
            if "=" in item:
                key, val = item.split("=", 1)
                key = key.strip()
                val = val.strip()
                entries.append(f"{key}: {val}")
                if re.fullmatch(r"-?\d+", val):
                    next_val = int(val) + 1
            else:
                entries.append(f"{item}: {next_val}")
                next_val += 1
        return "var %s = Object.freeze({ %s })" % (name, ", ".join(entries))

    return re.sub(r"enum\s+(\w+)\s*\{([^}]*)\}", repl, src)


def strip_access_modifiers(src):
    return re.sub(r"\b(public|private|protected|readonly)\s+", "", src)


def strip_generic_params(src):
    src = re.sub(r"(function\s+\w+)\s*<[^<>()]*>\s*\(", r"\1(", src)
    return src


def strip_as_casts(src):
    return re.sub(r"\s+as\s+[A-Za-z_$][\w$]*(<[^<>]*>)?(\[\])?", "", src)


def strip_non_null(src):
    return re.sub(r"([\w$\])])!(?=[.\[]|;|,|\)|\s|$)", r"\1", src)


def looks_like_ternary(out):
    """判断这个冒号是不是三元运算符的冒号：同一表达式内前面有未配对的 ?。"""
    depth = 0
    i = len(out) - 1
    while i >= 0:
        ch = out[i]
        if ch == ")":
            depth += 1
        elif ch == "(":
            depth -= 1
        elif ch == "?" and depth == 0:
            return True
        elif ch in ";{}\n" and depth == 0:
            return False
        i -= 1
    return False


def erase_types(src):
    """按转译器的核心规则擦除类型标注。

    只处理课程里出现的形状：冒号后跟一个简单类型表达式，终止于 = ; , ) { } 换行。
    对象字面量的键（前面是 { 或 , 且处于花括号内）不擦。
    """
    mask = strip_comments_and_strings(src)
    out = []
    i = 0
    n = len(src)
    brace = 0
    paren = 0
    while i < n:
        ch = src[i]
        if mask[i] != ch:
            # 字符串 / 注释内部：原样拷贝
            out.append(ch)
            i += 1
            continue
        if ch == "{":
            brace += 1
            out.append(ch)
            i += 1
            continue
        if ch == "}":
            brace = max(0, brace - 1)
            out.append(ch)
            i += 1
            continue
        if ch == "(":
            paren += 1
            out.append(ch)
            i += 1
            continue
        if ch == ")":
            paren = max(0, paren - 1)
            out.append(ch)
            i += 1
            continue
        if ch != ":":
            out.append(ch)
            i += 1
            continue

        # 三元表达式的冒号：向前找同一表达式内未配对的 ?
        if looks_like_ternary(out):
            out.append(ch)
            i += 1
            continue

        # 判断是否对象键：在花括号内、前一个 token 是标识符且它的前面是 { 或 ,
        prev_nonspace = len(out) - 1
        while prev_nonspace >= 0 and out[prev_nonspace] in " \t":
            prev_nonspace -= 1
        if paren == 0 and brace > 0 and prev_nonspace >= 0 and (out[prev_nonspace].isalnum() or out[prev_nonspace] in "_$"):
            j = prev_nonspace
            while j >= 0 and (out[j].isalnum() or out[j] in "_$"):
                j -= 1
            k = j
            while k >= 0 and out[k] in " \t":
                k -= 1
            if k >= 0 and out[k] in "{,":
                out.append(ch)
                i += 1
                continue

        # 读类型表达式
        j = i + 1
        while j < n and src[j] in " \t":
            j += 1
        start = j
        depth = 0
        while j < n:
            c = src[j]
            if c in "<([":
                depth += 1
            elif c in ">)]":
                if depth == 0:
                    break
                depth -= 1
            elif c in "=;,{}\n\r" and depth == 0:
                break
            j += 1
        type_text = src[start:j].strip()
        head = re.split(r"[<\[]", type_text)[0].strip()
        if (not type_text
                or not re.fullmatch(r"[A-Za-z_$][\w$<>\[\].|&\s,'\"]*", type_text)
                or head in VALUE_KEYWORDS):
            out.append(ch)
            i += 1
            continue
        # 擦除标注（以及冒号前的空格）
        while out and out[-1] == " ":
            out.pop()
        next_ch = src[j] if j < n else ""
        if next_ch in "=:" or (next_ch and (next_ch.isalnum() or next_ch in "_$")):
            out.append(" ")
        i = j
    return "".join(out).rstrip()


def transpile(src):
    s = strip_interfaces(src)
    s = strip_type_aliases(s)
    s = strip_declare(s)
    s = convert_enums(s)
    s = strip_access_modifiers(s)
    s = strip_generic_params(s)
    s = erase_types(s)
    s = strip_as_casts(s)
    s = strip_non_null(s)
    return s


# ---------------------------------------------------------------- Node 执行

ASSERT_SHIM = "function assert(c, m) { if (!c) { throw new Error(m || 'assert failed'); } }\n"


def node_available():
    return shutil.which("node") is not None


def run_node(script):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "case.js"
        path.write_text(script, encoding="utf-8")
        proc = subprocess.run(
            ["node", str(path)],
            capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def check_logic(run_checks=True):
    results = []
    for pack_name in PACKS:
        data = json.loads((ROOT / "content_packs" / pack_name).read_text(encoding="utf-8"))
        for lesson in data:
            lid = lesson["id"]
            ex = lesson["exercise"]
            js_solution = transpile(ex["solution"])
            js_tests = [transpile(t) for t in ex["tests"]]
            js_starter = transpile(ex["starterCode"])

            joined_solution = ASSERT_SHIM + js_solution + "\n" + "\n".join(js_tests) + "\n"
            joined_starter = ASSERT_SHIM + js_starter + "\n" + "\n".join(js_tests) + "\n"

            if run_checks:
                code_ok, out_ok = run_node(joined_solution)
                if code_ok != 0:
                    raise VerifyError(
                        f"[{lid}] solution 未通过 tests：\n{out_ok}\n--- 擦除后 ---\n{js_solution}"
                    )
                code_bad, out_bad = run_node(joined_starter)
                if code_bad == 0:
                    raise VerifyError(f"[{lid}] starter 竟然直接通过了 tests（题目没有意义）")
            results.append((lid, js_solution, js_tests))
    return results


# ---------------------------------------------------------------- 入口

def main():
    args = set(sys.argv[1:])
    run_node_checks = "--no-node" not in args

    print("== 结构校验 ==")
    report, total_cases = check_structure()
    for pack_name, lid, blocks, prose, cases in report:
        print(f"  {pack_name:18s} {lid}  块={blocks:2d}  正文={prose:4d}字  用例={cases}")

    print("== 擦除校验 ==")
    runnable_blocks = []
    for pack_name in PACKS:
        data = json.loads((ROOT / "content_packs" / pack_name).read_text(encoding="utf-8"))
        for lesson in data:
            for idx, b in enumerate(lesson["blocks"]):
                if b["type"] != "code":
                    continue
                js = transpile(b["code"])
                if re.search(r"\b(interface|declare)\s+\w", js):
                    raise VerifyError(f"[{lesson['id']}] 代码块擦除后仍残留声明关键字")
                if b.get("runnable", True):
                    runnable_blocks.append((lesson["id"], idx, js))
    print(f"  {len(runnable_blocks)} 个可运行代码块全部擦除成功，无声明残留")

    if run_node_checks:
        if not node_available():
            raise VerifyError("未找到 node，无法执行逻辑校验；可用 --no-node 只跑结构校验")
        print("== Node 执行校验 ==")
        for lid, idx, js in runnable_blocks:
            code, out = run_node(ASSERT_SHIM + js + "\n")
            if code != 0:
                raise VerifyError(f"[{lid}] 第 {idx} 个代码块运行失败：\n{out}")
        print(f"  {len(runnable_blocks)} 个讲解代码块全部正常运行")
        results = check_logic(True)
        print(f"  {len(results)} 讲：solution 全部通过，starter 全部不通过")
    else:
        print("== Node 执行校验：已跳过（--no-node）==")

    print()
    print(f"通过：3 个课程包，30 讲，{total_cases} 条判题用例")


if __name__ == "__main__":
    try:
        main()
    except VerifyError as e:
        print(f"\n验证失败：{e}", file=sys.stderr)
        sys.exit(1)
