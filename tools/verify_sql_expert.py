#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQL 专业篇验证器：结构 + 真实 sqlite3 执行 + 判题 + starter 拒绝。"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app" / "src" / "main" / "python"))

import sql_runner  # noqa: E402

PACK = ROOT / "content_packs" / "sql-expert.json"
EXPECTED = [f"sql{n}" for n in range(31, 39)]
ORDERS = list(range(530, 538))


def main() -> int:
    problems = []
    lessons = json.loads(PACK.read_text(encoding="utf-8"))
    if len(lessons) != 8:
        problems.append(f"讲数应为 8，实际 {len(lessons)}")
    if [l["id"] for l in lessons] != EXPECTED:
        problems.append("讲 id 应为 sql31..sql38")
    if [l["order"] for l in lessons] != ORDERS:
        problems.append("order 应为 530..537")

    runnable = 0
    for lesson in lessons:
        lid = lesson["id"]
        if lesson.get("lang") != "sql":
            problems.append(f"{lid}: lang 应为 sql")
        if lesson.get("chapter") != 54 or lesson.get("chapterName") != "SQL · 专业篇":
            problems.append(f"{lid}: chapter 不正确")
        blocks = lesson["blocks"]
        if len(blocks) < 10:
            problems.append(f"{lid}: 内容块过少")
        code_n = sum(1 for b in blocks if b["type"] == "code")
        out_n = sum(1 for b in blocks if b["type"] == "output")
        if code_n != out_n:
            problems.append(f"{lid}: code/output 不配对")
        for i, b in enumerate(blocks):
            if b["type"] == "quiz" and not (0 <= b["answer"] < len(b["options"])):
                problems.append(f"{lid}: quiz 答案越界")
        # 真实执行每个代码块，并与其后的 output 块逐字比对
        for i, b in enumerate(blocks):
            if b["type"] != "code":
                continue
            runnable += 1
            r = sql_runner.run_sql(b["code"])
            if not r["ok"]:
                problems.append(f"{lid}#{i}: 执行失败 {r['error']}")
                continue
            declared = blocks[i + 1].get("text", "") if i + 1 < len(blocks) and blocks[i + 1]["type"] == "output" else None
            if declared is None:
                problems.append(f"{lid}#{i}: 缺少紧随其后的 output 块")
            elif r["stdout"].strip() != declared.strip():
                problems.append(f"{lid}#{i}: output 与真实结果不一致\n期望 {declared[:120]!r}\n实际 {r['stdout'][:120]!r}")
        # 判题
        ex = lesson["exercise"]
        r = sql_runner.check_sql(ex["solution"], ex["tests"])
        if not r["passed"]:
            problems.append(f"{lid}: 参考答案未通过 {r['error']['message'][:120]}")
        rs = sql_runner.check_sql(ex["starterCode"], ex["tests"])
        if rs["passed"]:
            problems.append(f"{lid}: starter 不应通过")

    total_tests = sum(len(l["exercise"]["tests"]) for l in lessons)
    print(f"讲数={len(lessons)} 可运行块={runnable} 判题用例={total_tests} 问题数={len(problems)}")
    for p in problems:
        print(" -", p)
    if problems:
        return 1
    print("全部通过：结构 + 真实执行 + 输出比对 + 判题 + starter 拒绝")
    return 0


if __name__ == "__main__":
    sys.exit(main())
