package com.pyneon.academy.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * 段位与成就逻辑单测。
 *
 * 为什么重要：段位由 XP 阈值决定，边界算错会出现「0 XP 就显示系统架构师」
 * 或「达到阈值还停在上一阶」这类明显错误，直接影响用户信任。
 */
class GamificationTest {

    @Test
    fun `zero xp is the lowest rank`() {
        val rank = Ranks.forXp(0)
        assertEquals(0, rank.minXp)
        assertTrue("0 XP 应是第一阶", rank.name.isNotEmpty())
    }

    @Test
    fun `rank boundaries are inclusive`() {
        // 遍历所有段位阈值，恰好等于阈值时应落在该段位
        Ranks.all.forEach { r ->
            assertEquals(
                "在 ${r.minXp} XP 应处于 ${r.name}",
                r.name,
                Ranks.forXp(r.minXp).name
            )
        }
    }

    @Test
    fun `one xp below threshold stays in previous rank`() {
        Ranks.all.drop(1).forEach { r ->
            val justBelow = r.minXp - 1
            if (justBelow >= 0) {
                val actual = Ranks.forXp(justBelow)
                assertTrue(
                    "在 $justBelow XP 不应已达 ${r.name}，实际 ${actual.name}",
                    actual.minXp < r.minXp
                )
            }
        }
    }

    @Test
    fun `next rank is correct`() {
        assertEquals(Ranks.all[1].name, Ranks.next(0)?.name)
        // 满级后没有下一阶
        val maxXp = Ranks.all.last().minXp
        assertNull("满级后 next 应返回 null", Ranks.next(maxXp))
    }

    @Test
    fun `fraction is bounded zero to one`() {
        assertEquals(0f, Ranks.fraction(0), 0.01f)
        assertEquals(1f, Ranks.fraction(Ranks.all.last().minXp), 0.01f)
        // 中间值应在 0..1 之间
        val mid = Ranks.all[1].minXp
        val f = Ranks.fraction(mid)
        assertTrue("fraction 应在 0..1，实际 $f", f in 0f..1f)
    }

    @Test
    fun `ranks are ordered by minXp`() {
        val mins = Ranks.all.map { it.minXp }
        assertEquals("段位必须按 XP 升序排列", mins.sorted(), mins)
    }

    @Test
    fun `achievement list is not empty and has unique keys`() {
        val all = Achievement.entries
        assertTrue("成就不能为空", all.isNotEmpty())
        assertEquals(
            "成就枚举名必须唯一",
            all.size,
            all.map { it.name }.toSet().size
        )
        all.forEach {
            assertTrue("${it.name} 缺少标题", it.title.isNotEmpty())
            assertTrue("${it.name} 缺少描述", it.desc.isNotEmpty())
        }
    }
}
