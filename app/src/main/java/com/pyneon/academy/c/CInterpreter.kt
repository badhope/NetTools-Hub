package com.pyneon.academy.c

/**
 * C 语言教学子集解释器（纯 Kotlin，无 NDK、无外部工具链）。
 *
 * 为什么是解释器而不是编译器
 * --------------------------
 * Android 上离线运行 C 需要 clang + 系统头文件 + 链接器，体积 200–400 MB，
 * 且无法链接 Android 的 bionic libc——对学习场景不成立。因此这里实现一个
 * **直接解释执行 C 源码**的子集解释器：语义与 gcc 一致的部分照做，不支持
 * 的部分明确报错（不是静默错误答案）。
 *
 * 支持的子集（课程内容严格限定在此范围）
 * ------------------------------------
 *   类型      int / double / char / void，一维数组
 *   语句      声明、赋值、if/else、while、for、break、continue、return、复合语句
 *   表达式    算术 + - * / %、比较、逻辑 && || !、自增自减、三元 ?:、函数调用、下标
 *   函数      定义、调用、递归、参数按值传递
 *   输入输出  printf（%d %i %f %.Nf %c %s %%）、puts、putchar、scanf（从 stdin 队列）
 *   内置      assert(cond[, msg])，仅用于判题
 *
 * 明确不支持（遇到即报错，绝不静默错答）
 * ------------------------------------
 *   指针与取地址运算、结构体、联合、位运算、宏与预处理、多文件头文件、
 *   switch/goto、可变参数函数、函数指针、二维数组
 *
 * 设计取舍：整数一律用 Long 承载（避免 Int 溢出与 C 的 int 宽度歧义），
 * char 用 Long 存储其码点；double 用 Kotlin Double。运算时按「有 double 则浮点，
 * 否则整型」提升，与 C 的常规算术转换一致。
 */
object CInterpreter {

    // ===== 值模型 =====

    private sealed class Value {
        data class Num(val v: Long) : Value()
        data class Real(val v: Double) : Value()
        data class Str(val v: String) : Value()
        data class Arr(val items: MutableList<Value>) : Value()
        object Void : Value()

        fun asDouble(): Double = when (this) {
            is Num -> v.toDouble()
            is Real -> v
            is Str -> v.toDoubleOrNull() ?: 0.0
            else -> 0.0
        }

        fun asLong(): Long = when (this) {
            is Num -> v
            is Real -> v.toLong()
            is Str -> v.toLongOrNull() ?: 0L
            else -> 0L
        }

        fun truthy(): Boolean = when (this) {
            is Num -> v != 0L
            is Real -> v != 0.0
            is Str -> v.isNotEmpty()
            else -> false
        }

        fun display(): String = when (this) {
            is Num -> v.toString()
            is Real -> formatDouble(v)
            is Str -> v
            is Arr -> items.joinToString(" ") { it.display() }
            Void -> ""
        }
    }

    /** 与 C 的 %g 接近的默认浮点显示：整数值不带小数点，否则最多 6 位有效小数。 */
    private fun formatDouble(d: Double): String {
        if (d.isNaN()) return "nan"
        if (d.isInfinite()) return if (d > 0) "inf" else "-inf"
        if (d == d.toLong().toDouble() && kotlin.math.abs(d) < 1e15) return d.toLong().toString()
        val s = String.format("%.6f", d).trimEnd('0').trimEnd('.')
        return s
    }

    // ===== 词法 =====

    private enum class T { NUM, REAL, STR, CHARLIT, IDENT, KEYWORD, OP, PUNCT, EOF }

    private data class Token(val type: T, val text: String, val line: Int)

    private class Lexer(private val src: String) {
        private var i = 0
        private var line = 1

        fun tokenize(): List<Token> {
            val out = mutableListOf<Token>()
            while (i < src.length) {
                val c = src[i]
                when {
                    c == '\n' -> { line++; i++ }
                    c.isWhitespace() -> i++
                    c == '/' && i + 1 < src.length && src[i + 1] == '/' -> {
                        while (i < src.length && src[i] != '\n') i++
                    }
                    c == '/' && i + 1 < src.length && src[i + 1] == '*' -> {
                        i += 2
                        while (i + 1 < src.length && !(src[i] == '*' && src[i + 1] == '/')) {
                            if (src[i] == '\n') line++
                            i++
                        }
                        i += 2
                    }
                    c == '"' -> out.add(readString())
                    c == '\'' -> out.add(readChar())
                    c.isDigit() || (c == '.' && i + 1 < src.length && src[i + 1].isDigit()) ->
                        out.add(readNumber())
                    c.isLetter() || c == '_' -> out.add(readIdent())
                    else -> out.add(readOp())
                }
            }
            out.add(Token(T.EOF, "", line))
            return out
        }

        private fun readString(): Token {
            val startLine = line
            i++ // skip "
            val sb = StringBuilder()
            while (i < src.length && src[i] != '"') {
                if (src[i] == '\\' && i + 1 < src.length) {
                    sb.append(unescape(src[i + 1])); i += 2
                } else {
                    if (src[i] == '\n') line++
                    sb.append(src[i]); i++
                }
            }
            i++ // skip closing "
            return Token(T.STR, sb.toString(), startLine)
        }

        private fun readChar(): Token {
            val startLine = line
            i++
            val ch: Char = if (src[i] == '\\' && i + 1 < src.length) {
                val c = unescape(src[i + 1]); i += 2; c
            } else {
                val c = src[i]; i++; c
            }
            if (i < src.length && src[i] == '\'') i++
            return Token(T.CHARLIT, ch.code.toString(), startLine)
        }

        private fun unescape(c: Char): Char = when (c) {
            'n' -> '\n'; 't' -> '\t'; 'r' -> '\r'; '0' -> '\u0000'
            '\\' -> '\\'; '"' -> '"'; '\'' -> '\''
            else -> c
        }

        private fun readNumber(): Token {
            val start = i
            var isReal = false
            while (i < src.length && (src[i].isDigit() || src[i] == '.')) {
                if (src[i] == '.') isReal = true
                i++
            }
            // 科学计数法
            if (i < src.length && (src[i] == 'e' || src[i] == 'E')) {
                isReal = true; i++
                if (i < src.length && (src[i] == '+' || src[i] == '-')) i++
                while (i < src.length && src[i].isDigit()) i++
            }
            // 整型后缀
            while (i < src.length && (src[i] == 'l' || src[i] == 'L' || src[i] == 'u' || src[i] == 'U')) i++
            val text = src.substring(start, i).filter { !it.isLetter() }
            return Token(if (isReal) T.REAL else T.NUM, text.ifEmpty { "0" }, line)
        }

        private fun readIdent(): Token {
            val start = i
            while (i < src.length && (src[i].isLetterOrDigit() || src[i] == '_')) i++
            val text = src.substring(start, i)
            return Token(if (text in KEYWORDS) T.KEYWORD else T.IDENT, text, line)
        }

        private fun readOp(): Token {
            val two = if (i + 1 < src.length) src.substring(i, i + 2) else ""
            if (two in TWO_CHAR_OPS) { i += 2; return Token(T.OP, two, line) }
            val c = src[i]; i++
            return if (c in PUNCT_CHARS) Token(T.PUNCT, c.toString(), line)
            else Token(T.OP, c.toString(), line)
        }
    }

    // ===== 语法树 =====

    private sealed class Expr {
        data class NumLit(val v: Long) : Expr()
        data class RealLit(val v: Double) : Expr()
        data class StrLit(val v: String) : Expr()
        data class Var(val name: String, val line: Int) : Expr()
        data class Bin(val op: String, val l: Expr, val r: Expr) : Expr()
        data class Un(val op: String, val e: Expr) : Expr()
        data class Assign(val target: Expr, val value: Expr) : Expr()
        data class Call(val name: String, val args: List<Expr>, val line: Int) : Expr()
        data class Index(val arr: Expr, val idx: Expr) : Expr()
        data class Ternary(val cond: Expr, val a: Expr, val b: Expr) : Expr()
        data class PreInc(val op: String, val target: Expr) : Expr()
        data class PostInc(val op: String, val target: Expr) : Expr()
    }

    private sealed class Stmt {
        data class Block(val body: List<Stmt>) : Stmt()
        data class Decl(val type: String, val decls: List<DeclItem>) : Stmt()
        data class If(val cond: Expr, val then: Stmt, val otherwise: Stmt?) : Stmt()
        data class While(val cond: Expr, val body: Stmt) : Stmt()
        data class For(val init: Stmt?, val cond: Expr?, val step: Expr?, val body: Stmt) : Stmt()
        data class Return(val value: Expr?) : Stmt()
        object Break : Stmt()
        object Continue : Stmt()
        data class ExprStmt(val e: Expr) : Stmt()
        object Empty : Stmt()
    }

    private data class DeclItem(val name: String, val arraySize: Int?, val init: Expr?)

    private data class FuncDef(
        val name: String,
        val returnType: String,
        val params: List<Pair<String, String>>,
        val body: Stmt.Block
    )

    // ===== 解析器 =====

    private class Parser(private val tokens: List<Token>) {
        private var p = 0
        private val funcs = linkedMapOf<String, FuncDef>()

        fun parseProgram(): Map<String, FuncDef> {
            while (!atEnd()) {
                if (checkKeyword("int") || checkKeyword("double") || checkKeyword("char") ||
                    checkKeyword("void") || checkKeyword("long") || checkKeyword("float")
                ) {
                    parseFunction()
                } else {
                    throw CError("语法错误", "顶层只允许函数定义（第 ${peek().line} 行）")
                }
            }
            return funcs
        }

        private fun isTypeToken(): Boolean =
            checkKeyword("int") || checkKeyword("double") || checkKeyword("char") ||
                checkKeyword("void") || checkKeyword("long") || checkKeyword("float")

        private fun parseFunction() {
            val ret = advance().text
            val nameTok = expect(T.IDENT, "函数名")
            expectPunct("(")
            val params = mutableListOf<Pair<String, String>>()
            if (!checkPunct(")")) {
                do {
                    val ty = advance().text
                    val pn = expect(T.IDENT, "参数名").text
                    // 参数数组形式（int a[]）按指针处理——不支持，明确报错
                    if (checkPunct("[")) throw CError("不支持", "不支持数组参数（第 ${peek().line} 行）")
                    params.add(pn to ty)
                } while (matchPunct(","))
            }
            expectPunct(")")
            val body = parseBlock()
            if (funcs.containsKey(nameTok.text)) {
                // C 不允许同一翻译单元内重定义函数。这里报错而不是静默覆盖：
                // 否则「用户写了空 main + 测试也带 main」会让测试的 main 顶替用户代码，
                // 造成判题假通过（2026-11 实测漏洞）。
                throw CError("语法错误", "函数 '${nameTok.text}' 重复定义（第 ${nameTok.line} 行）")
            }
            funcs[nameTok.text] = FuncDef(nameTok.text, ret, params, body)
        }

        private fun parseBlock(): Stmt.Block {
            expectPunct("{")
            val body = mutableListOf<Stmt>()
            while (!checkPunct("}") && !atEnd()) body.add(parseStmt())
            expectPunct("}")
            return Stmt.Block(body)
        }

        private fun parseStmt(): Stmt {
            if (checkPunct("{")) return parseBlock()
            if (checkPunct(";")) { advance(); return Stmt.Empty }
            if (checkKeyword("if")) {
                advance(); expectPunct("(")
                val cond = parseExpr(); expectPunct(")")
                val then = parseStmt()
                var other: Stmt? = null
                if (checkKeyword("else")) { advance(); other = parseStmt() }
                return Stmt.If(cond, then, other)
            }
            if (checkKeyword("while")) {
                advance(); expectPunct("(")
                val cond = parseExpr(); expectPunct(")")
                return Stmt.While(cond, parseStmt())
            }
            if (checkKeyword("for")) {
                advance(); expectPunct("(")
                val init: Stmt? = when {
                    checkPunct(";") -> { advance(); null }
                    isTypeToken() -> parseDecl()
                    else -> { val e = parseExpr(); expectPunct(";"); Stmt.ExprStmt(e) }
                }
                val cond: Expr? = if (checkPunct(";")) null else parseExpr()
                expectPunct(";")
                val step: Expr? = if (checkPunct(")")) null else parseExpr()
                expectPunct(")")
                return Stmt.For(init, cond, step, parseStmt())
            }
            if (checkKeyword("return")) {
                advance()
                val v = if (checkPunct(";")) null else parseExpr()
                expectPunct(";")
                return Stmt.Return(v)
            }
            if (checkKeyword("break")) { advance(); expectPunct(";"); return Stmt.Break }
            if (checkKeyword("continue")) { advance(); expectPunct(";"); return Stmt.Continue }
            if (isTypeToken()) return parseDecl()
            val e = parseExpr()
            expectPunct(";")
            return Stmt.ExprStmt(e)
        }

        private fun parseDecl(): Stmt {
            val type = advance().text
            val items = mutableListOf<DeclItem>()
            do {
                val name = expect(T.IDENT, "变量名").text
                var size: Int? = null
                if (matchPunct("[")) {
                    size = expect(T.NUM, "数组长度").text.toIntOrNull() ?: 0
                    expectPunct("]")
                }
                var init: Expr? = null
                if (matchOp("=")) init = parseExpr()
                items.add(DeclItem(name, size, init))
            } while (matchPunct(","))
            expectPunct(";")
            return Stmt.Decl(type, items)
        }

        // ---- 表达式（优先级自上而下） ----

        fun parseExpr(): Expr = parseAssignment()

        private fun parseAssignment(): Expr {
            val left = parseTernary()
            if (checkOp("=")) {
                advance()
                val right = parseAssignment()
                return Expr.Assign(left, right)
            }
            return left
        }

        private fun parseTernary(): Expr {
            val cond = parseOr()
            if (checkOp("?")) {
                advance()
                val a = parseExpr()
                expectOp(":")
                val b = parseTernary()
                return Expr.Ternary(cond, a, b)
            }
            return cond
        }

        private fun parseOr(): Expr {
            var e = parseAnd()
            while (checkOp("||")) { advance(); e = Expr.Bin("||", e, parseAnd()) }
            return e
        }

        private fun parseAnd(): Expr {
            var e = parseEquality()
            while (checkOp("&&")) { advance(); e = Expr.Bin("&&", e, parseEquality()) }
            return e
        }

        private fun parseEquality(): Expr {
            var e = parseRelational()
            while (checkOp("==") || checkOp("!=")) {
                val op = advance().text
                e = Expr.Bin(op, e, parseRelational())
            }
            return e
        }

        private fun parseRelational(): Expr {
            var e = parseAdditive()
            while (checkOp("<") || checkOp(">") || checkOp("<=") || checkOp(">=")) {
                val op = advance().text
                e = Expr.Bin(op, e, parseAdditive())
            }
            return e
        }

        private fun parseAdditive(): Expr {
            var e = parseMultiplicative()
            while (checkOp("+") || checkOp("-")) {
                val op = advance().text
                e = Expr.Bin(op, e, parseMultiplicative())
            }
            return e
        }

        private fun parseMultiplicative(): Expr {
            var e = parseUnary()
            while (checkOp("*") || checkOp("/") || checkOp("%")) {
                val op = advance().text
                e = Expr.Bin(op, e, parseUnary())
            }
            return e
        }

        private fun parseUnary(): Expr {
            if (checkOp("-")) { advance(); return Expr.Un("-", parseUnary()) }
            if (checkOp("+")) { advance(); return Expr.Un("+", parseUnary()) }
            if (checkOp("!")) { advance(); return Expr.Un("!", parseUnary()) }
            if (checkOp("++")) { advance(); return Expr.PreInc("++", parseUnary()) }
            if (checkOp("--")) { advance(); return Expr.PreInc("--", parseUnary()) }
            return parsePostfix()
        }

        private fun parsePostfix(): Expr {
            var e = parsePrimary()
            while (true) {
                when {
                    checkPunct("[") -> {
                        advance()
                        val idx = parseExpr()
                        expectPunct("]")
                        e = Expr.Index(e, idx)
                    }
                    checkOp("++") -> { advance(); e = Expr.PostInc("++", e) }
                    checkOp("--") -> { advance(); e = Expr.PostInc("--", e) }
                    else -> return e
                }
            }
        }

        private fun parsePrimary(): Expr {
            val t = peek()
            return when (t.type) {
                T.NUM -> { advance(); Expr.NumLit(t.text.toLongOrNull() ?: 0L) }
                T.REAL -> { advance(); Expr.RealLit(t.text.toDoubleOrNull() ?: 0.0) }
                T.STR -> { advance(); Expr.StrLit(t.text) }
                T.CHARLIT -> { advance(); Expr.NumLit(t.text.toLongOrNull() ?: 0L) }
                T.IDENT -> {
                    advance()
                    if (checkPunct("(")) {
                        advance()
                        val args = mutableListOf<Expr>()
                        if (!checkPunct(")")) {
                            do { args.add(parseExpr()) } while (matchPunct(","))
                        }
                        expectPunct(")")
                        Expr.Call(t.text, args, t.line)
                    } else {
                        Expr.Var(t.text, t.line)
                    }
                }
                T.PUNCT -> {
                    if (t.text == "(") {
                        advance(); val e = parseExpr(); expectPunct(")"); e
                    } else {
                        throw CError("语法错误", "意外的符号 '${t.text}'（第 ${t.line} 行）")
                    }
                }
                else -> throw CError("语法错误", "意外的标记 '${t.text}'（第 ${t.line} 行）")
            }
        }

        // ---- 辅助 ----

        private fun peek() = tokens[p]
        private fun atEnd() = peek().type == T.EOF
        private fun advance(): Token = tokens[p].also { if (!atEnd()) p++ }

        private fun checkKeyword(k: String) = peek().type == T.KEYWORD && peek().text == k
        private fun checkPunct(s: String) = peek().type == T.PUNCT && peek().text == s
        private fun checkOp(s: String) = peek().type == T.OP && peek().text == s
        private fun matchPunct(s: String): Boolean { if (checkPunct(s)) { advance(); return true }; return false }
        private fun matchOp(s: String): Boolean { if (checkOp(s)) { advance(); return true }; return false }

        private fun expectPunct(s: String) {
            if (!checkPunct(s)) throw CError("语法错误", "期望 '$s'，实际 '${peek().text}'（第 ${peek().line} 行）")
            advance()
        }

        private fun expectOp(s: String) {
            if (!checkOp(s)) throw CError("语法错误", "期望 '$s'，实际 '${peek().text}'（第 ${peek().line} 行）")
            advance()
        }

        private fun expect(t: T, what: String): Token {
            if (peek().type != t) throw CError("语法错误", "期望$what，实际 '${peek().text}'（第 ${peek().line} 行）")
            return advance()
        }
    }

    // ===== 运行时 =====

    class CError(val type: String, message: String) : RuntimeException(message)

    private class BreakSignal : RuntimeException()
    private class ContinueSignal : RuntimeException()
    private class ReturnSignal(val value: Value) : RuntimeException()

    private class Scope(val parent: Scope?) {
        val vars = linkedMapOf<String, Value>()
        fun lookup(name: String): Value? = vars[name] ?: parent?.lookup(name)
        fun find(name: String): Scope? = if (vars.containsKey(name)) this else parent?.find(name)
    }

    private class Interpreter(
        private val funcs: Map<String, FuncDef>,
        private val out: StringBuilder,
        private val stdin: ArrayDeque<String>
    ) {
        private var scopes = mutableListOf(Scope(null))
        private var steps = 0
        private val maxSteps = 2_000_000

        fun callEntry(entry: String): Value {
            val fn = funcs[entry] ?: throw CError("运行时错误", "缺少 $entry 函数")
            return invoke(fn, emptyList())
        }

        /**
         * 判题入口：先跑用户代码的 main（产出真实输出），再跑测试入口。
         *
         * 两步必须共用一个输出缓冲区，这样测试里的 assertOutput 才能看到
         * 用户 main 打印了什么。若用户没有 main，则只跑测试（允许练习
         * 只实现函数、由测试自己调用的情况）。
         */
        fun callMainThenTest(testEntry: String) {
            funcs["main"]?.let { invoke(it, emptyList()) }
            val test = funcs[testEntry] ?: throw CError("运行时错误", "缺少测试入口 $testEntry")
            invoke(test, emptyList())
        }

        private fun tick() {
            if (++steps > maxSteps) throw CError("Timeout", "执行步数超过上限（疑似死循环）")
        }

        private fun invoke(fn: FuncDef, args: List<Value>): Value {
            if (args.size != fn.params.size) {
                throw CError("运行时错误", "函数 ${fn.name} 期望 ${fn.params.size} 个参数，实际 ${args.size} 个")
            }
            val scope = Scope(scopes.first())
            fn.params.forEachIndexed { i, (name, ty) ->
                scope.vars[name] = coerce(args[i], ty)
            }
            val saved = scopes
            scopes = mutableListOf(scope)
            return try {
                execBlock(fn.body)
                Value.Void
            } catch (r: ReturnSignal) {
                r.value
            } finally {
                scopes = saved
            }
        }

        private fun coerce(v: Value, ty: String): Value = when (ty) {
            "double", "float" -> if (v is Value.Real) v else Value.Real(v.asDouble())
            "char" -> Value.Num(v.asLong())
            else -> if (v is Value.Real) v else Value.Num(v.asLong())
        }

        private fun execBlock(b: Stmt.Block) {
            val saved = scopes
            scopes = mutableListOf(Scope(saved.first()))
            try {
                for (s in b.body) exec(s)
            } finally {
                scopes = saved
            }
        }

        private fun exec(s: Stmt) {
            tick()
            when (s) {
                is Stmt.Block -> execBlock(s)
                is Stmt.Empty -> Unit
                is Stmt.Decl -> for (d in s.decls) {
                    val v: Value = when {
                        d.arraySize != null -> {
                            val size = d.arraySize
                            if (size < 0) throw CError("运行时错误", "数组长度为负")
                            Value.Arr(MutableList(size) { Value.Num(0) })
                        }
                        d.init != null -> coerce(eval(d.init), s.type)
                        s.type in setOf("double", "float") -> Value.Real(0.0)
                        else -> Value.Num(0)
                    }
                    scopes.first().vars[d.name] = v
                }
                is Stmt.If -> if (eval(s.cond).truthy()) exec(s.then) else s.otherwise?.let { exec(it) }
                is Stmt.While -> {
                    var guard = 0
                    while (eval(s.cond).truthy()) {
                        tick()
                        if (++guard > maxSteps) throw CError("Timeout", "循环次数超过上限（疑似死循环）")
                        try { exec(s.body) }
                        catch (_: BreakSignal) { break }
                        catch (_: ContinueSignal) { continue }
                    }
                }
                is Stmt.For -> {
                    val saved = scopes
                    scopes = mutableListOf(Scope(saved.first()))
                    try {
                        s.init?.let { exec(it) }
                        var guard = 0
                        while (s.cond == null || eval(s.cond).truthy()) {
                            tick()
                            if (++guard > maxSteps) throw CError("Timeout", "循环次数超过上限（疑似死循环）")
                            try { exec(s.body) }
                            catch (_: BreakSignal) { break }
                            catch (_: ContinueSignal) { /* 继续执行 step */ }
                            s.step?.let { eval(it) }
                        }
                    } finally {
                        scopes = saved
                    }
                }
                is Stmt.Return -> throw ReturnSignal(s.value?.let { eval(it) } ?: Value.Void)
                Stmt.Break -> throw BreakSignal()
                Stmt.Continue -> throw ContinueSignal()
                is Stmt.ExprStmt -> eval(s.e)
            }
        }

        private fun eval(e: Expr): Value {
            tick()
            return when (e) {
                is Expr.NumLit -> Value.Num(e.v)
                is Expr.RealLit -> Value.Real(e.v)
                is Expr.StrLit -> Value.Str(e.v)
                is Expr.Var -> scopes.first().lookup(e.name)
                    ?: throw CError("运行时错误", "未声明的变量 '${e.name}'（第 ${e.line} 行）")
                is Expr.Bin -> binop(e)
                is Expr.Un -> unop(e)
                is Expr.Assign -> assign(e)
                is Expr.Call -> callBuiltinOrUser(e)
                is Expr.Index -> {
                    val arr = eval(e.arr)
                    if (arr !is Value.Arr) throw CError("运行时错误", "对非数组使用下标")
                    val idx = eval(e.idx).asLong().toInt()
                    if (idx < 0 || idx >= arr.items.size) {
                        throw CError("运行时错误", "数组下标越界：$idx（长度 ${arr.items.size}）")
                    }
                    arr.items[idx]
                }
                is Expr.Ternary -> if (eval(e.cond).truthy()) eval(e.a) else eval(e.b)
                is Expr.PreInc -> {
                    val delta = if (e.op == "++") 1L else -1L
                    val cur = readTarget(e.target)
                    val nv = Value.Num(cur.asLong() + delta)
                    writeTarget(e.target, nv)
                    nv
                }
                is Expr.PostInc -> {
                    val delta = if (e.op == "++") 1L else -1L
                    val cur = readTarget(e.target)
                    writeTarget(e.target, Value.Num(cur.asLong() + delta))
                    cur
                }
            }
        }

        private fun readTarget(t: Expr): Value = when (t) {
            is Expr.Var -> scopes.first().lookup(t.name)
                ?: throw CError("运行时错误", "未声明的变量 '${t.name}'")
            else -> eval(t)
        }

        private fun writeTarget(t: Expr, v: Value) {
            when (t) {
                is Expr.Var -> {
                    val scope = scopes.first().find(t.name)
                        ?: throw CError("运行时错误", "未声明的变量 '${t.name}'")
                    scope.vars[t.name] = v
                }
                is Expr.Index -> {
                    val arr = eval(t.arr)
                    if (arr !is Value.Arr) throw CError("运行时错误", "对非数组写入")
                    val idx = eval(t.idx).asLong().toInt()
                    if (idx < 0 || idx >= arr.items.size) {
                        throw CError("运行时错误", "数组下标越界：$idx（长度 ${arr.items.size}）")
                    }
                    arr.items[idx] = v
                }
                else -> throw CError("运行时错误", "赋值目标不是变量")
            }
        }

        private fun assign(e: Expr.Assign): Value {
            val v = eval(e.value)
            writeTarget(e.target, v)
            return v
        }

        private fun binop(e: Expr.Bin): Value {
            // 短路
            if (e.op == "&&") {
                if (!eval(e.l).truthy()) return Value.Num(0)
                return Value.Num(if (eval(e.r).truthy()) 1 else 0)
            }
            if (e.op == "||") {
                if (eval(e.l).truthy()) return Value.Num(1)
                return Value.Num(if (eval(e.r).truthy()) 1 else 0)
            }
            val l = eval(e.l)
            var r = eval(e.r)
            // 字符串拼接：任一侧是字符串且运算符为 +
            if (e.op == "+" && (l is Value.Str || r is Value.Str)) {
                return Value.Str(l.display() + r.display())
            }
            val bothInt = l is Value.Num && r is Value.Num
            if (bothInt) {
                val a = l.asLong(); val b = r.asLong()
                return when (e.op) {
                    "+" -> Value.Num(a + b)
                    "-" -> Value.Num(a - b)
                    "*" -> Value.Num(a * b)
                    "/" -> if (b == 0L) throw CError("运行时错误", "整数除以零") else Value.Num(a / b)
                    "%" -> if (b == 0L) throw CError("运行时错误", "整数取模零") else Value.Num(a % b)
                    "==" -> Value.Num(if (a == b) 1 else 0)
                    "!=" -> Value.Num(if (a != b) 1 else 0)
                    "<" -> Value.Num(if (a < b) 1 else 0)
                    ">" -> Value.Num(if (a > b) 1 else 0)
                    "<=" -> Value.Num(if (a <= b) 1 else 0)
                    ">=" -> Value.Num(if (a >= b) 1 else 0)
                    else -> throw CError("运行时错误", "不支持的运算符 ${e.op}")
                }
            }
            val a = l.asDouble(); val b = r.asDouble()
            return when (e.op) {
                "+" -> Value.Real(a + b)
                "-" -> Value.Real(a - b)
                "*" -> Value.Real(a * b)
                "/" -> Value.Real(a / b)
                "%" -> Value.Real(a % b)
                "==" -> Value.Num(if (a == b) 1 else 0)
                "!=" -> Value.Num(if (a != b) 1 else 0)
                "<" -> Value.Num(if (a < b) 1 else 0)
                ">" -> Value.Num(if (a > b) 1 else 0)
                "<=" -> Value.Num(if (a <= b) 1 else 0)
                ">=" -> Value.Num(if (a >= b) 1 else 0)
                else -> throw CError("运行时错误", "不支持的运算符 ${e.op}")
            }
        }

        private fun unop(e: Expr.Un): Value = when (e.op) {
            "-" -> when (val v = eval(e.e)) {
                is Value.Real -> Value.Real(-v.v)
                else -> Value.Num(-v.asLong())
            }
            "+" -> eval(e.e)
            "!" -> Value.Num(if (eval(e.e).truthy()) 0 else 1)
            else -> throw CError("运行时错误", "不支持的运算符 ${e.op}")
        }

        private fun callBuiltinOrUser(e: Expr.Call): Value {
            when (e.name) {
                "printf" -> {
                    val fmt = eval(e.args[0])
                    val args = e.args.drop(1).map { eval(it) }
                    out.append(formatPrintf(fmt.display(), args))
                    return Value.Num(0)
                }
                "puts" -> {
                    val s = e.args.firstOrNull()?.let { eval(it).display() } ?: ""
                    out.append(s).append('\n')
                    return Value.Num(0)
                }
                "putchar" -> {
                    val c = eval(e.args[0]).asLong().toInt().toChar()
                    out.append(c)
                    return Value.Num(0)
                }
                "scanf" -> {
                    val fmt = eval(e.args[0]).display()
                    // 只支持 "%d" / "%lf" / "%s" 三种，且必须配合 &变量 —— 不支持取址，
                    // 因此这里明确拒绝，避免用户以为能读入
                    throw CError(
                        "不支持",
                        "本课程暂不支持 scanf（需要指针取址）。请把输入直接写在代码里，或使用 input 相关示例"
                    )
                }
                "assert" -> {
                    val cond = eval(e.args[0]).truthy()
                    if (!cond) {
                        val msg = e.args.getOrNull(1)?.let { eval(it).display() } ?: "断言未通过"
                        throw CError("TestFailed", msg)
                    }
                    return Value.Num(0)
                }
                // 输出断言：判题时用来检查用户代码真实打印了什么。
                // 没有它，测试只能自己 printf，于是「用户什么都没写」也能通过
                // （2026-11 实测漏洞）。
                "assertOutput" -> {
                    if (e.args.size < 2) {
                        throw CError("运行时错误", "assertOutput(期望输出, 提示) 需要两个参数")
                    }
                    val expected = eval(e.args[0]).display()
                    val actual = out.toString()
                    if (!actual.contains(expected)) {
                        val msg = eval(e.args[1]).display()
                        throw CError(
                            "TestFailed",
                            "$msg（期望输出包含「$expected」，实际为「${actual.take(80)}」）"
                        )
                    }
                    return Value.Num(0)
                }
                "abs" -> return Value.Num(kotlin.math.abs(eval(e.args[0]).asLong()))
                "sqrt" -> return Value.Real(kotlin.math.sqrt(eval(e.args[0]).asDouble()))
                "pow" -> return Value.Real(
                    Math.pow(eval(e.args[0]).asDouble(), eval(e.args[1]).asDouble())
                )
            }
            val fn = funcs[e.name] ?: throw CError(
                "运行时错误", "未定义的函数 '${e.name}'（第 ${e.line} 行）"
            )
            val args = e.args.map { eval(it) }
            return invoke(fn, args)
        }

        /** printf 格式串：支持 %d %i %ld %f %.Nf %c %s %% %x */
        private fun formatPrintf(fmt: String, args: List<Value>): String {
            val sb = StringBuilder()
            var ai = 0
            var i = 0
            while (i < fmt.length) {
                val c = fmt[i]
                if (c != '%') { sb.append(c); i++; continue }
                if (i + 1 < fmt.length && fmt[i + 1] == '%') { sb.append('%'); i += 2; continue }
                // 解析 %[flags][width][.precision][length]spec
                var j = i + 1
                val spec = StringBuilder()
                while (j < fmt.length && (fmt[j].isDigit() || fmt[j] == '.' || fmt[j] == '-' ||
                        fmt[j] == '+' || fmt[j] == ' ' || fmt[j] == 'l' || fmt[j] == 'h')
                ) { spec.append(fmt[j]); j++ }
                if (j >= fmt.length) { sb.append('%'); i++; continue }
                val conv = fmt[j]
                val arg = args.getOrNull(ai++) ?: Value.Num(0)
                when (conv) {
                    'd', 'i' -> sb.append(arg.asLong())
                    'u' -> sb.append(arg.asLong().toULong())
                    'x' -> sb.append(arg.asLong().toString(16))
                    'X' -> sb.append(arg.asLong().toString(16).uppercase())
                    'f', 'F' -> {
                        val prec = Regex("""\.(\d+)""").find(spec.toString())
                            ?.groupValues?.get(1)?.toIntOrNull() ?: 6
                        sb.append(String.format("%.${prec}f", arg.asDouble()))
                    }
                    'g' -> sb.append(formatDouble(arg.asDouble()))
                    'c' -> sb.append(arg.asLong().toInt().toChar())
                    's' -> sb.append(arg.display())
                    else -> sb.append('%').append(spec).append(conv)
                }
                i = j + 1
            }
            return sb.toString()
        }
    }

    // ===== 对外接口 =====

    data class Result(
        val ok: Boolean,
        val stdout: String,
        val errorType: String?,
        val errorMessage: String?,
        val variables: List<Triple<String, String, String>>
    )

    /** 执行一段 C 源码（必须有 main）。 */
    fun run(
        source: String,
        stdinLines: List<String> = emptyList(),
        entry: String = "main",
        runMainFirst: Boolean = false
    ): Result {
        val out = StringBuilder()
        return try {
            // 先拦截明确不支持的语法，给出「不支持」而不是晦涩的语法错误
            rejectUnsupported(source)
            val tokens = Lexer(source).tokenize()
            val funcs = Parser(tokens).parseProgram()
            val interp = Interpreter(funcs, out, ArrayDeque(stdinLines))
            if (runMainFirst) interp.callMainThenTest(entry) else interp.callEntry(entry)
            Result(true, out.toString(), null, null, emptyList())
        } catch (e: CError) {
            Result(false, out.toString(), e.type, e.message, emptyList())
        } catch (e: StackOverflowError) {
            Result(false, out.toString(), "StackOverflow", "递归层数过深", emptyList())
        } catch (e: Throwable) {
            Result(false, out.toString(), "InternalError", "${e.javaClass.simpleName}: ${e.message}", emptyList())
        }
    }

    /**
     * 判题：先跑用户代码（必须有 main），再依次执行每条测试。
     *
     * 测试是独立的 C 片段，可以调用用户定义的函数——因此把用户代码与测试
     * **拼成同一个翻译单元**再解析，符合 C 的「函数先定义后使用」语义，
     * 也让测试能断言用户的函数。
     */
    fun check(source: String, tests: List<String>): Result {
        val failures = mutableListOf<String>()
        var lastOut = ""
        for ((index, test) in tests.withIndex()) {
            // 把测试里的 main 改名为 __test_main：用户代码通常自己也有 main，
            // 同名会在同一翻译单元里冲突。改名后两者共存，入口指向测试那个。
            // 只替换无参形式，避免误伤其他标识符。
            val renamed = test.replace(Regex("""\bmain\s*\(\s*\)"""), "__test_main()")
            val combined = "$source\n$renamed"
            // 先跑用户 main（真实输出），再跑测试入口；两者共用输出缓冲
            val r = run(combined, entry = "__test_main", runMainFirst = true)
            lastOut = r.stdout
            if (!r.ok) {
                failures.add("用例 ${index + 1}：${r.errorMessage}")
                if (r.errorType == "TestFailed") continue
                // 语法/运行时错误直接返回，后续用例没有意义
                break
            }
        }
        return if (failures.isEmpty()) {
            Result(true, lastOut, null, null, emptyList())
        } else {
            Result(
                false, lastOut, "TestFailed",
                "共 ${tests.size} 个用例，${failures.size} 个未通过；首个失败：${failures.first()}",
                emptyList()
            )
        }
    }

    /** 遇到不支持的语法直接抛 CError("不支持", …)，而不是让解析器报「意外标记」。 */
    private fun rejectUnsupported(source: String) {
        for ((pattern, label) in UNSUPPORTED_PATTERNS) {
            val hit = pattern.find(source) ?: continue
            val line = source.substring(0, hit.range.first).count { it == '\n' } + 1
            throw CError("不支持", "暂不支持 $label（第 $line 行）。本课程是 C 教学子集，不是完整 gcc。")
        }
    }

    private val KEYWORDS = setOf(
        "int", "double", "char", "void", "long", "float", "short", "unsigned", "signed",
        "if", "else", "while", "for", "return", "break", "continue", "do", "switch",
        "case", "default", "const", "static", "struct", "typedef", "sizeof", "goto"
    )

    private val PUNCT_CHARS = setOf('(', ')', '{', '}', '[', ']', ',', ';')

    private val TWO_CHAR_OPS = setOf(
        "==", "!=", "<=", ">=", "&&", "||", "++", "--", "+=", "-=", "*=", "/=", "%=", "->"
    )

    /**
     * 明确不支持的语法前置检查：在解析前拦下，给出「不支持」而不是晦涩的
     * 语法错误，让学习者知道这不是 bug 而是课程范围。
     */
    private val UNSUPPORTED_PATTERNS = listOf(
        Regex("""\bstruct\b""") to "struct（结构体）",
        Regex("""\btypedef\b""") to "typedef",
        Regex("""\bswitch\b""") to "switch 语句",
        Regex("""\bgoto\b""") to "goto 语句",
        Regex("""#\s*include""") to "预处理指令 #include（课程内置常用函数，无需引入头文件）",
        Regex("""#\s*define""") to "预处理宏 #define",
        Regex("""\bsizeof\b""") to "sizeof",
        Regex("""\bunsigned\b""") to "unsigned",
        Regex("""\bdo\s*\{""") to "do-while 循环"
    )
}
