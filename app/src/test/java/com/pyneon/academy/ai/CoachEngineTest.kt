package com.pyneon.academy.ai

import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * 离线规则教练单测。
 *
 * 核心约束（产品红线）：**只引导、不代写**。判题失败时绝不能直接把正确答案
 * 塞给用户，否则学习闭环失效。这条必须有测试锁住。
 */
class CoachEngineTest {

    private fun analyze(
        type: String?,
        msg: String?,
        tb: String? = null,
        code: String = ""
    ) = CoachEngine.analyze(type, msg, tb, code)

    @Test
    fun `test failed gives checklist not answer`() {
        val tip = analyze("TestFailed", "共 3 个用例，1 个未通过")
        assertTrue("应有标题", tip.title.isNotEmpty())
        assertTrue("应给出引导步骤", tip.steps.isNotEmpty())
        // 红线：判题失败不得直接给修复代码
        assertFalse(
            "判题失败时不得给出可直接提交的答案示例",
            tip.example != null && tip.example.contains("return")
        )
    }

    @Test
    fun `name error gives diagnosis`() {
        val tip = analyze(
            "NameError",
            "name 'x' is not defined",
            "Traceback...\n  File \"<pyneon>\", line 3, in <module>\nNameError: name 'x' is not defined"
        )
        assertTrue("应识别为命名错误", tip.title.isNotEmpty())
        assertTrue("应给出步骤", tip.steps.isNotEmpty())
        assertNotNull("应能定位行号", tip.lineRef)
        assertTrue("行号应为正数", (tip.lineRef ?: 0) > 0)
    }

    @Test
    fun `indentation error is recognized`() {
        val tip = analyze("IndentationError", "unexpected indent")
        assertTrue("缩进错误应给出标题，实际为空", tip.title.isNotEmpty())
        assertTrue("缩进错误应给出步骤", tip.steps.isNotEmpty())
    }

    @Test
    fun `type error is recognized`() {
        val tip = analyze("TypeError", "unsupported operand type(s) for +: 'int' and 'str'")
        assertTrue(tip.title.isNotEmpty())
        assertTrue(tip.summary.isNotEmpty())
    }

    @Test
    fun `index error is recognized`() {
        val tip = analyze("IndexError", "list index out of range")
        assertTrue(tip.title.isNotEmpty())
    }

    @Test
    fun `timeout is recognized`() {
        val tip = analyze("Timeout", "代码运行超过 8.0 秒，已被强制中断")
        assertTrue("超时应给出提示", tip.title.isNotEmpty())
    }

    @Test
    fun `unknown error still returns a usable tip`() {
        val tip = analyze("SomeWeirdError", "something happened")
        assertTrue("未知错误也必须给出可读提示", tip.title.isNotEmpty())
        assertTrue(tip.steps.isNotEmpty())
    }

    @Test
    fun `null inputs do not crash`() {
        val tip = analyze(null, null)
        assertTrue("空输入不应崩溃", tip.title.isNotEmpty())
    }

    @Test
    fun `line number picks first frame not last`() {
        // 回归：旧实现取 lastOrNull，命中的是库内部帧而不是用户代码行
        val tb = """
            Traceback (most recent call last):
              File "<pyneon>", line 2, in <module>
              File "/stdlib/json/__init__.py", line 999, in loads
        """.trimIndent()
        val tip = analyze("ValueError", "bad", tb)
        assertNotNull(tip.lineRef)
    }
}
