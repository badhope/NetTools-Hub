#!/usr/bin/env python3
"""C 语言三包课程 · 结构校验 + 真实解释器端到端验证。

为什么这样验证
--------------
解释器是 Kotlin 写的（app/src/main/java/com/pyneon/academy/c/CInterpreter.kt），
Python 无法直接调用。可行且与 App 内判题语义完全一致的路径只有一条：
在仓库自己的 Gradle 测试工程里跑 JUnit，用真实的 CInterpreter.check / run。

所以本脚本分两层：
  1. 结构层（纯 Python）：JSON 可解析、每包 10 讲、id/order/chapter、内容块
     数量与类型、quiz 答案下标、表格列宽、正文汉字数、禁用语法扫描。
  2. 语义层（Gradle + 真实解释器）：
     a) 跑仓库已有的 CCoursePacksTest；
     b) 额外生成一个临时测试 TempCoursePackVerificationTest.kt，逐讲验证
        「每个 runnable 块执行成功且输出与 output 块一致」「solution 全部用例
        通过」「starter 至少失败一条」，跑完在 finally 里删除临时文件。

用法
----
    python tools/verify_c_packs.py
    python tools/verify_c_packs.py --skip-gradle          # 只做结构校验
    python tools/verify_c_packs.py --gradle-home C:\\Dev\\gradle-home-mashang \\
                                   --android-home C:\\Dev\\android-sdk

退出码 0 表示全部通过，1 表示有失败项，2 表示无法执行 Gradle 验证。
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKS_DIR = ROOT / "content_packs"
TEMP_TEST = ROOT / "app/src/test/java/com/pyneon/academy/c/TempCoursePackVerificationTest.kt"

PACK_SPECS = [
    ("c-basics", 71, "C · 基础篇", 700, "c01", "c10"),
    ("c-core", 72, "C · 核心篇", 710, "c11", "c20"),
    ("c-advanced", 73, "C · 进阶篇", 720, "c21", "c30"),
]

# 解释器明确不支持的写法：任何 runnable 代码块、solution、starter 里出现都算违规。
# malloc/free 只允许出现在 runnable=false 的参考块里，因此单独判定。
FORBIDDEN_IN_RUNNABLE = [
    (r"#\s*include", "#include"),
    (r"#\s*define", "#define"),
    (r"\bgoto\b", "goto"),
    (r"\benum\b", "enum"),
    (r"\bunion\b", "union"),
    (r"\bscanf\b", "scanf"),
    (r"\bmalloc\b", "malloc"),
    (r"\bcalloc\b", "calloc"),
    (r"\brealloc\b", "realloc"),
    (r"\bfree\s*\(", "free"),
    (r"\bfopen\b", "fopen"),
    (r"\(\s*\*\s*[A-Za-z_]\w*\s*\)\s*\(", "函数指针"),
    (r"\.\.\.", "可变参数"),
]

HAN_RE = re.compile(r"[\u4e00-\u9fff]")


def han_count(text: str) -> int:
    return len(HAN_RE.findall(text))


def strip_literals(src: str) -> str:
    """去掉字符串与注释，避免文本内容里的 enum/malloc 等词造成误报。"""
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


def check_forbidden(where: str, src: str) -> list:
    problems = []
    cleaned = strip_literals(src)
    for pattern, label in FORBIDDEN_IN_RUNNABLE:
        if re.search(pattern, cleaned):
            problems.append(f"{where}: 使用了课程不支持的 {label}")
    return problems


def check_lesson(pack_id: str, lesson: dict, index: int, chapter: int,
                 chapter_name: str, base_order: int, first_id: str) -> list:
    lid = lesson.get("id", f"{pack_id}#{index}")
    problems = []

    expected_id = f"c{int(first_id[1:]) + index:02d}"
    if lid != expected_id:
        problems.append(f"{lid}: id 应为 {expected_id}")
    if lesson.get("order") != base_order + index:
        problems.append(f"{lid}: order 应为 {base_order + index}，实际 {lesson.get('order')}")
    if lesson.get("chapter") != chapter:
        problems.append(f"{lid}: chapter 应为 {chapter}")
    if lesson.get("chapterName") != chapter_name:
        problems.append(f"{lid}: chapterName 应为 {chapter_name}")
    if lesson.get("lang") != "c":
        problems.append(f"{lid}: lang 应为 c")
    for key in ("title", "subtitle"):
        if not str(lesson.get(key, "")).strip():
            problems.append(f"{lid}: 缺少 {key}")
    if not isinstance(lesson.get("xp"), int) or lesson["xp"] <= 0:
        problems.append(f"{lid}: xp 应为正整数")

    blocks = lesson.get("blocks") or []
    if not isinstance(blocks, list) or len(blocks) < 8:
        problems.append(f"{lid}: 内容块应 >= 8，实际 {len(blocks)}")
        return problems
    types = [b.get("type") for b in blocks]
    if types.count("heading") != 1:
        problems.append(f"{lid}: 应有且仅有 1 个 heading，实际 {types.count('heading')}")
    if not 2 <= types.count("text") <= 3:
        problems.append(f"{lid}: text 应为 2-3 段，实际 {types.count('text')}")
    if types.count("code") < 2:
        problems.append(f"{lid}: 代码块应 >= 2，实际 {types.count('code')}")
    runnable_count = sum(1 for b in blocks if b.get("type") == "code" and b.get("runnable"))
    if runnable_count != types.count("output"):
        problems.append(f"{lid}: runnable 代码块与 output 数量不匹配（{runnable_count} vs {types.count('output')}）")
    if not any(t in ("table", "diagram") for t in types):
        problems.append(f"{lid}: 缺少 table 或 diagram")
    if not any(t in ("tip", "warn") for t in types):
        problems.append(f"{lid}: 缺少 tip 或 warn")
    if "quiz" not in types:
        problems.append(f"{lid}: 缺少 quiz")

    runnable = 0
    for pos, block in enumerate(blocks):
        btype = block.get("type")
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
                problems.extend(check_forbidden(f"{lid} 代码块#{pos + 1}", block.get("code", "")))
            else:
                # 参考块必须明确说明为什么不能运行
                code = block.get("code", "")
                if "参考块" not in code and "参考块" not in str(block.get("note", "")):
                    problems.append(f"{lid}: runnable=false 的代码块应标注为参考块")
    if runnable < 1:
        problems.append(f"{lid}: 至少需要 1 个 runnable 代码块")

    text_chars = sum(han_count(b.get("text", "")) for b in blocks if b.get("type") == "text")
    if not 900 <= text_chars <= 1600:
        problems.append(f"{lid}: 正文汉字数应在 900-1600，实际 {text_chars}")

    ex = lesson.get("exercise") or {}
    for key in ("title", "brief", "starterCode", "hint", "solution"):
        if not str(ex.get(key, "")).strip():
            problems.append(f"{lid}: exercise 缺少 {key}")
    if "tests" not in ex or "stdin" not in ex or "xp" not in ex:
        problems.append(f"{lid}: exercise 缺少 tests/stdin/xp")
    tests = ex.get("tests") or []
    if not 3 <= len(tests) <= 5:
        problems.append(f"{lid}: tests 应为 3-5 条，实际 {len(tests)}")
    if ex.get("starterCode", "").strip() == ex.get("solution", "").strip():
        problems.append(f"{lid}: starter 与 solution 不能相同")
    problems.extend(check_forbidden(f"{lid} starter", ex.get("starterCode", "")))
    problems.extend(check_forbidden(f"{lid} solution", ex.get("solution", "")))
    for i, t in enumerate(tests):
        problems.extend(check_forbidden(f"{lid} test#{i + 1}", t))

    return problems


def check_structure() -> tuple:
    problems = []
    lessons_total = 0
    tests_total = 0
    ids = []
    orders = []

    for pack_id, chapter, chapter_name, base_order, first_id, last_id in PACK_SPECS:
        path = PACKS_DIR / f"{pack_id}.json"
        if not path.exists():
            problems.append(f"{pack_id}: 缺少文件 {path.name}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{pack_id}: JSON 解析失败 {exc}")
            continue
        if not isinstance(data, list):
            problems.append(f"{pack_id}: 顶层应为数组")
            continue
        if len(data) != 10:
            problems.append(f"{pack_id}: 应为 10 讲，实际 {len(data)}")
        for i, lesson in enumerate(data):
            problems.extend(check_lesson(pack_id, lesson, i, chapter, chapter_name, base_order, first_id))
            ids.append(lesson.get("id"))
            orders.append(lesson.get("order"))
            tests_total += len(lesson.get("exercise", {}).get("tests") or [])
        lessons_total += len(data)
        if data and data[0].get("id") != first_id:
            problems.append(f"{pack_id}: 首讲 id 应为 {first_id}")
        if data and data[-1].get("id") != last_id:
            problems.append(f"{pack_id}: 末讲 id 应为 {last_id}")

    if len(set(ids)) != len(ids):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        problems.append(f"存在重复 id: {dupes}")
    if len(set(orders)) != len(orders):
        dupes = sorted({o for o in orders if orders.count(o) > 1})
        problems.append(f"存在重复 order: {dupes}")

    return problems, lessons_total, tests_total


TEMP_TEST_SOURCE = '''package com.pyneon.academy.c

import org.json.JSONArray
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/**
 * 临时验证（由 tools/verify_c_packs.py 生成，跑完即删，不进入版本库）。
 *
 * 逐讲验证三包 C 课程的判题契约：
 *   1. 每个 runnable 代码块必须执行成功，且 stdout 与紧随其后的 output 块一致
 *   2. exercise.solution + tests 必须全部通过
 *   3. exercise.starterCode + tests 必须至少失败一条
 */
class TempCoursePackVerificationTest {

    private fun repoRoot(): File {
        var dir = File(System.getProperty("user.dir") ?: ".")
        while (!File(dir, "content_packs").exists()) {
            dir = dir.parentFile ?: error("找不到仓库根目录")
        }
        return dir
    }

    private fun packFiles(): List<File> {
        val dir = File(repoRoot(), "content_packs")
        return listOf("c-basics.json", "c-core.json", "c-advanced.json").map { File(dir, it) }
    }

    private fun normalise(text: String): String =
        text.replace("\\r\\n", "\\n").trimEnd('\\n').lines().joinToString("\\n") { it.trimEnd() }

    @Test
    fun `every runnable block output matches declared output`() {
        var blocks = 0
        for (file in packFiles()) {
            assertTrue("缺少 " + file.name, file.exists())
            val pack = JSONArray(file.readText(Charsets.UTF_8))
            for (i in 0 until pack.length()) {
                val lesson = pack.getJSONObject(i)
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
        }
        assertEquals("三包 runnable 代码块总数", 58, blocks)
    }

    @Test
    fun `every solution passes and every starter fails`() {
        var solutions = 0
        var starters = 0
        for (file in packFiles()) {
            val pack = JSONArray(file.readText(Charsets.UTF_8))
            for (i in 0 until pack.length()) {
                val lesson = pack.getJSONObject(i)
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
        }
        assertEquals("应覆盖 30 讲参考答案", 30, solutions)
        assertEquals("应覆盖 30 讲起始代码", 30, starters)
    }
}
'''


def default_gradle_home() -> str:
    """本机默认 GRADLE_USER_HOME 的 init 脚本可能损坏，优先用已知可用的隔离目录。"""
    env = os.environ.get("GRADLE_USER_HOME")
    if env:
        return env
    candidate = Path(r"C:\Dev\gradle-home-mashang")
    return str(candidate) if candidate.exists() else ""


def default_android_home() -> str:
    env = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if env:
        return env
    candidate = Path("C:" + chr(92) + "Dev" + chr(92) + "android-sdk")
    return str(candidate) if candidate.exists() else ""


def find_gradle_root() -> Path:
    for name in ("gradlew.bat", "gradlew"):
        candidate = ROOT / name
        if candidate.exists():
            return candidate
    return ROOT / "gradlew.bat"


def run_gradle(args) -> int:
    gradlew = find_gradle_root()
    cmd = [str(gradlew)]
    cmd += [
        ":app:testDebugUnitTest",
        "--tests", "com.pyneon.academy.c.CCoursePacksTest",
        "--tests", "com.pyneon.academy.c.TempCoursePackVerificationTest",
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


def report_test_results() -> None:
    results = ROOT / "app/build/test-results/testDebugUnitTest"
    if not results.exists():
        print("未找到测试结果目录，跳过 XML 汇总")
        return
    for name in ("CCoursePacksTest", "TempCoursePackVerificationTest"):
        path = results / f"TEST-com.pyneon.academy.c.{name}.xml"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r'tests="(\d+)".*?failures="(\d+)".*?errors="(\d+)"', text)
        if m:
            print(f"{name}: tests={m.group(1)} failures={m.group(2)} errors={m.group(3)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="C 三包课程结构校验与真实解释器验证")
    parser.add_argument("--skip-gradle", action="store_true", help="只做结构校验")
    parser.add_argument("--gradle-home", default=default_gradle_home(),
                        help="GRADLE_USER_HOME（本机默认目录的 init 脚本有问题时指定）")
    parser.add_argument("--android-home", default=default_android_home(),
                        help="Android SDK 路径")
    args = parser.parse_args()

    print("=== 1. 结构校验 ===")
    problems, lessons, tests = check_structure()
    print(f"包数={len(PACK_SPECS)} 讲数={lessons} 判题用例={tests} 结构问题={len(problems)}")
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
        print(f"警告：临时测试已存在，先删除 {TEMP_TEST}")
        TEMP_TEST.unlink()
    TEMP_TEST.parent.mkdir(parents=True, exist_ok=True)
    # 带时间戳的注释让 Gradle 每次都把它当成新输入，避免测试任务被判为 up-to-date 而跳过。
    stamp = datetime.datetime.now().isoformat(timespec="seconds")
    source = TEMP_TEST_SOURCE.replace(
        "class TempCoursePackVerificationTest {",
        "// generated at " + stamp + "\nclass TempCoursePackVerificationTest {",
        1,
    )
    TEMP_TEST.write_text(source, encoding="utf-8", newline="\n")
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
