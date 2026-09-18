from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f'Expected block not found: {label}')
    return text.replace(old, new, 1)

# 1. Technical catalog: explicit search clear action.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt'),
]:
    text = path.read_text()
    text = replace_once(
        text,
        'import androidx.compose.material3.HorizontalDivider\n',
        'import androidx.compose.material3.HorizontalDivider\nimport androidx.compose.material3.IconButton\n',
        f'{path}: IconButton import',
    )
    text = replace_once(
        text,
        '''                label = { Text("Поиск по названию, аппарату или признаку") },
                shape = RoundedCornerShape(16.dp)
''',
        '''                label = { Text("Поиск по названию, аппарату или признаку") },
                trailingIcon = {
                    if (query.isNotEmpty()) {
                        IconButton(onClick = { query = "" }) {
                            Text("×", style = MaterialTheme.typography.titleLarge)
                        }
                    }
                },
                shape = RoundedCornerShape(16.dp)
''',
        f'{path}: search field',
    )
    path.write_text(text)

# 2. Restore the original amber palette as a separate option.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt'),
]:
    text = path.read_text()
    text = replace_once(
        text,
        '''    BLUE("Холодный синий", Color(0xFF82A9FF), Color(0xFF182947)),
    GREEN''',
        '''    BLUE("Холодный синий", Color(0xFF82A9FF), Color(0xFF182947)),
    AMBER("Янтарный", RailAmber, RailAmberSoft),
    GREEN''',
        f'{path}: amber palette',
    )
    path.write_text(text)

# 3. User-facing presentation: translate acceptance source metadata that leaked into UI.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt'),
]:
    text = path.read_text()
    text = replace_once(
        text,
        '''    "section-aware applicability" to "Применимость определяется по фактическому исполнению секции",
    "unknown"''',
        '''    "section-aware applicability" to "Применимость определяется по фактическому исполнению секции",
    "applicable acceptance/safety requirements" to "Применимые требования приёмки и безопасности",
    "locomotive inspection duty scope" to "Объём обязанностей при осмотре локомотива",
    "unknown"''',
        f'{path}: acceptance labels',
    )
    path.write_text(text)

# 4. Calculators: persist last axle count, slope and available shoes locally.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt'),
]:
    text = path.read_text()

    text = replace_once(
        text,
        '''private fun MassScreen(
    onHistory: (HistoryRecord) -> Unit,
    onOpenAppendix: (AppendixPrefill) -> Unit,
    onExamQuestionsUnlocked: () -> Unit
) {
    var outputModeName''',
        '''private fun MassScreen(
    onHistory: (HistoryRecord) -> Unit,
    onOpenAppendix: (AppendixPrefill) -> Unit,
    onExamQuestionsUnlocked: () -> Unit
) {
    val context = LocalContext.current
    val inputPrefs = remember { context.getSharedPreferences("calculation_inputs", android.content.Context.MODE_PRIVATE) }
    var outputModeName''',
        f'{path}: MassScreen prefs',
    )
    text = replace_once(
        text,
        '    var directAxles by rememberSaveable { mutableStateOf("") }\n',
        '    var directAxles by rememberSaveable { mutableStateOf(inputPrefs.getString("axles", "").orEmpty()) }\n',
        f'{path}: mass axles initial',
    )
    text = replace_once(
        text,
        '    var slope by rememberSaveable { mutableStateOf(12.0) }\n',
        '    var slope by rememberSaveable { mutableStateOf(inputPrefs.getString("slope", "").orEmpty().toRuDoubleOrNull() ?: 12.0) }\n',
        f'{path}: mass slope initial',
    )
    text = replace_once(
        text,
        '    var availableShoes by rememberSaveable { mutableStateOf("") }\n',
        '    var availableShoes by rememberSaveable { mutableStateOf(inputPrefs.getString("available_shoes", "").orEmpty()) }\n',
        f'{path}: mass shoes initial',
    )
    text = replace_once(
        text,
        'NumericField("Количество учитываемых осей", directAxles, false) { directAxles = it; invalidate() }',
        'NumericField("Количество учитываемых осей", directAxles, false) { directAxles = it; inputPrefs.edit().putString("axles", it).apply(); invalidate() }',
        f'{path}: mass axles save',
    )
    text = replace_once(
        text,
        'onClick = { slope = value; invalidate() },',
        'onClick = { slope = value; inputPrefs.edit().putString("slope", value.toString()).apply(); invalidate() },',
        f'{path}: mass slope save',
    )
    text = replace_once(
        text,
        'NumericField("Доступно тормозных башмаков (например, 16)", availableShoes, false) { availableShoes = it; invalidate() }',
        'NumericField("Доступно тормозных башмаков (например, 16)", availableShoes, false) { availableShoes = it; inputPrefs.edit().putString("available_shoes", it).apply(); invalidate() }',
        f'{path}: mass shoes save',
    )

    text = replace_once(
        text,
        '''private fun AppendixScreen(
    prefill: AppendixPrefill?,
    onHistory: (HistoryRecord) -> Unit
) {
    var axles by rememberSaveable(prefill?.token) { mutableStateOf(prefill?.axleCount?.toString() ?: "") }
''',
        '''private fun AppendixScreen(
    prefill: AppendixPrefill?,
    onHistory: (HistoryRecord) -> Unit
) {
    val context = LocalContext.current
    val inputPrefs = remember { context.getSharedPreferences("calculation_inputs", android.content.Context.MODE_PRIVATE) }
    var axles by rememberSaveable(prefill?.token) { mutableStateOf(prefill?.axleCount?.toString() ?: inputPrefs.getString("axles", "").orEmpty()) }
''',
        f'{path}: AppendixScreen prefs',
    )
    text = replace_once(
        text,
        '    var slope by rememberSaveable { mutableStateOf("8") }\n',
        '    var slope by rememberSaveable { mutableStateOf(inputPrefs.getString("slope", "8").orEmpty()) }\n',
        f'{path}: appendix slope initial',
    )
    text = replace_once(
        text,
        '    var availableShoes by rememberSaveable { mutableStateOf("") }\n',
        '    var availableShoes by rememberSaveable { mutableStateOf(inputPrefs.getString("available_shoes", "").orEmpty()) }\n',
        f'{path}: appendix shoes initial',
    )
    text = replace_once(
        text,
        'NumericField("Количество осей", axles, false) { axles = it; result = null }',
        'NumericField("Количество осей", axles, false) { axles = it; inputPrefs.edit().putString("axles", it).apply(); result = null }',
        f'{path}: appendix axles save',
    )
    text = replace_once(
        text,
        'NumericField("Уклон, ‰", slope, true) { slope = it; result = null }',
        'NumericField("Уклон, ‰", slope, true) { slope = it; inputPrefs.edit().putString("slope", it).apply(); result = null }',
        f'{path}: appendix slope save',
    )
    text = replace_once(
        text,
        'NumericField("Доступно тормозных башмаков (например, 16)", availableShoes, false) { availableShoes = it; result = null }',
        'NumericField("Доступно тормозных башмаков (например, 16)", availableShoes, false) { availableShoes = it; inputPrefs.edit().putString("available_shoes", it).apply(); result = null }',
        f'{path}: appendix shoes save',
    )

    text = replace_once(
        text,
        '''                    AccentPalette.BLUE -> "Классический холодный синий акцент приложения"
                    AccentPalette.GREEN ->''',
        '''                    AccentPalette.BLUE -> "Классический холодный синий акцент приложения"
                    AccentPalette.AMBER -> "Тёплый янтарный акцент прежнего оформления"
                    AccentPalette.GREEN ->''',
        f'{path}: amber settings description',
    )
    path.write_text(text)

# Version this polish package as Beta12.
for path in [Path('app/build.gradle.kts'), Path('patch/app/build.gradle.kts')]:
    text = path.read_text()
    text = replace_once(text, 'versionCode = 156', 'versionCode = 157', f'{path}: versionCode')
    text = replace_once(text, 'versionName = "1.2.2-dev14-beta11"', 'versionName = "1.2.2-dev14-beta12"', f'{path}: versionName')
    path.write_text(text)

# Sanity checks.
assert 'IconButton(onClick = { query = "" })' in Path('app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt').read_text()
assert 'AMBER("Янтарный", RailAmber, RailAmberSoft)' in Path('app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt').read_text()
assert 'applicable acceptance/safety requirements" to "Применимые требования приёмки и безопасности' in Path('app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt').read_text()
assert 'getSharedPreferences("calculation_inputs"' in Path('app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt').read_text()
