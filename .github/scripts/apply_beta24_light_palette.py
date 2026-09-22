from pathlib import Path
import re

ROOT = Path('.')


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding='utf-8')


def write(path: str, text: str) -> None:
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one occurrence, found {count}')
    return text.replace(old, new, 1)


def regex_replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one regex match, found {count}')
    return updated


# ---------------------------------------------------------------------------
# Theme: light mode gets its own stronger palette tokens and semantic colors.
# Dark mode intentionally keeps the established visual identity.
# ---------------------------------------------------------------------------
theme = '''package ru.railbrake.calculator.ui.theme

import android.app.Activity
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.Immutable
import androidx.compose.runtime.ReadOnlyComposable
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.staticCompositionLocalOf
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

@Immutable
data class RailSemanticColors(
    val info: Color,
    val infoContainer: Color,
    val infoBorder: Color,
    val warning: Color,
    val warningContainer: Color,
    val warningBorder: Color,
    val success: Color,
    val successContainer: Color,
    val successBorder: Color,
    val disabledContent: Color
)

private val LocalRailSemanticColors = staticCompositionLocalOf {
    RailSemanticColors(
        info = Accent,
        infoContainer = AccentSoft,
        infoBorder = Accent.copy(alpha = 0.42f),
        warning = Warning,
        warningContainer = Warning.copy(alpha = 0.08f),
        warningBorder = Warning.copy(alpha = 0.32f),
        success = Success,
        successContainer = Success.copy(alpha = 0.10f),
        successBorder = Success.copy(alpha = 0.38f),
        disabledContent = RailSteel
    )
}

object RailTheme {
    val colors: RailSemanticColors
        @Composable
        @ReadOnlyComposable
        get() = LocalRailSemanticColors.current
}

private data class LightAccentTokens(
    val primary: Color,
    val container: Color
)

private fun lightAccentTokens(palette: AccentPalette): LightAccentTokens = when (palette) {
    AccentPalette.BLUE -> LightAccentTokens(Color(0xFF1D5FAE), Color(0xFFDCE8FF))
    AccentPalette.AMBER -> LightAccentTokens(Color(0xFFA34B00), Color(0xFFFFE0C2))
    AccentPalette.GREEN -> LightAccentTokens(Color(0xFF1B7354), Color(0xFFD1F0E3))
    AccentPalette.YELLOW -> LightAccentTokens(Color(0xFF765C00), Color(0xFFFFEFA8))
    AccentPalette.PURPLE -> LightAccentTokens(Color(0xFF69499E), Color(0xFFEADFFA))
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

private fun lightColors(palette: AccentPalette) = lightAccentTokens(palette).let { accent ->
    lightColorScheme(
        primary = accent.primary,
        onPrimary = Color.White,
        primaryContainer = accent.container,
        onPrimaryContainer = Color(0xFF172033),
        secondary = Color(0xFF4A5B6E),
        onSecondary = Color.White,
        secondaryContainer = Color(0xFFDCE4ED),
        onSecondaryContainer = Color(0xFF17202A),
        tertiary = Color(0xFF425F77),
        onTertiary = Color.White,
        tertiaryContainer = Color(0xFFD8E7F2),
        onTertiaryContainer = Color(0xFF102331),
        background = Color(0xFFF4F6F8),
        onBackground = Color(0xFF191C20),
        surface = Color(0xFFFDFDFE),
        onSurface = Color(0xFF191C20),
        surfaceVariant = Color(0xFFE9EDF1),
        onSurfaceVariant = Color(0xFF3F454C),
        error = Color(0xFFB3261E),
        onError = Color.White,
        errorContainer = Color(0xFFFFDAD6),
        onErrorContainer = Color(0xFF410002),
        outline = Color(0xFF676D75),
        outlineVariant = Color(0xFFB7BCC4)
    )
}

private fun darkSemanticColors(palette: AccentPalette) = RailSemanticColors(
    info = palette.primary,
    infoContainer = palette.container,
    infoBorder = palette.primary.copy(alpha = 0.42f),
    warning = Warning,
    warningContainer = Warning.copy(alpha = 0.08f),
    warningBorder = Warning.copy(alpha = 0.32f),
    success = Success,
    successContainer = Success.copy(alpha = 0.10f),
    successBorder = Success.copy(alpha = 0.38f),
    disabledContent = RailSteel
)

private fun lightSemanticColors(palette: AccentPalette): RailSemanticColors {
    val accent = lightAccentTokens(palette)
    return RailSemanticColors(
        info = accent.primary,
        infoContainer = accent.container.copy(alpha = 0.72f),
        infoBorder = accent.primary.copy(alpha = 0.58f),
        warning = Color(0xFF984600),
        warningContainer = Color(0xFFFFF0DF),
        warningBorder = Color(0xFFD47B27),
        success = Color(0xFF176A4B),
        successContainer = Color(0xFFE0F4EB),
        successBorder = Color(0xFF65AA8F),
        disabledContent = Color(0xFF68717A)
    )
}

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
    CompositionLocalProvider(
        LocalRailSemanticColors provides if (isLight) lightSemanticColors(palette) else darkSemanticColors(palette)
    ) {
        MaterialTheme(
            colorScheme = if (isLight) lightColors(palette) else darkColors(palette),
            content = content
        )
    }
}
'''

for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt',
]:
    write(path, theme)


# ---------------------------------------------------------------------------
# Shared design components: use semantic info colors rather than dark-theme
# constants so borders/containers remain visible on the light background.
# ---------------------------------------------------------------------------
for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/RailDesign.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/RailDesign.kt',
]:
    text = read(path)
    text = replace_once(
        text,
        'import ru.railbrake.calculator.ui.theme.RailMetal\n',
        'import ru.railbrake.calculator.ui.theme.RailTheme\n',
        f'{path}: semantic theme import',
    )
    text = regex_replace_once(
        text,
        r'@Composable\ninternal fun RailInfoBand\(text: String\) \{.*?\n\}',
        '''@Composable
internal fun RailInfoBand(text: String) {
    val colors = RailTheme.colors
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(14.dp),
        color = colors.infoContainer,
        border = BorderStroke(1.dp, colors.infoBorder)
    ) {
        Text(
            text,
            modifier = Modifier.padding(12.dp),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}''',
        f'{path}: RailInfoBand',
    )
    write(path, text)


# ---------------------------------------------------------------------------
# Calculation UI: migrate warnings/results to semantic tokens. This fixes the
# pale III.4 notice and makes the same components correct in both themes.
# ---------------------------------------------------------------------------
for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt',
]:
    text = read(path)
    text = replace_once(
        text,
        'import ru.railbrake.calculator.ui.theme.Success\nimport ru.railbrake.calculator.ui.theme.Warning\n',
        'import ru.railbrake.calculator.ui.theme.RailTheme\n',
        f'{path}: semantic theme import',
    )
    text = regex_replace_once(
        text,
        r'@Composable\nprivate fun HeroResult\(title: String, subtitle: String, success: Boolean\) \{.*?\n\}\n\n@Composable\nprivate fun StatusText',
        '''@Composable
private fun HeroResult(title: String, subtitle: String, success: Boolean) {
    val colors = RailTheme.colors
    val accent = if (success) colors.success else colors.warning
    val container = if (success) colors.successContainer else colors.warningContainer
    val border = if (success) colors.successBorder else colors.warningBorder
    Surface(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(24.dp),
        color = container,
        border = BorderStroke(1.dp, border)
    ) {
        Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
            Text(title, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Black, color = accent)
            Text(subtitle, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun StatusText''',
        f'{path}: HeroResult',
    )
    text = regex_replace_once(
        text,
        r'@Composable\nprivate fun StatusText\(text: String, success: Boolean\) \{.*?\n\}',
        '''@Composable
private fun StatusText(text: String, success: Boolean) {
    val colors = RailTheme.colors
    Text(
        text,
        style = MaterialTheme.typography.bodyMedium,
        fontWeight = FontWeight.SemiBold,
        color = if (success) colors.success else colors.warning
    )
}''',
        f'{path}: StatusText',
    )
    text = regex_replace_once(
        text,
        r'@Composable\nprivate fun WarningBox\(text: String\) \{.*?\n\}',
        '''@Composable
private fun WarningBox(text: String) {
    val colors = RailTheme.colors
    Surface(
        shape = RoundedCornerShape(15.dp),
        color = colors.warningContainer,
        border = BorderStroke(1.dp, colors.warningBorder)
    ) {
        Text(
            text,
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            style = MaterialTheme.typography.bodySmall,
            color = colors.warning
        )
    }
}''',
        f'{path}: WarningBox',
    )
    text = text.replace('color = Warning, maxLines = 1', 'color = RailTheme.colors.warning, maxLines = 1')
    if ' color = Warning' in text or ' Success' in text:
        raise SystemExit(f'{path}: old fixed semantic colors remain')
    write(path, text)


# ---------------------------------------------------------------------------
# Beta24 identity.
# ---------------------------------------------------------------------------
for path in ['app/build.gradle.kts', 'patch/app/build.gradle.kts']:
    text = read(path)
    text = replace_once(
        text,
        '// Beta23: improve contrast of dark interactive atlas controls in light mode.',
        '// Beta24: dedicated light-theme palette and semantic contrast tokens.',
        f'{path}: beta comment',
    )
    text = replace_once(text, 'versionCode = 168', 'versionCode = 169', f'{path}: versionCode')
    text = replace_once(
        text,
        'versionName = "1.2.2-dev14-beta23"',
        'versionName = "1.2.2-dev14-beta24"',
        f'{path}: versionName',
    )
    write(path, text)


# Contract assertions.
for left, right in [
    ('app/build.gradle.kts', 'patch/app/build.gradle.kts'),
    ('app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt', 'patch/app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt'),
    ('app/src/main/java/ru/railbrake/calculator/ui/RailDesign.kt', 'patch/app/src/main/java/ru/railbrake/calculator/ui/RailDesign.kt'),
    ('app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt', 'patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt'),
]:
    if read(left) != read(right):
        raise SystemExit(f'mirror mismatch: {left} != {right}')

assert 'RailSemanticColors' in read('app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt')
assert 'warningContainer = Color(0xFFFFF0DF)' in read('app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt')
assert 'RailTheme.colors' in read('app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt')
assert 'versionName = "1.2.2-dev14-beta24"' in read('app/build.gradle.kts')
