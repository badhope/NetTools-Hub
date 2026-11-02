package com.pyneon.academy.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider

/**
 * 根据 AppTheme 创建 ColorScheme（亮色主题使用 lightColorScheme）
 */
private fun createColorScheme(theme: AppTheme) = if (theme.isLight) {
    lightColorScheme(
        primary = theme.primary,
        onPrimary = theme.background,
        primaryContainer = theme.surfaceHigh,
        onPrimaryContainer = theme.primary,
        secondary = theme.secondary,
        onSecondary = theme.background,
        secondaryContainer = theme.surfaceHigh,
        onSecondaryContainer = theme.secondary,
        tertiary = theme.accent,
        onTertiary = theme.background,
        background = theme.background,
        onBackground = theme.textPrimary,
        surface = theme.surface,
        onSurface = theme.textPrimary,
        surfaceVariant = theme.surfaceHigh,
        onSurfaceVariant = theme.textSecondary,
        outline = theme.textDim,
        error = theme.textDim,
        onError = theme.background
    )
} else {
    darkColorScheme(
        primary = theme.primary,
        onPrimary = theme.background,
        primaryContainer = theme.surfaceHigh,
        onPrimaryContainer = theme.primary,
        secondary = theme.secondary,
        onSecondary = theme.background,
        secondaryContainer = theme.surfaceHigh,
        onSecondaryContainer = theme.secondary,
        tertiary = theme.accent,
        onTertiary = theme.background,
        background = theme.background,
        onBackground = theme.textPrimary,
        surface = theme.surface,
        onSurface = theme.textPrimary,
        surfaceVariant = theme.surfaceHigh,
        onSurfaceVariant = theme.textSecondary,
        outline = theme.textDim,
        error = DarkTokens.danger,
        onError = theme.background
    )
}

/**
 * 默认赛博霓虹主题（保持向后兼容；非组合上下文，直接取深色常量）
 */
private val PyNeonColorScheme = darkColorScheme(
    primary = DarkTokens.primary,
    onPrimary = DarkTokens.bg0,
    primaryContainer = DarkTokens.surfaceHigh,
    onPrimaryContainer = DarkTokens.primary,
    secondary = DarkTokens.secondary,
    onSecondary = DarkTokens.bg0,
    secondaryContainer = DarkTokens.surfaceHigh,
    onSecondaryContainer = DarkTokens.secondary,
    tertiary = DarkTokens.success,
    onTertiary = DarkTokens.bg0,
    background = DarkTokens.bg0,
    onBackground = DarkTokens.textHi,
    surface = DarkTokens.surfaceDark,
    onSurface = DarkTokens.textHi,
    surfaceVariant = DarkTokens.surfaceHigh,
    onSurfaceVariant = DarkTokens.textMid,
    outline = DarkTokens.textDim,
    error = DarkTokens.danger,
    onError = DarkTokens.bg0
)

/**
 * 默认主题（保持向后兼容）
 */
@Composable
fun PyNeonTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = PyNeonColorScheme,
        typography = AppTypography,
        shapes = AppShapes,
        content = content
    )
}

/**
 * 自定义主题（支持动态切换深色/亮色）。
 * 通过 CompositionLocalProvider 同时驱动全局 Token（Bg0/TextHi/NeonCyan…），
 * 使所有界面代码无需感知主题切换。
 */
@Composable
fun PyNeonTheme(
    appTheme: AppTheme,
    visualStyle: VisualStyle = VisualStyle.DEFAULT,
    fontScale: FontScale = FontScale.DEFAULT,
    content: @Composable () -> Unit
) {
    val tokens = appTheme.toNeonTokens()
    CompositionLocalProvider(
        LocalNeonTokens provides tokens,
        LocalVisualStyle provides visualStyle
    ) {
        MaterialTheme(
            colorScheme = createColorScheme(appTheme),
            typography = typographyFor(fontScale),
            shapes = AppShapes,
            content = content
        )
    }
}
