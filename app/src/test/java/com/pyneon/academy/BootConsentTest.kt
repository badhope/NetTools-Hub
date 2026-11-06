package com.pyneon.academy

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.printToString
import androidx.test.core.app.ApplicationProvider
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.pyneon.academy.screens.BootScreen
import com.pyneon.academy.ui.theme.AppThemes
import com.pyneon.academy.ui.theme.PyNeonTheme
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config

/**
 * 启动页在「未同意隐私政策」时必须能正常渲染且不崩溃。
 *
 * 背景（2026-11 发布前审计）：未同意时 BootScreen 会跳过运行时初始化直接
 * onDone，旧实现随后点「同意」不会重跑初始化，导致 Python/SQL 永远不 start。
 * 修复涉及 AppNav 的 consentEpoch + BootScreen 的 retryKey/runCatching，
 * 这里锁住「未同意也能安全渲染」这条基线，避免回归成启动即崩。
 */
@RunWith(AndroidJUnit4::class)
@Config(sdk = [34], qualifiers = "w411dp-h891dp-xhdpi")
class BootConsentTest {

    @get:Rule
    val rule = createComposeRule()

    @Test
    fun bootScreenRendersWithoutConsent() {
        var doneCalled = false
        rule.setContent {
            PyNeonTheme(appTheme = AppThemes.paperLight) {
                BootScreen(consented = false, onDone = { doneCalled = true })
            }
        }
        rule.waitForIdle()
        val tree = rule.onRoot().printToString()
        assertTrue("启动页渲染为空", tree.isNotBlank())
        assertTrue("启动页应有引导文字", tree.contains("初始化执行引擎") || tree.contains("CodeLearning") || tree.contains("码上"))
    }
}
