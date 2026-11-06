package com.pyneon.academy.lang

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertSame
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * 运行时注册表的回落语义（2026-11 发布前审计修复的回归锁）。
 *
 * 旧实现 `get(id) = runtimes[id] ?: runtimes[DEFAULT]`：任何未注册的 id
 * 都会拿到 Python。后果是语言中心把「没有运行时的语言」显示成「可离线运行」，
 * 用户写完代码被 Python 用语法错误拒绝，排查方向完全错。
 */
class LanguageRegistryFallbackTest {

    private class FakeRuntime(override val id: String) : LanguageRuntime {
        override val displayName: String get() = id
        override val fileExtension: String get() = "txt"
        override val grammarScope: String get() = "text.plain"
        override val version: String get() = "test"
        override fun isAvailable(): Boolean = true
        override fun ensureStarted(context: android.content.Context) = Unit
        override fun runCode(code: String, stdinLines: List<String>, timeoutSec: Double) =
            RunResult(true, "", "", null, null, null, 0L, emptyList(), null)
        override fun checkExercise(code: String, tests: List<String>, stdinLines: List<String>) =
            RunResult(true, "", "", null, null, null, 0L, emptyList(), true)
        override fun warmup(): Boolean = true
        override fun replStart() = Unit
        override fun replPush(line: String) = false to ""
    }

    @Test
    fun `unknown non-empty id returns unsupported runtime`() {
        val runtimes = mapOf<String, LanguageRuntime>(LanguageIds.PYTHON to FakeRuntime(LanguageIds.PYTHON))
        val r = LanguageRegistry.resolveRuntime("java", runtimes)
        assertFalse("未注册语言不得回落到 Python 并声称可用", r.isAvailable())
        assertTrue("应返回 UnsupportedRuntime", r is UnsupportedRuntime)
        assertEquals("java", r.id)
    }

    @Test
    fun `known id returns the real runtime`() {
        val py = FakeRuntime(LanguageIds.PYTHON)
        assertSame(py, LanguageRegistry.resolveRuntime(LanguageIds.PYTHON, mapOf(LanguageIds.PYTHON to py)))
    }

    @Test
    fun `blank id falls back to default language`() {
        val py = FakeRuntime(LanguageIds.PYTHON)
        assertSame(py, LanguageRegistry.resolveRuntime("", mapOf(LanguageIds.PYTHON to py)))
    }

    @Test
    fun `unsupported runtime reports a readable error instead of crashing`() {
        val r = UnsupportedRuntime("rust")
        assertFalse(r.isAvailable())
        val result = r.runCode("fn main(){}", emptyList(), 1.0)
        assertFalse(result.ok)
        assertEquals("LanguageNotBundled", result.errorType)
        assertTrue(result.errorMessage!!.contains("运行时未内置"))
    }
}
