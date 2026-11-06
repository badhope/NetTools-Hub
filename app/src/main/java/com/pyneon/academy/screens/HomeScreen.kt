package com.pyneon.academy.screens

import com.pyneon.academy.utils.AppConstants

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.MenuBook
import androidx.compose.material.icons.outlined.ChevronRight
import androidx.compose.material.icons.outlined.Bolt
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.LocalFireDepartment
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.PlayArrow
import androidx.compose.material.icons.outlined.Terminal
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.pyneon.academy.data.LessonRepository
import com.pyneon.academy.data.Progress
import com.pyneon.academy.data.ProgressStore
import com.pyneon.academy.data.Ranks
import com.pyneon.academy.data.Track
import com.pyneon.academy.data.TrackRepository
import com.pyneon.academy.data.dailyMissionDone
import com.pyneon.academy.lang.LanguageRegistry
import com.pyneon.academy.ui.components.NeonButton
import com.pyneon.academy.ui.effects.GlitchText
import com.pyneon.academy.ui.effects.NeonCard
import com.pyneon.academy.ui.effects.ProgressRing
import com.pyneon.academy.ui.effects.SectionHeader
import com.pyneon.academy.ui.effects.cyberGrid
import com.pyneon.academy.ui.effects.scanlines
import com.pyneon.academy.ui.theme.Bg0
import com.pyneon.academy.ui.theme.NeonCyan
import com.pyneon.academy.ui.theme.NeonGreen
import com.pyneon.academy.ui.theme.NeonMagenta
import com.pyneon.academy.ui.theme.NeonYellow
import com.pyneon.academy.ui.theme.SurfaceHigh
import com.pyneon.academy.ui.theme.TextDim
import com.pyneon.academy.ui.theme.TextHi
import com.pyneon.academy.ui.theme.TextMid

@Composable
fun HomeScreen(
    onOpenLesson: (String) -> Unit,
    onOpenTerminal: () -> Unit,
    onOpenArena: () -> Unit,
    onOpenLessons: () -> Unit,
    onOpenTracks: () -> Unit,
    /** 全部课程完成后「继续学习」按钮改指复习台（null 允许调用方缺省为空操作） */
    onOpenReview: () -> Unit = {}
) {
    val context = LocalContext.current
    val progress by ProgressStore.flow(context).collectAsState(initial = Progress())
    val lessons = remember { LessonRepository.lessons(context) }
    // 首页进度只统计内置主线（Python）。下载的语言包/增补包属于扩展内容，
    // 若一并计入会出现「课程体系 38 讲」与「课程进度 x/44」自相矛盾（实测）。
    val coreLessons = remember(lessons) { LessonRepository.mainline(context) }
    val runtime = remember { LanguageRegistry.current(context) }
    val pythonVersion = remember { runtime.version }

    // 「继续学习」目标：
    //   1. 优先上一个没完成的课（学习的自然推进）
    //   2. 全部完成后不再把用户踹回 l01 从头再来——那等于宣告「你的进度没意义」；
    //      此时按钮应指向复习（学完了就该复习巩固），由调用方处理 null
    val continueTarget = remember(progress.completedLessons) {
        lessons.firstOrNull { it.id !in progress.completedLessons }?.id
    }
    val doneCount = coreLessons.count { it.id in progress.completedLessons }

    // 断点续读：最近一次【打开】的课（不是最近完成的）。与「继续学习」互补——
    // 「继续学习」指向下一节新课；「继续上次」回到可能还没读完的那节。
    val resumeTarget by produceState("", progress.completedLessons) {
        value = ProgressStore.lastOpenedLesson(context) ?: ""
    }
    val resumeLesson = remember(resumeTarget, lessons) {
        lessons.firstOrNull { it.id == resumeTarget }
    }

    Column(
        Modifier
            .fillMaxSize()
            .background(Bg0)
            .verticalScroll(rememberScrollState())
            .cyberGrid(NeonCyan.copy(alpha = 0.04f), 48.dp)
            .scanlines()
            .statusBarsPadding()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                GlitchText("CodeLearning", style = MaterialTheme.typography.headlineMedium, color = NeonCyan)
                Text("码上 · 编程学院 v${AppConstants.VERSION_NAME}", style = MaterialTheme.typography.labelSmall, color = TextDim)
            }
            // 运行时名可能很长（如 "JavaScript Rhino 1.7.15 (ES5/部分 ES6)"），
            // 不限制宽度会把左侧品牌名与版本号挤成两行，因此限宽 + 单行省略。
            // 首页只报「当前运行时是否就绪」：JS 的完整版本串（Rhino 1.7.15 (ES5/部分 ES6)）
            // 在 200dp 里会被截成 "ES5/部…"，完整版本留给终端页展示。
            Text(
                if (runtime.id == "python") "${runtime.displayName} $pythonVersion 就绪"
                else "${runtime.displayName} 就绪",
                style = MaterialTheme.typography.labelSmall,
                color = NeonGreen.copy(alpha = 0.8f),
                maxLines = 1,
                overflow = androidx.compose.ui.text.style.TextOverflow.Ellipsis,
                modifier = Modifier.widthIn(max = 200.dp)
            )
        }

        NeonCard(accent = NeonCyan) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(18.dp)) {
                ProgressRing(
                    fraction = Ranks.fraction(progress.xpTotal),
                    diameter = 104.dp,
                    stroke = 9.dp,
                    accent = NeonCyan,
                    trackColor = SurfaceHigh,
                    modifier = Modifier.size(104.dp)
                ) {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        val rank = Ranks.forXp(progress.xpTotal)
                        Text(rank.name, style = MaterialTheme.typography.titleMedium, color = rank.color)
                        Text("${progress.xpTotal} XP", style = MaterialTheme.typography.labelMedium, color = TextMid)
                    }
                }
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    StatLine(Icons.Outlined.Bolt, "连击 ${progress.streakDays} 天", NeonYellow)
                    StatLine(Icons.Outlined.CheckCircle, "课程进度 $doneCount/${coreLessons.size}", NeonGreen)
                    val next = Ranks.next(progress.xpTotal)
                    Text(
                        if (next != null) "距「${next.name}」还需 ${next.minXp - progress.xpTotal} XP"
                        else "已达最高阶",
                        style = MaterialTheme.typography.bodySmall,
                        color = TextDim
                    )
                }
            }
        }

        SectionHeader("每日任务")
        NeonCard(accent = if (dailyMissionDone(progress)) NeonGreen else NeonYellow, filled = dailyMissionDone(progress)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Outlined.LocalFireDepartment,
                    contentDescription = null,
                    tint = if (dailyMissionDone(progress)) NeonGreen else NeonYellow,
                    modifier = Modifier.size(22.dp)
                )
                Spacer(Modifier.size(10.dp))
                Column(Modifier.weight(1f)) {
                    Text("今日通过 1 个练习或挑战", style = MaterialTheme.typography.bodyLarge, color = TextHi)
                    Text("奖励：+30 XP", style = MaterialTheme.typography.bodySmall, color = TextMid)
                }
                if (dailyMissionDone(progress)) {
                    Icon(Icons.Outlined.CheckCircle, contentDescription = null, tint = NeonGreen)
                } else {
                    Text("待完成", style = MaterialTheme.typography.labelMedium, color = TextDim)
                }
            }
        }

        SectionHeader("课程体系")
        val readyTrack = TrackRepository.readyTrack(context, progress.completedLessons)
        if (readyTrack != null) {
            NeonCard(accent = NeonCyan, filled = true, onClick = onOpenTracks) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        Modifier
                            .size(44.dp)
                            .background(NeonCyan.copy(alpha = 0.12f), androidx.compose.foundation.shape.CutCornerShape(6.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(Icons.Outlined.PlayArrow, contentDescription = null, tint = NeonCyan, modifier = Modifier.size(22.dp))
                    }
                    Spacer(Modifier.size(12.dp))
                    Column(Modifier.weight(1f)) {
                        Text(readyTrack.title, style = MaterialTheme.typography.titleMedium, color = NeonCyan)
                        Text("${readyTrack.progressHint} · 查看全部路线", style = MaterialTheme.typography.bodySmall, color = TextMid)
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Outlined.CheckCircle, contentDescription = null, tint = NeonGreen, modifier = Modifier.size(14.dp))
                        Text(" 已上线", style = MaterialTheme.typography.labelSmall, color = NeonGreen)
                    }
                }
            }
        }

        resumeLesson?.let { resume ->
            if (resume.id !in progress.completedLessons) {
                SectionHeader("继续上次")
                NeonCard(accent = NeonGreen, onClick = { onOpenLesson(resume.id) }) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.AutoMirrored.Outlined.MenuBook,
                            contentDescription = null,
                            tint = NeonGreen,
                            modifier = Modifier.size(22.dp)
                        )
                        Spacer(Modifier.size(12.dp))
                        Column(Modifier.weight(1f)) {
                            Text(
                                resume.title,
                                style = MaterialTheme.typography.titleMedium,
                                color = TextHi
                            )
                            Text(
                                "上次学到这一讲，点这里接着学",
                                style = MaterialTheme.typography.bodySmall,
                                color = TextMid
                            )
                        }
                        Icon(
                            Icons.Outlined.ChevronRight,
                            contentDescription = null,
                            tint = NeonGreen
                        )
                    }
                }
            }
        }

        SectionHeader("继续行动")
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            NeonButton(
                label = if (continueTarget != null) "继续学习" else "已完成，去复习",
                onClick = {
                    // 全部完成时把入口让给复习——比「回到 l01 重学」更符合学习闭环
                    if (continueTarget != null) onOpenLesson(continueTarget) else onOpenReview()
                },
                modifier = Modifier.weight(1f),
                accent = NeonMagenta,
                leadingIcon = Icons.Outlined.PlayArrow
            )
            NeonButton(
                label = "课程列表",
                onClick = onOpenLessons,
                modifier = Modifier.weight(1f),
                accent = NeonCyan,
                leadingIcon = Icons.AutoMirrored.Outlined.MenuBook
            )
        }
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            NeonButton(
                label = "终端 REPL",
                onClick = onOpenTerminal,
                modifier = Modifier.weight(1f),
                accent = NeonGreen,
                leadingIcon = Icons.Outlined.Terminal
            )
            NeonButton(
                label = "挑战",
                onClick = onOpenArena,
                modifier = Modifier.weight(1f),
                accent = NeonYellow,
                leadingIcon = Icons.Outlined.LocalFireDepartment
            )
        }

        Spacer(Modifier.height(8.dp))
    }
}

@Composable
private fun StatLine(icon: androidx.compose.ui.graphics.vector.ImageVector, text: String, color: androidx.compose.ui.graphics.Color) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Icon(icon, contentDescription = null, tint = color, modifier = Modifier.size(18.dp))
        Text(text, style = MaterialTheme.typography.bodyMedium, color = TextMid)
    }
}
