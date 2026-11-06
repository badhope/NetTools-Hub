#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQL 三个课程包的真执行门禁。

与 tests/test_sql_lessons.py 的区别：那个测试只覆盖 sql-basics.json，
本脚本把三个包全部纳入，并且做三件事：

1. 直接 import app/src/main/python/sql_runner.py，逐讲执行所有 runnable 代码块，
   断言 sql_runner.run_sql() 返回 ok；
2. 用 check_sql(solution, tests) 验证参考答案全部通过；
3. 用 check_sql(starterCode, tests) 验证 starter 必须不通过。

另外校验结构与内容契约：每包 10 讲、id 全局唯一、order / chapter 连号、
每讲至少 8 个内容块、必须有 heading / text / code / output / table 或 diagram /
tip 或 warn / quiz、output 与真实执行结果逐字一致、tests 数量 3 到 5 条。

运行：python tools/verify_sql_packs.py
退出码：0 全部通过；1 有任何失败。

用法提示：本脚本只读，不会修改 content_packs。加 --verbose 打印每讲明细。
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app" / "src" / "main" / "python"))

import sql_runner  # noqa: E402

PACKS = [
    ("sql-basics.json", "sql01", "sql10", 500, 51, "SQL · 基础篇"),
    ("sql-core.json", "sql11", "sql20", 510, 52, "SQL · 核心篇"),
    ("sql-advanced.json", "sql21", "sql30", 520, 53, "SQL · 进阶篇"),
]

HAN = re.compile(r"[\u4e00-\u9fff]")
REQUIRED_TYPES = ("heading", "text", "code", "output")
MIN_BLOCKS = 8
MIN_PROSE = 900
MAX_PROSE = 1600
MIN_TESTS = 3
MAX_TESTS = 5


def render_output(sql):
    """按 sql_runner 的格式渲染最后一条结果集，用于和 output 块对比。"""
    result = sql_runner._execute(sql)
    if not result["ok"]:
        return None
    last = result["last"]
    if last is None:
        return None
    lines = ["\t".join(last["columns"])]
    for row in last["rows"]:
        lines.append("\t".join("NULL" if v is None else str(v) for v in row))
    return "\n".join(lines)


def prose_len(lesson):
    total = 0
    for block in lesson["blocks"]:
        kind = block.get("type")
        if kind in ("heading", "text", "tip", "warn"):
            total += len(HAN.findall(block["text"]))
    return total


def check_structure(filename, lessons, first_id, last_id, first_order, chapter, chapter_name):
    problems = []

    if len(lessons) != 10:
        problems.append("%s: 应为 10 讲，实际 %d 讲" % (filename, len(lessons)))

    expected_ids = ["sql%02d" % n for n in range(int(first_id[3:]), int(last_id[3:]) + 1)]
    actual_ids = [lesson["id"] for lesson in lessons]
    if actual_ids != expected_ids:
        problems.append("%s: id 序列应为 %s，实际 %s" % (filename, expected_ids, actual_ids))

    for offset, lesson in enumerate(lessons):
        lid = lesson["id"]
        if lesson["order"] != first_order + offset:
            problems.append("%s: order 应为 %d，实际 %d" % (lid, first_order + offset, lesson["order"]))
        if lesson["chapter"] != chapter:
            problems.append("%s: chapter 应为 %d，实际 %d" % (lid, chapter, lesson["chapter"]))
        if lesson["chapterName"] != chapter_name:
            problems.append("%s: chapterName 应为 %s，实际 %s" % (lid, chapter_name, lesson["chapterName"]))
        if lesson["lang"] != "sql":
            problems.append("%s: lang 应为 sql，实际 %s" % (lid, lesson["lang"]))

        blocks = lesson["blocks"]
        if len(blocks) < MIN_BLOCKS:
            problems.append("%s: 内容块 %d 个，少于 %d" % (lid, len(blocks), MIN_BLOCKS))

        types = [block["type"] for block in blocks]
        for required in REQUIRED_TYPES:
            if required not in types:
                problems.append("%s: 缺少 %s 块" % (lid, required))
        if "table" not in types and "diagram" not in types:
            problems.append("%s: 缺少 table 或 diagram" % lid)
        if "tip" not in types and "warn" not in types:
            problems.append("%s: 缺少 tip 或 warn" % lid)
        if "quiz" not in types:
            problems.append("%s: 缺少 quiz" % lid)

        text_blocks = [b for b in blocks if b["type"] == "text"]
        if len(text_blocks) < 2:
            problems.append("%s: text 块 %d 个，至少 2 个" % (lid, len(text_blocks)))

        runnable = [b for b in blocks if b["type"] == "code" and b.get("runnable")]
        if not (1 <= len(runnable) <= 2):
            problems.append("%s: runnable code 块 %d 个，应为 1 到 2 个" % (lid, len(runnable)))

        prose = prose_len(lesson)
        if not (MIN_PROSE <= prose <= MAX_PROSE):
            problems.append("%s: 正文 %d 汉字，应在 %d 到 %d" % (lid, prose, MIN_PROSE, MAX_PROSE))

        for block in blocks:
            if block["type"] == "quiz":
                if not (0 <= block["answer"] < len(block["options"])):
                    problems.append("%s: quiz answer 越界" % lid)
            if block["type"] == "table":
                width = len(block["headers"])
                for row in block["rows"]:
                    if len(row) != width:
                        problems.append("%s: table 列数不一致" % lid)

        ex = lesson.get("exercise")
        if not ex:
            problems.append("%s: 缺少 exercise" % lid)
            continue
        for key in ("title", "brief", "starterCode", "hint", "tests", "stdin", "xp", "solution"):
            if key not in ex:
                problems.append("%s: exercise 缺少 %s" % (lid, key))
        if not (MIN_TESTS <= len(ex.get("tests") or []) <= MAX_TESTS):
            problems.append("%s: tests 数量 %d，应为 %d 到 %d" % (
                lid, len(ex.get("tests") or []), MIN_TESTS, MAX_TESTS))
        if ex.get("stdin"):
            problems.append("%s: SQL 练习的 stdin 应为空数组" % lid)

    return problems


def check_execution(lessons, verbose=False):
    """真实执行：runnable 块、solution、starter。"""
    problems = []
    stats = {"runnable": 0, "solution_pass": 0, "starter_rejected": 0, "cases": 0}

    for lesson in lessons:
        lid = lesson["id"]
        blocks = lesson["blocks"]

        for index, block in enumerate(blocks):
            if block["type"] != "code" or not block.get("runnable"):
                continue
            stats["runnable"] += 1
            result = sql_runner.run_sql(block["code"])
            if not result["ok"]:
                error = result["error"] or {}
                problems.append("%s: runnable 块 #%d 执行失败：%s: %s" % (
                    lid, index, error.get("type"), error.get("message")))
                continue
            if index + 1 < len(blocks) and blocks[index + 1]["type"] == "output":
                expected = blocks[index + 1]["text"]
                actual = render_output(block["code"])
                if actual is None:
                    problems.append("%s: runnable 块 #%d 没有结果集，无法对应 output" % (lid, index))
                elif actual != expected:
                    problems.append("%s: output 与真实结果不一致\n  期望：%r\n  实际：%r" % (
                        lid, expected, actual))

        ex = lesson["exercise"]
        tests = ex["tests"]
        stats["cases"] += len(tests)

        solution = sql_runner.check_sql(ex["solution"], tests)
        if not solution["passed"]:
            error = solution["error"] or {}
            problems.append("%s: solution 未通过测试：%s" % (lid, error.get("message")))
        else:
            stats["solution_pass"] += 1

        starter = sql_runner.check_sql(ex["starterCode"], tests)
        if starter["passed"]:
            problems.append("%s: starterCode 不应通过测试，但它通过了" % lid)
        else:
            stats["starter_rejected"] += 1

        if verbose:
            print("  %-6s blocks=%2d prose=%4d tests=%d" % (
                lid, len(blocks), prose_len(lesson), len(tests)))

    return problems, stats


def main():
    parser = argparse.ArgumentParser(description="SQL 课程包真执行校验")
    parser.add_argument("--verbose", action="store_true", help="打印每讲明细")
    args = parser.parse_args()

    all_problems = []
    all_ids = []
    total_lessons = 0

    for filename, first_id, last_id, first_order, chapter, chapter_name in PACKS:
        path = ROOT / "content_packs" / filename
        if not path.is_file():
            all_problems.append("%s: 文件不存在" % filename)
            continue

        try:
            lessons = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            all_problems.append("%s: JSON 解析失败：%s" % (filename, exc))
            continue

        print("== %s (%d 讲)" % (filename, len(lessons)))
        structural = check_structure(
            filename, lessons, first_id, last_id, first_order, chapter, chapter_name
        )
        execution, stats = check_execution(lessons, verbose=args.verbose)

        all_problems.extend(structural)
        all_problems.extend(execution)
        all_ids.extend(lesson["id"] for lesson in lessons)
        total_lessons += len(lessons)

        print("   结构问题 %d，执行问题 %d；runnable %d 块，solution 通过 %d/%d，"
              "starter 拒绝 %d/%d，判题用例 %d 条" % (
                  len(structural), len(execution), stats["runnable"],
                  stats["solution_pass"], len(lessons),
                  stats["starter_rejected"], len(lessons), stats["cases"]))

    duplicates = sorted({lid for lid in all_ids if all_ids.count(lid) > 1})
    if duplicates:
        all_problems.append("出现重复 id：%s" % ", ".join(duplicates))

    print()
    print("总讲数 %d，id 唯一 %d 个" % (total_lessons, len(set(all_ids))))
    if all_problems:
        print("校验失败，共 %d 个问题：" % len(all_problems))
        for problem in all_problems:
            print("  - %s" % problem)
        return 1

    print("全部通过：3 个包 / %d 讲 / runnable 块全部执行成功 / solution 全部通过 / starter 全部不通过"
          % total_lessons)
    return 0


if __name__ == "__main__":
    sys.exit(main())
