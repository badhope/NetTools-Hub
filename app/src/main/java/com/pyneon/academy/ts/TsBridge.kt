package com.pyneon.academy.ts

import android.content.Context
import com.pyneon.academy.js.JsBridge
import com.pyneon.academy.lang.LanguageIds
import com.pyneon.academy.lang.LanguageRuntime
import com.pyneon.academy.lang.RunResult

/**
 * TypeScript 运行时。
 *
 * 实现策略：**转译后交给已有的 Rhino 执行器**，不引入第二个 JS 引擎。
 *  - 类型系统在运行时本就不存在，擦除类型标注后的语义与 JS 完全一致；
 *  - 因此判题、变量快照、超时看门狗、输出截断、REPL 全部复用 [JsBridge]，
 *    行为与 JavaScript 课程保持一致（同一套沙箱，不会出现「TS 能访问 Java 类」的漏洞）；
 *  - 不新增 native 依赖，APK 体积零增长。
 *
 * 与 JavaScript 运行时的差异：
 *  - 带类型标注的源码会先经 [TypeScriptTranspiler] 擦除；
 *  - 判题用例同样需要转译（课程里的 tests 是 TS 写法）；
 *  - `version` 报 TypeScript 语言版本而非 Rhino 版本，避免误导。
 *
 * 明确的边界：这是**教学子集**，不支持装饰器/命名空间/条件类型等高级特性。
 * 课程内容与 `tools/gen_language_packs.py` 共同保证不越界，越界时 JS 会报语法错误
 * 而不是静默给出错误结果——宁可报错，不可错答。
 */
object TsBridge : LanguageRuntime {

    override val id: String = LanguageIds.TYPESCRIPT
    override val displayName: String = LanguageIds.displayNameOf(LanguageIds.TYPESCRIPT)
    override val fileExtension: String = "ts"
    override val grammarScope: String = "source.ts"

    /**
     * 展示用版本串。TypeScript 本身只是「带类型的 JS 写法」，
     * 这里报语义子集版本，避免让人误以为内置了完整 tsc。
     */
    override val version: String get() = "教学子集（类型擦除）"

    override fun isAvailable(): Boolean = true

    override fun ensureStarted(context: Context) = JsBridge.ensureStarted(context)

    override fun runCode(
        code: String,
        stdinLines: List<String>,
        timeoutSec: Double
    ): RunResult {
        val result = TypeScriptTranspiler.transpile(code)
        return JsBridge.runCode(result.code, stdinLines, timeoutSec)
    }

    override fun checkExercise(
        code: String,
        tests: List<String>,
        stdinLines: List<String>
    ): RunResult {
        val js = TypeScriptTranspiler.transpile(code)
        // 判题用例里也可能写类型标注（例如 `const f: (n: number) => number = ...`），同样转译
        val jsTests = tests.map { TypeScriptTranspiler.transpile(it).code }
        return JsBridge.checkExercise(js.code, jsTests, stdinLines)
    }

    override fun warmup(): Boolean = JsBridge.warmup()

    override fun replStart() = JsBridge.replStart()

    /**
     * REPL 单行推送。转译后再交给 JS 会话；
     * 多行块（`more=true`）的缓冲由 JsBridge 维护，这里无需重复处理。
     */
    override fun replPush(line: String): Pair<Boolean, String> =
        JsBridge.replPush(TypeScriptTranspiler.transpile(line).code)
}
