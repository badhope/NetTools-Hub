package com.pyneon.academy.c

import android.content.Context
import com.pyneon.academy.lang.LanguageIds
import com.pyneon.academy.lang.LanguageRuntime
import com.pyneon.academy.lang.RunResult
import com.pyneon.academy.lang.VarInfo

/**
 * C 运行时（教学子集解释器，纯 Kotlin 实现）。
 *
 * 为什么不是真编译器：Android 离线场景下 clang + 头文件 + 链接器要 200–400 MB，
 * 且无法链接 bionic libc。本项目用 [CInterpreter] 直接解释执行 C 子集，
 * 语义与 gcc 一致的部分照做，不支持的部分明确报错。
 *
 * 与 Java/C++/Go/Rust 的区别：那四门在 [LanguageIds.PLANNED] 里标注「暂不支持」，
 * 而 C 有真实可用的运行时——学习者写 `printf` 能看到真实输出、能判题、能改错。
 */
object CBridge : LanguageRuntime {

    override val id: String = LanguageIds.C
    override val displayName: String = LanguageIds.displayNameOf(LanguageIds.C)
    override val fileExtension: String = "c"
    override val grammarScope: String = "source.c"

    /** 展示版本：明确标注是子集解释器，不冒充 gcc。 */
    override val version: String get() = "教学子集（解释执行）"

    override fun isAvailable(): Boolean = true

    override fun ensureStarted(context: Context) = Unit

    override fun runCode(
        code: String,
        stdinLines: List<String>,
        timeoutSec: Double
    ): RunResult {
        val started = System.nanoTime()
        val r = CInterpreter.run(code, stdinLines)
        return toRunResult(r, started)
    }

    override fun checkExercise(
        code: String,
        tests: List<String>,
        stdinLines: List<String>
    ): RunResult {
        val started = System.nanoTime()
        val r = CInterpreter.check(code, tests)
        val base = toRunResult(r, started)
        return base.copy(passed = r.ok)
    }

    override fun warmup(): Boolean = true

    // C 是编译型语言，没有 REPL 语义；这里提供「单次执行」的等价体验。
    override fun replStart() = Unit

    override fun replPush(line: String): Pair<Boolean, String> {
        val r = CInterpreter.run(line)
        val text = buildString {
            append(r.stdout)
            if (!r.ok) append("\n${r.errorType}: ${r.errorMessage}")
        }
        return false to text
    }

    private fun toRunResult(r: CInterpreter.Result, startedAt: Long): RunResult = RunResult(
        ok = r.ok,
        stdout = r.stdout,
        stderr = "",
        errorType = r.errorType,
        errorMessage = r.errorMessage,
        traceback = null,
        durationMs = (System.nanoTime() - startedAt) / 1_000_000,
        variables = r.variables.map { VarInfo(it.first, it.second, it.third) },
        passed = null
    )
}
