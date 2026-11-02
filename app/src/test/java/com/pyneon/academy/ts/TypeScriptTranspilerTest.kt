package com.pyneon.academy.ts

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * TypeScript 转译器单测（纯 JVM，不需要 Android 设备）。
 *
 * 重点覆盖三类最容易写错的地方：
 *  1. 类型标注必须被擦除（正向）
 *  2. 字符串 / 注释 / 对象键 / 三元冒号**不能被**误擦（反向，最关键）
 *  3. enum 转译为冻结对象且编号规则正确
 */
class TypeScriptTranspilerTest {

    // ===== 正向：该擦的要擦干净 =====

    @Test
    fun `variable type annotation is erased`() {
        val out = TypeScriptTranspiler.transpile("var n: number = 5;").code
        assertEquals("var n = 5;", out.trim())
    }

    @Test
    fun `function params and return type are erased`() {
        val out = TypeScriptTranspiler.transpile(
            "function add(a: number, b: number): number {\n  return a + b;\n}"
        ).code
        assertTrue(out, out.contains("function add(a, b)"))
        assertFalse(out, out.contains(": number"))
    }

    @Test
    fun `arrow function types are erased`() {
        val out = TypeScriptTranspiler.transpile("var f = (x: number): number => x * 2;").code
        assertTrue(out, out.contains("(x)"))
        assertTrue(out, out.contains("=> x * 2"))
        assertFalse(out, out.contains(": number"))
    }

    @Test
    fun `interface block is removed entirely`() {
        val src = "interface Hero {\n  name: string;\n  level: number;\n}\nvar v = 1;"
        val out = TypeScriptTranspiler.transpile(src).code
        assertFalse("interface 应被整段删除: $out", out.contains("interface"))
        assertFalse("字段声明不应残留: $out", out.contains("level: number"))
        assertTrue("后续代码必须保留: $out", out.contains("var v = 1;"))
    }

    @Test
    fun `type alias is removed`() {
        val out = TypeScriptTranspiler.transpile("type Id = string;\nvar x = 1;").code
        assertFalse(out, out.contains("type Id"))
        assertTrue(out, out.contains("var x = 1;"))
    }

    @Test
    fun `generic params are erased`() {
        val out = TypeScriptTranspiler.transpile("function first<T>(arr: T[]): T {\n  return arr[0];\n}").code
        assertTrue(out, out.contains("function first(arr)"))
        assertFalse(out, out.contains("<T>"))
    }

    @Test
    fun `union type is erased as a whole`() {
        val out = TypeScriptTranspiler.transpile("function f(v: string | number): string { return ''; }").code
        assertTrue(out, out.contains("function f(v)"))
        assertFalse("联合类型必须整段擦除，不能只删掉一部分", out.contains("| number"))
    }

    @Test
    fun `array type is erased`() {
        val out = TypeScriptTranspiler.transpile("var nums: number[] = [1, 2];").code
        assertEquals("var nums = [1, 2];", out.trim())
    }

    @Test
    fun `access modifiers are removed`() {
        val out = TypeScriptTranspiler.transpile("class A {\n  private x = 1;\n  readonly y = 2;\n}").code
        assertFalse(out, out.contains("private"))
        assertFalse(out, out.contains("readonly"))
    }

    @Test
    fun `as cast is removed`() {
        val out = TypeScriptTranspiler.transpile("var n = (x as number) + 1;").code
        assertTrue(out, out.contains("(x) + 1"))
        assertFalse(out, out.contains("as number"))
    }

    @Test
    fun `non null assertion is removed`() {
        val out = TypeScriptTranspiler.transpile("var v = obj!.name;").code
        assertTrue(out, out.contains("obj.name"))
    }

    // ===== 反向：不该擦的绝不能被擦（最容易出 bug） =====

    @Test
    fun `object literal keys are preserved`() {
        val out = TypeScriptTranspiler.transpile("var o = { key: 'val', other: 2 };").code
        assertTrue("对象键不能被当成类型标注擦掉: $out", out.contains("key: 'val'"))
        assertTrue(out, out.contains("other: 2"))
    }

    @Test
    fun `ternary colon is preserved`() {
        val out = TypeScriptTranspiler.transpile("var a = n > 3 ? 'big' : 'small';").code
        assertTrue("三元冒号不能被擦: $out", out.contains("? 'big' : 'small'"))
    }

    @Test
    fun `colon inside string is preserved`() {
        val out = TypeScriptTranspiler.transpile("var s = 'a: b: c';").code
        assertTrue("字符串里的冒号必须保留: $out", out.contains("'a: b: c'"))
    }

    @Test
    fun `comment content is untouched`() {
        val src = "// note: this is a comment\nvar x = 1;"
        val out = TypeScriptTranspiler.transpile(src).code
        assertTrue(out, out.contains("// note: this is a comment"))
    }

    @Test
    fun `plain javascript passes through unchanged`() {
        val js = "function add(a, b) {\n  return a + b;\n}\nconsole.log(add(1, 2));"
        val result = TypeScriptTranspiler.transpile(js)
        assertEquals("纯 JS 不应被改动", js, result.code)
        assertFalse(result.changed)
    }

    // ===== enum =====

    @Test
    fun `enum becomes frozen object with correct numbering`() {
        val out = TypeScriptTranspiler.transpile("enum Level {\n  Low,\n  Mid = 10,\n  High\n}").code
        assertTrue(out, out.contains("Object.freeze"))
        assertTrue("Low 应为 0: $out", out.contains("Low: 0"))
        assertTrue("Mid 应为 10: $out", out.contains("Mid: 10"))
        assertTrue("High 应接着 Mid +1 = 11: $out", out.contains("High: 11"))
        assertFalse(out, out.contains("enum"))
    }

    @Test
    fun `transpiled output is valid javascript syntax`() {
        // 仅检查擦除后没有残留的 TS 专有关键字
        val src = """
            interface P { name: string; }
            type Id = number;
            function get(p: P): string { return p.name; }
            var id: Id = 1;
        """.trimIndent()
        val out = TypeScriptTranspiler.transpile(src).code
        for (bad in listOf("interface", "type Id", ": string", ": P", ": Id")) {
            assertFalse("残留 TS 语法 '$bad':\n$out", out.contains(bad))
        }
    }
}
