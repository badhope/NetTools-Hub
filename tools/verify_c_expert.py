#!/usr/bin/env python3
"""C 语言「专业篇」课程包（content_packs/c-expert.json）结构校验 + 真实解释器验证。

层次与 tools/verify_c_packs.py 一致：
  1. 结构层（纯 Python）：JSON 可解析、8 讲、id/order/chapter、内容块数量与
     类型、正文汉字数、quiz/table 合法性、禁用语法扫描。
  2. 语义层（Gradle + 真实 CInterpreter）：生成临时 JUnit 测试，逐讲验证
     - 每个 runnable 代码块执行成功，且 stdout 与紧跟的 output 块一致
     - 每个 exercise 的 solution + tests 全部通过
     - 每个 exercise 的 starterCode + tests 至少失败一条
     - runnable=false 的参考块确实无法执行（证明标注诚实）
     跑完在 finally 中删除临时测试文件。

用法：
    python tools/verify_c_expert.py
    python tools/verify_c_expert.py --skip-gradle     # 只做结构校验
    python tools/verify_c_expert.py --gradle-home C:\\Dev\\gradle-home-mashang ^
                                    --android-home C:\\Dev\\android-sdk

退出码 0 表示全部通过，1 表示有失败项，2 表示无法执行 Gradle。
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_PATH = ROOT / "content_packs" / "c-expert.json"
TEMP_TEST = ROOT / "app/src/test/java/com/pyneon/academy/c/TempCExpertVerificationTest.kt"

EXPECTED_IDS = [f"c{n}" for n in range(31, 39)]
EXPECTED_ORDERS = list(range(730, 738))
CHAPTER = 74
CHAPTER_NAME = "C · 专业篇"

FORBIDDEN_IN_RUNNABLE = [
    (r"#\s*include", "#include"),
    (r"#\s*define", "#define"),
    (r"(?m)^\s*#", "预处理指令"),
    (r"\bgoto\b", "goto"),
    (r"\benum\b", "enum"),
    (r"\bunion\b", "union"),
    (r"\bscanf\b", "scanf"),
    (r"\bmalloc\b", "malloc"),
    (r"\bcalloc\b", "calloc"),
    (r"\brealloc\b", "realloc"),
    (r"\bfree\s*\(", "free"),
    (r"\bfopen\b", "fopen"),
    (r"\bfclose\b", "fclose"),
    (r"\bfread\b", "fread"),
    (r"\bfwrite\b", "fwrite"),
    (r"\bFILE\b", "FILE 文件流"),
    (r"\(\s*\*\s*[A-Za-z_]\w*\s*\)\s*\(", "函数指针"),
    (r"\.\.\.", "可变参数"),
]

HAN_RE = re.compile(r"[\u4e00-\u9fff]")
SINGLE_RUNNABLE_IDS = {"c32", "c33", "c35"}
REFERENCE_ALLOWED_IDS = {"c32", "c33", "c35"}


def han_count(text):
    return len(HAN_RE.findall(text))


def strip_literals(src):
    """去掉字符串/字符字面量与注释，避免文本里的关键字造成误报。"""
    out = []
    i, n = 0, len(src)
    while i < n:
        ch = src[i]
        if ch in ("'", '"'):
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


def check_forbidden(where, src):
    cleaned = strip_literals(src)
    problems = []
    for pattern, label in FORBIDDEN_IN_RUNNABLE:
        if re.search(pattern, cleaned):
            problems.append(f"{where}: 使用了课程不支持的 {label}")
    return problems


def check_lesson(lesson, index):
    lid = lesson.get("id", f"#{index}")
    problems = []

    if lid != EXPECTED_IDS[index]:
        problems.append(f"{lid}: id 应为 {EXPECTED_IDS[index]}")
    if lesson.get("order") != EXPECTED_ORDERS[index]:
        problems.append(f"{lid}: order 应为 {EXPECTED_ORDERS[index]}，实际 {lesson.get('order')}")
    if lesson.get("chapter") != CHAPTER:
        problems.append(f"{lid}: chapter 应为 {CHAPTER}")
    if lesson.get("chapterName") != CHAPTER_NAME:
        problems.append(f"{lid}: chapterName 应为 {CHAPTER_NAME}")
    if lesson.get("lang") != "c":
        problems.append(f"{lid}: lang 应为 c")
    for key in ("title", "subtitle"):
        if not str(lesson.get(key, "")).strip():
            problems.append(f"{lid}: 缺少 {key}")
    if not isinstance(lesson.get("xp"), int) or lesson["xp"] <= 0:
        problems.append(f"{lid}: xp 应为正整数")

    blocks = lesson.get("blocks") or []
    if not isinstance(blocks, list) or len(blocks) < 10:
        problems.append(f"{lid}: 内容块应 >= 10，实际 {len(blocks)}")
        return problems
    types = [b.get("type") for b in blocks]
    if types.count("heading") != 1:
        problems.append(f"{lid}: 应有且仅有 1 个 heading，实际 {types.count('heading')}")
    if types.count("text") != 3:
        problems.append(f"{lid}: text 应为 3 段，实际 {types.count('text')}")
    if not any(t in ("table", "diagram") for t in types):
        problems.append(f"{lid}: 缺少 table 或 diagram")
    if not any(t in ("tip", "warn") for t in types):
        problems.append(f"{lid}: 缺少 tip 或 warn")
    if "quiz" not in types:
        problems.append(f"{lid}: 缺少 quiz")
    if not any(t in ("task", "practice") for t in types):
        problems.append(f"{lid}: 缺少 task 或 practice")

    runnable = 0
    reference = 0
    output = 0
    for pos, block in enumerate(blocks):
        btype = block.get("type")
        if btype == "output":
            output += 1
            if not str(block.get("text", "")).strip():
                problems.append(f"{lid}: output 文本为空")
        if btype == "heading" and not str(block.get("text", "")).strip():
            problems.append(f"{lid}: heading 文本为空")
        if btype == "text" and not str(block.get("text", "")).strip():
            problems.append(f"{lid}: text 文本为空")
        if btype == "quiz":
            options = block.get("options") or []
            if len(options) != 4:
                problems.append(f"{lid}: quiz 应有 4 个选项")
            answer = block.get("answer")
            if not isinstance(answer, int) or not 0 <= answer < len(options):
                problems.append(f"{lid}: quiz answer 越界")
            if not str(block.get("explain", "")).strip():
                problems.append(f"{lid}: quiz 缺少 explain")
        if btype == "table":
            width = len(block.get("headers") or [])
            for row in block.get("rows") or []:
                if len(row) != width:
                    problems.append(f"{lid}: 表格列数不一致")
        if btype == "code":
            if "runnable" not in block:
                problems.append(f"{lid}: 代码块必须显式写 runnable")
            if block.get("runnable"):
                runnable += 1
                if pos + 1 >= len(blocks) or blocks[pos + 1].get("type") != "output":
                    problems.append(f"{lid}: runnable 代码块后必须紧跟 output 块")
                code = block.get("code", "")
                if "main" not in code:
                    problems.append(f"{lid}: runnable 代码块应包含 main")
                problems.extend(check_forbidden(f"{lid} 代码块#{pos + 1}", code))
            else:
                reference += 1
                code = block.get("code", "")
                if "参考块" not in code:
                    problems.append(f"{lid}: runnable=false 的代码块应标注为「参考块」")

    if runnable != output:
        problems.append(f"{lid}: runnable 块与 output 数量不匹配（{runnable} vs {output}）")
    if not 1 <= runnable <= 2:
        problems.append(f"{lid}: runnable 代码块应为 1-2 个，实际 {runnable}")
    if lid in SINGLE_RUNNABLE_IDS:
        if runnable != 1 or reference != 1:
            problems.append(f"{lid}: 应为 1 个 runnable + 1 个参考块，实际 {runnable}+{reference}")
    elif reference and lid not in REFERENCE_ALLOWED_IDS:
        problems.append(f"{lid}: 除 c32/c33/c35 外不应有参考块，实际 {reference}")

    text_chars = sum(han_count(b.get("text", "")) for b in blocks if b.get("type") == "text")
    if not 900 <= text_chars <= 1600:
        problems.append(f"{lid}: 正文汉字数应在 900-1600，实际 {text_chars}")

    exercise = lesson.get("exercise") or {}
    for key in ("title", "brief", "starterCode", "hint", "solution"):
        if not str(exercise.get(key, "")).strip():
            problems.append(f"{lid}: exercise 缺少 {key}")
    for key in ("tests", "stdin", "xp"):
        if key not in exercise:
            problems.append(f"{lid}: exercise 缺少 {key}")
    tests = exercise.get("tests") or []
    if not 3 <= len(tests) <= 5:
        problems.append(f"{lid}: tests 应为 3-5 条，实际 {len(tests)}")
    if exercise.get("starterCode", "").strip() == exercise.get("solution", "").strip():
        problems.append(f"{lid}: starter 与 solution 不能相同")
    problems.extend(check_forbidden(f"{lid} starter", exercise.get("starterCode", "")))
    problems.extend(check_forbidden(f"{lid} solution", exercise.get("solution", "")))
    for ti, test in enumerate(tests):
        problems.extend(check_forbidden(f"{lid} test#{ti + 1}", test))

    return problems


def check_structure():
    problems = []
    if not PACK_PATH.exists():
        return [f"缺少 {PACK_PATH.name}"], 0, 0
    try:
        data = json.loads(PACK_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{PACK_PATH.name}: JSON 解析失败 {exc}"], 0, 0
    if not isinstance(data, list):
        return [f"{PACK_PATH.name}: 顶层应为数组"], 0, 0
    if len(data) != 8:
        problems.append(f"应为 8 讲，实际 {len(data)}")

    for index, lesson in enumerate(data[:8]):
        problems.extend(check_lesson(lesson, index))

    ids = [l.get("id") for l in data]
    orders = [l.get("order") for l in data]
    if ids != EXPECTED_IDS:
        problems.append(f"讲 id 顺序应为 {EXPECTED_IDS}，实际 {ids}")
    if orders != EXPECTED_ORDERS:
        problems.append(f"order 应为 {EXPECTED_ORDERS}，实际 {orders}")
    if len(set(ids)) != len(ids):
        problems.append("存在重复 id")
    if len(set(orders)) != len(orders):
        problems.append("存在重复 order")

    # 与既有三包对照：id/order 不得冲突，标题不得重复
    existing_ids = set()
    existing_orders = set()
    for name in ("c-basics", "c-core", "c-advanced"):
        path = ROOT / "content_packs" / f"{name}.json"
        if not path.exists():
            continue
        for lesson in json.loads(path.read_text(encoding="utf-8")):
            existing_ids.add(lesson.get("id"))
            existing_orders.add(lesson.get("order"))
    overlap_ids = sorted(existing_ids & set(ids))
    overlap_orders = sorted(existing_orders & set(orders))
    if overlap_ids:
        problems.append(f"与既有 C 课程 id 冲突：{overlap_ids}")
    if overlap_orders:
        problems.append(f"与既有 C 课程 order 冲突：{overlap_orders}")

    tests_total = sum(len(l.get("exercise", {}).get("tests") or []) for l in data)
    return problems, len(data), tests_total


TEMP_TEST_SOURCE = '''package com.pyneon.academy.c

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/**
 * 临时验证（由 tools/verify_c_expert.py 生成，跑完即删，不进入版本库）。
 *
 * 逐讲验证 C「专业篇」的判题契约：
 *   1. 每个 runnable 代码块必须执行成功，且 stdout 与紧随其后的 output 块一致
 *   2. exercise.solution + tests 必须全部通过
 *   3. exercise.starterCode + tests 必须至少失败一条
 *   4. runnable=false 的参考块确实无法执行（标注诚实）
 */
class TempCExpertVerificationTest {

    private fun repoRoot(): File {
        var dir = File(System.getProperty("user.dir") ?: ".")
        while (!File(dir, "content_packs").exists()) {
            dir = dir.parentFile ?: error("找不到仓库根目录")
        }
        return dir
    }

    private fun pack(): JSONArray =
        JSONArray(File(repoRoot(), "content_packs/c-expert.json").readText(Charsets.UTF_8))

    private fun normalise(text: String): String =
        text.replace("\\r\\n", "\\n").trimEnd('\\n').lines().joinToString("\\n") { it.trimEnd() }

    private fun lessons(): List<JSONObject> {
        val arr = pack()
        return (0 until arr.length()).map { arr.getJSONObject(it) }
    }

    @Test
    fun `expert pack covers eight lessons`() {
        val all = lessons()
        assertEquals("专业篇应为 8 讲", 8, all.size)
        val ids = all.map { it.getString("id") }
        assertEquals("讲 id 应从 c31 到 c38", (31..38).map { "c" + it }, ids)
        val orders = all.map { it.getInt("order") }
        assertEquals("order 应为 730-737", (730..737).toList(), orders)
        for (lesson in all) {
            assertEquals("chapter", 74, lesson.getInt("chapter"))
            assertEquals("chapterName", "C · 专业篇", lesson.getString("chapterName"))
            assertEquals("lang", "c", lesson.getString("lang"))
        }
    }

    @Test
    fun `every runnable block output matches declared output`() {
        var blocks = 0
        for (lesson in lessons()) {
            val id = lesson.getString("id")
            val arr = lesson.getJSONArray("blocks")
            for (b in 0 until arr.length()) {
                val block = arr.getJSONObject(b)
                if (block.getString("type") != "code") continue
                if (!block.optBoolean("runnable", false)) continue
                blocks++
                val code = block.getString("code")
                val r = CInterpreter.run(code)
                assertTrue("[" + id + "] 代码块 #" + (b + 1) + " 执行失败：" + r.errorMessage + "\\n--- 代码 ---\\n" + code, r.ok)
                val expected = if (b + 1 < arr.length() && arr.getJSONObject(b + 1).getString("type") == "output")
                    arr.getJSONObject(b + 1).getString("text") else null
                assertTrue("[" + id + "] 代码块 #" + (b + 1) + " 后缺少 output 块", expected != null)
                assertEquals(
                    "[" + id + "] 代码块 #" + (b + 1) + " 输出不一致\\n期望：[" + normalise(expected!!) + "]\\n实际：[" + normalise(r.stdout) + "]",
                    normalise(expected), normalise(r.stdout)
                )
            }
        }
        assertEquals("专业篇 runnable 代码块总数", 13, blocks)
    }

    @Test
    fun `every solution passes and every starter fails`() {
        var solutions = 0
        var starters = 0
        for (lesson in lessons()) {
            val id = lesson.getString("id")
            val ex = lesson.getJSONObject("exercise")
            val testsArr = ex.getJSONArray("tests")
            val tests = (0 until testsArr.length()).map { testsArr.getString(it) }

            val ok = CInterpreter.check(ex.getString("solution"), tests)
            assertTrue("[" + id + "] 参考答案未通过：" + ok.errorMessage, ok.ok)
            solutions++

            val bad = CInterpreter.check(ex.getString("starterCode"), tests)
            assertFalse("[" + id + "] 起始代码不应通过判题", bad.ok)
            starters++
        }
        assertEquals("应覆盖 8 讲参考答案", 8, solutions)
        assertEquals("应覆盖 8 讲起始代码", 8, starters)
    }

    @Test
    fun `reference blocks are honestly non runnable`() {
        var reference = 0
        for (lesson in lessons()) {
            val id = lesson.getString("id")
            val arr = lesson.getJSONArray("blocks")
            for (b in 0 until arr.length()) {
                val block = arr.getJSONObject(b)
                if (block.getString("type") != "code") continue
                if (block.optBoolean("runnable", true)) continue
                reference++
                val r = CInterpreter.run(block.getString("code"))
                assertFalse("[" + id + "] 参考块 #" + (b + 1) + " 不应可执行", r.ok)
            }
        }
        assertEquals("参考块数量", 3, reference)
    }
}
'''


def default_gradle_home():
    env = os.environ.get("GRADLE_USER_HOME")
    if env:
        return env
    candidate = Path(r"C:\Dev\gradle-home-mashang")
    return str(candidate) if candidate.exists() else ""


def default_android_home():
    env = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if env:
        return env
    candidate = Path(r"C:\Dev\android-sdk")
    return str(candidate) if candidate.exists() else ""


def find_gradle_wrapper():
    for name in ("gradlew.bat", "gradlew"):
        candidate = ROOT / name
        if candidate.exists():
            return candidate
    return ROOT / "gradlew.bat"


def run_gradle(args):
    cmd = [
        str(find_gradle_wrapper()),
        ":app:testDebugUnitTest",
        "--tests", "com.pyneon.academy.c.TempCExpertVerificationTest",
        "--tests", "com.pyneon.academy.c.CCoursePacksTest",
        "--console=plain",
    ]
    env = dict(os.environ)
    if args.gradle_home:
        env["GRADLE_USER_HOME"] = args.gradle_home
    if args.android_home:
        env["ANDROID_HOME"] = args.android_home
        env["ANDROID_SDK_ROOT"] = args.android_home
    print("运行: " + " ".join(cmd))
    if args.gradle_home:
        print("GRADLE_USER_HOME=" + args.gradle_home)
    if args.android_home:
        print("ANDROID_HOME=" + args.android_home)
    proc = subprocess.run(cmd, cwd=str(ROOT), env=env, text=True,
                          encoding="utf-8", errors="replace")
    return proc.returncode


def report_test_results():
    results = ROOT / "app/build/test-results/testDebugUnitTest"
    if not results.exists():
        print("未找到测试结果目录，跳过 XML 汇总")
        return
    for name in ("CCoursePacksTest", "TempCExpertVerificationTest"):
        path = results / f"TEST-com.pyneon.academy.c.{name}.xml"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'tests="(\d+)".*?failures="(\d+)".*?errors="(\d+)"', text)
        if m:
            print(f"{name}: tests={m.group(1)} failures={m.group(2)} errors={m.group(3)}")


def main():
    parser = argparse.ArgumentParser(description="C 专业篇课程包结构校验与真实解释器验证")
    parser.add_argument("--skip-gradle", action="store_true", help="只做结构校验")
    parser.add_argument("--gradle-home", default=default_gradle_home(),
                        help="GRADLE_USER_HOME（本机默认目录的 init 脚本有问题时指定）")
    parser.add_argument("--android-home", default=default_android_home(),
                        help="Android SDK 路径")
    args = parser.parse_args()

    print("=== 1. 结构校验 ===")
    problems, lessons, tests = check_structure()
    print(f"讲数={lessons} 判题用例={tests} 结构问题={len(problems)}")
    for p in problems:
        print("STRUCT:", p)

    if args.skip_gradle:
        if problems:
            print("结果=结构校验失败")
            return 1
        print("结果=结构校验通过（已跳过 Gradle）")
        return 0

    print()
    print("=== 2. 真实解释器验证（Gradle + 临时 JUnit） ===")
    if TEMP_TEST.exists():
        print(f"警告：临时测试已存在，先删除 {TEMP_TEST.relative_to(ROOT)}")
        TEMP_TEST.unlink()
    TEMP_TEST.parent.mkdir(parents=True, exist_ok=True)
    TEMP_TEST.write_text(TEMP_TEST_SOURCE, encoding="utf-8", newline="\n")
    print(f"已生成临时测试: {TEMP_TEST.relative_to(ROOT)}")
    code = 2
    try:
        code = run_gradle(args)
    except FileNotFoundError as exc:
        print(f"无法启动 Gradle: {exc}")
    finally:
        if TEMP_TEST.exists():
            TEMP_TEST.unlink()
            print(f"已删除临时测试: {TEMP_TEST.relative_to(ROOT)}")
        else:
            print("临时测试已被删除")
        if TEMP_TEST.exists():
            print("错误：临时测试仍然存在")
            code = 2 if code == 0 else code

    print()
    report_test_results()
    print()
    if problems:
        print(f"结果=失败（结构问题 {len(problems)} 项，Gradle 退出码 {code}）")
        return 1
    if code != 0:
        print(f"结果=失败（Gradle 退出码 {code}）")
        return 1
    print("结果=全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
