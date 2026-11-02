package com.pyneon.academy.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val AppTypography = Typography(
    // 标题/标签保留等宽字以维持赛博视觉；正文改用系统无衬线并放大，保证长文阅读清晰
    headlineLarge = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 30.sp, lineHeight = 38.sp),
    headlineMedium = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 24.sp, lineHeight = 32.sp),
    headlineSmall = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 20.sp, lineHeight = 28.sp),
    titleLarge = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 18.sp, lineHeight = 26.sp),
    titleMedium = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 15.sp, lineHeight = 22.sp),
    bodyLarge = TextStyle(fontSize = 16.sp, lineHeight = 25.sp),
    bodyMedium = TextStyle(fontSize = 14.sp, lineHeight = 22.sp),
    bodySmall = TextStyle(fontSize = 12.sp, lineHeight = 18.sp),
    labelLarge = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 13.sp, lineHeight = 20.sp),
    labelMedium = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 12.sp, lineHeight = 18.sp),
    labelSmall = TextStyle(fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Bold, fontSize = 10.sp, lineHeight = 15.sp)
)

/**
 * 代码专用样式：等宽字体保证缩进/对齐精确（代码块、编辑器、终端、输出统一使用）。
 * 字号取整、行高与字号成比例，避免 Compose 在不同字体下的间距抖动。
 */
val MonoCode = TextStyle(
    fontFamily = FontFamily.Monospace,
    fontSize = 14.sp,
    lineHeight = 21.sp
)

/**
 * 字号缩放档位（可访问性）。
 *
 * 为什么需要：课程正文是长文阅读，默认 16sp 对一部分用户偏小；而系统级字体
 * 缩放会让等宽代码块错位。因此提供应用内三档缩放，只放大**阅读类文本**
 * （正文/标题/标签），代码块与编辑器保持原始字号——保证缩进与对齐不被破坏。
 */
enum class FontScale(val id: String, val label: String, val factor: Float) {
    COMPACT("compact", "紧凑", 0.9f),
    NORMAL("normal", "标准", 1.0f),
    COMFORT("comfort", "舒适", 1.15f),
    LARGE("large", "大字", 1.3f);

    companion object {
        val DEFAULT = NORMAL
        fun fromId(id: String?): FontScale = entries.firstOrNull { it.id == id } ?: DEFAULT
    }
}

/**
 * 按缩放档位生成排版。只缩放非等宽（阅读类）文本的字号与行高；
 * 等宽标题保持原样以避免布局抖动。
 */
fun typographyFor(scale: FontScale): Typography {
    if (scale == FontScale.NORMAL) return AppTypography
    val f = scale.factor
    fun TextStyle.scaled(): TextStyle = copy(
        fontSize = (fontSize.value * f).sp,
        lineHeight = (lineHeight.value * f).sp
    )
    // 只放大正文与小型标签；等宽标题（headline/title/label*）不动，
    // 否则中文标题在窄屏会换行错位
    return AppTypography.copy(
        bodyLarge = AppTypography.bodyLarge.scaled(),
        bodyMedium = AppTypography.bodyMedium.scaled(),
        bodySmall = AppTypography.bodySmall.scaled()
    )
}
