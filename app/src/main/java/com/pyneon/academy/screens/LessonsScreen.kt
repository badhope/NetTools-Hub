package com.pyneon.academy.screens

import android.widget.Toast
import androidx.compose.foundation.background
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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
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
    val lessons = remember(langFilter) {
        if (langFilter == null) allLessons else allLessons.filter { it.lang == langFilter }
    }
    val langOptions = remember(allLessons) {
        allLessons.map { it.lang }.distinct().map { it to com.pyneon.academy.lang.LanguageIds.displayNameOf(it) }
    }

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

                // 解锁与序号都按「章节（=课程包）」内部计算，而不是全局列表位置。
                // 原因：各内容包的 order 是跳跃的（DSA 100 / 彩蛋 200 / JS 300 / …），
                // 用全局 index-1 会导致「下载了 C 语言，第一讲却被 Python 的 l38 锁住」，
                // 每门语言必须先学完上一门——这与「六门语言任选」的定位矛盾。
                // 现在：每个包的第一讲默认解锁，包内逐讲推进；序号显示包内 01..N。
                val chapterStart = lessons.indexOfFirst { it.chapterName == lesson.chapterName }
                val indexInChapter = index - chapterStart
                val locked = indexInChapter > 0 &&
                    lessons[index - 1].id !in progress.completedLessons
                val prevLesson = if (indexInChapter > 0) lessons[index - 1] else null
                val displayOrder = indexInChapter + 1
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
