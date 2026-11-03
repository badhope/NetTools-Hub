package com.pyneon.academy.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.pyneon.academy.data.ContentCatalog
import com.pyneon.academy.data.ContentCenter
import com.pyneon.academy.data.LessonRepository
import com.pyneon.academy.debug.DebugLog
import com.pyneon.academy.lang.LanguageIds
import com.pyneon.academy.lang.LanguageRegistry
import com.pyneon.academy.ui.components.NeonButton
import com.pyneon.academy.ui.effects.GlitchText
import com.pyneon.academy.ui.effects.NeonCard
import com.pyneon.academy.ui.effects.SectionHeader
import com.pyneon.academy.ui.theme.Bg0
import com.pyneon.academy.ui.theme.NeonCyan
import com.pyneon.academy.ui.theme.NeonGreen
import com.pyneon.academy.ui.theme.NeonMagenta
import com.pyneon.academy.ui.theme.NeonYellow
import com.pyneon.academy.ui.theme.TextDim
import com.pyneon.academy.ui.theme.TextHi
import com.pyneon.academy.ui.theme.TextMid
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * 语言中心：把「运行时是否内置」与「课程包是否已下载」分成两栏展示。
 *
 * 设计红线（2026-10-24 复核后确立）：
 * - 内置运行时（Python / JavaScript / Lua / SQL）显示为可用，课程包按需下载；
 * - 未内置运行时的语言（Java / C++ / Go / Rust）只显示「暂不支持」，
 *   不出现任何下载入口——项目没有运行时下载机制，不能让用户白点。
 * - 课程包未下载前，课程列表里不出现该语言的任何讲；
 *   预置包（js/lua/sql）只下载课程内容，不下载运行时。
 */
@Composable
fun LanguageCenterScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    val center = remember { ContentCenter() }

    var catalog by remember { mutableStateOf<ContentCatalog?>(null) }
    var catalogBase by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(false) }
    var message by remember { mutableStateOf<String?>(null) }
    var installed by remember { mutableStateOf(center.installedVersions(context)) }

    fun refresh() {
        scope.launch {
            loading = true
            message = null
            try {
                val (cat, base) = withContext(Dispatchers.IO) { center.fetchCatalog() }
                catalog = cat
                catalogBase = base
            } catch (e: Exception) {
                message = "连接失败：${e.message?.take(60) ?: "网络不可用"}（离线课程不受影响）"
            }
            loading = false
        }
    }

    Column(
        Modifier
            .fillMaxSize()
            .background(Bg0)
            .verticalScroll(rememberScrollState())
            .statusBarsPadding()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            NeonButton(label = "◄ 返回", accent = TextMid, onClick = onBack)
            Spacer(Modifier.size(10.dp))
            GlitchText("语言中心 // LANGS", style = MaterialTheme.typography.titleMedium, color = NeonCyan)
        }

        Text(
            "运行时随 APK 内置，课程包按需下载。下载前不会出现在课程列表里。",
            style = MaterialTheme.typography.bodySmall,
            color = TextDim
        )

        SectionHeader("已内置运行时", accent = NeonGreen)
        LanguageRegistry.all().forEach { runtime ->
            NeonCard(accent = NeonGreen) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) {
                        Text(runtime.displayName, style = MaterialTheme.typography.titleMedium, color = TextHi)
                        Text(runtime.version, style = MaterialTheme.typography.bodySmall, color = TextMid)
                    }
                    Text(
                        if (runtime.isAvailable()) "可离线运行" else "初始化失败",
                        style = MaterialTheme.typography.labelMedium,
                        color = if (runtime.isAvailable()) NeonGreen else NeonMagenta
                    )
                }
            }
        }

        SectionHeader("暂不支持", accent = NeonMagenta)
        NeonCard(accent = NeonMagenta) {
            Text(
                LanguageIds.PLANNED.joinToString(" · ") { LanguageIds.displayNameOf(it) },
                style = MaterialTheme.typography.bodyMedium,
                color = TextHi
            )
            Text(
                "这些语言需要编译器或原生工具链，无法随 APK 离线提供，也没有下载入口。",
                style = MaterialTheme.typography.bodySmall,
                color = TextMid,
                modifier = Modifier.padding(top = 4.dp)
            )
        }

        SectionHeader("课程包（按需下载）", accent = NeonYellow)
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            NeonButton(
                label = if (loading) "检查中…" else "检查课程包",
                accent = NeonCyan,
                enabled = !loading,
                onClick = { refresh() },
                modifier = Modifier.weight(1f)
            )
        }
        message?.let {
            Text(it, style = MaterialTheme.typography.bodySmall, color = if (it.startsWith("连接")) TextMid else TextDim)
        }

        catalog?.let { cat ->
            val installedLangs = LessonRepository.lessons(context).map { it.lang }.distinct()
            cat.packs.forEach { pack ->
                val ver = installed[pack.id]
                val runtime = if (pack.lang.isBlank()) null else LanguageRegistry.get(pack.lang)
                val runtimeReady = runtime == null || runtime.isAvailable()
                val state = when {
                    !runtimeReady -> null
                    ver == null -> "下载"
                    ver < pack.version -> "更新到 v${pack.version}"
                    else -> null
                }
                NeonCard(accent = if (state == null) NeonGreen else NeonYellow) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(pack.name, style = MaterialTheme.typography.titleMedium, color = TextHi)
                            Text(
                                if (pack.lang.isBlank()) "通用" else "语言：${LanguageIds.displayNameOf(pack.lang)}",
                                style = MaterialTheme.typography.labelSmall,
                                color = TextDim
                            )
                        }
                        if (pack.lang.isNotBlank() && installedLangs.contains(pack.lang)) {
                            Text("已可学习", style = MaterialTheme.typography.labelMedium, color = NeonGreen)
                        }
                    }
                    Text(pack.description, style = MaterialTheme.typography.bodySmall, color = TextMid, modifier = Modifier.padding(top = 4.dp))
                    Spacer(Modifier.height(10.dp))
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                        if (!runtimeReady) {
                            Text("缺运行时，暂不可下载", style = MaterialTheme.typography.labelMedium, color = NeonMagenta)
                        } else if (state != null) {
                            NeonButton(
                                label = state,
                                accent = NeonYellow,
                                onClick = {
                                    scope.launch {
                                        message = "下载中 ${pack.name}…"
                                        try {
                                            withContext(Dispatchers.IO) { center.download(context, pack, catalogBase) }
                                            installed = center.installedVersions(context)
                                            LessonRepository.invalidateCache()
                                            DebugLog.i("Content", "课程包安装成功 ${pack.id} v${pack.version}")
                                            message = "安装完成，课程列表已刷新"
                                        } catch (e: Exception) {
                                            DebugLog.e("Content", "课程包下载失败 ${pack.id}", e)
                                            message = "下载失败：${e.message?.take(50)}"
                                        }
                                    }
                                }
                            )
                        } else {
                            Text("✓ 已是最新 v$ver", style = MaterialTheme.typography.labelMedium, color = NeonGreen)
                        }
                        Text("v${pack.version}", style = MaterialTheme.typography.labelSmall, color = TextDim)
                    }
                }
            }
            if (cat.packs.isEmpty()) {
                Text("目录为空，敬请期待新资料片。", style = MaterialTheme.typography.bodySmall, color = TextDim)
            }
        }
    }
}
