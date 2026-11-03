package com.pyneon.academy.utils

import android.content.Context
import android.content.SharedPreferences
import com.pyneon.academy.ui.theme.AppTheme
import com.pyneon.academy.ui.theme.AppThemes
import com.pyneon.academy.ui.theme.FontScale
import com.pyneon.academy.ui.theme.VisualStyle

/**
 * 主题偏好管理器
 * 使用 SharedPreferences 存储用户选择的主题
 *
 * 两个正交维度，可自由组合：
 *  - 配色主题（[KEY_THEME_ID] / 自定义主色）：决定色值
 *  - 视觉风格（[KEY_VISUAL_STYLE]）：决定动效、描边、形状
 */
object ThemePreference {
    private const val PREFS_NAME = "pyneon_theme"
    const val KEY_THEME_ID = "theme_id"
    const val KEY_CUSTOM_COLOR = "custom_color"
    const val KEY_VISUAL_STYLE = "visual_style"
    const val KEY_FONT_SCALE = "font_scale"

    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    }

    /**
     * 注册主题偏好监听（供 MainActivity 实现即时切换，无需重启）
     */
    fun registerListener(context: Context, listener: SharedPreferences.OnSharedPreferenceChangeListener) {
        getPrefs(context).registerOnSharedPreferenceChangeListener(listener)
    }

    fun unregisterListener(context: Context, listener: SharedPreferences.OnSharedPreferenceChangeListener) {
        getPrefs(context).unregisterOnSharedPreferenceChangeListener(listener)
    }

    /**
     * 获取当前主题（自定义 id 时按用户主色实时生成）
     */
    fun getCurrentTheme(context: Context): AppTheme {
        val themeId = getCurrentThemeId(context)
        return if (themeId == AppThemes.CUSTOM_THEME_ID) {
            AppThemes.customTheme(getCustomColor(context))
        } else {
            AppThemes.getThemeById(themeId)
        }
    }

    /**
     * 保存主题选择
     */
    fun saveTheme(context: Context, themeId: String) {
        getPrefs(context).edit().putString(KEY_THEME_ID, themeId).apply()
    }

    /**
     * 获取当前主题 ID
     */
    /**
     * 默认主题：白纸模式（亮色）。
     *
     * 2026-11 决策：默认亮色，因为长文阅读场景下亮底更省眼、更接近常见阅读器；
     * 赛博霓虹仍完整保留，用户在「我的 → 配色主题」一键切回。
     * 首次安装取 [DEFAULT_THEME_ID]；已选过主题的用户不受影响。
     */
    fun getCurrentThemeId(context: Context): String {
        return getPrefs(context).getString(KEY_THEME_ID, DEFAULT_THEME_ID) ?: DEFAULT_THEME_ID
    }

    /** 首次安装的默认主题 id */
    const val DEFAULT_THEME_ID = "paper_light"

    /** 获取自定义主色（hex，如 "#00E5FF"） */
    fun getCustomColor(context: Context): String {
        return getPrefs(context).getString(KEY_CUSTOM_COLOR, "#00E5FF") ?: "#00E5FF"
    }

    /** 保存自定义主色 */
    fun saveCustomColor(context: Context, hex: String) {
        getPrefs(context).edit().putString(KEY_CUSTOM_COLOR, hex).apply()
    }

    // ===== 视觉风格（与配色正交） =====

    /** 当前视觉风格；未设置过时取默认（赛博朋克），保证老用户升级后观感不变 */
    fun getVisualStyle(context: Context): VisualStyle =
        VisualStyle.fromId(getPrefs(context).getString(KEY_VISUAL_STYLE, null))

    /** 保存视觉风格 */
    fun saveVisualStyle(context: Context, style: VisualStyle) {
        getPrefs(context).edit().putString(KEY_VISUAL_STYLE, style.id).apply()
    }

    // ===== 字号缩放（可访问性） =====

    /** 当前字号档位；未设置时取标准档，老用户观感不变 */
    fun getFontScale(context: Context): FontScale =
        FontScale.fromId(getPrefs(context).getString(KEY_FONT_SCALE, null))

    fun saveFontScale(context: Context, scale: FontScale) {
        getPrefs(context).edit().putString(KEY_FONT_SCALE, scale.id).apply()
    }
}
