package com.pyneon.academy.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * 课程路线进度计算单测（纯数据逻辑，不依赖 Android）。
 *
 * 为什么重要：路线页显示的百分比与文案直接暴露给用户，
 * 算错会出现「0/0 显示 100%」或「完成 3/5 显示 60%」这类明显错误。
 */
class TrackProgressTest {

    private fun track(
        lessonCount: Int = 5,
        doneCount: Int = 0,
        status: TrackStatus = TrackStatus.READY
    ) = Track(
        id = "t", title = "T", subtitle = "", category = "编程语言",
        status = status, accentArgb = 0L,
        lessonCount = lessonCount, doneCount = doneCount
    )

    @Test
    fun `percent is proportional`() {
        assertEquals(0, track(lessonCount = 5, doneCount = 0).progressPercent)
        assertEquals(50, track(lessonCount = 10, doneCount = 5).progressPercent)
        assertEquals(100, track(lessonCount = 5, doneCount = 5).progressPercent)
    }

    @Test
    fun `zero lessons yields zero percent not crash`() {
        assertEquals(0, track(lessonCount = 0, doneCount = 0).progressPercent)
    }

    @Test
    fun `percent is clamped to 0-100`() {
        // 异常数据（done > total）不应显示 120%
        assertEquals(100, track(lessonCount = 5, doneCount = 9).progressPercent)
        // 负数也不应出现
        assertTrue(track(lessonCount = 5, doneCount = -3).progressPercent >= 0)
    }

    @Test
    fun `not installed hint mentions language center`() {
        val t = track(lessonCount = 6, doneCount = 0, status = TrackStatus.NOT_INSTALLED)
        assertTrue(
            "未安装的包必须提示去语言中心下载，实际：${t.progressHint}",
            t.progressHint.contains("语言中心")
        )
    }

    @Test
    fun `installed hint shows progress`() {
        val t = track(lessonCount = 6, doneCount = 2, status = TrackStatus.READY)
        assertTrue("应显示已完成数量", t.progressHint.contains("2"))
        assertTrue("应显示总数", t.progressHint.contains("6"))
    }
}
