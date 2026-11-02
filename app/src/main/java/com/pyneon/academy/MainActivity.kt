package com.pyneon.academy

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import com.pyneon.academy.nav.AppRoot
import com.pyneon.academy.ui.theme.PyNeonTheme
import com.pyneon.academy.utils.ThemePreference

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            var currentTheme by remember { mutableStateOf(ThemePreference.getCurrentTheme(this)) }
            var visualStyle by remember { mutableStateOf(ThemePreference.getVisualStyle(this)) }
            var fontScale by remember { mutableStateOf(ThemePreference.getFontScale(this)) }
            // 主题 / 风格偏好变更即时生效（SharedPreferences 监听，无需重启应用）
            DisposableEffect(Unit) {
                val listener =
                    android.content.SharedPreferences.OnSharedPreferenceChangeListener { _, key ->
                        when (key) {
                            ThemePreference.KEY_THEME_ID ->
                                currentTheme = ThemePreference.getCurrentTheme(this@MainActivity)
                            ThemePreference.KEY_VISUAL_STYLE ->
                                visualStyle = ThemePreference.getVisualStyle(this@MainActivity)
                            ThemePreference.KEY_FONT_SCALE ->
                                fontScale = ThemePreference.getFontScale(this@MainActivity)
                        }
                    }
                ThemePreference.registerListener(this@MainActivity, listener)
                onDispose { ThemePreference.unregisterListener(this@MainActivity, listener) }
            }
            PyNeonTheme(appTheme = currentTheme, visualStyle = visualStyle, fontScale = fontScale) {
                AppRoot()
            }
        }
    }
}
