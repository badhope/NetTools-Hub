package com.pyneon.academy.ui.components

import android.graphics.Typeface
import android.util.Log
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.SpanStyle
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.viewinterop.AndroidView
import io.github.rosemoe.sora.event.ContentChangeEvent
import io.github.rosemoe.sora.langs.textmate.TextMateColorScheme
import io.github.rosemoe.sora.langs.textmate.TextMateLanguage
import io.github.rosemoe.sora.langs.textmate.registry.model.DefaultGrammarDefinition
import io.github.rosemoe.sora.widget.CodeEditor as SoraCodeEditor
import io.github.rosemoe.sora.widget.schemes.EditorColorScheme
import kotlinx.coroutines.awaitCancellation
import org.eclipse.tm4e.core.registry.IGrammarSource

/**
 * F3 重构：练习编辑器由 sora-editor（开源，LGPL-2.1）提供。
 *
 * 替换自研 BasicTextField 的理由：
 *  - 旧实现只有“死代码”级正则高亮（annotatedText 算了从未使用），无自动缩进、
 *    无 Tab 键处理、无撤销栈、行号与内容滚动不同步；
 *  - sora-editor 内置增量语法高亮、自动缩进（`:` 换行缩进）、行号、撤销/重做、
 *    括号匹配，均为成熟实现，不再重复造轮子。
 *
 * 高亮方案：TextMate Python 语法（assets/syntaxes/python.tmLanguage，plist）
 *  + 自建 PyNeon 主题（tokenColors 映射到品牌四色）。
 */

/** 自建轻量 PyNeon 主题：把 TextMate scope 映射到品牌色板。 */
private val PYNEON_THEME_JSON: String =
    """
{
  "name": "PyNeon Dark",
  "type": "dark",
  "colors": {
    "editor.background": "#10141C",
    "editor.foreground": "#D8E2E8",
    "editor.lineHighlightBackground": "#1A2230",
    "editorLineNumber.foreground": "#3E4C5C",
    "editorLineNumber.activeForeground": "#00E5FF",
    "editorCursor.foreground": "#00E5FF",
    "editor.selectionBackground": "#1E4C5A",
    "editorIndentGuide.background": "#1A2230",
    "editorIndentGuide.activeBackground": "#00E5FF",
    "editorWhitespace.foreground": "#263244",
    "editor.findMatchBackground": "#4A3A00",
    "editorSuggestWidget.background": "#10141C",
    "editorSuggestWidget.foreground": "#D8E2E8",
    "editorSuggestWidget.selectedBackground": "#1A2230",
    "editorSuggestWidget.highlightForeground": "#F7FF00"
  },
  "tokenColors": [
    { "scope": "comment", "settings": { "foreground": "#5A6B78", "fontStyle": "italic" } },
    { "scope": "keyword", "settings": { "foreground": "#00E5FF", "fontStyle": "bold" } },
    { "scope": "keyword.operator", "settings": { "foreground": "#00E5FF" } },
    { "scope": "storage.type", "settings": { "foreground": "#00E5FF", "fontStyle": "bold" } },
    { "scope": "string", "settings": { "foreground": "#00FF9C" } },
    { "scope": "constant.numeric", "settings": { "foreground": "#F7FF00" } },
    { "scope": "constant.language", "settings": { "foreground": "#B45CFF", "fontStyle": "bold" } },
    { "scope": "entity.name.function", "settings": { "foreground": "#FF2D78" } },
    { "scope": "support.function.builtin", "settings": { "foreground": "#B45CFF" } },
    { "scope": "support.type.python", "settings": { "foreground": "#B45CFF" } },
    { "scope": "variable.language", "settings": { "foreground": "#B45CFF" } }
  ]
}
""".trimIndent()

private const val TAG = "PyNeonCodeEditor"

/**
 * 创建并配置一个 sora CodeEditor 实例（每个 Composable 实例只建一次）。
 * 语法：TextMate，按 [language] 加载 assets/syntaxes/<language>.tmLanguage.json
 * （python / javascript，plist XML；未内置语法的语言降级为纯文本）。
 * 主题：PyNeon Dark（scope → 品牌四色，token scope 与各语法文件保持对齐）。
 */
private fun createEditor(
    context: android.content.Context,
    language: String
): SoraCodeEditor {
    val editor = SoraCodeEditor(context)
    try {
        val grammarText = context.assets
            .open("syntaxes/$language.tmLanguage.json")
            .bufferedReader(Charsets.UTF_8)
            .use { it.readText() }
        // .tmLanguage 文件是 plist(XML) 格式，显式声明 ContentType.XML。
        // 必须把真实 scopeName 一起传进去：单参数的 withGrammarSource 会把
        // scopeName 默认成 "source.string"，与语法文件里的声明不符，
        // TextMateLanguage.create 会抛 IllegalStateException 并静默降级成
        // 默认（白底）编辑器 —— 曾因此在深色主题上出现刺眼的白底代码框。
        val scopeName = when (language) {
            "python" -> "source.python"
            "javascript" -> "source.js"
            "typescript" -> "source.ts"
            "c" -> "source.c"
            "lua" -> "source.lua"
            "sql" -> "source.sql"
            else -> "source.$language"
        }
        val grammarSource = IGrammarSource.fromString(IGrammarSource.ContentType.XML, grammarText)
        val grammar = DefaultGrammarDefinition.withGrammarSource(
            grammarSource, language, scopeName
        )
        val textMateLanguage = TextMateLanguage.create(grammar, true)
        editor.setEditorLanguage(textMateLanguage)

        val themeSource = org.eclipse.tm4e.core.registry.IThemeSource.fromString(
            org.eclipse.tm4e.core.registry.IThemeSource.ContentType.JSON,
            PYNEON_THEME_JSON
        )
        val scheme = TextMateColorScheme.create(themeSource)
        editor.setColorScheme(scheme)
    } catch (t: Throwable) {
        // 语法/主题加载失败时降级为纯文本编辑器（不崩溃、不影响输入）
        Log.w(TAG, "TextMate 语法加载失败，回退默认高亮: ${t.message}")
        editor.setColorScheme(EditorColorScheme())
    }

    editor.apply {
        setUndoEnabled(true)
        setWordwrap(false)
        setTabWidth(4)
        // 14sp（文本缩放跟随系统字体设置）
        setTextSizePx(14f * context.resources.displayMetrics.scaledDensity)
        setTypefaceText(Typeface.MONOSPACE)
        setTypefaceLineNumber(Typeface.MONOSPACE)
        setEditable(true)
        setPinLineNumber(true)
    }
    return editor
}

/**
 * 练习代码编辑器（sora-editor 封装）。
 *
 * 参数保持与旧实现兼容，调用方无需改动：
 *  - [hint]：旧实现的占位提示；sora 无内置 placeholder，调用处上方通常已有
 *    题目简介文本，故保留参数但不渲染。
 *  - [onEnter]：sora 编辑器无回车钩子，保留参数（默认 null，调用方未使用）。
 */
@Composable
fun CodeEditor(
    modifier: Modifier = Modifier,
    value: String,
    onValueChange: (String) -> Unit,
    onEnter: (() -> Unit)? = null,
    hint: String = "",
    readOnly: Boolean = false,
    showLineNumbers: Boolean = true,
    language: String = "python"
) {
    val context = LocalContext.current
    // 编辑器实例 + 语法/主题只创建一次；sora 支持增量高亮，不必随文本重建
    val editor = remember(context, language) { createEditor(context, language) }
    var listener by remember { mutableStateOf<((String) -> Unit)?>(null) }

    LaunchedEffect(editor) {
        val receipt = editor.subscribeEvent(ContentChangeEvent::class.java) { event, _ ->
            if (event.action != ContentChangeEvent.ACTION_SET_NEW_TEXT) {
                listener?.invoke(editor.text.toString())
            }
        }
        // 视图销毁时解除订阅，避免泄漏
        awaitCancellationSafe { receipt.unsubscribe() }
    }

    AndroidView(
        factory = { editor },
        modifier = modifier,
        update = { view ->
            // 外部值变化 → 同步进编辑器（内容一致时跳过，避免打断用户光标/撤销栈）
            val current = view.text.toString()
            if (current != value) {
                view.setText(value)
            }
            view.setEditable(!readOnly)
            listener = onValueChange
        }
    )
}

/** 等待协程取消时执行 [block]（订阅清理）。 */
private suspend fun awaitCancellationSafe(block: () -> Unit) {
    try {
        kotlinx.coroutines.awaitCancellation()
    } finally {
        block()
    }
}

// ===== 以下为只读示例代码块（PythonCodeField）继续使用的高亮工具，保持不动 =====

/**
 * 简易语法高亮（正则版），支持 python / javascript。
 * 仅供只读示例代码块 [PythonCodeField] 使用；可编辑编辑器已由 sora-editor 接管。
 * 注意：正则高亮无法覆盖三引号字符串、f-string、正则字面量等边界场景，
 * 只读展示场景下可接受。
 */
fun buildAnnotatedString(
    code: String,
    language: String,
    tokens: com.pyneon.academy.ui.theme.NeonTokens = com.pyneon.academy.ui.theme.DarkTokens
): AnnotatedString {
    val builder = AnnotatedString.Builder(code)
    if (language != "python" && language != "javascript" && language != "lua" && language != "sql") {
        return builder.toAnnotatedString()
    }

    val keywordStyle = SpanStyle(color = tokens.primary, fontWeight = FontWeight.Bold)
    val stringStyle = SpanStyle(color = tokens.success)
    val commentStyle = SpanStyle(color = tokens.textDim, fontStyle = FontStyle.Italic)
    val numberStyle = SpanStyle(color = tokens.secondary)
    val functionStyle = SpanStyle(color = tokens.primary, fontWeight = FontWeight.Normal)
    val builtinStyle = SpanStyle(color = tokens.purple)

    val (keywords, builtins, commentPrefix) = when (language) {
        "javascript" -> jsHighlightSets()
        "lua" -> luaHighlightSets()
        "sql" -> sqlHighlightSets()
        else -> pythonHighlightSets()
    }

    // Regex patterns
    val keywordPattern = "\\b(${keywords.joinToString("|")})\\b".toRegex()
    val stringPattern = """(["'])(?:(?=(\\?))\2.)*?\1""".toRegex()
    val commentPattern = "$commentPrefix.*".toRegex()
    val numberPattern = "\\b\\d+(\\.\\d+)?\\b".toRegex()
    val functionPattern = "\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s*(?=\\()".toRegex()
    val builtinPattern = "\\b(${builtins.joinToString("|")})\\b".toRegex()

    // Apply highlights (order matters: comments first, then strings, then others)
    commentPattern.findAll(code).forEach { match ->
        builder.addStyle(commentStyle, match.range.first, match.range.last + 1)
    }

    stringPattern.findAll(code).forEach { match ->
        builder.addStyle(stringStyle, match.range.first, match.range.last + 1)
    }

    keywordPattern.findAll(code).forEach { match ->
        builder.addStyle(keywordStyle, match.range.first, match.range.last + 1)
    }

    numberPattern.findAll(code).forEach { match ->
        builder.addStyle(numberStyle, match.range.first, match.range.last + 1)
    }

    builtinPattern.findAll(code).forEach { match ->
        builder.addStyle(builtinStyle, match.range.first, match.range.last + 1)
    }

    functionPattern.findAll(code).forEach { match ->
        val name = match.groupValues[1]
        if (name !in keywords && name !in builtins) {
            builder.addStyle(functionStyle, match.range.first, match.range.last + 1)
        }
    }

    return builder.toAnnotatedString()
}

private fun pythonHighlightSets(): Triple<Set<String>, Set<String>, String> = Triple(
    setOf(
        "def", "class", "if", "elif", "else", "for", "while", "try", "except", "finally",
        "with", "as", "import", "from", "return", "yield", "lambda", "pass", "break",
        "continue", "raise", "assert", "del", "global", "nonlocal", "and", "or", "not",
        "in", "is", "None", "True", "False", "async", "await", "match", "case"
    ),
    setOf(
        "print", "len", "range", "int", "str", "float", "bool", "list", "dict", "set",
        "tuple", "open", "input", "round", "abs", "max", "min", "sum", "sorted", "reversed",
        "enumerate", "zip", "map", "filter", "any", "all", "isinstance", "issubclass",
        "hasattr", "getattr", "setattr", "type", "super", "object", "Exception", "ValueError",
        "TypeError", "KeyError", "IndexError", "FileNotFoundError", "ImportError", "AttributeError"
    ),
    "#"
)

private fun luaHighlightSets(): Triple<Set<String>, Set<String>, String> = Triple(
    setOf(
        "and", "break", "do", "else", "elseif", "end", "false", "for", "function", "goto",
        "if", "in", "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while"
    ),
    setOf(
        "print", "type", "tostring", "tonumber", "pairs", "ipairs", "next", "select",
        "assert", "error", "pcall", "xpcall", "setmetatable", "getmetatable", "rawget",
        "rawset", "rawequal", "rawlen", "string", "table", "math", "coroutine"
    ),
    "--"
)

private fun sqlHighlightSets(): Triple<Set<String>, Set<String>, String> = Triple(
    setOf(
        "select", "from", "where", "insert", "into", "values", "update", "set", "delete",
        "create", "table", "drop", "alter", "join", "inner", "left", "right", "outer", "on",
        "group", "by", "order", "having", "limit", "offset", "distinct", "as", "and", "or",
        "not", "null", "is", "in", "between", "like", "exists", "union", "all", "case",
        "when", "then", "else", "end", "primary", "key", "foreign", "references", "default",
        "unique", "check", "index", "view", "with", "asc", "desc", "count", "sum", "avg",
        "min", "max", "integer", "text", "real", "blob", "numeric", "begin", "commit", "rollback"
    ),
    setOf("sqlite_master", "sqlite_sequence", "rowid", "typeof", "coalesce", "ifnull", "nullif", "substr", "length", "round", "random"),
    "--"
)

private fun jsHighlightSets(): Triple<Set<String>, Set<String>, String> = Triple(
    setOf(
        "var", "let", "const", "function", "class", "return", "if", "else", "for",
        "while", "do", "switch", "case", "default", "break", "continue", "new",
        "typeof", "instanceof", "delete", "in", "of", "try", "catch", "finally",
        "throw", "yield", "async", "await", "this", "super", "extends", "static",
        "null", "undefined", "true", "false", "NaN", "Infinity"
    ),
    setOf(
        "console", "Math", "JSON", "Object", "Array", "String", "Number", "Boolean",
        "parseInt", "parseFloat", "isNaN", "isFinite", "Promise", "Symbol", "Date",
        "toFixed", "slice", "split", "join", "toUpperCase", "toLowerCase", "push", "pop"
    ),
    "//"
)
