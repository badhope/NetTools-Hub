package com.pyneon.academy.ts

/**
 * TypeScript → JavaScript 转译器（**教学子集**，不是完整实现）。
 *
 * 定位与边界
 * ----------
 * 本项目要在 Android 上离线提供 TypeScript，但没有可用的完整 tsc：
 * 官方编译器是数 MB 的现代 JS 包，Rhino（ES5）跑不动它。因此这里实现一个
 * 只做「类型擦除」的轻量转译器——TypeScript 的类型系统本来就在运行时不存在，
 * 擦掉类型标注后的语义与 JS 完全一致，这正是 TS 的设计前提。
 *
 * 支持的子集（课程内容严格限制在此范围内）：
 *   - 变量 / 参数 / 返回值的类型标注：`let x: number = 1`
 *   - 函数与箭头函数的参数、返回值标注
 *   - interface / type 别名（整段删除，仅作声明）
 *   - 泛型参数列表：`function id<T>(x: T): T`
 *   - 类型断言：`x as number`、`<number>x` 不处理（避免与比较运算符歧义）
 *   - 非空断言：`x!`
 *   - 访问修饰符：`public/private/protected/readonly`
 *   - enum（转成冻结对象）
 *
 * **不支持**（课程里不得出现，遇到会原样保留并交由 JS 报错）：
 *   - 装饰器、命名空间、声明合并、抽象类
 *   - 泛型约束 `extends`、条件类型、映射类型
 *   - `<T>x` 尖括号断言（与 `<` 比较歧义，故意不做）
 *
 * 设计原则：宁可少转、不可错转。所有擦除都基于字符扫描并跳过字符串 /
 * 模板字符串 / 注释，避免把字符串内容误当类型标注。
 */
object TypeScriptTranspiler {

    /** 转译结果。`applied` 便于测试断言「确实做了擦除」而非原样返回。 */
    data class Result(val code: String, val changed: Boolean)

    fun transpile(source: String): Result {
        var s = source

        s = stripInterfaces(s)
        s = stripTypeAliases(s)
        s = stripDeclare(s)
        s = convertEnums(s)
        s = stripAccessModifiers(s)
        s = stripGenericParams(s)
        s = stripTypeAnnotations(s)
        s = stripAsCasts(s)
        s = stripNonNullAssertions(s)

        return Result(s, s != source)
    }

    // ===== 各阶段实现 =====

    /**
     * 删除 `interface Name { ... }` / `interface Name extends X { ... }` 整块。
     * 用花括号配平扫描，跳字符串与注释。
     */
    private fun stripInterfaces(src: String): String {
        val out = StringBuilder()
        var i = 0
        while (i < src.length) {
            val at = indexOfKeyword(src, "interface", i)
            if (at < 0) {
                out.append(src, i, src.length)
                break
            }
            out.append(src, i, at)
            // 跳过 interface 头部直到 '{'
            var j = at + "interface".length
            while (j < src.length && src[j] != '{') j++
            if (j >= src.length) {
                out.append(src, at, src.length)
                break
            }
            // 配平花括号
            var depth = 0
            var k = j
            while (k < src.length) {
                val ch = src[k]
                if (ch == '{') depth++
                if (ch == '}') {
                    depth--
                    if (depth == 0) break
                }
                k++
            }
            val end = if (k < src.length) k + 1 else src.length
            // 吃掉行尾多余空白/换行，保持行号大致稳定
            var e = end
            while (e < src.length && (src[e] == ' ' || src[e] == '\t')) e++
            if (e < src.length && src[e] == '\r') e++
            if (e < src.length && src[e] == '\n') e++
            out.append("\n")
            i = e
        }
        return out.toString()
    }

    /** 删除 `type Name = ...;` 单行别名声明。 */
    private fun stripTypeAliases(src: String): String {
        val lines = src.split("\n").toMutableList()
        val out = mutableListOf<String>()
        var i = 0
        while (i < lines.size) {
            val trimmed = lines[i].trimStart()
            if (trimmed.startsWith("type ") && trimmed.contains("=") &&
                Regex("""^type\s+\w+(<[^>]*>)?\s*=""").containsMatchIn(trimmed)
            ) {
                // 花括号类型字面量可能跨行，配平后整体丢弃
                var depth = lines[i].count { it == '{' } - lines[i].count { it == '}' }
                var j = i
                while (depth > 0 && j + 1 < lines.size) {
                    j++
                    depth += lines[j].count { it == '{' } - lines[j].count { it == '}' }
                }
                out.add("")
                i = j + 1
                continue
            }
            out.add(lines[i])
            i++
        }
        return out.joinToString("\n")
    }

    private fun stripDeclare(src: String): String =
        src.split("\n").map { if (it.trimStart().startsWith("declare ")) "" else it }
            .joinToString("\n")

    /**
     * `enum Color { Red, Green = 5 }` → `var Color = Object.freeze({ Red: 0, Green: 5 })`
     * 只支持数值/无初始化成员，够教学用。
     */
    private fun convertEnums(src: String): String {
        val regex = Regex("""enum\s+(\w+)\s*\{([^}]*)}""")
        return regex.replace(src) { m ->
            val name = m.groupValues[1]
            val body = m.groupValues[2]
            var next = 0
            val entries = body.split(",").mapNotNull { raw ->
                val item = raw.trim()
                if (item.isEmpty()) return@mapNotNull null
                val eq = item.indexOf('=')
                if (eq >= 0) {
                    val key = item.substring(0, eq).trim()
                    val value = item.substring(eq + 1).trim()
                    next = value.toIntOrNull()?.plus(1) ?: next
                    "$key: $value"
                } else {
                    val key = item
                    "${key}: ${next}"
                    next++
                    "$key: ${next - 1}"
                }
            }
            "var $name = Object.freeze({ ${entries.joinToString(", ")} })"
        }
    }

    /** 去掉构造参数上的 `public` / `private` / `protected` / `readonly`。 */
    private fun stripAccessModifiers(src: String): String =
        Regex("""\b(public|private|protected|readonly)\s+""").replace(src, "")

    /** 去掉函数/类名后的泛型参数表：`function id<T>(` → `function id(`。 */
    private fun stripGenericParams(src: String): String {
        val fn = Regex("""(function\s+\w+)\s*<[^<>()]*>\s*\(""")
        val cls = Regex("""(class\s+\w+)\s*<[^<>()]*>\s*(\{|extends)""")
        var s = fn.replace(src) { "${it.groupValues[1]}(" }
        s = cls.replace(s) { "${it.groupValues[1]} ${it.groupValues[2]}" }
        return s
    }

    /** 去掉 `x as Type`（含链式）。 */
    private fun stripAsCasts(src: String): String =
        Regex("""\s+as\s+[A-Za-z_$][\w$]*(<[^<>]*>)?(\[\])?""").replace(src, "")

    /** 去掉表达式后的非空断言 `foo!.bar` / `foo!`。 */
    private fun stripNonNullAssertions(src: String): String =
        Regex("""([\w$\])])!(?=[.\[]|;|,|\)|\s|$)""").replace(src, "$1")

    /**
     * 核心：擦除类型标注。
     *
     * 用字符扫描而不是正则，因为必须正确跳过：
     *   - 字符串 `'a: b'`、`"x: y"`、模板字符串
     *   - 注释（行注释与块注释）
     *   - 对象字面量的键值对 `{ name: 'V' }`（这里的 `:` 不是类型标注）
     *   - 三元表达式 `cond ? a : b`
     *
     * 判定规则：`:` 之后进入「类型上下文」，一直吃到以下任一终止符（括号深度为 0 时）：
     *   `=`、`;`、`,`、`)`、`{`、`}`、换行、`=>`
     * 且类型文本必须匹配「类型形状」（标识符、尖括号、方括号、点、竖线、&、空格、字面量），
     * 否则判定为对象键或三元表达式，保留原样。
     */
    private fun stripTypeAnnotations(src: String): String {
        val out = StringBuilder()
        var i = 0
        var braceDepth = 0        // 0 = 顶层，>0 = 对象/代码块内
        var parenDepth = 0
        var lastSignificant = ' '  // 上一个非空白字符

        while (i < src.length) {
            val ch = src[i]

            // --- 字符串 / 模板字符串：原样拷贝 ---
            if (ch == '\'' || ch == '"' || ch == '`') {
                val quote = ch
                out.append(ch)
                i++
                while (i < src.length) {
                    val c = src[i]
                    out.append(c)
                    if (c == '\\' && i + 1 < src.length) {
                        out.append(src[i + 1]); i += 2; continue
                    }
                    i++
                    if (c == quote) break
                }
                lastSignificant = quote
                continue
            }

            // --- 单行注释：原样拷贝到行尾 ---
            if (ch == '/' && i + 1 < src.length && src[i + 1] == '/') {
                while (i < src.length && src[i] != '\n') { out.append(src[i]); i++ }
                continue
            }

            // --- 块注释：整体拷贝 ---
            if (ch == '/' && i + 1 < src.length && src[i + 1] == '*') {
                out.append("/*"); i += 2
                while (i + 1 < src.length && !(src[i] == '*' && src[i + 1] == '/')) {
                    out.append(src[i]); i++
                }
                if (i + 1 < src.length) { out.append("*/"); i += 2 }
                continue
            }

            when (ch) {
                '{' -> { braceDepth++; out.append(ch); i++; lastSignificant = ch; continue }
                '}' -> { if (braceDepth > 0) braceDepth--; out.append(ch); i++; lastSignificant = ch; continue }
                '(' -> { parenDepth++; out.append(ch); i++; lastSignificant = ch; continue }
                ')' -> { if (parenDepth > 0) parenDepth--; out.append(ch); i++; lastSignificant = ch; continue }
            }

            // --- 冒号：判断是否为类型标注 ---
            if (ch == ':') {
                // 三元的 `? ... : ...` 不处理
                if (looksLikeTernaryColon(out)) {
                    out.append(ch); i++; lastSignificant = ch; continue
                }
                // 对象字面量键值对：`{ key: value }` —— 键是标识符且前面紧邻 '{' 或 ','
                if (isObjectKeyColon(out, braceDepth, parenDepth)) {
                    out.append(ch); i++; lastSignificant = ch; continue
                }
                // 形如 `: Type` 且后面紧跟类型形状 → 擦除
                val (typeText, endIdx) = readTypeText(src, i + 1)
                if (typeText.isNotEmpty() && looksLikeType(typeText, lastSignificant)) {
                    // 擦除策略：连「冒号前的空白」一起收掉，再按**下一个字符**决定是否补空格。
                    //   `(x: T)`        → `(x)`      下一个是 ')' ，不补
                    //   `f(a: T, b: T)` → `f(a, b)`  下一个是 ',' 或 ')' ，不补
                    //   `n: T = 5`      → `n = 5`    下一个是 '=' ，补一个空格
                    //   `a:T`           → `a`（与后续标识符相邻时才补，防止粘成一个词）
                    while (out.isNotEmpty() && out.last() == ' ') out.setLength(out.length - 1)
                    val nextCh = if (endIdx < src.length) src[endIdx] else null
                    val wouldMerge = nextCh != null &&
                        (nextCh.isLetterOrDigit() || nextCh == '_' || nextCh == '$')
                    val needsSpace = wouldMerge || nextCh == '='
                    if (needsSpace && out.isNotEmpty()) out.append(' ')
                    i = endIdx
                    lastSignificant = ' '
                    continue
                }
                out.append(ch); i++; lastSignificant = ch
                continue
            }

            out.append(ch)
            if (!ch.isWhitespace()) lastSignificant = ch
            i++
        }
        // 清理「擦除后留下的多余空格」：`) :` → `)` 之类已由上面处理；
        // 再收掉行尾空格与空行
        return out.toString().lines().joinToString("\n") { it.trimEnd() }
    }

    /** 读到类型结束位置；返回 (类型文本, 结束下标)。 */
    private fun readTypeText(src: String, start: Int): Pair<String, Int> {
        var i = start
        // 跳过冒号后的前导空白（`a: T` 里 `: ` 的空格不应算进类型文本的结束位置之外的残留）
        while (i < src.length && (src[i] == ' ' || src[i] == '\t')) i++
        var depth = 0
        val sb = StringBuilder()
        while (i < src.length) {
            val c = src[i]
            when (c) {
                '<', '[', '(' -> { depth++; sb.append(c); i++; continue }
                '>', ']', ')' -> {
                    if (depth == 0) break   // `)` 是参数表结束，类型到此为止
                    depth--; sb.append(c); i++; continue
                }
                '=', ';', ',', '{', '}', '\n', '\r' -> if (depth == 0) break
                ':' -> if (depth == 0) break
            }
            // `=>` 终止（函数类型已完整）
            if (c == '=' && i + 1 < src.length && src[i + 1] == '>') break
            sb.append(c)
            i++
        }
        return sb.toString().trim() to i
    }

    /** 类型文本的形状校验：只允许类型语法字符，防止把表达式误吞。 */
    private fun looksLikeType(text: String, lastSignificant: Char): Boolean {
        if (text.isEmpty() || text.length > 120) return false
        // 必须像类型：标识符/尖括号/方括号/点/竖线/与/空格/字面量
        if (!Regex("""^[A-Za-z_$][\w$<>\[\].|&\s,]*$""").matches(text)) return false
        // 常见值关键字（true/false/this/new/typeof/in/instanceof）说明这是表达式不是类型
        val head = text.trim().substringBefore('<').substringBefore('[').trim()
        if (head in VALUE_KEYWORDS) return false
        // `{` 开头的是对象/代码块，不是类型标注起点（此时 lastSignificant 会是 '{' 或 ','）
        if (lastSignificant == '{' || lastSignificant == ',') {
            // `function f(a, b: T)` 里 b 前是 ','，仍需擦除；用「前一个 token 是标识符」再判
            return true
        }
        return true
    }

    /** 判断 `:` 是不是三元运算符的冒号（同一表达式内前面出现过未配对的 `?`）。 */
    private fun looksLikeTernaryColon(out: StringBuilder): Boolean {
        var depthParen = 0
        var i = out.length - 1
        while (i >= 0) {
            when (out[i]) {
                ')' -> depthParen++
                '(' -> depthParen--
                '?' -> if (depthParen == 0) return true
                ';', '{', '}', '\n' -> if (depthParen == 0) return false
            }
            i--
        }
        return false
    }

    /** 判断 `:` 是不是对象字面量的键分隔符（`{ a: 1 }` 或 `, a: 1`）。 */
    private fun isObjectKeyColon(out: StringBuilder, braceDepth: Int, parenDepth: Int): Boolean {
        // 参数里的类型标注形如 `function f(a: T)` —— 前面是 '(' 或 ','
        if (parenDepth > 0) return false
        if (braceDepth <= 0) return false
        // 回看：跳过空白，取前一个 token
        var i = out.length - 1
        while (i >= 0 && out[i].isWhitespace()) i--
        val end = i
        while (i >= 0 && (out[i].isLetterOrDigit() || out[i] == '_' || out[i] == '$' || out[i] == '"' || out[i] == '\'')) i--
        if (end == i) return false
        var j = i
        while (j >= 0 && out[j].isWhitespace()) j--
        // `{ a: 1` 或 `, a: 1` → 是对象键
        return j >= 0 && (out[j] == '{' || out[j] == ',')
    }

    /** 在 src 中查找独立关键字（前后不能是标识符字符）。 */
    private fun indexOfKeyword(src: String, keyword: String, from: Int): Int {
        var idx = src.indexOf(keyword, from)
        while (idx >= 0) {
            val beforeOk = idx == 0 || !(src[idx - 1].isLetterOrDigit() || src[idx - 1] == '_' || src[idx - 1] == '$')
            val after = idx + keyword.length
            val afterOk = after >= src.length || !(src[after].isLetterOrDigit() || src[after] == '_' || src[after] == '$')
            if (beforeOk && afterOk) return idx
            idx = src.indexOf(keyword, idx + 1)
        }
        return -1
    }

    private val VALUE_KEYWORDS = setOf(
        "true", "false", "this", "new", "typeof", "in", "instanceof", "void", "delete", "yield", "await"
    )
}
