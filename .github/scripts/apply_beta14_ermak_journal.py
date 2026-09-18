from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f'Expected block not found: {label}')
    return text.replace(old, new, 1)

# Shared diagnostic-session storage: add profile filtering and profile-scoped clearing.
patch_repo = Path('patch/app/src/main/java/ru/railbrake/calculator/data/DiagnosticSessionRepository.kt')
repo_text = patch_repo.read_text()
repo_text = replace_once(
    repo_text,
    '''    fun add(record: DiagnosticSessionRecord) {
        val next = (load() + record)
            .distinctBy { it.timestampMillis }
            .take(MAX)
        prefs.edit().putStringSet(KEY, next.map(::encode).toSet()).apply()
    }

    fun clear() = prefs.edit().remove(KEY).apply()
''',
    '''    fun add(record: DiagnosticSessionRecord) {
        val next = (load() + record)
            .distinctBy { it.timestampMillis }
            .take(MAX)
        prefs.edit().putStringSet(KEY, next.map(::encode).toSet()).apply()
    }

    fun loadForProfile(profileId: String): List<DiagnosticSessionRecord> =
        load().filter { it.profileId == profileId }

    fun clearProfile(profileId: String) {
        val kept = load().filterNot { it.profileId == profileId }
        if (kept.isEmpty()) prefs.edit().remove(KEY).apply()
        else prefs.edit().putStringSet(KEY, kept.map(::encode).toSet()).apply()
    }

    fun clear() = prefs.edit().remove(KEY).apply()
''',
    'DiagnosticSessionRepository profile helpers',
)
repo_text = replace_once(
    repo_text,
    '''    companion object {
        private const val KEY = "records"
        private const val MAX = 100
    }
''',
    '''    companion object {
        const val PROFILE_VL80S = "vl80s"
        const val PROFILE_ERMAK = "ermak"
        const val VARIANT_ERMAK_GENERAL = "ermak-general"

        private const val KEY = "records"
        private const val MAX = 100
    }
''',
    'DiagnosticSessionRepository profile constants',
)
patch_repo.write_text(repo_text)
root_repo = Path('app/src/main/java/ru/railbrake/calculator/data/DiagnosticSessionRepository.kt')
root_repo.parent.mkdir(parents=True, exist_ok=True)
root_repo.write_text(repo_text)

# Keep the VL80S journal visually scoped to VL80S even though storage is shared.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt'),
]:
    text = path.read_text()
    text = replace_once(
        text,
        '    val sessions = remember(historyVersion) { sessionRepository.load() }\n',
        '    val sessions = remember(historyVersion) { sessionRepository.loadForProfile(DiagnosticSessionRepository.PROFILE_VL80S) }\n',
        f'{path}: VL80S journal filter',
    )
    text = replace_once(
        text,
        'if (sessions.isNotEmpty()) TextButton(onClick = { sessionRepository.clear(); historyVersion++ }) { Text("Очистить") }',
        'if (sessions.isNotEmpty()) TextButton(onClick = { sessionRepository.clearProfile(DiagnosticSessionRepository.PROFILE_VL80S); historyVersion++ }) { Text("Очистить") }',
        f'{path}: VL80S journal scoped clear',
    )
    path.write_text(text)

# Ermak: add its own journal tab and explicit session saving at the end of a route.
for path in [
    Path('app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt'),
]:
    text = path.read_text()
    text = replace_once(text, 'import androidx.compose.foundation.lazy.LazyColumn\n', 'import androidx.compose.foundation.lazy.LazyColumn\nimport androidx.compose.foundation.lazy.LazyRow\n', f'{path}: LazyRow import')
    text = replace_once(text, 'import androidx.compose.material3.CircularProgressIndicator\n', 'import androidx.compose.material3.CircularProgressIndicator\nimport androidx.compose.material3.FilterChip\n', f'{path}: FilterChip import')
    text = replace_once(
        text,
        'import ru.railbrake.calculator.core.ErmakDiagnosticScenario\n',
        'import ru.railbrake.calculator.core.ErmakDiagnosticScenario\nimport ru.railbrake.calculator.data.DiagnosticSessionRecord\nimport ru.railbrake.calculator.data.DiagnosticSessionRepository\nimport java.text.SimpleDateFormat\nimport java.util.Date\nimport java.util.Locale\n',
        f'{path}: journal imports',
    )
    text = replace_once(
        text,
        '''    var selectedId by rememberSaveable(initialScenarioId, initialEquipmentId) { mutableStateOf(initialScenarioId) }
    var query by rememberSaveable { mutableStateOf("") }
    val selected = scenarios?.firstOrNull { it.id == selectedId }
''',
        '''    var selectedId by rememberSaveable(initialScenarioId, initialEquipmentId) { mutableStateOf(initialScenarioId) }
    var query by rememberSaveable { mutableStateOf("") }
    var catalogMode by rememberSaveable { mutableStateOf("scenarios") }
    var historyVersion by remember { mutableIntStateOf(0) }
    val sessionRepository = remember { DiagnosticSessionRepository(context) }
    val sessions = remember(historyVersion, selectedId) {
        sessionRepository.loadForProfile(DiagnosticSessionRepository.PROFILE_ERMAK)
    }
    val selected = scenarios?.firstOrNull { it.id == selectedId }
''',
        f'{path}: catalog journal state',
    )
    text = replace_once(
        text,
        '        ErmakDiagnosticRoute(selected, onBack = { selectedId = null })\n',
        '        ErmakDiagnosticRoute(selected, onBack = { selectedId = null }, onSaved = { historyVersion++ })\n',
        f'{path}: route callback',
    )
    text = replace_once(
        text,
        '''        item {
            RailSectionHeader("Диагностика Ермак", "Выберите неисправность или наблюдаемый симптом")
            DiagnosticSafetyNotice()
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Поиск по симптому") },
                singleLine = true,
                shape = RoundedCornerShape(16.dp)
            )
        }
        if (scenarios == null) {
''',
        '''        item {
            RailSectionHeader("Диагностика Ермак", "Выберите неисправность или наблюдаемый симптом")
            DiagnosticSafetyNotice()
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                item { FilterChip(catalogMode == "scenarios", { catalogMode = "scenarios" }, label = { Text("Неисправность") }) }
                item { FilterChip(catalogMode == "history", { catalogMode = "history" }, label = { Text("Журнал") }) }
            }
            if (catalogMode == "scenarios") {
                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Поиск по симптому") },
                    singleLine = true,
                    shape = RoundedCornerShape(16.dp)
                )
            }
        }
        if (catalogMode == "history") {
            item {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("Локальный журнал Ермака", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
                    if (sessions.isNotEmpty()) {
                        TextButton(onClick = {
                            sessionRepository.clearProfile(DiagnosticSessionRepository.PROFILE_ERMAK)
                            historyVersion++
                        }) { Text("Очистить") }
                    }
                }
            }
            if (sessions.isEmpty()) {
                item {
                    InfoCard(
                        "Пока пусто",
                        listOf("Сохранённые результаты диагностики Ермака появятся здесь и останутся на устройстве."),
                        MaterialTheme.colorScheme.surfaceVariant
                    )
                }
            }
            items(sessions, key = { it.timestampMillis }) { session ->
                Card(
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                        Text(session.scenarioTitle, fontWeight = FontWeight.Black)
                        Text(
                            SimpleDateFormat("dd.MM.yyyy HH:mm", Locale.getDefault()).format(Date(session.timestampMillis)),
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(session.severity)
                        Text(session.report, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
        } else if (scenarios == null) {
''',
        f'{path}: journal UI',
    )
    text = replace_once(
        text,
        'private fun ErmakDiagnosticRoute(scenario: ErmakDiagnosticScenario, onBack: () -> Unit) {\n',
        'private fun ErmakDiagnosticRoute(scenario: ErmakDiagnosticScenario, onBack: () -> Unit, onSaved: () -> Unit) {\n',
        f'{path}: route signature',
    )
    text = replace_once(
        text,
        '''    var questionNumber by rememberSaveable(scenario.id) { mutableIntStateOf(1) }
    val node = scenario.nodes[nodeId]
''',
        '''    var questionNumber by rememberSaveable(scenario.id) { mutableIntStateOf(1) }
    var savedLocally by rememberSaveable(scenario.id) { mutableStateOf(false) }
    val context = LocalContext.current
    val sessionRepository = remember { DiagnosticSessionRepository(context) }
    val node = scenario.nodes[nodeId]
''',
        f'{path}: route save state',
    )
    text = replace_once(
        text,
        '''                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    OutlinedButton(onClick = {
                        nodeId = scenario.startNodeId
                        history = emptyList()
                        uncertain = false
                        questionNumber = 1
                    }) { Text("Начать заново") }
                    Button(onClick = onBack) { Text("К списку неисправностей") }
                }
''',
        '''                val savedReport = buildErmakDiagnosticReport(
                    scenario = scenario,
                    terminalText = node?.text,
                    uncertain = uncertain,
                    history = history,
                    observations = observations,
                    report = report
                )
                OutlinedButton(
                    onClick = {
                        sessionRepository.add(
                            DiagnosticSessionRecord(
                                timestampMillis = System.currentTimeMillis(),
                                profileId = DiagnosticSessionRepository.PROFILE_ERMAK,
                                variantId = DiagnosticSessionRepository.VARIANT_ERMAK_GENERAL,
                                scenarioId = scenario.id,
                                scenarioTitle = scenario.title,
                                severity = ermakSeverityTitle(scenario.severity),
                                report = savedReport
                            )
                        )
                        savedLocally = true
                        onSaved()
                    },
                    enabled = !savedLocally,
                    modifier = Modifier.fillMaxWidth()
                ) { Text(if (savedLocally) "Сохранено в журнал" else "Сохранить в локальную историю") }
                if (savedLocally) {
                    Text("Сессия сохранена на устройстве.", color = MaterialTheme.colorScheme.primary)
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    OutlinedButton(onClick = {
                        nodeId = scenario.startNodeId
                        history = emptyList()
                        uncertain = false
                        questionNumber = 1
                        savedLocally = false
                    }) { Text("Начать заново") }
                    Button(onClick = onBack) { Text("К списку неисправностей") }
                }
''',
        f'{path}: save button',
    )
    text = replace_once(
        text,
        '\n}\n',
        '''
}

private fun ermakSeverityTitle(value: String): String = when (value.trim().uppercase()) {
    "INFORMATION", "INFO" -> "Информация"
    "ATTENTION", "WARNING" -> "Внимание"
    "RESTRICT_OPERATION", "RESTRICT" -> "Ограничить эксплуатацию"
    "STOP_AND_REPORT", "STOP" -> "Остановиться и доложить"
    else -> value.replace('_', ' ').trim().ifBlank { "Диагностическая запись" }
}

private fun buildErmakDiagnosticReport(
    scenario: ErmakDiagnosticScenario,
    terminalText: String?,
    uncertain: Boolean,
    history: List<String>,
    observations: String,
    report: String
): String = buildString {
    appendLine("Ермак — ${scenario.title}")
    appendLine("Симптом: ${scenario.symptom}")
    appendLine("Результат: ${if (uncertain) "Недостаточно данных" else terminalText.orEmpty().ifBlank { "Маршрут завершён" }}")
    if (history.isNotEmpty()) {
        appendLine("Пройденная ветка:")
        history.forEach { appendLine("• $it") }
    }
    if (observations.isNotBlank()) appendLine("Наблюдения: ${observations.trim()}")
    if (report.isNotBlank()) appendLine("Доклад / заметки: ${report.trim()}")
    if (scenario.reportFields.isNotEmpty()) {
        appendLine("Что зафиксировать: ${scenario.reportFields.joinToString()}")
    }
}.trim()
''',
        f'{path}: report helpers (first closing brace)',
    )
    path.write_text(text)

# Beta14 identity.
for path in [Path('app/build.gradle.kts'), Path('patch/app/build.gradle.kts')]:
    text = path.read_text()
    text = replace_once(text, 'versionCode = 158', 'versionCode = 159', f'{path}: versionCode')
    text = replace_once(text, 'versionName = "1.2.2-dev14-beta13"', 'versionName = "1.2.2-dev14-beta14"', f'{path}: versionName')
    path.write_text(text)

# Sanity checks.
assert root_repo.read_text() == patch_repo.read_text()
assert 'loadForProfile(DiagnosticSessionRepository.PROFILE_VL80S)' in Path('app/src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt').read_text()
ermak = Path('app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt').read_text()
assert 'Локальный журнал Ермака' in ermak
assert 'Сохранить в локальную историю' in ermak
assert 'profileId = DiagnosticSessionRepository.PROFILE_ERMAK' in ermak
