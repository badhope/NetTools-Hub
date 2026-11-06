#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用真实 LuaJ 3.0.1 校验三套 Lua 课程包。

不是结构校验：这里生成一个临时 Java harness（.tmp/lua_verify/ 下，不提交），
用与 App 相同的沙箱配置（Globals + JseBaseLib / TableLib / StringLib /
JseMathLib / CoroutineLib，PackageLib 的 finder 置空，print 重定向捕获，
注入 assert）逐条执行：

  1. 每个 runnable 代码块，必须执行成功，且 stdout 必须与紧随其后的
     output 块逐字一致；
  2. 每个 practice 块，代码必须执行成功且 stdout 与块内 output 一致；
  3. 每讲 exercise.solution + tests，必须全部通过；
  4. 每讲 exercise.starterCode + tests，必须至少有一个用例失败
     （否则练习没有难度）。

同时做结构校验：3 包 × 10 讲、id 唯一且连续、order / chapter /
chapterName 对齐、每讲内容块数量与类型覆盖、正文汉字数、测试条数。

用法：
    python tools/verify_lua_packs.py
    python tools/verify_lua_packs.py --keep     # 保留 .tmp/lua_verify

退出码 0 全部通过；1 有失败。
"""
import argparse
import base64
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PACKS = ROOT / "content_packs"
TMP = ROOT / ".tmp" / "lua_verify"

LUAJ_JAR = pathlib.Path(
    "C:/Dev/gradle-home-mashang/caches/modules-2/files-2.1/org.luaj/luaj-jse/3.0.1/"
    "99245b2df284805e1cb835e9be47c243f9717511/luaj-jse-3.0.1.jar"
)

PACK_SPECS = [
    ("lua-basics", 41, "Lua · 基础篇", 400),
    ("lua-core", 42, "Lua · 核心篇", 410),
    ("lua-advanced", 43, "Lua · 进阶篇", 420),
]

CONTENT_TYPES = {"heading", "text", "code", "output", "table", "diagram",
                 "tip", "warn", "quiz", "practice", "steps", "fill", "order",
                 "compare", "visualize", "task"}

CJK = re.compile(r"[\u4e00-\u9fff]")


def cjk_count(lesson):
    """正文汉字数：只统计 text 块，代码与 output 不算正文。"""
    return sum(len(CJK.findall(b.get("text", "")))
               for b in lesson["blocks"] if b.get("type") == "text")


def all_cjk_count(lesson):
    """全部讲解类文本的汉字数（含提示/表格/测验），用于辅助判断篇幅。"""
    total = 0
    for b in lesson["blocks"]:
        if b.get("type") in ("code", "output"):
            continue
        for k, v in b.items():
            if k == "type":
                continue
            if isinstance(v, str):
                total += len(CJK.findall(v))
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        total += len(CJK.findall(item))
                    elif isinstance(item, list):
                        for cell in item:
                            if isinstance(cell, str):
                                total += len(CJK.findall(cell))
    return total


def structure_checks():
    problems = []
    lessons = []
    for pack, chapter, chapter_name, base_order in PACK_SPECS:
        path = PACKS / f"{pack}.json"
        if not path.is_file():
            problems.append(f"{pack}: 文件不存在 {path}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"{pack}: JSON 解析失败 {exc}")
            continue
        if len(data) != 10:
            problems.append(f"{pack}: 应为 10 讲，实际 {len(data)}")
        for i, item in enumerate(data):
            lid = item.get("id", f"{pack}#{i}")
            lessons.append(item)
            if item.get("lang") != "lua":
                problems.append(f"{lid}: lang 应为 lua，实际 {item.get('lang')!r}")
            if item.get("order") != base_order + i:
                problems.append(f"{lid}: order 应为 {base_order + i}，实际 {item.get('order')}")
            if item.get("chapter") != chapter:
                problems.append(f"{lid}: chapter 应为 {chapter}，实际 {item.get('chapter')}")
            if item.get("chapterName") != chapter_name:
                problems.append(f"{lid}: chapterName 应为 {chapter_name!r}，实际 {item.get('chapterName')!r}")
            expected_id = {
                "lua-basics": f"lua{i + 1:02d}",
                "lua-core": f"lua{i + 11:02d}",
                "lua-advanced": f"lua{i + 21:02d}",
            }[pack]
            if lid != expected_id:
                problems.append(f"{lid}: id 应为 {expected_id}")
            blocks = item.get("blocks") or []
            if len(blocks) < 8:
                problems.append(f"{lid}: 内容块 {len(blocks)} 个，少于 8 个")
            types = [b.get("type") for b in blocks]
            for t in types:
                if t not in CONTENT_TYPES:
                    problems.append(f"{lid}: 未知块类型 {t}")
            for required in ("heading", "text", "code", "output", "table", "quiz"):
                if required not in types:
                    problems.append(f"{lid}: 缺少 {required} 块")
            if "tip" not in types and "warn" not in types:
                problems.append(f"{lid}: 缺少 tip/warn 块")
            if "table" not in types and "diagram" not in types:
                problems.append(f"{lid}: 缺少 table/diagram 块")
            n_text = types.count("text")
            if not 2 <= n_text <= 4:
                problems.append(f"{lid}: text 块 {n_text} 个，应在 2-4 之间")
            if types.count("quiz") < 1:
                problems.append(f"{lid}: quiz 数量不足")
            n_cjk = cjk_count(item)
            if not 900 <= n_cjk <= 1600:
                problems.append(f"{lid}: 正文汉字 {n_cjk}，不在 900-1600 之间")

            # code 块必须显式 runnable，且后接 output
            for j, b in enumerate(blocks):
                if b.get("type") != "code":
                    continue
                if not b.get("runnable"):
                    problems.append(f"{lid}: 第 {j + 1} 个代码块没有显式 runnable")
                nxt = blocks[j + 1] if j + 1 < len(blocks) else None
                if not nxt or nxt.get("type") != "output":
                    problems.append(f"{lid}: 第 {j + 1} 个代码块后面缺少 output 块")
                # LuaJ 3.0.1 / Lua 5.2 沙箱的禁用特性
                for bad in ("goto ", "utf8.", "io.", "os.", "loadstring", "//", "<<"):
                    if bad in b["code"]:
                        problems.append(f"{lid}: 第 {j + 1} 个代码块使用了禁用写法 {bad!r}")

            ex = item.get("exercise") or {}
            for key in ("title", "brief", "starterCode", "hint", "tests", "stdin", "xp", "solution"):
                if key not in ex:
                    problems.append(f"{lid}: exercise 缺少字段 {key}")
            tests = ex.get("tests") or []
            if not 3 <= len(tests) <= 5:
                problems.append(f"{lid}: tests {len(tests)} 条，应为 3-5 条")
            if not ex.get("solution"):
                problems.append(f"{lid}: 缺少 solution")

            # 与 LessonRepository.parseLesson 对齐的字段校验
            for j, b in enumerate(blocks):
                t = b.get("type")
                if t == "quiz":
                    opts = b.get("options") or []
                    if not 2 <= len(opts) <= 4:
                        problems.append(f"{lid}: 第 {j + 1} 块 quiz 选项数 {len(opts)} 越界")
                    if not isinstance(b.get("answer"), int) or not 0 <= b["answer"] < len(opts):
                        problems.append(f"{lid}: 第 {j + 1} 块 quiz answer 越界")
                if t == "table":
                    width = len(b.get("headers") or [])
                    for row in b.get("rows") or []:
                        if len(row) != width:
                            problems.append(f"{lid}: 第 {j + 1} 块表格列数不一致")

    ids = [x.get("id") for x in lessons]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        problems.append(f"重复 id: {dup}")
    missing = [f"lua{i:02d}" for i in range(1, 31) if f"lua{i:02d}" not in ids]
    if missing:
        problems.append(f"缺少讲次: {missing}")
    return lessons, problems


HARNESS_JAVA = r"""
import org.luaj.vm2.Globals;
import org.luaj.vm2.LuaError;
import org.luaj.vm2.LuaValue;
import org.luaj.vm2.Varargs;
import org.luaj.vm2.compiler.LuaC;
import org.luaj.vm2.lib.CoroutineLib;
import org.luaj.vm2.lib.DebugLib;
import org.luaj.vm2.lib.PackageLib;
import org.luaj.vm2.lib.StringLib;
import org.luaj.vm2.lib.TableLib;
import org.luaj.vm2.lib.VarArgFunction;
import org.luaj.vm2.lib.jse.JseBaseLib;
import org.luaj.vm2.lib.jse.JseMathLib;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/**
 * 与 LuaBridge.newGlobals / checkInternal 对齐的校验 harness。
 * 输入：TSV，每行 CASE \t id \t kind \t codeB64 \t test1B64 \t ...
 * 输出：TSV，每行 RESULT \t id \t ok(0/1) \t stdoutB64 \t errorB64
 */
public class LuaVerifyHarness {

    static class Timeout extends RuntimeException {
        Timeout() { super("lua-sandbox-timeout"); }
    }

    static class Watch extends DebugLib {
        @Override
        public void onInstruction(int pc, Varargs v, int top) {
            if (System.nanoTime() > deadline) throw new Timeout();
        }
    }

    static volatile long deadline = Long.MAX_VALUE;

    static class Sink {
        final StringBuilder main = new StringBuilder();
        final StringBuilder test = null;
    }

    static Globals newGlobals(StringBuilder out) {
        Globals g = new Globals();
        g.load(new JseBaseLib());
        g.load(new PackageLib());
        g.load(new TableLib());
        g.load(new StringLib());
        g.load(new JseMathLib());
        g.load(new CoroutineLib());
        g.load(new Watch());
        LuaC.install(g);
        g.finder = name -> null;
        g.set("debug", LuaValue.NIL);
        g.set("dofile", LuaValue.NIL);
        g.set("loadfile", LuaValue.NIL);
        g.set("print", new VarArgFunction() {
            @Override
            public Varargs invoke(Varargs args) {
                StringBuilder sb = new StringBuilder();
                for (int i = 1; i <= args.narg(); i++) {
                    if (i > 1) sb.append('\t');
                    sb.append(args.arg(i).tojstring());
                }
                out.append(sb).append('\n');
                return LuaValue.NONE;
            }
        });
        return g;
    }

    static String firstLine(Throwable t) {
        String m = t.getMessage() == null ? "错误" : t.getMessage();
        for (String line : m.split("\\R")) {
            if (!line.trim().isEmpty()) return line.trim();
        }
        return "错误";
    }

    public static void main(String[] args) throws Exception {
        Path input = Paths.get(args[0]);
        Path output = Paths.get(args[1]);
        List<String> results = new ArrayList<>();
        for (String line : Files.readAllLines(input, StandardCharsets.UTF_8)) {
            if (line.isEmpty()) continue;
            String[] parts = line.split("\t", -1);
            String id = parts[0];
            String kind = parts[1];
            String code = new String(Base64.getDecoder().decode(parts[2]), StandardCharsets.UTF_8);
            List<String> tests = new ArrayList<>();
            for (int i = 3; i < parts.length; i++) {
                if (!parts[i].isEmpty())
                    tests.add(new String(Base64.getDecoder().decode(parts[i]), StandardCharsets.UTF_8));
            }
            StringBuilder out = new StringBuilder();
            String error = "";
            boolean ok = true;
            Globals g = newGlobals(out);
            deadline = System.nanoTime() + 5_000_000_000L;
            try {
                g.load(code, "<lesson>").call();
            } catch (Throwable t) {
                ok = false;
                error = firstLine(t);
            } finally {
                deadline = Long.MAX_VALUE;
            }
            if (ok && "exercise".equals(kind)) {
                for (int i = 0; i < tests.size(); i++) {
                    deadline = System.nanoTime() + 2_000_000_000L;
                    try {
                        g.load(tests.get(i), "<lua-test-" + (i + 1) + ">").call();
                    } catch (Throwable t) {
                        ok = false;
                        error = "test#" + (i + 1) + ": " + firstLine(t);
                        break;
                    } finally {
                        deadline = Long.MAX_VALUE;
                    }
                }
            }
            results.add(String.join("\t",
                    "RESULT", id, ok ? "1" : "0",
                    Base64.getEncoder().encodeToString(out.toString().getBytes(StandardCharsets.UTF_8)),
                    Base64.getEncoder().encodeToString(error.getBytes(StandardCharsets.UTF_8))));
        }
        Files.write(output, results, StandardCharsets.UTF_8);
    }
}
"""


def build_cases(lessons):
    cases = []  # (id, kind, code, tests, expected_output or None, label)
    for item in lessons:
        lid = item["id"]
        blocks = item["blocks"]
        for idx, b in enumerate(blocks):
            if b.get("type") != "code" or not b.get("runnable"):
                continue
            expected = None
            if idx + 1 < len(blocks) and blocks[idx + 1].get("type") == "output":
                expected = blocks[idx + 1]["text"]
            cases.append((f"{lid}#code{idx + 1}", "code", b["code"], [], expected, "runnable"))
        # practice 块也带可执行代码与期望输出，同样实跑
        for idx, b in enumerate(blocks):
            if b.get("type") != "practice":
                continue
            cases.append((f"{lid}#practice{idx + 1}", "code", b["code"], [], b["output"], "practice"))
        ex = item["exercise"]
        cases.append((f"{lid}#solution", "exercise", ex["solution"], ex["tests"], None, "solution"))
        cases.append((f"{lid}#starter", "exercise", ex["starterCode"], ex["tests"], None, "starter"))
    return cases


def run_harness(cases):
    TMP.mkdir(parents=True, exist_ok=True)
    java_file = TMP / "LuaVerifyHarness.java"
    java_file.write_text(HARNESS_JAVA, encoding="utf-8")

    cases_file = TMP / "cases.tsv"
    lines = []
    for cid, kind, code, tests, _expected, _label in cases:
        row = [cid, kind, base64.b64encode(code.encode("utf-8")).decode("ascii")]
        row += [base64.b64encode(t.encode("utf-8")).decode("ascii") for t in tests]
        lines.append("\t".join(row))
    cases_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    jar = str(LUAJ_JAR)
    subprocess.run(
        ["javac", "-encoding", "UTF-8", "-cp", jar, "-d", str(TMP), str(java_file)],
        check=True, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    result_file = TMP / "results.tsv"
    proc = subprocess.run(
        ["java", "-cp", f"{jar}{';' if sys.platform == 'win32' else ':'}{TMP}",
         "LuaVerifyHarness", str(cases_file), str(result_file)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"harness 执行失败：{proc.stderr[-2000:]}")
    results = {}
    for line in result_file.read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        parts = line.split("\t", -1)
        results[parts[1]] = {
            "ok": parts[2] == "1",
            "stdout": base64.b64decode(parts[3]).decode("utf-8"),
            "error": base64.b64decode(parts[4]).decode("utf-8"),
        }
    return results


def normalize(text):
    return text.replace("\r\n", "\n").rstrip("\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true", help="保留 .tmp/lua_verify")
    args = ap.parse_args()

    if not LUAJ_JAR.is_file():
        print(f"[FAIL] 找不到 LuaJ jar: {LUAJ_JAR}")
        return 1

    lessons, problems = structure_checks()
    print(f"结构校验：{len(lessons)} 讲，{len(problems)} 个问题")
    for x in problems:
        print("  STRUCT:", x)

    cases = build_cases(lessons)
    runnable_cases = [c for c in cases if c[5] == "runnable"]
    practice_cases = [c for c in cases if c[5] == "practice"]
    solution_cases = [c for c in cases if c[5] == "solution"]
    starter_cases = [c for c in cases if c[5] == "starter"]
    print(f"执行用例：runnable {len(runnable_cases)} 段 / practice {len(practice_cases)} 段"
          f" / solution {len(solution_cases)} 讲 / starter {len(starter_cases)} 讲")

    results = run_harness(cases)

    failures = []
    checked_output = 0
    run_ok = sol_ok = starter_rejected = 0
    practice_ok = 0
    for cid, kind, code, tests, expected, label in cases:
        r = results.get(cid)
        if r is None:
            failures.append(f"{cid}: harness 没有返回结果")
            continue
        if label == "practice":
            if not r["ok"]:
                failures.append(f"{cid}: practice 执行失败 {r['error']}")
            elif expected is not None and normalize(r["stdout"]) != normalize(expected):
                failures.append(
                    f"{cid}: practice 输出与块内 output 不一致\n"
                    f"    实际: {normalize(r['stdout'])!r}\n"
                    f"    期望: {normalize(expected)!r}"
                )
            else:
                practice_ok += 1
        elif label == "runnable":
            if r["ok"]:
                run_ok += 1
            else:
                failures.append(f"{cid}: 执行失败 {r['error']}")
            if expected is not None:
                checked_output += 1
                if normalize(r["stdout"]) != normalize(expected):
                    failures.append(
                        f"{cid}: 输出与 output 块不一致\n"
                        f"    实际: {normalize(r['stdout'])!r}\n"
                        f"    期望: {normalize(expected)!r}"
                    )
        elif label == "solution":
            if r["ok"]:
                sol_ok += 1
            else:
                failures.append(f"{cid}: 参考答案未通过 {r['error']}")
        elif label == "starter":
            if r["ok"]:
                failures.append(f"{cid}: starter 竟然通过了全部用例（练习没有难度）")
            else:
                starter_rejected += 1

    print(f"执行结果：runnable 通过 {run_ok}/{len(runnable_cases)}，输出比对 {checked_output} 段，"
          f"practice 通过 {practice_ok}/{len(practice_cases)}，"
          f"solution 通过 {sol_ok}/{len(solution_cases)}，"
          f"starter 拒绝 {starter_rejected}/{len(starter_cases)}")
    if failures:
        print(f"\n失败 {len(failures)} 项：")
        for f in failures:
            print(" ", f)
    else:
        print("\n全部通过：结构、runnable/practice 执行与输出、solution 判题、starter 拒绝")

    if not args.keep:
        shutil.rmtree(TMP, ignore_errors=True)
    return 1 if (failures or problems) else 0


if __name__ == "__main__":
    sys.exit(main())
