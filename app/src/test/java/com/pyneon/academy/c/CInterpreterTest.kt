package com.pyneon.academy.c

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * C 解释器单测（纯 JVM）。
 *
 * 定位：这是「教学子集」，不是 gcc。测试既验证支持的功能真的能跑，
 * 也验证不支持的功能**明确报错**（而不是静默给出错误答案）。
 */
class CInterpreterTest {

    private fun run(src: String, stdin: List<String> = emptyList()) = CInterpreter.run(src, stdin)

    // ===== 基础执行 =====

    @Test
    fun `hello world prints`() {
        val r = run("""int main() { printf("hello\n"); return 0; }""")
        assertTrue(r.errorMessage ?: "", r.ok)
        assertEquals("hello\n", r.stdout)
    }

    @Test
    fun `arithmetic and precedence`() {
        val r = run("""int main() { printf("%d\n", 2 + 3 * 4); return 0; }""")
        assertTrue(r.ok)
        assertEquals("14\n", r.stdout)
    }

    @Test
    fun `integer division truncates`() {
        val r = run("""int main() { printf("%d\n", 7 / 2); return 0; }""")
        assertTrue(r.ok)
        assertEquals("3\n", r.stdout)
    }

    @Test
    fun `double formatting`() {
        val r = run("""int main() { double x = 7.0 / 2.0; printf("%.2f\n", x); return 0; }""")
        assertTrue(r.ok)
        assertEquals("3.50\n", r.stdout)
    }

    @Test
    fun `variables and assignment`() {
        val r = run("""int main() { int a = 5; a = a + 3; printf("%d\n", a); return 0; }""")
        assertTrue(r.ok)
        assertEquals("8\n", r.stdout)
    }

    // ===== 控制流 =====

    @Test
    fun `if else`() {
        val src = """int main() { int n = 7; if (n > 5) { printf("big"); } else { printf("small"); } return 0; }"""
        assertEquals("big", run(src).stdout)
    }

    @Test
    fun `while loop`() {
        val r = run("""int main() { int i = 0; while (i < 3) { printf("%d", i); i++; } return 0; }""")
        assertTrue(r.ok)
        assertEquals("012", r.stdout)
    }

    @Test
    fun `for loop`() {
        val r = run("""int main() { for (int i = 1; i <= 3; i++) { printf("%d", i); } return 0; }""")
        assertTrue(r.ok)
        assertEquals("123", r.stdout)
    }

    @Test
    fun `break and continue`() {
        val r = run("""int main() { for (int i = 0; i < 5; i++) { if (i == 3) break; if (i == 1) continue; printf("%d", i); } return 0; }""")
        assertTrue(r.ok)
        assertEquals("02", r.stdout)
    }

    // ===== 函数与递归 =====

    @Test
    fun `function call`() {
        val src = """
            int add(int a, int b) { return a + b; }
            int main() { printf("%d\n", add(2, 3)); return 0; }
        """.trimIndent()
        val r = run(src)
        assertTrue(r.errorMessage ?: "", r.ok)
        assertEquals("5\n", r.stdout)
    }

    @Test
    fun `recursion factorial`() {
        val src = """
            int fact(int n) { if (n <= 1) return 1; return n * fact(n - 1); }
            int main() { printf("%d\n", fact(5)); return 0; }
        """.trimIndent()
        val r = run(src)
        assertTrue(r.errorMessage ?: "", r.ok)
        assertEquals("120\n", r.stdout)
    }

    // ===== 数组 =====

    @Test
    fun `array declaration and indexing`() {
        val src = """
            int main() {
              int a[3];
              a[0] = 10; a[1] = 20; a[2] = 30;
              printf("%d %d\n", a[0], a[2]);
              return 0;
            }
        """.trimIndent()
        val r = run(src)
        assertTrue(r.errorMessage ?: "", r.ok)
        assertEquals("10 30\n", r.stdout)
    }

    @Test
    fun `array out of bounds is an error`() {
        val r = run("""int main() { int a[2]; a[5] = 1; return 0; }""")
        assertFalse("越界必须报错而不是静默写入", r.ok)
        assertTrue(r.errorMessage ?: "", r.errorMessage!!.contains("越界"))
    }

    // ===== 错误路径 =====

    @Test
    fun `missing main is reported`() {
        val r = run("""int foo() { return 1; }""")
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!.contains("main"))
    }

    @Test
    fun `division by zero is reported`() {
        val r = run("""int main() { int a = 1 / 0; return 0; }""")
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!.contains("零"))
    }

    @Test
    fun `infinite loop hits step limit`() {
        val r = run("""int main() { while (1) { } return 0; }""")
        assertFalse(r.ok)
        assertEquals("Timeout", r.errorType)
    }

    // ===== 明确不支持的语法要报「不支持」而不是晦涩错误 =====

    @Test
    fun `struct is rejected explicitly`() {
        val r = run("""struct P { int x; }; int main() { return 0; }""")
        assertFalse(r.ok)
        assertTrue("应提示不支持 struct：${r.errorMessage}", r.errorMessage!!.contains("不支持"))
    }

    @Test
    fun `include is rejected with guidance`() {
        val r = run("""#include <stdio.h>
int main() { return 0; }""")
        assertFalse(r.ok)
        assertTrue("应提示无需 include：${r.errorMessage}", r.errorMessage!!.contains("不支持"))
    }

    @Test
    fun `pointer declaration is rejected`() {
        val r = run("""int main() { int *p; return 0; }""")
        assertFalse("指针应报错而非静默", r.ok)
    }

    // ===== 判题 =====

    @Test
    fun `check passes when tests hold`() {
        val src = """int square(int n) { return n * n; }"""
        val tests = listOf(
            """int main() { assert(square(3) == 9, "square(3) 应为 9"); return 0; }""",
            """int main() { assert(square(0) == 0, "square(0) 应为 0"); return 0; }"""
        )
        val r = CInterpreter.check(src, tests)
        assertTrue(r.errorMessage ?: "", r.ok)
    }

    @Test
    fun `check fails when a test breaks`() {
        val src = """int square(int n) { return n + n; }"""
        val tests = listOf("""int main() { assert(square(3) == 9, "square(3) 应为 9"); return 0; }""")
        val r = CInterpreter.check(src, tests)
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!.contains("未通过"))
    }

    // ===== printf 格式 =====

    @Test
    fun `printf supports common specifiers`() {
        val src = """
            int main() {
              printf("%d|%c|%s|%.1f|%%\n", 42, 'A', "hi", 3.14159);
              return 0;
            }
        """.trimIndent()
        val r = run(src)
        assertTrue(r.errorMessage ?: "", r.ok)
        assertEquals("42|A|hi|3.1|%\n", r.stdout)
    }
}
