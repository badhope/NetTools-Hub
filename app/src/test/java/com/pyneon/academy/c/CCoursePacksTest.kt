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

    private fun loadPack(): JSONArray {
        val f = File(repoRoot(), "content_packs/c-basics.json")
        assertTrue("缺少 content_packs/c-basics.json", f.exists())
        return JSONArray(f.readText(Charsets.UTF_8))
    }

    @Test
    fun `pack has six lessons with c lang`() {
        val pack = loadPack()
        assertEquals(6, pack.length())
        for (i in 0 until pack.length()) {
            val lesson = pack.getJSONObject(i)
            assertEquals("c", lesson.getString("lang"))
            assertTrue("order 需 >= 700 避开其他包", lesson.getInt("order") >= 700)
        }
    }

    @Test
    fun `every solution passes its own tests`() {
        val pack = loadPack()
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

    @Test
    fun `starter code does not pass`() {
        val pack = loadPack()
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

    @Test
    fun `every runnable code block executes without error`() {
        val pack = loadPack()
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
