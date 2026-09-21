package ru.railbrake.calculator

import android.content.Context
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.core.view.WindowCompat
import ru.railbrake.calculator.ui.BrakeCalculatorApp
import ru.railbrake.calculator.ui.theme.AccentPalette
import ru.railbrake.calculator.ui.theme.AppThemeMode
import ru.railbrake.calculator.ui.theme.RailBrakeTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        WindowCompat.setDecorFitsSystemWindows(window, false)

        setContent {
            val preferences = remember {
                getSharedPreferences("calculation_inputs", Context.MODE_PRIVATE)
            }
            var palette by remember {
                mutableStateOf(
                    runCatching {
                        AccentPalette.valueOf(
                            preferences.getString("accent_palette", AccentPalette.BLUE.name)
                                ?: AccentPalette.BLUE.name
                        )
                    }.getOrDefault(AccentPalette.BLUE)
                )
            }
            var themeMode by remember {
                mutableStateOf(
                    runCatching {
                        AppThemeMode.valueOf(
                            preferences.getString("theme_mode", AppThemeMode.LIGHT.name)
                                ?: AppThemeMode.LIGHT.name
                        )
                    }.getOrDefault(AppThemeMode.LIGHT)
                )
            }

            RailBrakeTheme(palette = palette, themeMode = themeMode) {
                BrakeCalculatorApp(
                    palette = palette,
                    onPaletteChange = { selected ->
                        palette = selected
                        preferences.edit().putString("accent_palette", selected.name).apply()
                    },
                    themeMode = themeMode,
                    onThemeModeChange = { selected ->
                        themeMode = selected
                        preferences.edit().putString("theme_mode", selected.name).apply()
                    }
                )
            }
        }
    }
}
