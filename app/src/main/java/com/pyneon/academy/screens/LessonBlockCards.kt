package com.pyneon.academy.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.mutableIntStateOf
import com.pyneon.academy.data.Block
import com.pyneon.academy.lang.RunResult
import com.pyneon.academy.ui.components.ConsoleResult
import com.pyneon.academy.ui.components.NeonButton
import com.pyneon.academy.ui.components.PythonCodeField
import com.pyneon.academy.ui.effects.NeonCard
import com.pyneon.academy.ui.theme.Bg0
import com.pyneon.academy.ui.theme.Bg1
import com.pyneon.academy.ui.theme.MonoCode
import com.pyneon.academy.ui.theme.NeonCyan
import com.pyneon.academy.ui.theme.NeonGreen
import com.pyneon.academy.ui.theme.NeonMagenta
import com.pyneon.academy.ui.theme.NeonYellow
import com.pyneon.academy.ui.theme.SurfaceHigh
import com.pyneon.academy.ui.theme.TextDim
import com.pyneon.academy.ui.theme.TextHi
import com.pyneon.academy.ui.theme.TextMid

// M3a: 从 LessonDetailScreen.kt 拆出的课程内容卡片组件（原私有函数改 internal，
// 仅供本包使用）。主屏幕文件只保留页面骨架与业务编排。
@Composable
internal fun TipBox(text: String, accent: androidx.compose.ui.graphics.Color, tag: String) {
    Column(
        Modifier
            .fillMaxWidth()
            .background(accent.copy(alpha = 0.07f), MaterialTheme.shapes.medium)
            .border(1.dp, accent.copy(alpha = 0.18f), MaterialTheme.shapes.medium)
            .padding(horizontal = 14.dp, vertical = 14.dp)
    ) {
        Text(tag, style = MaterialTheme.typography.labelMedium, color = accent)
        Spacer(Modifier.height(4.dp))
        Text(text, style = MaterialTheme.typography.bodyMedium, color = TextMid)
    }
}

@Composable
internal fun OutputPreview(text: String) {
    Column(
        Modifier
            .fillMaxWidth()
            .background(Bg1, MaterialTheme.shapes.medium)
            .border(1.dp, NeonGreen.copy(alpha = 0.35f), MaterialTheme.shapes.medium)
            .padding(14.dp)
    ) {
        Text("OUTPUT · 运行结果", style = MaterialTheme.typography.labelSmall, color = NeonGreen.copy(alpha = 0.7f))
        Spacer(Modifier.height(4.dp))
        Text(
            text,
            style = com.pyneon.academy.ui.theme.MonoCode.copy(color = NeonGreen.copy(alpha = 0.95f))
        )
    }
}

@Composable
internal fun DiagramBox(text: String) {
    Column(
        Modifier
            .fillMaxWidth()
            .background(NeonCyan.copy(alpha = 0.05f), MaterialTheme.shapes.medium)
            .border(1.dp, NeonCyan.copy(alpha = 0.4f), MaterialTheme.shapes.medium)
            .padding(14.dp)
    ) {
        Text("DIAGRAM · 图示", style = MaterialTheme.typography.labelSmall, color = NeonCyan.copy(alpha = 0.75f))
        Spacer(Modifier.height(6.dp))
        Text(
            text,
            style = com.pyneon.academy.ui.theme.MonoCode.copy(color = TextHi.copy(alpha = 0.95f))
        )
    }
}

@Composable
internal fun NeonTable(headers: List<String>, rows: List<List<String>>) {
    val lineColor = NeonCyan.copy(alpha = 0.30f)
    Column(
        Modifier
            .fillMaxWidth()
            .border(1.dp, lineColor, MaterialTheme.shapes.small)
    ) {
        Row(Modifier.background(SurfaceHigh).fillMaxWidth()) {
            headers.forEach { h ->
                Box(Modifier.weight(1f).padding(8.dp)) {
                    Text(h, style = MaterialTheme.typography.labelMedium, color = NeonCyan)
                }
            }
        }
        rows.forEachIndexed { rowIndex, row ->
            Row(Modifier.fillMaxWidth().background(if (rowIndex % 2 == 1) SurfaceHigh.copy(alpha = 0.35f) else androidx.compose.ui.graphics.Color.Transparent)) {
                row.forEach { cell ->
                    Box(Modifier.weight(1f).padding(horizontal = 8.dp, vertical = 6.dp)) {
                        Text(cell, style = MaterialTheme.typography.bodySmall, color = TextMid)
                    }
                }
            }
            Box(Modifier.fillMaxWidth().height(1.dp).background(lineColor.copy(alpha = 0.5f)))
        }
    }
}

@Composable
internal fun QuizCard(quiz: Block.Quiz) {
    var selected by remember(quiz.question) { mutableStateOf<Int?>(null) }
    NeonCard(accent = if (selected == null) NeonYellow else if (selected == quiz.answerIndex) NeonGreen else NeonMagenta) {
        Text("QUIZ · 随堂一问", style = MaterialTheme.typography.labelSmall, color = NeonYellow.copy(alpha = 0.85f))
        Text(
            quiz.question,
            style = MaterialTheme.typography.bodyLarge,
            color = TextHi,
            modifier = Modifier.padding(top = 6.dp, bottom = 12.dp)
        )
        quiz.options.forEachIndexed { i, opt ->
            val isAnswer = i == quiz.answerIndex
            val chosen = selected == i
            val borderColor = when {
                selected == null -> TextDim
                chosen && isAnswer -> NeonGreen
                chosen && !isAnswer -> NeonMagenta
                isAnswer -> NeonGreen.copy(alpha = 0.6f)
                else -> TextDim.copy(alpha = 0.4f)
            }
            val bg = when {
                selected != null && isAnswer -> NeonGreen.copy(alpha = 0.10f)
                selected != null && chosen -> NeonMagenta.copy(alpha = 0.10f)
                else -> androidx.compose.ui.graphics.Color.Transparent
            }
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .fillMaxWidth()
                    .androidxClickable { if (selected == null) selected = i }
                    .background(bg, MaterialTheme.shapes.extraSmall)
                    .border(1.dp, borderColor, MaterialTheme.shapes.extraSmall)
                    .padding(horizontal = 12.dp, vertical = 12.dp)
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(26.dp)
                        .background(borderColor.copy(alpha = 0.15f), MaterialTheme.shapes.extraSmall)
                ) {
                    Text(
                        "${'A' + i}",
                        style = MaterialTheme.typography.labelLarge,
                        color = borderColor
                    )
                }
                Spacer(Modifier.size(10.dp))
                Text(opt, style = MaterialTheme.typography.bodyMedium, color = TextMid)
            }
            Spacer(Modifier.height(8.dp))
        }
        if (selected != null) {
            Column(
                Modifier
                    .fillMaxWidth()
                    .padding(top = 6.dp)
                    .background(
                        if (selected == quiz.answerIndex) NeonGreen.copy(alpha = 0.06f) else NeonYellow.copy(alpha = 0.06f),
                        MaterialTheme.shapes.extraSmall
                    )
                    .padding(10.dp)
            ) {
                Text(
                    if (selected == quiz.answerIndex) "✓ 答对了" else "✗ 正确答案是 ${'A' + quiz.answerIndex}",
                    style = MaterialTheme.typography.labelMedium,
                    color = if (selected == quiz.answerIndex) NeonGreen else NeonYellow
                )
                Text(quiz.explain, style = MaterialTheme.typography.bodySmall, color = TextMid, modifier = Modifier.padding(top = 4.dp))
            }
        }
    }
}

internal fun Modifier.androidxClickable(onClick: () -> Unit): Modifier = this.clickable(onClick = onClick)

@Composable
internal fun StepsCard(items: List<String>) {
    NeonCard(accent = NeonGreen, filled = true) {
        Text("STEPS · 解题步骤", style = MaterialTheme.typography.labelSmall, color = NeonGreen)
        Spacer(Modifier.height(8.dp))
        items.forEachIndexed { i, step ->
            if (i > 0) {
                Box(
                    Modifier
                        .padding(start = 14.dp, top = 2.dp, bottom = 2.dp)
                        .size(width = 20.dp, height = 1.dp)
                        .background(NeonGreen.copy(alpha = 0.25f))
                )
            }
            Row(
                verticalAlignment = Alignment.Top,
                modifier = Modifier.padding(top = if (i == 0) 0.dp else 8.dp)
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(30.dp)
                        .background(NeonGreen, MaterialTheme.shapes.extraSmall)
                        .padding(horizontal = 0.dp)
                ) {
                    Text(
                        "${i + 1}",
                        style = MaterialTheme.typography.labelLarge,
                        color = Bg0
                    )
                }
                Spacer(Modifier.size(12.dp))
                Text(
                    step,
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextMid,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }
    }
}

@Composable
internal fun Modifier.androidxBackground(color: androidx.compose.ui.graphics.Color, shape: androidx.compose.ui.graphics.Shape): Modifier =
    this.background(color, shape)

@Composable
internal fun PracticeCard(practice: Block.Practice, lang: String = "python") {
    NeonCard(accent = NeonCyan, filled = true) {
        Text("PRACTICE · 跟做练习", style = MaterialTheme.typography.labelSmall, color = NeonCyan)
        Spacer(Modifier.height(4.dp))
        Text(practice.title, style = MaterialTheme.typography.titleSmall, color = TextHi)
        Spacer(Modifier.height(10.dp))
        Text("试一试：", style = MaterialTheme.typography.labelSmall, color = NeonCyan.copy(alpha = 0.7f))
        Spacer(Modifier.height(4.dp))
        PythonCodeField(
            value = remember(practice.code) { TextFieldValue(practice.code) },
            onValueChange = {},
            readOnly = true,
            language = lang,
            modifier = Modifier
                .fillMaxWidth()
                .background(SurfaceHigh.copy(alpha = 0.45f))
                .border(1.dp, NeonCyan.copy(alpha = 0.15f), MaterialTheme.shapes.extraSmall)
                .padding(4.dp),
            minHeight = 60
        )
        Spacer(Modifier.height(10.dp))
        Text("预期输出：", style = MaterialTheme.typography.labelSmall, color = NeonGreen.copy(alpha = 0.7f))
        Spacer(Modifier.height(4.dp))
        OutputPreview(practice.output)
        Spacer(Modifier.height(8.dp))
        TipBox(practice.hint, NeonCyan, "提示")
    }
}

@Composable
internal fun FillCard(fill: Block.Fill, lang: String = "python") {
    var input by remember(fill.goal) { mutableStateOf("") }
    var attempts by remember(fill.goal) { mutableStateOf(0) }
    val correct = input.trim() == fill.answer.trim()
    val checked = attempts > 0
    NeonCard(accent = NeonYellow, filled = true) {
        Text("FILL · 填空补全", style = MaterialTheme.typography.labelSmall, color = NeonYellow)
        Spacer(Modifier.height(4.dp))
        Text(fill.goal, style = MaterialTheme.typography.bodyMedium, color = TextHi)
        Spacer(Modifier.height(8.dp))
        PythonCodeField(
            value = remember(fill.code) { TextFieldValue(fill.code) },
            onValueChange = {},
            readOnly = true,
            language = lang,
            modifier = Modifier
                .fillMaxWidth()
                .background(SurfaceHigh.copy(alpha = 0.45f))
                .border(1.dp, NeonYellow.copy(alpha = 0.2f), MaterialTheme.shapes.extraSmall)
                .padding(4.dp),
            minHeight = 60
        )
        Spacer(Modifier.height(10.dp))
        OutlinedTextField(
            value = input,
            onValueChange = { input = it },
            singleLine = true,
            label = { Text("输入 ____ 处缺失的内容", style = MaterialTheme.typography.labelMedium) },
            // 代码大小写敏感：IME 自动大写会把 True 变成 true 的相反结果
            keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(
                keyboardType = androidx.compose.ui.text.input.KeyboardType.Password,
                capitalization = androidx.compose.ui.text.input.KeyboardCapitalization.None,
                autoCorrect = false
            ),
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            NeonButton(label = "检查", accent = NeonYellow, onClick = { attempts += 1 })
            if (checked && !correct) {
                NeonButton(label = "看答案", accent = TextMid, onClick = { input = fill.answer })
            }
        }
        if (checked) {
            Spacer(Modifier.height(6.dp))
            Text(
                if (correct) "✓ 正确！" else "✗ 还不对，再试试",
                style = MaterialTheme.typography.labelMedium,
                color = if (correct) NeonGreen else NeonMagenta
            )
            if (correct || attempts >= 3) {
                Spacer(Modifier.height(2.dp))
                Text(fill.explain, style = MaterialTheme.typography.bodySmall, color = TextMid)
            }
        }
    }
}

@Composable
internal fun OrderPuzzleCard(order: Block.Order) {
    val shuffled = remember(order.title) { order.lines.shuffled() }
    val selection = remember(order.title) { mutableStateListOf<Int>() }
    val solved = selection.size == order.lines.size &&
        selection.map { shuffled[it] } == order.lines
    val verdict: Boolean? = if (selection.size == order.lines.size) solved else null
    NeonCard(accent = when (verdict) { true -> NeonGreen; false -> NeonMagenta; null -> NeonCyan }, filled = true) {
        Text("ORDER · 代码排序", style = MaterialTheme.typography.labelSmall, color = NeonCyan)
        Spacer(Modifier.height(4.dp))
        Text(order.title, style = MaterialTheme.typography.bodyMedium, color = TextHi)
        Spacer(Modifier.height(2.dp))
        Text("按正确顺序依次点击下面的代码行", style = MaterialTheme.typography.labelSmall, color = TextDim)
        Spacer(Modifier.height(8.dp))
        shuffled.forEachIndexed { displayIdx, line ->
            val pickOrder = selection.indexOf(displayIdx)
            val picked = pickOrder >= 0
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 3.dp)
                    .androidxClickable {
                        if (verdict == null) {
                            if (picked) selection.remove(displayIdx) else selection.add(displayIdx)
                        }
                    }
                    .background(
                        when {
                            verdict == true -> NeonGreen.copy(alpha = 0.10f)
                            picked -> NeonCyan.copy(alpha = 0.12f)
                            else -> SurfaceHigh.copy(alpha = 0.35f)
                        },
                        MaterialTheme.shapes.extraSmall
                    )
                    .border(
                        1.dp,
                        when {
                            verdict == true -> NeonGreen.copy(alpha = 0.5f)
                            picked -> NeonCyan.copy(alpha = 0.55f)
                            else -> TextDim.copy(alpha = 0.35f)
                        },
                        MaterialTheme.shapes.extraSmall
                    )
                    .padding(horizontal = 10.dp, vertical = 10.dp)
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(24.dp)
                        .background(
                            if (picked) NeonCyan else TextDim.copy(alpha = 0.3f),
                            MaterialTheme.shapes.extraSmall
                        )
                ) {
                    Text(
                        if (picked) "${pickOrder + 1}" else "·",
                        style = MaterialTheme.typography.labelMedium,
                        color = if (picked) Bg0 else TextMid
                    )
                }
                Spacer(Modifier.size(10.dp))
                Text(line, style = com.pyneon.academy.ui.theme.MonoCode.copy(fontSize = 12.sp, lineHeight = 18.sp), color = TextMid)
            }
        }
        if (verdict != null) {
            Spacer(Modifier.height(6.dp))
            Text(
                if (verdict) "✓ 顺序正确，程序逻辑成立！" else "✗ 顺序不对，点行可取消重选",
                style = MaterialTheme.typography.labelMedium,
                color = if (verdict) NeonGreen else NeonMagenta
            )
        }
        if (selection.isNotEmpty()) {
            Spacer(Modifier.height(6.dp))
            NeonButton(label = "重排", accent = TextMid, onClick = { selection.clear() })
        }
    }
}

@Composable
internal fun CodeExampleCard(
    code: String,
    runnable: Boolean,
    result: RunResult?,
    running: Boolean,
    onRun: () -> Unit,
    lang: String = "python"
) {
    NeonCard(accent = NeonCyan) {
        PythonCodeField(
            value = remember(code) { TextFieldValue(code) },
            onValueChange = {},
            readOnly = true,
            language = lang,
            modifier = Modifier
                .fillMaxWidth()
                .background(SurfaceHigh.copy(alpha = 0.45f))
                .border(1.dp, NeonCyan.copy(alpha = 0.15f), MaterialTheme.shapes.extraSmall)
                .padding(4.dp),
            minHeight = 80
        )
        Spacer(Modifier.height(10.dp))
        if (runnable) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                NeonButton(label = "▶ 运行", accent = NeonGreen, enabled = !running, onClick = onRun)
                if (running) {
                    Text("EXECUTING…", style = MaterialTheme.typography.labelMedium, color = NeonYellow)
                }
            }
        }
        ConsoleResult(result = result, running = running)
    }
}

/**
 * 多语言对照卡：同一件事在几门语言里怎么写。
 *
 * 每栏独立运行——学习者可以当场对比「同样算 1 到 5 的和」在 Python / C / Lua
 * 里的写法差异与输出差异。这是「概念共通、语法不同」最直观的教学形式。
 */
@Composable
internal fun CompareCard(
    block: Block.Compare,
    results: Map<Int, RunResult>,
    runningKey: Int?,
    onRun: (Int, Block.CompareColumn) -> Unit
) {
    NeonCard(accent = NeonMagenta) {
        Text(block.title, style = MaterialTheme.typography.titleSmall, color = NeonMagenta)
        Spacer(Modifier.height(10.dp))
        block.columns.forEachIndexed { index, col ->
            val langName = com.pyneon.academy.lang.LanguageIds.displayNameOf(col.lang)
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    Modifier
                        .background(NeonMagenta.copy(alpha = 0.15f), MaterialTheme.shapes.extraSmall)
                        .padding(horizontal = 8.dp, vertical = 2.dp)
                ) {
                    Text(langName, style = MaterialTheme.typography.labelMedium, color = NeonMagenta)
                }
                if (col.note.isNotEmpty()) {
                    Text(col.note, style = MaterialTheme.typography.labelSmall, color = TextDim)
                }
            }
            Spacer(Modifier.height(4.dp))
            PythonCodeField(
                value = remember(col.code) { TextFieldValue(col.code) },
                onValueChange = {},
                readOnly = true,
                language = col.lang,
                modifier = Modifier
                    .fillMaxWidth()
                    .background(SurfaceHigh.copy(alpha = 0.45f))
                    .border(1.dp, NeonMagenta.copy(alpha = 0.15f), MaterialTheme.shapes.extraSmall)
                    .padding(4.dp),
                minHeight = 60
            )
            if (col.runnable) {
                Spacer(Modifier.height(6.dp))
                NeonButton(
                    label = if (runningKey == index) "运行中…" else "▶ 运行 $langName",
                    accent = NeonGreen,
                    enabled = runningKey == null,
                    onClick = { onRun(index, col) }
                )
            }
            results[index]?.let {
                Spacer(Modifier.height(6.dp))
                ConsoleResult(result = it, running = false)
            }
            if (index < block.columns.lastIndex) {
                Spacer(Modifier.height(12.dp))
            }
        }
    }
}

/**
 * 过程可视化卡：把抽象过程逐帧播放出来。
 *
 * 交互：上一帧 / 下一帧 / 自动播放 / 重置。变化项用霓虹高亮标出，
 * 让「哪个变量在这一步变了」一眼可见——这是纯文字讲解做不到的。
 *
 * 简洁风格下自动播放会关闭（避免持续动画），但仍可手动翻帧。
 */
@Composable
internal fun VisualizeCard(block: Block.Visualize) {
    if (block.frames.isEmpty()) return
    var frame by remember(block) { mutableIntStateOf(0) }
    var playing by remember(block) { mutableStateOf(false) }
    val style = com.pyneon.academy.ui.theme.LocalVisualStyle.current
    // 自动播放：每 900ms 前进一帧，到末帧停止
    LaunchedEffect(playing, block) {
        if (!playing) return@LaunchedEffect
        while (playing && frame < block.frames.lastIndex) {
            kotlinx.coroutines.delay(900)
            if (!playing) break
            frame += 1
        }
        if (frame >= block.frames.lastIndex) playing = false
    }
    val current = block.frames[frame.coerceIn(0, block.frames.lastIndex)]

    NeonCard(accent = NeonYellow) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(block.title, style = MaterialTheme.typography.titleSmall, color = NeonYellow)
            Spacer(Modifier.weight(1f))
            Text(
                "${frame + 1} / ${block.frames.size}",
                style = MaterialTheme.typography.labelSmall,
                color = TextDim
            )
        }
        if (block.caption.isNotEmpty()) {
            Text(
                block.caption,
                style = MaterialTheme.typography.bodySmall,
                color = TextMid,
                modifier = Modifier.padding(top = 4.dp)
            )
        }
        Spacer(Modifier.height(10.dp))

        // 当前帧的说明
        Text(current.label, style = MaterialTheme.typography.bodyMedium, color = TextHi)

        Spacer(Modifier.height(8.dp))
        // 变量格子
        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
            current.items.forEach { item ->
                val changed = item.name in current.highlight
                Row(
                    Modifier
                        .fillMaxWidth()
                        .background(
                            if (changed) NeonYellow.copy(alpha = 0.12f) else Color.Transparent,
                            MaterialTheme.shapes.extraSmall
                        )
                        .padding(horizontal = 8.dp, vertical = 5.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        item.name,
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (changed) NeonYellow else TextMid,
                        modifier = Modifier.weight(1f)
                    )
                    Text(
                        item.value,
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (changed) NeonYellow else TextHi
                    )
                }
            }
        }

        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            NeonButton(
                label = "◀",
                accent = NeonCyan,
                enabled = frame > 0,
                onClick = { playing = false; frame -= 1 }
            )
            NeonButton(
                label = "▶",
                accent = NeonCyan,
                enabled = frame < block.frames.lastIndex,
                onClick = { playing = false; frame += 1 }
            )
            // 简洁风格不做自动播放（避免持续动画干扰阅读）
            if (style.pressAnimationEnabled) {
                NeonButton(
                    label = if (playing) "暂停" else "自动播放",
                    accent = NeonGreen,
                    enabled = frame < block.frames.lastIndex || playing,
                    onClick = { playing = !playing }
                )
            }
            NeonButton(
                label = "重置",
                accent = TextDim,
                onClick = { playing = false; frame = 0 }
            )
        }
    }
}
