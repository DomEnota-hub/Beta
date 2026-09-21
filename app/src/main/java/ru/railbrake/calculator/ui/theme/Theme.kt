package ru.railbrake.calculator.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

enum class AccentPalette(val title: String, val primary: Color, val container: Color) {
    BLUE("Холодный синий", Color(0xFF82A9FF), Color(0xFF182947)),
    AMBER("Янтарный", RailAmber, RailAmberSoft),
    GREEN("Стальной зелёный", Color(0xFF68C9A5), Color(0xFF18342C)),
    YELLOW("Сигнальный жёлтый", Color(0xFFFFC857), Color(0xFF3B3017)),
    PURPLE("Холодный фиолетовый", Color(0xFFB9A3E8), Color(0xFF302744))
}

enum class AppThemeMode(val title: String) {
    LIGHT("Светлая"),
    DARK("Тёмная")
}

private fun darkColors(palette: AccentPalette) = darkColorScheme(
    primary = palette.primary,
    onPrimary = Color(0xFF11161B),
    primaryContainer = palette.container,
    onPrimaryContainer = Ink,
    secondary = RailMetal,
    onSecondary = Color(0xFF1C252E),
    secondaryContainer = palette.container,
    onSecondaryContainer = Ink,
    tertiary = Color(0xFF88A7C5),
    onTertiary = Color(0xFF10202E),
    tertiaryContainer = Color(0xFF20303D),
    onTertiaryContainer = Color(0xFFDCECF7),
    background = Night,
    onBackground = Ink,
    surface = NightRaised,
    onSurface = Ink,
    surfaceVariant = palette.container,
    onSurfaceVariant = InkMuted,
    error = Danger,
    errorContainer = Color(0xFF3B1C1E),
    onErrorContainer = Color(0xFFFFDAD9),
    outline = Divider,
    outlineVariant = Color(0xFF222B34)
)

private fun lightPrimary(palette: AccentPalette): Color = when (palette) {
    AccentPalette.BLUE -> Color(0xFF315EA8)
    AccentPalette.AMBER -> Color(0xFF9B4600)
    AccentPalette.GREEN -> Color(0xFF236C54)
    AccentPalette.YELLOW -> Color(0xFF725C00)
    AccentPalette.PURPLE -> Color(0xFF624D91)
}

private fun lightPrimaryContainer(palette: AccentPalette): Color = when (palette) {
    AccentPalette.BLUE -> Color(0xFFD9E2FF)
    AccentPalette.AMBER -> Color(0xFFFFDCC5)
    AccentPalette.GREEN -> Color(0xFFC7EBDD)
    AccentPalette.YELLOW -> Color(0xFFF5E6A7)
    AccentPalette.PURPLE -> Color(0xFFE6DDF7)
}

private fun lightColors(palette: AccentPalette) = lightColorScheme(
    primary = lightPrimary(palette),
    onPrimary = Color.White,
    primaryContainer = lightPrimaryContainer(palette),
    onPrimaryContainer = Color(0xFF172033),
    secondary = Color(0xFF536273),
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFE0E7EF),
    onSecondaryContainer = Color(0xFF17202A),
    tertiary = Color(0xFF4B657C),
    onTertiary = Color.White,
    tertiaryContainer = Color(0xFFDCE8F2),
    onTertiaryContainer = Color(0xFF102331),
    background = Color(0xFFF4F6F8),
    onBackground = Color(0xFF1A1C1E),
    surface = Color(0xFFFCFDFE),
    onSurface = Color(0xFF1A1C1E),
    surfaceVariant = Color(0xFFEAEDF1),
    onSurfaceVariant = Color(0xFF45484E),
    error = Color(0xFFBA1A1A),
    onError = Color.White,
    errorContainer = Color(0xFFFFDAD6),
    onErrorContainer = Color(0xFF410002),
    outline = Color(0xFF74777D),
    outlineVariant = Color(0xFFC4C7CD)
)

@Composable
fun RailBrakeTheme(
    palette: AccentPalette = AccentPalette.BLUE,
    themeMode: AppThemeMode = AppThemeMode.LIGHT,
    content: @Composable () -> Unit
) {
    val isLight = themeMode == AppThemeMode.LIGHT
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = Color.Transparent.toArgb()
            window.navigationBarColor = Color.Transparent.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = isLight
            WindowCompat.getInsetsController(window, view).isAppearanceLightNavigationBars = isLight
        }
    }
    MaterialTheme(
        colorScheme = if (isLight) lightColors(palette) else darkColors(palette),
        content = content
    )
}
