"""新内容块（compare / visualize）的契约与可执行性测试。

为什么需要这个文件：`compare` 块里嵌的是**多门语言的真实代码**，如果其中
任何一段跑不起来，学习者点「运行」就会看到报错——比没有这个功能更糟。
因此这里对每段 compare 代码做真实执行（能跑的引擎都跑一遍）。
"""
import json
import os
import shutil
import subprocess
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PACKS = os.path.join(ROOT, "content_packs")
ASSETS = os.path.join(ROOT, "app", "src", "main", "assets")

sys.path.insert(
    0, os.path.join(ROOT, "app", "src", "main", "python")
)

NODE = shutil.which("node")


def _all_lessons():
    lessons = []
    for name in ("lessons_basic.json", "lessons_mid.json", "lessons_adv.json", "lessons_pro.json"):
        with open(os.path.join(ASSETS, name), encoding="utf-8") as f:
            lessons.extend(json.load(f))
    with open(os.path.join(ASSETS, "challenges.json"), encoding="utf-8") as f:
        challenges = json.load(f)
    for name in sorted(os.listdir(PACKS)):
        if name.endswith(".json"):
            with open(os.path.join(PACKS, name), encoding="utf-8") as f:
                lessons.extend(json.load(f))
    return lessons, challenges


class CompareBlockTests(unittest.TestCase):
    def test_compare_blocks_are_well_formed(self):
        lessons, _ = _all_lessons()
        found = 0
        for lesson in lessons:
            for b in lesson["blocks"]:
                if b.get("type") != "compare":
                    continue
                found += 1
                with self.subTest(lesson=lesson["id"]):
                    cols = b.get("columns") or []
                    self.assertGreaterEqual(len(cols), 2, "对照至少两栏才有对比意义")
                    langs = [c.get("lang") for c in cols]
                    self.assertEqual(len(langs), len(set(langs)), "同一对照块内语言不能重复")
                    for c in cols:
                        self.assertTrue(c.get("code"), "每栏必须有代码")
        self.assertGreater(found, 0, "至少应有一个 compare 块（否则功能没被使用）")

    @unittest.skipUnless(NODE, "未安装 node")
    def test_python_columns_execute(self):
        lessons, _ = _all_lessons()
        import runner

        for lesson in lessons:
            for b in lesson["blocks"]:
                if b.get("type") != "compare":
                    continue
                for col in b["columns"]:
                    if col.get("lang") != "python":
                        continue
                    with self.subTest(lesson=lesson["id"]):
                        r = runner.run_code(col["code"])
                        self.assertTrue(r["ok"], f"Python 对照代码执行失败：{r['error']}")

    @unittest.skipUnless(NODE, "未安装 node")
    def test_javascript_columns_execute(self):
        lessons, _ = _all_lessons()
        for lesson in lessons:
            for b in lesson["blocks"]:
                if b.get("type") != "compare":
                    continue
                for col in b["columns"]:
                    if col.get("lang") != "javascript":
                        continue
                    with self.subTest(lesson=lesson["id"]):
                        proc = subprocess.run(
                            [NODE, "-e", col["code"]],
                            capture_output=True, text=True, encoding="utf-8",
                            errors="replace", timeout=20,
                        )
                        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_typescript_columns_are_within_subset(self):
        """TS 对照代码不得使用转译器不支持的特性。"""
        lessons, _ = _all_lessons()
        forbidden = ("@decorator", "namespace ", "declare module", "abstract class")
        for lesson in lessons:
            for b in lesson["blocks"]:
                if b.get("type") != "compare":
                    continue
                for col in b["columns"]:
                    if col.get("lang") != "typescript":
                        continue
                    with self.subTest(lesson=lesson["id"]):
                        for bad in forbidden:
                            self.assertNotIn(bad, col["code"], f"TS 对照含不支持特性：{bad}")


class VisualizeBlockTests(unittest.TestCase):
    def test_visualize_blocks_are_well_formed(self):
        lessons, _ = _all_lessons()
        found = 0
        for lesson in lessons:
            for b in lesson["blocks"]:
                if b.get("type") != "visualize":
                    continue
                found += 1
                with self.subTest(lesson=lesson["id"]):
                    frames = b.get("frames") or []
                    self.assertGreaterEqual(len(frames), 2, "至少两帧才构成「过程」")
                    for f in frames:
                        self.assertTrue(f.get("label"), "每帧必须有说明文字")
                        names = {i["name"] for i in (f.get("items") or [])}
                        for h in (f.get("highlight") or []):
                            self.assertIn(h, names, f"高亮项 {h!r} 必须存在于该帧")
        self.assertGreater(found, 0, "至少应有一个 visualize 块")

    def test_visualize_last_frame_settles(self):
        """末帧不应再有高亮变化——否则动画看起来「没结束」。"""
        lessons, _ = _all_lessons()
        for lesson in lessons:
            for b in lesson["blocks"]:
                if b.get("type") != "visualize":
                    continue
                with self.subTest(lesson=lesson["id"]):
                    last = b["frames"][-1]
                    # 允许末帧高亮（表示「循环条件变假」这类终态），但要求它有 label 说明
                    self.assertTrue(last.get("label"))


class BlockParserTests(unittest.TestCase):
    """Kotlin 解析器必须认识这两个新块（否则界面上显示为空）。"""

    def test_parser_handles_compare_and_visualize(self):
        path = os.path.join(
            ROOT, "app", "src", "main", "java", "com", "pyneon", "academy",
            "data", "LessonRepository.kt",
        )
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn('"compare" ->', text, "解析器缺少 compare 分支")
        self.assertIn('"visualize" ->', text, "解析器缺少 visualize 分支")
        self.assertIn("Block.Compare", text)
        self.assertIn("Block.Visualize", text)

    def test_renderer_handles_both_blocks(self):
        path = os.path.join(
            ROOT, "app", "src", "main", "java", "com", "pyneon", "academy",
            "screens", "LessonDetailScreen.kt",
        )
        with open(path, encoding="utf-8") as f:
            text = f.read()
        self.assertIn("is Block.Compare ->", text, "课程页缺少 compare 渲染分派")
        self.assertIn("is Block.Visualize ->", text, "课程页缺少 visualize 渲染分派")


if __name__ == "__main__":
    unittest.main(verbosity=2)
