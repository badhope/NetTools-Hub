package com.pyneon.academy.screens

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
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.pyneon.academy.lang.LanguageRegistry
import com.pyneon.academy.ui.effects.GlitchText
import com.pyneon.academy.ui.effects.cyberGrid
import com.pyneon.academy.ui.effects.scanlines
import com.pyneon.academy.ui.theme.Bg0
import com.pyneon.academy.ui.theme.NeonCyan
import com.pyneon.academy.ui.theme.NeonGreen
import com.pyneon.academy.ui.theme.NeonMagenta
import com.pyneon.academy.ui.theme.TextDim
import com.pyneon.academy.ui.theme.TextMid
import kotlinx.coroutines.delay

@Composable
fun BootScreen(
    onDone: () -> Unit,
    /**
     * 用户是否已同意隐私政策。
     *
     * 合规要求（个保法 / 商店审核）：未取得同意前不得处理任何用户数据。
     * 因此为 false 时本页只播动画，**不预热运行时、不写连击、不记日志**。
     */
    consented: Boolean = true
) {
    val context = LocalContext.current
    val streakVm: com.pyneon.academy.data.StreakViewModel =
        androidx.lifecycle.viewmodel.compose.viewModel()
    var pyStatus by remember { mutableStateOf("RUN") }
    // S7: 运行时预热失败时置 true，停在恢复页而不是硬着头皮进首页
    var bootFailed by remember { mutableStateOf(false) }
    
    // Use current release version
    val appVersion = "v${com.pyneon.academy.utils.AppConstants.VERSION_NAME}"
    
    val bootLines = remember(pyStatus) {
        listOf(
            "码上 $appVersion .............. OK",
            "初始化执行引擎 ............ OK",
            when (pyStatus) {
                "RUN" -> "加载语言运行时 ............. 校验中"
                "OK" -> "加载语言运行时 ............. OK"
                else -> "加载语言运行时 ............. FAIL"
            },
            "加载本地课程数据 .............. OK",
            "准备离线学习环境 .............. 完成",
            "",
            "> 欢迎回来，编程学徒_"
        )
    }
    var shown by remember { mutableIntStateOf(0) }

    LaunchedEffect(Unit) {
        shown = 1
        delay(170L)
        shown = 2
        delay(170L)

        if (consented) {
            // 只在已同意后才初始化运行时、写连击数据
            val runtime = LanguageRegistry.current(context)
            runtime.ensureStarted(context)
            val ok = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                runtime.warmup()
            }
            pyStatus = if (ok) "OK" else "FAIL"
            if (ok) {
                streakVm.onAppOpen()
            } else {
                // S7: 预热失败不能静默进首页——用户会看到「Python 3.x 就绪」的假象，
                // 之后每次运行都报错却不知原因。停在恢复页，给出可操作的出口。
                bootFailed = true
                return@LaunchedEffect
            }
        } else {
            // 未同意：跳过一切数据处理，直接交给上层继续弹同意框
            pyStatus = "SKIP"
        }

        shown = 3
        for (i in 3 until bootLines.size) {
            shown = i + 1
            delay(190L)
        }
        delay(650)
        onDone()
    }

    Box(
        Modifier
            .fillMaxSize()
            .background(Bg0)
            .cyberGrid(NeonCyan.copy(alpha = 0.05f), 44.dp)
            .scanlines()
            .padding(28.dp)
    ) {
        Column(Modifier.align(Alignment.Center)) {
            GlitchText("码上", style = MaterialTheme.typography.headlineLarge, color = NeonCyan)
            Text(
                "编程学院",
                style = MaterialTheme.typography.labelMedium,
                color = NeonMagenta,
                modifier = Modifier.padding(top = 6.dp)
            )
            Spacer(Modifier.height(28.dp))
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                bootLines.take(shown).forEachIndexed { idx, line ->
                    val failLine = idx == 2 && pyStatus == "FAIL"
                    Text(
                        line,
                        style = MaterialTheme.typography.bodySmall,
                        color = if (failLine) NeonMagenta else NeonGreen.copy(alpha = 0.85f)
                    )
                }
            }
            Spacer(Modifier.height(24.dp))
            if (bootFailed) {
                // 运行时初始化失败的恢复出口：不能只显示一行 FAIL 就把用户放进主界面
                Text(
                    "运行时初始化失败，无法执行代码。",
                    style = MaterialTheme.typography.bodyMedium,
                    color = NeonMagenta
                )
                Text(
                    "可尝试：重启应用 / 查看诊断日志 / 反馈给开发者",
                    style = MaterialTheme.typography.bodySmall,
                    color = TextMid,
                    modifier = Modifier.padding(top = 6.dp)
                )
                Spacer(Modifier.height(12.dp))
                com.pyneon.academy.ui.components.NeonButton(
                    label = "重试",
                    accent = NeonCyan,
                    onClick = { bootFailed = false; pyStatus = "RUN" }
                )
                Spacer(Modifier.height(8.dp))
                com.pyneon.academy.ui.components.NeonButton(
                    label = "仍要继续（可能无法运行代码）",
                    accent = TextDim,
                    onClick = { onDone() }
                )
            } else {
                val fraction = if (bootLines.isEmpty()) 0f else shown.toFloat() / bootLines.size
                LinearProgressIndicator(
                    progress = { fraction },
                    modifier = Modifier.fillMaxWidth(),
                    color = NeonCyan,
                    trackColor = NeonCyan.copy(alpha = 0.12f)
                )
            }
        }
        Row(
            Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 12.dp)
        ) {
            Text("完全离线 · 无需网络 · 随时学习", style = MaterialTheme.typography.labelSmall, color = TextDim)
        }
    }
}
