"""每日任务与徽章的日期语义（2026-11 发布前审计修复的回归锁）。"""
import ast
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
GAM = ROOT / "app" / "src" / "main" / "java" / "com" / "pyneon" / "academy" / "data" / "Gamification.kt"
VM = ROOT / "app" / "src" / "main" / "java" / "com" / "pyneon" / "academy" / "data" / "ViewModels.kt"


class DailyMissionTests(unittest.TestCase):
    def test_daily_mission_checks_date(self):
        """只判断 dailyCount 会让昨天的完成状态延续到今天。"""
        text = GAM.read_text(encoding="utf-8")
        m = re.search(r"fun dailyMissionDone\([^)]*\)[^\n]*\n?[^\n]*", text)
        self.assertIsNotNone(m, "找不到 dailyMissionDone")
        seg = m.group(0)
        self.assertIn("dailyDate", seg, "每日任务必须比较 dailyDate")
        self.assertIn("todayEpochDay", seg, "必须与当天日期比较")


class BadgePersistenceTests(unittest.TestCase):
    def test_badges_are_merged_not_replaced(self):
        """徽章是历史成就：断档后重算不能把已获得的删掉。"""
        text = VM.read_text(encoding="utf-8")
        start = text.index("private suspend fun updateBadges")
        seg = text[start:start + 900]
        self.assertIn("progress.badges", seg, "必须读取已有徽章")
        self.assertIn("longestStreak", seg, "必须按历史最长连击补发")
        self.assertIn("setBadges", seg)
        # 不能出现「新建空集合直接覆盖」的旧写法
        self.assertNotIn("val badges = mutableSetOf<String>()", seg,
                         "旧实现会覆盖并丢失历史徽章")

    def test_first_day_badge_is_awarded_on_first_open(self):
        text = VM.read_text(encoding="utf-8")
        first_branch = text[text.index("if (last == -1L)"):][:600]
        self.assertIn("updateBadges", first_branch, "首日必须发放 first_day 徽章")
