package com.pyneon.academy.c

import org.json.JSONArray
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/**
 * C 课程包端到端验证（纯 JVM）。
 *
 * 用真实解释器跑每讲的参考答案 × 判题用例，证明课程可用而非摆设。
 * 同时验证「起始代码不通过」——否则练习没有意义。
 */
class CCoursePacksTest {

    private fun repoRoot(): File {
        var dir = File(System.getProperty("user.dir") ?: ".")
        while (!File(dir, "content_packs").exists()) {
            dir = dir.parentFile ?: error("找不到仓库根目录")
        }
        return dir
    }

    private fun packFiles(): List<File> {
        val dir = repoRoot()
        val files = dir.resolve("content_packs").listFiles()
            ?.filter { it.name.matches(Regex("""c-(basics|core|advanced)\.json""")) }
            ?.sortedBy { it.name }
            ?: emptyList()
        assertTrue("缺少 content_packs/c-*.json", files.isNotEmpty())
        return files
    }

    private fun loadPacks(): List<JSONArray> = packFiles().map { JSONArray(it.readText(Charsets.UTF_8)) }

    @Test
    fun `packs cover 30 lessons across three tiers`() {
        val packs = loadPacks()
        assertEquals("C 课程应为 基础/核心/进阶 三包", 3, packs.size)
        val ids = mutableListOf<String>()
        packs.forEach { pack ->
            assertEquals("每包 10 讲", 10, pack.length())
            for (i in 0 until pack.length()) {
                val lesson = pack.getJSONObject(i)
                assertEquals("c", lesson.getString("lang"))
                assertTrue("order 需 >= 700 避开其他包", lesson.getInt("order") >= 700)
                ids.add(lesson.getString("id"))
            }
        }
        assertEquals("合计 30 讲", 30, ids.size)
        assertEquals("讲 id 不得重复", 30, ids.distinct().size)
    }

    @Test
    fun `every solution passes its own tests`() {
        for (pack in loadPacks()) {
            for (i in 0 until pack.length()) {
                val lesson = pack.getJSONObject(i)
                val id = lesson.getString("id")
                val ex = lesson.getJSONObject("exercise")
                val solution = ex.getString("solution")
                val tests = ex.getJSONArray("tests").let { arr ->
                    (0 until arr.length()).map { arr.getString(it) }
                }
                val r = CInterpreter.check(solution, tests)
                assertTrue("[$id] 参考答案未通过判题：${r.errorMessage}", r.ok)
            }
        }
    }

    @Test
    fun `starter code does not pass`() {
        for (pack in loadPacks()) {
            for (i in 0 until pack.length()) {
                val lesson = pack.getJSONObject(i)
                val id = lesson.getString("id")
                val ex = lesson.getJSONObject("exercise")
                val starter = ex.getString("starterCode")
                val tests = ex.getJSONArray("tests").let { arr ->
                    (0 until arr.length()).map { arr.getString(it) }
                }
                val r = CInterpreter.check(starter, tests)
                assertFalse("[$id] 起始代码不应直接通过判题", r.ok)
            }
        }
    }

    @Test
    fun `every runnable code block executes without error`() {
        for (pack in loadPacks()) {
            for (i in 0 until pack.length()) {
                val lesson = pack.getJSONObject(i)
                val id = lesson.getString("id")
                val blocks = lesson.getJSONArray("blocks")
                for (b in 0 until blocks.length()) {
                    val block = blocks.getJSONObject(b)
                    if (block.getString("type") != "code") continue
                    if (!block.optBoolean("runnable", false)) continue
                    val code = block.getString("code")
                    val r = CInterpreter.run(code)
                    assertTrue("[$id] 可运行代码块执行失败：${r.errorMessage}\n--- 代码 ---\n$code", r.ok)
                }
            }
        }
    }
}
