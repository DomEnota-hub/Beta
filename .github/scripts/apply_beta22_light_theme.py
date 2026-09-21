from pathlib import Path

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


# ---------------------------------------------------------------------------
# Theme: add first-class light/dark modes. Light is the product default.
# ---------------------------------------------------------------------------
theme = '''package ru.railbrake.calculator.ui.theme

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
'''
for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt',
]:
    write(path, theme)


# ---------------------------------------------------------------------------
# MainActivity: persist accent + theme in the existing calculation_inputs
# SharedPreferences. This keeps the historical accent key and introduces
# theme_mode with LIGHT as the migration/default value.
# ---------------------------------------------------------------------------
main_activity = '''package ru.railbrake.calculator

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
'''
for path in [
    'app/src/main/java/ru/railbrake/calculator/MainActivity.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/MainActivity.kt',
]:
    write(path, main_activity)


# ---------------------------------------------------------------------------
# Settings screen: expose theme independently from accent palette.
# ---------------------------------------------------------------------------
for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt',
]:
    text = read(path)
    if 'import ru.railbrake.calculator.ui.theme.AppThemeMode\n' not in text:
        text = replace_once(
            text,
            'import ru.railbrake.calculator.ui.theme.AccentPalette\n',
            'import ru.railbrake.calculator.ui.theme.AccentPalette\nimport ru.railbrake.calculator.ui.theme.AppThemeMode\n',
            f'{path}: AppThemeMode import',
        )

    text = replace_once(
        text,
        '''fun BrakeCalculatorApp(\n    palette: AccentPalette,\n    onPaletteChange: (AccentPalette) -> Unit\n) {''',
        '''fun BrakeCalculatorApp(\n    palette: AccentPalette,\n    onPaletteChange: (AccentPalette) -> Unit,\n    themeMode: AppThemeMode,\n    onThemeModeChange: (AppThemeMode) -> Unit\n) {''',
        f'{path}: BrakeCalculatorApp signature',
    )

    text = replace_once(
        text,
        'PaletteScreen(palette, onPaletteChange)',
        'PaletteScreen(palette, onPaletteChange, themeMode, onThemeModeChange)',
        f'{path}: PaletteScreen call',
    )

    text = replace_once(
        text,
        '''private fun PaletteScreen(\n    palette: AccentPalette,\n    onPaletteChange: (AccentPalette) -> Unit\n) {''',
        '''private fun PaletteScreen(\n    palette: AccentPalette,\n    onPaletteChange: (AccentPalette) -> Unit,\n    themeMode: AppThemeMode,\n    onThemeModeChange: (AppThemeMode) -> Unit\n) {''',
        f'{path}: PaletteScreen signature',
    )

    text = replace_once(
        text,
        '    SectionCard("Оформление", "Графитовая основа постоянна; меняется только рабочий акцент") {',
        '''    SectionCard("Тема", "Светлая используется по умолчанию") {\n        ChoiceRow(\n            options = AppThemeMode.entries.map { it.title },\n            selectedIndex = AppThemeMode.entries.indexOf(themeMode),\n            onSelect = { index -> onThemeModeChange(AppThemeMode.entries[index]) }\n        )\n    }\n    SectionCard("Цветовой акцент", "Выбранный цвет работает независимо от светлой или тёмной темы") {''',
        f'{path}: appearance section',
    )

    text = replace_once(
        text,
        '    RailInfoBand("Графитовая основа постоянна; выбранная палитра меняет рабочий акцент. Красный зарезервирован для опасности и ОПП.")',
        '    RailInfoBand("Тема и цветовой акцент настраиваются независимо. Красный по-прежнему зарезервирован для опасности и ОПП.")',
        f'{path}: info band',
    )
    write(path, text)


# ---------------------------------------------------------------------------
# Dark interactive schemes remain intentionally dark inside either app theme.
# Give them their own content colors; replace black hyperlink borders with the
# theme outline so light mode does not look overly heavy.
# ---------------------------------------------------------------------------
for path in [
    'app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt',
]:
    text = read(path)
    text = text.replace(
        'BorderStroke(1.dp, Color.Black)',
        'BorderStroke(1.dp, MaterialTheme.colorScheme.outline)',
    )
    text = text.replace(
        'CardDefaults.cardColors(containerColor = InteractiveSchemeContainer)',
        'CardDefaults.cardColors(containerColor = InteractiveSchemeContainer, contentColor = InteractiveSchemeOnSurface)',
    )
    text = text.replace(
        'CardDefaults.cardColors(containerColor = if (interactive) InteractiveSchemeContainer else technicalSectionContainer(entry.section))',
        'CardDefaults.cardColors(\n                    containerColor = if (interactive) InteractiveSchemeContainer else technicalSectionContainer(entry.section),\n                    contentColor = if (interactive) InteractiveSchemeOnSurface else MaterialTheme.colorScheme.onSurface\n                )',
    )
    text = text.replace(
        'Text(shortcut.subtitle, color = MaterialTheme.colorScheme.onSurfaceVariant)',
        'Text(shortcut.subtitle, color = InteractiveSchemeMuted)',
    )
    text = text.replace(
        '''color = MaterialTheme.colorScheme.onSurfaceVariant,\n                            maxLines = if (entry.family == TechnicalFamily.ERMAK) 2 else Int.MAX_VALUE,''',
        '''color = if (interactive) InteractiveSchemeMuted else MaterialTheme.colorScheme.onSurfaceVariant,\n                            maxLines = if (entry.family == TechnicalFamily.ERMAK) 2 else Int.MAX_VALUE,''',
        1,
    )
    text = replace_once(
        text,
        '''private val InteractiveSchemeContainer = Color(0xFF17363A)\nprivate val InteractiveSchemeAccent = Color(0xFF65E3D2)''',
        '''private val InteractiveSchemeContainer = Color(0xFF17363A)\nprivate val InteractiveSchemeAccent = Color(0xFF65E3D2)\nprivate val InteractiveSchemeOnSurface = Color(0xFFF0F6F5)\nprivate val InteractiveSchemeMuted = Color(0xFFB8CCC9)''',
        f'{path}: interactive scheme colors',
    )
    write(path, text)


# ---------------------------------------------------------------------------
# Beta22 identity.
# ---------------------------------------------------------------------------
for path in ['app/build.gradle.kts', 'patch/app/build.gradle.kts']:
    text = read(path)
    text = replace_once(
        text,
        '// Beta21: compact progressive-disclosure presentation for Ermak.',
        '// Beta22: first-class light/dark theme with light mode as default.',
        f'{path}: beta comment',
    )
    text = replace_once(text, 'versionCode = 166', 'versionCode = 167', f'{path}: versionCode')
    text = replace_once(
        text,
        'versionName = "1.2.2-dev14-beta21"',
        'versionName = "1.2.2-dev14-beta22"',
        f'{path}: versionName',
    )
    write(path, text)

# Hard assertions for the intended contract.
for path in [
    'app/src/main/java/ru/railbrake/calculator/MainActivity.kt',
    'patch/app/src/main/java/ru/railbrake/calculator/MainActivity.kt',
]:
    value = read(path)
    assert 'AppThemeMode.LIGHT' in value
    assert 'theme_mode' in value

assert read('app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt') == read('patch/app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt')
assert read('app/src/main/java/ru/railbrake/calculator/MainActivity.kt') == read('patch/app/src/main/java/ru/railbrake/calculator/MainActivity.kt')
assert read('app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt') == read('patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt')
assert read('app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt') == read('patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt')
assert read('app/build.gradle.kts') == read('patch/app/build.gradle.kts')

print('Beta22 light/dark theme patch applied successfully')
