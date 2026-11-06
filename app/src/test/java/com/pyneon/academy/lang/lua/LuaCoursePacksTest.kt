package com.pyneon.academy.lang.lua

import com.pyneon.academy.lua.LuaBridge
import org.json.JSONArray
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/**
 * Lua 课程包真执行门禁：每一讲的参考答案都必须在真实 LuaJ 上跑过其全部判题用例。
 *
 * 只做结构校验是不够的——JS 课程曾经出现「用例写得对、但引擎跑不了」的漂移，
 * 这里直接调用 [LuaBridge.checkExercise]，与 App 内判题走同一条代码路径。
 */
class LuaCoursePacksTest {

    private fun repoRoot(): File {
        var dir = File(System.getProperty("user.dir")).absoluteFile
        repeat(5) {
            if (File(dir, "content_packs").isDirectory) return dir
            dir = dir.parentFile ?: return@repeat
        }
        error("找不到仓库根目录（content_packs）")
    }

    private fun packFiles(): List<File> {
        val files = File(repoRoot(), "content_packs").listFiles()
            ?.filter { it.name.matches(Regex("""lua-(basics|core|advanced|expert)\.json""")) }
            ?.sortedBy { it.name }
            ?: emptyList()
        assertTrue("缺少 content_packs/lua-*.json", files.isNotEmpty())
        return files
    }

    @Test
    fun everyLuaLessonSolutionPassesItsOwnTests() {
        for (pack in packFiles()) {
            val lessons = JSONArray(pack.readText(Charsets.UTF_8))
            assertTrue("Lua 课程包为空：$pack", lessons.length() > 0)
            for (i in 0 until lessons.length()) {
                val lesson = lessons.getJSONObject(i)
                val id = lesson.getString("id")
                val exercise = lesson.getJSONObject("exercise")
                val solution = exercise.getString("solution")
                val tests = exercise.getJSONArray("tests").let { arr ->
                    buildList { for (j in 0 until arr.length()) add(arr.getString(j)) }
                }
                val result = LuaBridge.checkExercise(solution, tests)
                assertTrue(
                    "$id 的参考答案未通过：${result.errorType} ${result.errorMessage}",
                    result.ok && result.passed == true
                )
            }
        }
    }

    @Test
    fun everyLuaRunnableCodeBlockExecutes() {
        for (pack in packFiles()) {
            val lessons = JSONArray(pack.readText(Charsets.UTF_8))
            for (i in 0 until lessons.length()) {
                val lesson = lessons.getJSONObject(i)
                val blocks = lesson.getJSONArray("blocks")
                for (j in 0 until blocks.length()) {
                    val block = blocks.getJSONObject(j)
                    if (block.optString("type") != "code") continue
                    if (!block.optBoolean("runnable", false)) continue
                    val result = LuaBridge.runCode(block.getString("code"), emptyList(), 5.0)
                    assertTrue(
                        "${lesson.getString("id")} 第 ${j + 1} 个代码块执行失败：${result.errorType} ${result.errorMessage}",
                        result.ok
                    )
                }
            }
        }
    }
}
