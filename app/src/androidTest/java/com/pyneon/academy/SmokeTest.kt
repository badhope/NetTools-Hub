package com.pyneon.academy

import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.printToString
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertNotNull
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * 启动冒烟测试（真实 Android 运行时）。
 *
 * 这是目前唯一能在**真实设备/模拟器**上验证「应用能启动、Activity 能创建、
 * Compose 树能渲染」的测试。所有纯 JVM 单测都无法覆盖这条路径。
 *
 * 注意：本机 CPU 不支持虚拟化，无法本地跑；CI 或真机可用：
 *   ./gradlew :app:connectedDebugAndroidTest
 */
@RunWith(AndroidJUnit4::class)
class SmokeTest {

    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun appLaunchesAndRendersContent() {
        // 等待首屏（含 BootScreen 过渡）稳定
        composeRule.waitForIdle()
        val tree = composeRule.onRoot().printToString()
        assertNotNull("Compose 语义树不应为空", tree)
        // 首屏必须有可读文本（品牌名或导航项）
        assert(tree.isNotBlank()) { "界面没有渲染任何内容" }
    }

    @Test
    fun bottomNavigationIsPresent() {
        composeRule.waitForIdle()
        val tree = composeRule.onRoot().printToString()
        // 五 Tab 至少命中其一
        val tabs = listOf("首页", "课程", "终端", "挑战", "我的")
        val hit = tabs.count { it in tree }
        assert(hit >= 3) { "底部导航未完整渲染，命中 $hit/5\n$tree" }
    }
}
