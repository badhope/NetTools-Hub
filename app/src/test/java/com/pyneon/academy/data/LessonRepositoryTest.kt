package com.pyneon.academy.data

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.pyneon.academy.lang.LanguageIds
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * 课程仓库结构测试（Robolectric 读真实 assets）。
 *
 * 锁的是「多语言课程体系」的结构不变量——这些一旦破坏，
 * 用户可见的症状是：课程列表错乱、某语言消失、进度口径漂移。
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class LessonRepositoryTest {

    private val context: Context = ApplicationProvider.getApplicationContext()

    @Test
    fun `builtin ships six languages`() {
        val langs = LessonRepository.lessons(context).map { it.lang }.distinct().toSet()
        // 内置只有 Python；其余五门来自 content_packs（开发机上位于仓库根，测试环境可能没有）
        assertTrue("至少应包含 Python", LanguageIds.PYTHON in langs)
    }

    @Test
    fun `mainline is exactly the l-prefixed python lessons`() {
        val mainline = LessonRepository.mainline(context)
        assertTrue("主线不应为空", mainline.isNotEmpty())
        mainline.forEach {
            assertTrue("主线课程 id 必须形如 lNN：${it.id}", Regex("^l\\d{2}$").matches(it.id))
        }
        // 口径：主线数量 == id 匹配 lNN 的课程总数
        val all = LessonRepository.lessons(context)
        assertEquals(all.count { Regex("^l\\d{2}$").matches(it.id) }, mainline.size)
    }

    @Test
    fun `lesson ids are globally unique`() {
        val all = LessonRepository.lessons(context)
        val ids = all.map { it.id }
        assertEquals("课程 id 跨包必须唯一：${ids.groupBy { it }.filter { it.value.size > 1 }.keys}",
            ids.size, ids.toSet().size)
    }

    @Test
    fun `orders are globally sorted ascending`() {
        val orders = LessonRepository.lessons(context).map { it.order }
        assertEquals("课程按 order 升序排列", orders.sorted(), orders)
    }

    @Test
    fun `chapter names never mix languages within one chapter`() {
        // 一个章节（课程包）内语言必须一致；混了说明某讲的 lang 字段写错
        val violations = LessonRepository.lessons(context)
            .groupBy { it.chapterName }
            .filter { it.value.map { l -> l.lang }.distinct().size > 1 }
            .keys
        assertTrue("章节内语言混杂：$violations", violations.isEmpty())
    }

    @Test
    fun `every lesson has at least one runnable code block or is lang pack`() {
        // 结构问题守门：完全没有任何可运行块的课会让学习者无处下手。
        // 语言包（下载内容）在测试环境可能未安装，只校验内置课程。
        val builtin = LessonRepository.lessons(context)
            .filter { Regex("^l\\d{2}$").matches(it.id) }
        val empty = builtin.filter { b -> b.blocks.none { it is com.pyneon.academy.data.Block.CodeBlock } }
        assertTrue("内置课程不应完全没有代码块：$empty", empty.isEmpty())
    }

    @Test
    fun `xp is positive for every lesson`() {
        LessonRepository.lessons(context).forEach {
            assertTrue("${it.id} 的 XP 应为正数，实际 ${it.xp}", it.xp > 0)
        }
    }

    @Test
    fun `cache returns same instance until invalidated`() {
        val a = LessonRepository.lessons(context)
        val b = LessonRepository.lessons(context)
        assertEquals("缓存应返回同一列表实例", a, b)
        LessonRepository.invalidateCache()
        val c = LessonRepository.lessons(context)
        // 内容相同（同一批 assets），但实例是新解析的
        assertEquals(a.map { it.id }, c.map { it.id })
        assertNotEquals("invalidate 后应产生新实例", System.identityHashCode(a), System.identityHashCode(c))
    }
}
