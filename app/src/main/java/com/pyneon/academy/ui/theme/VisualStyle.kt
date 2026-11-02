package com.pyneon.academy.ui.theme

import androidx.compose.runtime.Composable
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.graphics.Shape
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.shape.CutCornerShape

/**
 * 视觉风格（与「配色主题」正交的第二维）。
 *
 * 设计动机：赛博朋克是本项目的默认个性，但它是一种**强视觉语言**——
 * 故障字抖动、扫描线、霓虹渐变描边、切角卡片。对一部分用户（尤其是
 * 长时间阅读课程正文的学习者、或不偏好该审美的用户）这些效果是噪音。
 * 因此把「配色」（7 套主题 + 自定义主色）与「风格」（本枚举）拆成两个独立
 * 开关，用户可以自由组合：
 *
 *   - 赛博霓虹配色 + 赛博风格  → 默认体验
 *   - 白纸配色   + 简洁风格    → 最接近普通阅读器
 *   - 赛博霓虹配色 + 简洁风格  → 保留霓虹配色但不抖动
 *
 * 约定：**风格只管「怎么动、怎么描边、什么形状」，绝不改变色值。**
 * 色值一律来自 [AppTheme] / NeonTokens，避免出现两套色板。
 */
enum class VisualStyle(
    val id: String,
    val label: String,
    val description: String
) {
    /** 默认：故障字、扫描线、霓虹渐变描边、切角卡片、按压回弹 */
    CYBER(
        id = "cyber",
        label = "赛博朋克",
        description = "故障字 · 扫描线 · 霓虹描边 · 切角卡片"
    ),

    /** 简洁：静态文字、无扫描线、细实线描边、圆角卡片、无按压动效 */
    MINIMAL(
        id = "minimal",
        label = "简洁",
        description = "静态排版 · 细描边 · 圆角卡片 · 无动效"
    );

    /** 是否播放故障字抖动 */
    val glitchEnabled: Boolean get() = this == CYBER

    /** 是否绘制扫描线与网格底纹 */
    val backdropEnabled: Boolean get() = this == CYBER

    /** 卡片是否用霓虹渐变描边（false = 细实线） */
    val neonBorderEnabled: Boolean get() = this == CYBER

    /** 按压是否回弹缩放 */
    val pressAnimationEnabled: Boolean get() = this == CYBER

    /** 卡片形状：赛博切角，简洁圆角 */
    val cardShape: Shape
        get() = if (this == CYBER) CutCornerShape(14.dp) else RoundedCornerShape(12.dp)

    companion object {
        val DEFAULT = CYBER

        fun fromId(id: String?): VisualStyle =
            entries.firstOrNull { it.id == id } ?: DEFAULT
    }
}

/**
 * 当前视觉风格。默认值取 [VisualStyle.DEFAULT]，
 * 因此在未包裹 Provider 的场景（预览、独立 Composable 测试）下行为与旧版一致。
 */
val LocalVisualStyle = staticCompositionLocalOf { VisualStyle.DEFAULT }

/**
 * 当前是否为赛博风格。
 *
 * 注意：这是 @Composable 函数而非属性——`LocalVisualStyle.current` 的读取
 * 必须在 Composable 上下文内完成，写成属性 getter 会触发
 * "Functions which invoke @Composable functions must be marked with @Composable"。
 */
@Composable
fun isCyberStyle(): Boolean = LocalVisualStyle.current == VisualStyle.CYBER
