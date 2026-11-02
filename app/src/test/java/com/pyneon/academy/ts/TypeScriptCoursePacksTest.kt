package com.pyneon.academy.ts

import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File

/**
 * TypeScript 课程包端到端验证（纯 JVM，用 Node 真实执行）。
 *
 * 为什么必须端到端：转译器单测只证明「字符串擦对了」，但课程要的是
 * 「参考答案能通过判题用例」。只有把 solution 和 tests 都转译后交给真实
 * JS 引擎跑一遍，才能证明这 6 讲课程是可用的、不是摆着看的。
 *
 * 执行方式：拼成一段 Node 脚本（solution + 每条 test + 失败即退出非 0），
 * 与 App 内 `checkExercise` 的语义对齐（测试共享同一作用域、assert 抛错即失败）。
 */
class TypeScriptCoursePacksTest {

    private fun repoRoot(): File {
        var dir = File(System.getProperty("user.dir") ?: ".")
        while (!File(dir, "content_packs").exists()) {
            dir = dir.parentFile ?: error("找不到仓库根目录")
        }
        return dir
    }

    private fun loadPack(): JSONArray {
        val file = File(repoRoot(), "content_packs/ts-basics.json")
        assertTrue("缺少 content_packs/ts-basics.json", file.exists())
        return JSONArray(file.readText(Charsets.UTF_8))
    }

    private fun runNode(script: String): Pair<Int, String> {
        val tmp = File.createTempFile("mashang-ts-", ".js")
        try {
            tmp.writeText(script, Charsets.UTF_8)
            val proc = ProcessBuilder("node", tmp.absolutePath)
                .redirectErrorStream(true)
                .start()
            val out = proc.inputStream.bufferedReader().readText()
            val code = proc.waitFor()
            return code to out
        } finally {
            tmp.delete()
        }
    }

    private fun nodeAvailable(): Boolean = try {
        val p = ProcessBuilder("node", "--version").redirectErrorStream(true).start()
        p.inputStream.bufferedReader().readText().trim()
        p.waitFor() == 0
    } catch (_: Exception) {
        false
    }

    @Test
    fun `pack has six lessons with typescript lang`() {
        val pack = loadPack()
        assertEquals(6, pack.length())
        for (i in 0 until pack.length()) {
            val lesson = pack.getJSONObject(i)
            assertEquals("typescript", lesson.getString("lang"))
            assertTrue("order 需 >= 600 避开其他包", lesson.getInt("order") >= 600)
        }
    }

    @Test
    fun `every solution passes its own tests after transpilation`() {
        if (!nodeAvailable()) {
            println("[skip] 未安装 node，跳过端到端执行")
            return
        }
        val pack = loadPack()
        var checked = 0
        for (i in 0 until pack.length()) {
            val lesson = pack.getJSONObject(i)
            val id = lesson.getString("id")
            val exercise = lesson.getJSONObject("exercise")
            val solution = exercise.getString("solution")
            val tests = exercise.getJSONArray("tests")

            val jsSolution = TypeScriptTranspiler.transpile(solution).code
            val sb = StringBuilder()
            // App 内 `assert` 由 JsBridge.installHost 注入；Node 里需自己补一个等价 shim，
            // 语义与 JsBridge 保持一致：条件为假即抛错（进程非 0 退出）。
            sb.append("function assert(c, m) { if (!c) { throw new Error(m || 'assert failed'); } }\n")
            sb.append(jsSolution).append("\n")
            for (t in 0 until tests.length()) {
                val jsTest = TypeScriptTranspiler.transpile(tests.getString(t)).code
                sb.append(jsTest).append("\n")
            }
            val (code, out) = runNode(sb.toString())
            assertEquals("[$id] 参考答案未通过判题：\n$out\n--- 转译结果 ---\n$sb", 0, code)
            checked++
        }
        assertEquals("应覆盖全部 6 讲", 6, checked)
    }

    @Test
    fun `starter code alone does not pass`() {
        // 起始代码是空的/占位实现，必须判题失败——否则练习没有意义
        if (!nodeAvailable()) {
            println("[skip] 未安装 node")
            return
        }
        val pack = loadPack()
        for (i in 0 until pack.length()) {
            val lesson = pack.getJSONObject(i)
            val id = lesson.getString("id")
            val exercise = lesson.getJSONObject("exercise")
            val starter = TypeScriptTranspiler.transpile(exercise.getString("starterCode")).code
            val tests = exercise.getJSONArray("tests")
            val sb = StringBuilder()
            sb.append("function assert(c, m) { if (!c) { throw new Error(m || 'assert failed'); } }\n")
            sb.append(starter).append("\n")
            for (t in 0 until tests.length()) {
                sb.append(TypeScriptTranspiler.transpile(tests.getString(t)).code).append("\n")
            }
            val (code, _) = runNode(sb.toString())
            assertTrue("[$id] 起始代码不应直接通过判题", code != 0)
        }
    }
}
