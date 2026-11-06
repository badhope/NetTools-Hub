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

    private fun stdoutOf(src: String): String {
        val r = run(src)
        assertTrue(r.errorMessage ?: "", r.ok)
        return r.stdout
    }

    private fun failureOf(src: String): CInterpreter.Result {
        val r = run(src)
        assertFalse("本应失败却成功：${r.stdout}", r.ok)
        return r
    }

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

    // ===== switch / do-while =====

    @Test
    fun `switch selects one case and breaks`() {
        val src = """
            int main() {
              int x = 2;
              switch (x) {
                case 1: printf("one"); break;
                case 2: printf("two"); break;
                case 3: printf("three"); break;
                default: printf("other");
              }
              return 0;
            }
        """.trimIndent()
        assertEquals("two", stdoutOf(src))
    }

    @Test
    fun `switch falls through without break`() {
        val src = """
            int main() {
              int x = 2;
              switch (x) {
                case 1: printf("one");
                case 2: printf("two");
                case 3: printf("three"); break;
                default: printf("other");
              }
              return 0;
            }
        """.trimIndent()
        assertEquals("twothree", stdoutOf(src))
    }

    @Test
    fun `switch default runs when nothing matches`() {
        val src = """
            int main() {
              int x = 9;
              switch (x) {
                case 1: printf("one"); break;
                default: printf("other"); break;
              }
              return 0;
            }
        """.trimIndent()
        assertEquals("other", stdoutOf(src))
    }

    @Test
    fun `switch matches char case label`() {
        val src = """
            int main() {
              char c = 'b';
              switch (c) {
                case 'a': printf("A"); break;
                case 'b': printf("B"); break;
              }
              return 0;
            }
        """.trimIndent()
        assertEquals("B", stdoutOf(src))
    }

    @Test
    fun `switch break only exits the switch`() {
        val src = """
            int main() {
              for (int i = 0; i < 3; i++) {
                switch (i) {
                  case 1: printf("one"); break;
                  default: printf("%d", i);
                }
                printf("-");
              }
              return 0;
            }
        """.trimIndent()
        assertEquals("0-one-2-", stdoutOf(src))
    }

    @Test
    fun `continue inside switch continues the loop`() {
        val src = """
            int main() {
              for (int i = 0; i < 4; i++) {
                switch (i) {
                  case 1: continue;
                  default: printf("%d", i);
                }
              }
              return 0;
            }
        """.trimIndent()
        assertEquals("023", stdoutOf(src))
    }

    @Test
    fun `do while runs body at least once`() {
        val src = """
            int main() {
              int i = 5;
              do { printf("once"); } while (i < 3);
              return 0;
            }
        """.trimIndent()
        assertEquals("once", stdoutOf(src))
    }

    @Test
    fun `do while iterates with break and continue`() {
        val src = """
            int main() {
              int i = 0;
              do {
                i++;
                if (i == 2) continue;
                if (i == 4) break;
                printf("%d", i);
              } while (i < 10);
              return 0;
            }
        """.trimIndent()
        assertEquals("13", stdoutOf(src))
    }

    // ===== 位运算与复合赋值 =====

    @Test
    fun `bitwise operators`() {
        val src = """
            int main() {
              printf("%d %d %d %d\n", 6 & 3, 6 | 3, 6 ^ 3, ~0);
              return 0;
            }
        """.trimIndent()
        assertEquals("2 7 5 -1\n", stdoutOf(src))
    }

    @Test
    fun `shift operators`() {
        val src = """
            int main() {
              printf("%d %d\n", 1 << 4, 32 >> 2);
              return 0;
            }
        """.trimIndent()
        assertEquals("16 8\n", stdoutOf(src))
    }

    @Test
    fun `bitwise precedence matches c`() {
        // 位移低于加法：1 << (2 + 1) = 8
        assertEquals("8\n", stdoutOf("""int main() { printf("%d\n", 1 << 2 + 1); return 0; }"""))
        // & 低于 ==：5 & (3 == 3) = 1
        assertEquals("1\n", stdoutOf("""int main() { printf("%d\n", 5 & 3 == 3); return 0; }"""))
        // 1 | 2 ^ 3 & 2 = 1 | (2 ^ (3 & 2)) = 1
        assertEquals("1\n", stdoutOf("""int main() { printf("%d\n", 1 | 2 ^ 3 & 2); return 0; }"""))
        // 位运算高于 &&：1 & 0 || 2 = 2? -> (1&0)||2 = 1
        assertEquals("1\n", stdoutOf("""int main() { printf("%d\n", 1 & 0 || 2); return 0; }"""))
    }

    @Test
    fun `compound assignments`() {
        val src = """
            int main() {
              int a = 10;
              a += 5; a -= 3; a *= 2; a /= 4; a %= 4;
              a &= 3; a |= 8; a ^= 3; a <<= 2; a >>= 1;
              printf("%d\n", a);
              return 0;
            }
        """.trimIndent()
        assertEquals("18\n", stdoutOf(src))
    }

    @Test
    fun `compound assignment on array element`() {
        val src = """
            int main() {
              int a[2] = {7, 1};
              a[0] += 3;
              a[1] <<= 4;
              printf("%d %d\n", a[0], a[1]);
              return 0;
            }
        """.trimIndent()
        assertEquals("10 16\n", stdoutOf(src))
    }

    // ===== 指针对（至少 5 个） =====

    @Test
    fun `pointer address and dereference read write`() {
        val src = """
            int main() {
              int x = 1;
              int *p = &x;
              *p = 5;
              printf("%d %d\n", x, *p);
              return 0;
            }
        """.trimIndent()
        assertEquals("5 5\n", stdoutOf(src))
    }

    @Test
    fun `pointer to array indexes and dereferences`() {
        val src = """
            int main() {
              int a[5] = {10, 20, 30, 40, 50};
              int *p = a;
              printf("%d %d %d\n", p[2], *(p + 1), *(p + 4));
              return 0;
            }
        """.trimIndent()
        assertEquals("30 20 50\n", stdoutOf(src))
    }

    @Test
    fun `pointer increment walks the array`() {
        val src = """
            int sum(int *a, int n) {
              int s = 0;
              int *p = a;
              for (int i = 0; i < n; i++) { s += *p; p++; }
              return s;
            }
            int main() {
              int a[3] = {1, 2, 3};
              printf("%d\n", sum(a, 3));
              return 0;
            }
        """.trimIndent()
        assertEquals("6\n", stdoutOf(src))
    }

    @Test
    fun `pointer parameter gives reference semantics`() {
        val src = """
            void inc(int *p) { *p = *p + 1; }
            int main() {
              int x = 41;
              inc(&x);
              printf("%d\n", x);
              return 0;
            }
        """.trimIndent()
        assertEquals("42\n", stdoutOf(src))
    }

    @Test
    fun `swap through pointers`() {
        val src = """
            void swap(int *a, int *b) { int t = *a; *a = *b; *b = t; }
            int main() {
              int x = 1, y = 2;
              swap(&x, &y);
              printf("%d %d\n", x, y);
              return 0;
            }
        """.trimIndent()
        assertEquals("2 1\n", stdoutOf(src))
    }

    @Test
    fun `null pointer compares and dereference is an error`() {
        assertEquals(
            "null\n",
            stdoutOf("""int main() { int *p = NULL; if (p == NULL) printf("null\n"); return 0; }""")
        )
        val r = failureOf("int main() {\n int *p = NULL;\n int x = *p;\n return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("空指针"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 3 行"))
    }

    @Test
    fun `pointer difference and pointer plus integer`() {
        val src = """
            int main() {
              int a[4] = {1, 2, 3, 4};
              int *p = a;
              int *q = p + 2;
              printf("%d %d\n", *q, q - p);
              return 0;
            }
        """.trimIndent()
        assertEquals("3 2\n", stdoutOf(src))
    }

    // ===== 结构体（至少 5 个） =====

    @Test
    fun `struct fields read and write`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point p;
              p.x = 1;
              p.y = 2;
              printf("%d %d\n", p.x, p.y);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 2\n", stdoutOf(src))
    }

    @Test
    fun `struct initializer list`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point p = {3, 4};
              printf("%d %d\n", p.x, p.y);
              return 0;
            }
        """.trimIndent()
        assertEquals("3 4\n", stdoutOf(src))
    }

    @Test
    fun `struct array`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point ps[3];
              ps[0].x = 1;
              ps[1].y = 2;
              ps[2].x = 3;
              printf("%d %d %d\n", ps[0].x, ps[1].y, ps[2].x);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 2 3\n", stdoutOf(src))
    }

    @Test
    fun `struct pointer arrow access`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point p = {1, 2};
              struct Point *q = &p;
              q->x = 10;
              printf("%d %d\n", q->x, p.x);
              return 0;
            }
        """.trimIndent()
        assertEquals("10 10\n", stdoutOf(src))
    }

    @Test
    fun `struct passed by value is copied`() {
        val src = """
            struct Point { int x; int y; };
            void move(struct Point p) { p.x = 99; }
            int main() {
              struct Point p = {1, 2};
              move(p);
              printf("%d\n", p.x);
              return 0;
            }
        """.trimIndent()
        assertEquals("1\n", stdoutOf(src))
    }

    @Test
    fun `struct returned by value`() {
        val src = """
            struct Point { int x; int y; };
            struct Point make(int x, int y) {
              struct Point p;
              p.x = x; p.y = y;
              return p;
            }
            int main() {
              struct Point p = make(5, 6);
              printf("%d %d\n", p.x, p.y);
              return 0;
            }
        """.trimIndent()
        assertEquals("5 6\n", stdoutOf(src))
    }

    @Test
    fun `struct assignment copies fields`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point a = {1, 2};
              struct Point b;
              b = a;
              b.x = 9;
              printf("%d %d\n", a.x, b.x);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 9\n", stdoutOf(src))
    }

    @Test
    fun `typedef struct and typedef int`() {
        val src = """
            typedef struct { int x; int y; } Point;
            typedef int MyInt;
            int main() {
              Point p = {7, 8};
              MyInt n = 3;
              printf("%d %d %d\n", p.x, p.y, n);
              return 0;
            }
        """.trimIndent()
        assertEquals("7 8 3\n", stdoutOf(src))
    }

    @Test
    fun `nested struct one level`() {
        val src = """
            struct B { int x; int y; };
            struct A { struct B b; int c; };
            int main() {
              struct A a;
              a.b.x = 1;
              a.b.y = 2;
              a.c = 3;
              printf("%d %d %d\n", a.b.x, a.b.y, a.c);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 2 3\n", stdoutOf(src))
    }

    @Test
    fun `struct containing pointer member`() {
        val src = """
            struct Holder { int *p; int n; };
            int main() {
              int x = 7;
              struct Holder h;
              h.p = &x;
              h.n = 1;
              *(h.p) = 8;
              printf("%d %d\n", x, h.n);
              return 0;
            }
        """.trimIndent()
        assertEquals("8 1\n", stdoutOf(src))
    }

    // ===== sizeof（教学模型） =====

    @Test
    fun `sizeof scalar types follows teaching model`() {
        val src = """
            int main() {
              int *p = NULL;
              printf("%d %d %d %d %d\n", sizeof(int), sizeof(double), sizeof(char), sizeof(int *), sizeof(p));
              return 0;
            }
        """.trimIndent()
        assertEquals("4 8 1 8 8\n", stdoutOf(src))
    }

    @Test
    fun `sizeof arrays and elements`() {
        val src = """
            int main() {
              int a[5];
              int m[2][3];
              printf("%d %d %d %d\n", sizeof(a), sizeof(a[0]), sizeof(m), sizeof(m[0]));
              return 0;
            }
        """.trimIndent()
        assertEquals("20 4 24 12\n", stdoutOf(src))
    }

    @Test
    fun `sizeof struct rounds up to eight`() {
        val src = """
            struct Point { int x; int y; };
            struct B { int x; int y; };
            struct A { struct B b; int c; };
            int main() {
              printf("%d %d %d\n", sizeof(struct Point), sizeof(struct A), sizeof("abc"));
              return 0;
            }
        """.trimIndent()
        assertEquals("8 16 4\n", stdoutOf(src))
    }

    @Test
    fun `sizeof expression without parens`() {
        val src = """
            int main() {
              int x = 1;
              printf("%d\n", sizeof x);
              return 0;
            }
        """.trimIndent()
        assertEquals("4\n", stdoutOf(src))
    }

    // ===== 修饰符与字符串 =====

    @Test
    fun `const unsigned short modifiers accepted`() {
        val src = """
            int main() {
              const int a = 1;
              a = 2;
              unsigned int b = 3;
              short c = 4;
              unsigned d = 5;
              printf("%d %d %d %d\n", a, b, c, d);
              return 0;
            }
        """.trimIndent()
        assertEquals("2 3 4 5\n", stdoutOf(src))
    }

    @Test
    fun `char array string has terminator`() {
        val src = """
            int main() {
              char s[] = "abc";
              printf("%d %d %s\n", sizeof(s), strlen(s), s);
              return 0;
            }
        """.trimIndent()
        assertEquals("4 3 abc\n", stdoutOf(src))
    }

    @Test
    fun `char pointer string literal`() {
        val src = """
            int main() {
              char *s = "hello";
              printf("%s %d %c\n", s, strlen(s), s[1]);
              return 0;
            }
        """.trimIndent()
        assertEquals("hello 5 e\n", stdoutOf(src))
    }

    @Test
    fun `string copy and concat`() {
        val src = """
            int main() {
              char buf[20] = "ab";
              strcpy(buf, "hi");
              strcat(buf, "!");
              printf("%s %d\n", buf, strcmp(buf, "hi!"));
              return 0;
            }
        """.trimIndent()
        assertEquals("hi! 0\n", stdoutOf(src))
    }

    @Test
    fun `strcmp orders strings`() {
        val src = """
            int main() {
              printf("%d %d %d\n", strcmp("a", "b"), strcmp("b", "a"), strcmp("a", "a"));
              return 0;
            }
        """.trimIndent()
        assertEquals("-1 1 0\n", stdoutOf(src))
    }

    @Test
    fun `sprintf and atoi`() {
        val src = """
            int main() {
              char buf[32];
              sprintf(buf, "%d-%s", 42, "x");
              printf("%s %d %d\n", buf, atoi("123"), atoi(" -45abc"));
              return 0;
            }
        """.trimIndent()
        assertEquals("42-x 123 -45\n", stdoutOf(src))
    }

    @Test
    fun `char classification and case conversion`() {
        val src = """
            int main() {
              printf("%c %c %d %d %d\n", toupper('a'), tolower('Z'), isalpha('x'), isdigit('7'), isdigit('x'));
              return 0;
            }
        """.trimIndent()
        assertEquals("A z 1 1 0\n", stdoutOf(src))
    }

    @Test
    fun `math builtins`() {
        val src = """
            int main() {
              printf("%.1f %.1f %.1f %d %.0f %.0f\n",
                     fabs(-2.5), floor(2.9), ceil(2.1), abs(-7), pow(2, 3), sqrt(16.0));
              return 0;
            }
        """.trimIndent()
        assertEquals("2.5 2.0 3.0 7 8 4\n", stdoutOf(src))
    }

    @Test
    fun `memset fills memory`() {
        val src = """
            int main() {
              char buf[8];
              memset(buf, 'x', 3);
              buf[3] = 0;
              printf("%s\n", buf);
              return 0;
            }
        """.trimIndent()
        assertEquals("xxx\n", stdoutOf(src))
    }

    // ===== 二维数组 =====

    @Test
    fun `two dimensional array read write`() {
        val src = """
            int main() {
              int m[2][3];
              m[0][0] = 1;
              m[1][2] = 6;
              printf("%d %d %d\n", m[0][0], m[1][2], m[0][2]);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 6 0\n", stdoutOf(src))
    }

    @Test
    fun `two dimensional array nested initializer and loop`() {
        val src = """
            int main() {
              int m[2][2] = {{1, 2}, {3, 4}};
              int sum = 0;
              for (int i = 0; i < 2; i++) {
                for (int j = 0; j < 2; j++) sum += m[i][j];
              }
              printf("%d\n", sum);
              return 0;
            }
        """.trimIndent()
        assertEquals("10\n", stdoutOf(src))
    }

    @Test
    fun `two dimensional array row out of bounds reports line`() {
        val r = failureOf("int main() {\n int m[2][3];\n m[2][0] = 1;\n return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("越界"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 3 行"))
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
    fun `division by zero is reported with line`() {
        val r = failureOf("int main() {\n int a = 1 / 0;\n return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("零"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 2 行"))
    }

    @Test
    fun `undefined variable reports line`() {
        val r = failureOf("int main() {\n int a = 1;\n printf(\"%d\", b);\n return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("未声明"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 3 行"))
    }

    @Test
    fun `array index error reports line`() {
        val r = failureOf("int main() {\n int a[2];\n a[9] = 1;\n return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("越界"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 3 行"))
    }

    @Test
    fun `infinite loop hits step limit`() {
        val r = run("""int main() { while (1) { } return 0; }""")
        assertFalse(r.ok)
        assertEquals("Timeout", r.errorType)
    }

    // ===== 明确不支持的语法要报「不支持」而不是晦涩错误 =====

    @Test
    fun `struct is supported now`() {
        val src = """
            struct P { int x; };
            int main() { struct P p; p.x = 3; printf("%d\n", p.x); return 0; }
        """.trimIndent()
        assertEquals("3\n", stdoutOf(src))
    }

    @Test
    fun `include is rejected with guidance`() {
        val r = run("""#include <stdio.h>
int main() { return 0; }""")
        assertFalse(r.ok)
        assertTrue("应提示无需 include：${r.errorMessage}", r.errorMessage!!.contains("不支持"))
    }

    @Test
    fun `pointer declaration works now`() {
        val src = """
            int main() { int x = 2; int *p = &x; *p = 3; printf("%d\n", x); return 0; }
        """.trimIndent()
        assertEquals("3\n", stdoutOf(src))
    }

    @Test
    fun `goto is rejected`() {
        val r = run("""int main() { goto end; end: return 0; }""")
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!, r.errorMessage.contains("不支持"))
    }

    @Test
    fun `define is rejected`() {
        val r = run("""#define N 3
int main() { return 0; }""")
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!, r.errorMessage.contains("不支持"))
    }

    @Test
    fun `function pointer is rejected`() {
        val r = run("""int main() { int (*f)(int) = 0; return 0; }""")
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!, r.errorMessage.contains("不支持"))
        assertTrue(r.errorMessage, r.errorMessage.contains("函数指针"))
    }

    @Test
    fun `double pointer is rejected`() {
        val r = run("""int main() { int x = 1; int *p = &x; int **pp = &p; return 0; }""")
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!, r.errorMessage.contains("不支持"))
        assertTrue(r.errorMessage, r.errorMessage.contains("二级指针"))
    }

    @Test
    fun `union and enum are rejected`() {
        assertTrue(failureOf("""int main() { union U { int a; }; return 0; }""").errorMessage!!.contains("不支持"))
        assertTrue(failureOf("""int main() { enum E { A, B }; return 0; }""").errorMessage!!.contains("不支持"))
    }

    @Test
    fun `scanf is rejected`() {
        val r = run("""int main() { int x; scanf("%d", &x); return 0; }""")
        assertFalse(r.ok)
        assertTrue(r.errorMessage!!, r.errorMessage.contains("不支持"))
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

    @Test
    fun `check supports pointer and struct solutions`() {
        val src = """
            int sum_arr(int *a, int n) {
              int s = 0;
              for (int i = 0; i < n; i++) s += a[i];
              return s;
            }
            struct Point { int x; int y; };
            struct Point make(int x, int y) { struct Point p; p.x = x; p.y = y; return p; }
        """.trimIndent()
        val tests = listOf(
            """int main() { int a[3] = {1,2,3}; assert(sum_arr(a, 3) == 6, "应按引用求和"); return 0; }""",
            """int main() { struct Point p = make(2, 5); assert(p.x + p.y == 7, "结构体返回值应可读"); return 0; }"""
        )
        val r = CInterpreter.check(src, tests)
        assertTrue(r.errorMessage ?: "", r.ok)
    }

    @Test
    fun `check rejects starter that does nothing`() {
        val starter = """int sum_arr(int *a, int n) { return 0; }"""
        val tests = listOf("""int main() { int a[3] = {1,2,3}; assert(sum_arr(a, 3) == 6, "应为 6"); return 0; }""")
        assertFalse(CInterpreter.check(starter, tests).ok)
    }

    // ===== 作用域与全局变量 =====

    @Test
    fun `global variables persist across functions`() {
        val src = """
            int counter = 0;
            void bump() { counter++; }
            int main() {
              bump(); bump();
              printf("%d\n", counter);
              return 0;
            }
        """.trimIndent()
        assertEquals("2\n", stdoutOf(src))
    }

    @Test
    fun `local variable shadows global`() {
        val src = """
            int x = 9;
            int main() {
              int x = 1;
              { int x = 2; printf("%d", x); }
              printf("%d", x);
              return 0;
            }
        """.trimIndent()
        assertEquals("21", stdoutOf(src))
    }

    @Test
    fun `functions cannot see caller locals`() {
        val r = failureOf("""
            int peek() { return hidden; }
            int main() { int hidden = 1; return peek(); }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("未声明"))
    }

    // ===== 数组与函数配合 =====

    @Test
    fun `array decays to pointer when passed to function`() {
        val src = """
            void fill(int *a, int n, int v) {
              for (int i = 0; i < n; i++) a[i] = v;
            }
            int main() {
              int a[4];
              fill(a, 4, 7);
              printf("%d %d\n", a[0], a[3]);
              return 0;
            }
        """.trimIndent()
        assertEquals("7 7\n", stdoutOf(src))
    }

    @Test
    fun `two dimensional array as function parameter`() {
        val src = """
            int rowSum(int m[][3], int row) {
              int s = 0;
              for (int j = 0; j < 3; j++) s += m[row][j];
              return s;
            }
            int main() {
              int m[2][3] = {{1, 2, 3}, {4, 5, 6}};
              printf("%d %d\n", rowSum(m, 0), rowSum(m, 1));
              return 0;
            }
        """.trimIndent()
        assertEquals("6 15\n", stdoutOf(src))
    }

    @Test
    fun `string literal passes through char pointer parameter`() {
        val src = """
            int len(char *s) { return strlen(s); }
            int main() {
              char *t = "hello";
              printf("%d %d\n", len("abc"), len(t));
              return 0;
            }
        """.trimIndent()
        assertEquals("3 5\n", stdoutOf(src))
    }

    @Test
    fun `char array overflow on string init is an error`() {
        val r = failureOf("""int main() {
 char s[3] = "abc";
 return 0; }""")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("超出"))
    }

    @Test
    fun `struct array initializer and pointer traversal`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point ps[2] = {{1, 2}, {3, 4}};
              struct Point *q = ps;
              printf("%d %d %d\n", q->x, (q + 1)->y, ps[1].x);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 4 3\n", stdoutOf(src))
    }

    @Test
    fun `sizeof struct pointer`() {
        assertEquals(
            "8\n",
            stdoutOf("""int main() { struct Point { int x; }; struct Point p; printf("%d\n", sizeof(&p)); return 0; }""")
        )
    }

    // ===== 指针细节 =====

    @Test
    fun `pointer increment in for step`() {
        val src = """
            int main() {
              char *s = "abc";
              int n = 0;
              for (char *p = s; *p != 0; p++) n++;
              printf("%d\n", n);
              return 0;
            }
        """.trimIndent()
        assertEquals("3\n", stdoutOf(src))
    }

    @Test
    fun `dereference of post increment reads old target`() {
        val src = """
            int main() {
              int a[3] = {5, 6, 7};
              int *p = a;
              int first = *p++;
              printf("%d %d\n", first, *p);
              return 0;
            }
        """.trimIndent()
        assertEquals("5 6\n", stdoutOf(src))
    }

    @Test
    fun `struct pointer parameter mutates caller struct`() {
        val src = """
            struct Point { int x; int y; };
            void shift(struct Point *p, int d) { p->x += d; p->y += d; }
            int main() {
              struct Point p = {1, 2};
              shift(&p, 10);
              printf("%d %d\n", p.x, p.y);
              return 0;
            }
        """.trimIndent()
        assertEquals("11 12\n", stdoutOf(src))
    }

    @Test
    fun `array parameter with empty brackets`() {
        val src = """
            int first(int a[]) { return a[0]; }
            int main() { int a[2] = {9, 8}; printf("%d\n", first(a)); return 0; }
        """.trimIndent()
        assertEquals("9\n", stdoutOf(src))
    }

    @Test
    fun `break outside loop is a syntax error not internal error`() {
        val r = failureOf("int main() { break; return 0; }")
        assertEquals("语法错误", r.errorType)
    }

    @Test
    fun `check tolerates struct declared in both solution and test`() {
        val src = """
            struct Point { int x; int y; };
            int sum(struct Point p) { return p.x + p.y; }
        """.trimIndent()
        val tests = listOf("""
            struct Point { int x; int y; };
            int main() { struct Point p = {2, 3}; assert(sum(p) == 5, "结构体参数应按值传入"); return 0; }
        """.trimIndent())
        val r = CInterpreter.check(src, tests)
        assertTrue(r.errorMessage ?: "", r.ok)
    }

    // ===== 声明细节 =====

    @Test
    fun `function prototype allows call before definition`() {
        val src = """
            int add(int, int);
            int main() { printf("%d\n", add(2, 3)); return 0; }
            int add(int a, int b) { return a + b; }
        """.trimIndent()
        assertEquals("5\n", stdoutOf(src))
    }

    @Test
    fun `global array and struct initialization`() {
        val src = """
            struct Point { int x; int y; };
            int g[3] = {1, 2, 3};
            struct Point gp = {4, 5};
            int main() {
              printf("%d %d %d\n", g[0], g[2], gp.y);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 3 5\n", stdoutOf(src))
    }

    @Test
    fun `two dimensional flat initializer and trailing comma`() {
        val src = """
            int main() {
              int m[2][3] = {1, 2, 3, 4, 5, 6,};
              printf("%d %d %d\n", m[0][2], m[1][0], m[1][2]);
              return 0;
            }
        """.trimIndent()
        assertEquals("3 4 6\n", stdoutOf(src))
    }

    @Test
    fun `sizeof type with array suffix`() {
        assertEquals(
            "12\n",
            stdoutOf("""int main() { printf("%d\n", sizeof(int[3])); return 0; }""")
        )
    }

    @Test
    fun `modifying string literal is an error`() {
        val r = failureOf("""
            int main() {
              char *s = "abc";
              s[0] = 'x';
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("字面量"))
    }

    @Test
    fun `comparing string literals with equality operator is rejected`() {
        val r = failureOf("""int main() { if ("a" == "a") printf("same"); return 0; }""")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("strcmp"))
    }

    @Test
    fun `self referencing struct pointer member`() {
        val src = """
            struct Node { int v; struct Node *next; };
            int main() {
              struct Node a;
              struct Node b;
              a.v = 1; b.v = 2;
              a.next = &b;
              printf("%d %d\n", a.v, a.next->v);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 2\n", stdoutOf(src))
    }

    @Test
    fun `char pointer parameter string functions`() {
        val src = """
            int countDigits(char *s) {
              int n = 0;
              for (int i = 0; s[i] != 0; i++) if (isdigit(s[i])) n++;
              return n;
            }
            int main() { printf("%d\n", countDigits("a1b2c3")); return 0; }
        """.trimIndent()
        assertEquals("3\n", stdoutOf(src))
    }

    @Test
    fun `sizeof array length idiom`() {
        val src = """
            int main() {
              int a[7];
              printf("%d\n", sizeof(a) / sizeof(a[0]));
              return 0;
            }
        """.trimIndent()
        assertEquals("7\n", stdoutOf(src))
    }

    @Test
    fun `sizeof struct with mixed members rounds to eight`() {
        val src = """
            struct Mixed { char c; int i; };
            int main() { printf("%d\n", sizeof(struct Mixed)); return 0; }
        """.trimIndent()
        assertEquals("8\n", stdoutOf(src))
    }

    @Test
    fun `char array is mutable while literal pointer is not`() {
        val src = """
            int main() {
              char s[] = "abc";
              s[0] = 'x';
              printf("%s\n", s);
              return 0;
            }
        """.trimIndent()
        assertEquals("xbc\n", stdoutOf(src))
    }

    @Test
    fun `pointer comparison walks array`() {
        val src = """
            int main() {
              int a[3] = {1, 2, 3};
              int *p = a;
              int *end = a + 3;
              int n = 0;
              while (p < end) { n += *p; p++; }
              printf("%d\n", n);
              return 0;
            }
        """.trimIndent()
        assertEquals("6\n", stdoutOf(src))
    }

    @Test
    fun `pointer compound assignment moves address`() {
        val src = """
            int main() {
              int a[4] = {1, 2, 3, 4};
              int *p = a;
              p += 2;
              printf("%d\n", *p);
              p -= 1;
              printf("%d\n", *p);
              return 0;
            }
        """.trimIndent()
        assertEquals("3\n2\n", stdoutOf(src))
    }

    @Test
    fun `pointer arithmetic with non pointer operator is an error`() {
        val r = failureOf("""
            int main() {
              int a[2];
              int *p = a;
              printf("%d", p * 2);
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("指针"))
    }

    @Test
    fun `struct arithmetic is an error`() {
        val r = failureOf("""
            struct P { int x; };
            int main() {
              struct P a = {1};
              struct P b = {2};
              printf("%d", a + b);
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("结构体"))
    }

    @Test
    fun `memset with sizeof clears whole int array`() {
        val src = """
            int main() {
              int a[5];
              memset(a, 0, sizeof(a));
              printf("%d %d\n", a[0], a[4]);
              return 0;
            }
        """.trimIndent()
        assertEquals("0 0\n", stdoutOf(src))
    }

    @Test
    fun `printf width and zero padding`() {
        val src = """
            int main() {
              printf("[%3d][%-3d][%04d][%2s]\n", 7, 7, 42, "x");
              return 0;
            }
        """.trimIndent()
        assertEquals("[  7][7  ][0042][ x]\n", stdoutOf(src))
    }

    @Test
    fun `unsigned and short behave as int`() {
        val src = """
            int main() {
              unsigned int u = 10;
              short s = -3;
              printf("%d %d\n", u / 3, s * 2);
              return 0;
            }
        """.trimIndent()
        assertEquals("3 -6\n", stdoutOf(src))
    }

    @Test
    fun `switch on expression falls through into default`() {
        val src = """
            int main() {
              int x = 1;
              switch (x + 1) {
                case 2: printf("two");
                default: printf("!");
              }
              return 0;
            }
        """.trimIndent()
        assertEquals("two!", stdoutOf(src))
    }

    @Test
    fun `octal and hex literals`() {
        val src = """
            int main() {
              printf("%d %d %d\n", 077, 0x1F, 0);
              return 0;
            }
        """.trimIndent()
        assertEquals("63 31 0\n", stdoutOf(src))
    }

    @Test
    fun `designated initializer is rejected with guidance`() {
        val r = failureOf("""
            struct P { int x; int y; };
            int main() { struct P p = {.y = 2}; return 0; }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("不支持"))
    }

    @Test
    fun `bitwise on double is an error`() {
        val r = failureOf("""int main() { double d = 1.5; printf("%d", d & 1); return 0; }""")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("整数"))
    }

    @Test
    fun `no else dangling case in switch`() {
        val src = """
            int main() {
              int x = 3;
              switch (x) {
                case 1: printf("a");
                case 3: printf("c");
              }
              printf("\n");
              return 0;
            }
        """.trimIndent()
        assertEquals("c\n", stdoutOf(src))
    }

    @Test
    fun `struct array element assignment copies struct`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point ps[2];
              struct Point p = {7, 8};
              ps[0] = p;
              ps[0].x = 9;
              printf("%d %d %d\n", p.x, ps[0].x, ps[0].y);
              return 0;
            }
        """.trimIndent()
        assertEquals("7 9 8\n", stdoutOf(src))
    }

    @Test
    fun `struct with array member`() {
        val src = """
            struct Bucket { int items[3]; int n; };
            int main() {
              struct Bucket b;
              b.items[0] = 4;
              b.items[2] = 6;
              b.n = 2;
              printf("%d %d %d\n", b.items[0], b.items[2], b.n);
              return 0;
            }
        """.trimIndent()
        assertEquals("4 6 2\n", stdoutOf(src))
    }

    @Test
    fun `function returning pointer`() {
        val src = """
            int *pick(int *a, int i) { return &a[i]; }
            int main() {
              int a[3] = {10, 20, 30};
              *pick(a, 1) = 99;
              printf("%d\n", a[1]);
              return 0;
            }
        """.trimIndent()
        assertEquals("99\n", stdoutOf(src))
    }

    @Test
    fun `null pointer passed to function`() {
        val src = """
            int isNull(int *p) { return p == NULL; }
            int main() {
              int x = 1;
              printf("%d %d\n", isNull(NULL), isNull(&x));
              return 0;
            }
        """.trimIndent()
        assertEquals("1 0\n", stdoutOf(src))
    }

    @Test
    fun `switch on negative and zero cases`() {
        val src = """
            int main() {
              for (int i = -1; i <= 0; i++) {
                switch (i) {
                  case -1: printf("neg"); break;
                  case 0: printf("zero"); break;
                }
              }
              printf("\n");
              return 0;
            }
        """.trimIndent()
        assertEquals("negzero\n", stdoutOf(src))
    }

    @Test
    fun `array of struct pointers`() {
        val src = """
            struct Point { int x; };
            int main() {
              struct Point a = {1};
              struct Point b = {2};
              struct Point *ps[2];
              ps[0] = &a;
              ps[1] = &b;
              printf("%d %d\n", ps[0]->x, ps[1]->x);
              return 0;
            }
        """.trimIndent()
        assertEquals("1 2\n", stdoutOf(src))
    }

    @Test
    fun `char pointer array parameter is rejected as double pointer`() {
        val r = failureOf("""
            int main(int argc, char *argv[]) { return 0; }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("二级指针"))
    }

    @Test
    fun `assigning through struct pointer copies the whole struct`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point a = {1, 2};
              struct Point b = {3, 4};
              struct Point *q = &a;
              *q = b;
              printf("%d %d\n", a.x, a.y);
              return 0;
            }
        """.trimIndent()
        assertEquals("3 4\n", stdoutOf(src))
    }

    @Test
    fun `sizeof dereferenced pointer gives pointee size`() {
        val src = """
            int main() {
              int x = 1;
              int *p = &x;
              printf("%d %d\n", sizeof(*p), sizeof(p));
              return 0;
            }
        """.trimIndent()
        assertEquals("4 8\n", stdoutOf(src))
    }

    @Test
    fun `strcmp compares array against literal`() {
        val src = """
            int main() {
              char a[4] = "abc";
              printf("%d\n", strcmp(a, "abc"));
              return 0;
            }
        """.trimIndent()
        assertEquals("0\n", stdoutOf(src))
    }

    @Test
    fun `unsupported message includes line number`() {
        val r = failureOf("int main() {\n\n goto done;\n done: return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("第 3 行"))
        assertTrue(r.errorMessage, r.errorMessage.contains("不支持"))
    }

    @Test
    fun `shift left overflow wraps like 32 bit int`() {
        val src = """
            int main() {
              int x = 1 << 31;
              unsigned u = 0xFFFFFFFF;
              printf("%d %u %x\n", x, u, 255);
              return 0;
            }
        """.trimIndent()
        assertEquals("-2147483648 4294967295 ff\n", stdoutOf(src))
    }

    @Test
    fun `bitwise complement of zero is minus one`() {
        assertEquals("1 -1\n", stdoutOf("""
            int main() {
              printf("%d %d\n", ~0 + 2, ~0);
              return 0;
            }
        """.trimIndent()))
    }

    @Test
    fun `int overflow wraps at 32 bits`() {
        val src = """
            int main() {
              int big = 2147483647;
              big = big + 1;
              printf("%d\n", big);
              return 0;
            }
        """.trimIndent()
        assertEquals("-2147483648\n", stdoutOf(src))
    }

    @Test
    fun `factorial of 13 overflows like c int`() {
        val src = """
            int fact(int n) { return n <= 1 ? 1 : n * fact(n - 1); }
            int main() { printf("%d\n", fact(13)); return 0; }
        """.trimIndent()
        assertEquals("1932053504\n", stdoutOf(src))
    }

    @Test
    fun `char arithmetic promotes to int`() {
        val src = """
            int main() {
              char c = 'A';
              printf("%d %c\n", c + 1, c + 1);
              return 0;
            }
        """.trimIndent()
        assertEquals("66 B\n", stdoutOf(src))
    }

    @Test
    fun `pointer out of bounds dereference reports line`() {
        val r = failureOf("""
            int main() {
              int a[2] = {1, 2};
              int *p = a;
              int x = *(p + 5);
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("指针"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 4 行"))
    }

    @Test
    fun `pointer index out of bounds reports line`() {
        val r = failureOf("""
            int main() {
              int a[2] = {1, 2};
              int *p = a;
              p[3] = 9;
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("越界"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 4 行"))
    }

    @Test
    fun `course style integration program`() {
        val src = """
            typedef struct { char name[8]; int score; } Student;

            int best(Student *list, int n) {
              int idx = 0;
              for (int i = 1; i < n; i++) if (list[i].score > list[idx].score) idx = i;
              return idx;
            }

            int main() {
              Student list[3];
              strcpy(list[0].name, "ann"); list[0].score = 80;
              strcpy(list[1].name, "bob"); list[1].score = 95;
              strcpy(list[2].name, "cid"); list[2].score = 70;
              int i = best(list, 3);
              switch (i) {
                case 0: printf("ann"); break;
                case 1: printf("bob"); break;
                default: printf("cid");
              }
              printf(" %d \n", list[i].score);
              return 0;
            }
        """.trimIndent()
        assertEquals("bob 95 \n", stdoutOf(src))
    }

    @Test
    fun `memset out of bounds is an error`() {
        val r = failureOf("""
            int main() {
              char buf[4];
              memset(buf, 0, 10);
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("越界"))
        assertTrue(r.errorMessage, r.errorMessage.contains("第 3 行"))
    }

    @Test
    fun `sizeof array of structs`() {
        val src = """
            struct Point { int x; int y; };
            int main() {
              struct Point ps[3];
              printf("%d\n", sizeof(ps));
              return 0;
            }
        """.trimIndent()
        assertEquals("24\n", stdoutOf(src))
    }

    @Test
    fun `assigning string to int is an error`() {
        val r = failureOf("""
            int main() {
              int x = "abc";
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("int"))
    }

    @Test
    fun `oversized array is rejected instead of ooming`() {
        val r = failureOf("int main() { int a[1000000]; return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("过大"))
    }

    @Test
    fun `zero length array is rejected`() {
        val r = failureOf("int main() { int a[0]; return 0; }")
        assertTrue(r.errorMessage!!, r.errorMessage.contains("正数"))
    }

    @Test
    fun `void function called as expression yields zero`() {
        val src = """
            void noop() { }
            int main() {
              int x = noop();
              printf("%d\n", x);
              return 0;
            }
        """.trimIndent()
        assertEquals("0\n", stdoutOf(src))
    }

    @Test
    fun `incomplete struct declared but never defined is an error`() {
        val r = failureOf("""
            struct Node;
            int main() {
              struct Node n;
              return 0;
            }
        """.trimIndent())
        assertTrue(r.errorMessage!!, r.errorMessage.contains("不完整"))
    }

    @Test
    fun `float literals keep double precision`() {
        val src = """
            int main() {
              double a = 1.0 / 3.0;
              printf("%.4f\n", a);
              return 0;
            }
        """.trimIndent()
        assertEquals("0.3333\n", stdoutOf(src))
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

    // ===== REPL 会话语义（LanguageRuntime 契约要求） =====

    @Test
    fun `session keeps variables across pushes`() {
        val s = CInterpreter.Session()
        s.push("int x = 5;")
        val (more, out) = s.push("printf(\"%d\\n\", x + 3);")
        assertFalse(more)
        assertEquals("8\n", out)
    }

    @Test
    fun `session keeps function definitions`() {
        val s = CInterpreter.Session()
        s.push("int twice(int n) { return n * 2; }")
        val (_, out) = s.push("printf(\"%d\\n\", twice(21));")
        assertEquals("42\n", out)
    }

    @Test
    fun `session does not require main`() {
        val s = CInterpreter.Session()
        val (_, out) = s.push("printf(\"hi\");")
        assertEquals("hi", out)
    }

    @Test
    fun `session requests continuation on open brace`() {
        val s = CInterpreter.Session()
        val (more, _) = s.push("int f() {")
        assertTrue("未闭合花括号应请求续行", more)
    }

    @Test
    fun `session reports variables`() {
        val s = CInterpreter.Session()
        s.push("int a = 1;")
        s.push("double b = 2.5;")
        val vars = s.variables().associate { it.first to it.second }
        assertEquals("int", vars["a"])
        assertEquals("double", vars["b"])
    }

    @Test
    fun `session reset clears state`() {
        val s = CInterpreter.Session()
        s.push("int x = 1;")
        s.reset()
        val (_, out) = s.push("printf(\"%d\", x);")
        assertTrue("重置后 x 应不存在：$out", out.contains("未声明"))
    }

    @Test
    fun `session keeps typedef and struct definitions`() {
        val s = CInterpreter.Session()
        s.push("typedef struct { int x; int y; } Point;")
        s.push("Point p = {3, 4};")
        val (_, out) = s.push("printf(\"%d\", p.x + p.y);")
        assertEquals("7", out)
    }
}
