package com.pyneon.academy.data

import org.junit.Assert.assertEquals
import org.junit.Test

/**
 * 路线进度口径（2026-11 发布前审计修复的回归锁）。
 *
 * 旧实现用「当前已装包里的讲数」做分母：只装基础篇 10/10 通关 = 100%，
 * 再装核心篇立刻跌到 50%，用户会以为进度倒退。多包路线的分母必须固定为
 * 整门语言的总讲数。
 */
class TrackCompletionTest {

    @Test
    fun `multi-pack track keeps total as denominator`() {
        // 模拟：38 讲的路线，只完成 10 讲，分母仍应为 38
        val t = Track(
            id = "js", title = "JavaScript", subtitle = "", category = "编程语言",
            status = TrackStatus.READY, accentArgb = 0L,
            lessonCount = 38, doneCount = 10, packIds = listOf("js-basics", "js-core", "js-advanced", "js-expert")
        )
        assertEquals(26, t.progressPercent)
    }

    @Test
    fun `single-pack track uses its own count`() {
        val t = Track(
            id = "dsa", title = "DSA", subtitle = "", category = "算法",
            status = TrackStatus.READY, accentArgb = 0L,
            lessonCount = 5, doneCount = 5, packIds = listOf("dsa-basics")
        )
        assertEquals(100, t.progressPercent)
    }

    @Test
    fun `not installed track never reports 100 percent`() {
        val t = Track(
            id = "sql", title = "SQL", subtitle = "", category = "编程语言",
            status = TrackStatus.NOT_INSTALLED, accentArgb = 0L,
            lessonCount = 38, doneCount = 0,
            packIds = listOf("sql-basics", "sql-core", "sql-advanced", "sql-expert")
        )
        assertEquals(0, t.progressPercent)
        assert(t.progressHint.contains("语言中心"))
    }
}
