package com.pyneon.academy.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CutCornerShape
import androidx.compose.material.icons.outlined.Search
import androidx.compose.material.icons.outlined.Close
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.Icon
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.pyneon.academy.data.LessonRepository
import com.pyneon.academy.data.Progress
import com.pyneon.academy.data.ProgressStore
import com.pyneon.academy.ui.effects.GlitchText
import com.pyneon.academy.ui.effects.NeonCard
import com.pyneon.academy.ui.theme.Bg0
import com.pyneon.academy.ui.theme.NeonCyan
import com.pyneon.academy.ui.theme.NeonGreen
import com.pyneon.academy.ui.theme.NeonMagenta
import com.pyneon.academy.ui.theme.NeonYellow
import com.pyneon.academy.ui.theme.TextDim
import com.pyneon.academy.ui.theme.TextHi
import com.pyneon.academy.ui.theme.TextMid

@Composable
fun LessonsScreen(openLesson: (String) -> Unit) {
    val context = LocalContext.current
    val progress by ProgressStore.flow(context).collectAsState(initial = Progress())
    val allLessons = remember { LessonRepository.lessons(context) }
    // 语言过滤：null = 全部；选项来自课程数据里实际出现过的语言
    var langFilter by remember { mutableStateOf<String?>(null) }
    // 搜索：匹配标题 / 副标题 / 章节名。79 讲规模下找「装饰器」「JOIN」
    // 这类关键词，逐个翻列表不可接受（2026-11 技术债清理）。
    var query by rememberSaveable { mutableStateOf("") }
    val lessons = remember(langFilter, query, allLessons) {
        var r = if (langFilter == null) allLessons else allLessons.filter { it.lang == langFilter }
        val q = query.trim()
        if (q.isNotEmpty()) {
            r = r.filter {
                it.title.contains(q, ignoreCase = true) ||
                    it.subtitle.contains(q, ignoreCase = true) ||
                    it.chapterName.contains(q, ignoreCase = true)
            }
        }
        r
    }
    val langOptions = remember(allLessons) {
        allLessons.map { it.lang }.distinct().map { it to com.pyneon.academy.lang.LanguageIds.displayNameOf(it) }
    }

    // 每讲的「章节内序号」与「章节内上一讲」一次性预计算，按 lesson.id 索引。
    //
    // 为什么不能用列表下标：列表会被语言筛选、搜索过滤，过滤后的下标与全量列表
    // 完全对不上。旧实现用 orderInChapter[index] + lessons[index-1]，一旦切到
    // 「只看 JavaScript」，序号会变成错乱的 01/07/19…，锁定判断还会拿上一门语言
    // 的最后一讲当解锁条件（2026-11 审查发现）。按 id 预计算后，过滤不影响语义。
    val chapterPos = remember(allLessons) { buildChapterPositions(allLessons) }

    Column(
        Modifier
            .fillMaxSize()
            .background(Bg0)
    ) {
        Column(
            Modifier
                .statusBarsPadding()
                .padding(horizontal = 20.dp, vertical = 12.dp)
        ) {
            GlitchText("课程 // LESSONS", style = MaterialTheme.typography.headlineSmall, color = NeonCyan)
            Text(
                "按顺序解锁 · 完成练习即通关",
                style = MaterialTheme.typography.bodySmall,
                color = TextDim,
                modifier = Modifier.padding(top = 4.dp)
            )
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                singleLine = true,
                placeholder = {
                    Text("搜索课程：标题 / 主题（如 装饰器、JOIN）",
                        style = MaterialTheme.typography.bodySmall, color = TextDim)
                },
                leadingIcon = {
                    Icon(Icons.Outlined.Search, contentDescription = "搜索", tint = TextMid)
                },
                trailingIcon = {
                    if (query.isNotEmpty()) {
                        Icon(
                            Icons.Outlined.Close, contentDescription = "清空搜索",
                            tint = TextMid,
                            modifier = Modifier.clickable { query = "" }
                        )
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 8.dp)
            )
            if (langOptions.size > 1) {
                com.pyneon.academy.ui.components.LangChipRow(
                    options = listOf(null to "全部") + langOptions,
                    selected = langFilter,
                    accent = NeonCyan,
                    modifier = Modifier.padding(top = 8.dp)
                ) { picked -> langFilter = picked }
            }
        }
        LazyColumn(
            Modifier
                .fillMaxSize()
                .padding(horizontal = 20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(bottom = 96.dp, top = 8.dp)
        ) {
            items(lessons.size, key = { lessons[it].id }) { index ->
                val lesson = lessons[index]
                // 章节名来自课程数据本身（chapterName），不再依赖 UI 硬编码映射，
                // 新增课程包（DSA/彩蛋等）也能正确分组。
                val showHeader = index == 0 || lessons[index - 1].chapterName != lesson.chapterName

                // 解锁与序号都按「章节（=课程包）」内部计算，并且以 lesson.id 为键。
                // 原因一：各内容包的 order 是跳跃的（DSA 100 / 彩蛋 200 / JS 300 / …），
                //   用全局 index 会导致「下载了 C 语言，第一讲却被 Python 的 l38 锁住」，
                //   每门语言必须先学完上一门——这与「六门语言任选」的定位矛盾。
                // 原因二：列表会因语言筛选/搜索变短，下标随之漂移；按 id 查位置才稳定。
                val pos = chapterPos[lesson.id]
                val indexInChapter = pos?.index ?: 1
                val prevId = pos?.prevId
                val locked = prevId != null && prevId !in progress.completedLessons
                val prevLesson = prevId?.let { pid -> allLessons.firstOrNull { it.id == pid } }
                val displayOrder = indexInChapter
                val done = lesson.id in progress.completedLessons
                Column {
                    if (showHeader && lesson.chapterName.isNotBlank()) {
                        Text(
                            lesson.chapterName,
                            style = MaterialTheme.typography.titleMedium,
                            color = NeonMagenta,
                            modifier = Modifier.padding(top = if (index == 0) 0.dp else 14.dp, bottom = 4.dp)
                        )
                    }
                LessonRow(
                    order = displayOrder,
                    title = lesson.title,
                    subtitle = lesson.subtitle,
                    xp = lesson.xp,
                    locked = locked,
                    done = done || (lesson.exercise == null && "les_${lesson.id}" in progress.solvedKeys),
                    accent = when {
                        done -> NeonGreen
                        locked -> TextMid
                        else -> NeonCyan
                    },
                    onClick = {
                        if (locked) {
                            // 解锁条件显式化：告诉用户具体是哪一课挡住了
                            val target = prevLesson?.title ?: "上一课"
                            Toast.makeText(context, "先完成「$target」即可解锁本节", Toast.LENGTH_SHORT).show()
                        } else {
                            openLesson(lesson.id)
                        }
                    }
                )
                }
            }
        }
    }
}

@Composable
private fun LessonRow(
    order: Int,
    title: String,
    subtitle: String,
    xp: Int,
    locked: Boolean,
    done: Boolean,
    accent: androidx.compose.ui.graphics.Color,
    onClick: () -> Unit
) {
    NeonCard(accent = accent, onClick = onClick) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                Modifier
                    .clip(CutCornerShape(6.dp))
                    .background(accent.copy(alpha = if (locked) 0.06f else 0.14f))
                    .padding(horizontal = 10.dp, vertical = 8.dp)
            ) {
                Text(
                    "%02d".format(order),
                    style = MaterialTheme.typography.titleMedium,
                    color = accent
                )
            }
            Spacer(Modifier.size(14.dp))
            Column(Modifier.weight(1f)) {
                Text(title, style = MaterialTheme.typography.titleMedium, color = TextHi)
                if (subtitle.isNotEmpty()) {
                    Text(subtitle, style = MaterialTheme.typography.bodySmall, color = TextMid)
                }
            }
            Spacer(Modifier.size(10.dp))
            Text(
                "+$xp",
                style = MaterialTheme.typography.labelMedium,
                color = NeonYellow.copy(alpha = 0.85f)
            )
            Spacer(Modifier.size(10.dp))
            Icon(
                imageVector = when {
                    done -> Icons.Outlined.CheckCircle
                    locked -> Icons.Outlined.Lock
                    else -> Icons.Outlined.PlayArrow
                },
                contentDescription = null,
                tint = if (done) NeonGreen else accent,
                modifier = Modifier.size(20.dp)
            )
        }
    }
}

/** 章节内位置：index 从 1 开始，prevId 是同章上一讲（章节第一讲为 null）。 */
internal data class ChapterPos(val index: Int, val prevId: String?)

/**
 * 按 [chapterName] 切章，算出每讲在自己章节内的序号与上一讲 id。
 *
 * 之所以独立成函数：课程列表会被语言筛选与搜索裁剪，用列表下标定位必然错位；
 * 以 lesson.id 为键的映射对过滤天然免疫，也便于单测覆盖（见 LessonChapterPosTest）。
 */
internal fun buildChapterPositions(lessons: List<com.pyneon.academy.data.Lesson>): Map<String, ChapterPos> {
    val result = HashMap<String, ChapterPos>(lessons.size)
    var i = 0
    while (i < lessons.size) {
        val chapter = lessons[i].chapterName
        var j = i
        while (j < lessons.size && lessons[j].chapterName == chapter) j++
        for (k in i until j) {
            result[lessons[k].id] = ChapterPos(
                index = k - i + 1,
                prevId = if (k > i) lessons[k - 1].id else null
            )
        }
        i = j
    }
    return result
}
