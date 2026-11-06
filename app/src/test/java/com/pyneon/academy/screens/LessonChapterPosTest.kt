package com.pyneon.academy.screens

import com.pyneon.academy.data.Lesson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

/**
 * 课程列表「章节内序号 / 上一讲」定位逻辑（纯函数，不依赖 Android）。
 *
 * 背景（2026-11 审查发现）：课程列表会按语言筛选、按关键词搜索，列表下标随之
 * 漂移。旧实现用 `lessons[index-1]` 判断解锁、用 `orderInChapter[index]` 显示
 * 序号，切到「只看 JavaScript」时会显示 01/07/19 这类错乱序号，锁定条件还会
 * 错指到上一门语言的最后一讲。这里锁定修复后的行为。
 */
class LessonChapterPosTest {

    private fun lesson(id: String, chapterName: String, order: Int) = Lesson(
        id = id,
        order = order,
        chapter = 1,
        chapterName = chapterName,
        title = id,
        subtitle = "",
        xp = 50,
        blocks = emptyList(),
        exercise = null
    )

    @Test
    fun `first lesson of a chapter has no previous`() {
        val map = buildChapterPositions(listOf(lesson("a1", "A", 1), lesson("a2", "A", 2)))
        assertEquals(1, map.getValue("a1").index)
        assertNull(map.getValue("a1").prevId)
        assertEquals(2, map.getValue("a2").index)
        assertEquals("a1", map.getValue("a2").prevId)
    }

    @Test
    fun `each chapter restarts numbering`() {
        val map = buildChapterPositions(
            listOf(
                lesson("a1", "A", 1),
                lesson("a2", "A", 2),
                lesson("b1", "B", 10),
                lesson("b2", "B", 11)
            )
        )
        assertEquals(1, map.getValue("b1").index)
        assertEquals(2, map.getValue("b2").index)
        assertNull(map.getValue("b1").prevId)
        assertEquals("b1", map.getValue("b2").prevId)
    }

    @Test
    fun `lookup by id survives filtering`() {
        val all = listOf(
            lesson("a1", "A", 1),
            lesson("a2", "A", 2),
            lesson("b1", "B", 10),
            lesson("b2", "B", 11)
        )
        val map = buildChapterPositions(all)
        // 模拟「只看 B 章」：列表只剩 b1、b2，但位置信息必须仍然正确
        val filtered = all.filter { it.chapterName == "B" }
        assertEquals(1, map.getValue(filtered[0].id).index)
        assertEquals(2, map.getValue(filtered[1].id).index)
        assertNull(map.getValue(filtered[0].id).prevId)
    }

    @Test
    fun `unknown chapter name still groups together`() {
        // 空 chapterName 的课程会被归为同一章（旧数据兼容路径）
        val map = buildChapterPositions(listOf(lesson("x", "", 1), lesson("y", "", 2)))
        assertEquals(1, map.getValue("x").index)
        assertEquals(2, map.getValue("y").index)
    }
}
