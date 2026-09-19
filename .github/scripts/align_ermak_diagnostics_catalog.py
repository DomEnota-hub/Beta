from pathlib import Path

HOME_PATHS = [
    Path("app/src/main/java/ru/railbrake/calculator/ui/HomeScreen.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/ui/HomeScreen.kt"),
]
ERMAK_PATHS = [
    Path("app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt"),
]

for path in HOME_PATHS:
    text = path.read_text(encoding="utf-8")
    old = '''        RailHeroCard(
            title = "Диагностика ВЛ80С",
            subtitle = "Поиск неисправности по наблюдаемым признакам, ветвящиеся уточнения и безопасные проверки.",'''
    new = '''        RailHeroCard(
            title = "Диагностика",
            subtitle = "ВЛ80С и Ермак: поиск неисправности по наблюдаемым признакам, ветвящиеся уточнения и безопасные проверки.",'''
    if old not in text:
        raise SystemExit(f"Home diagnostic card marker not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

replacement = r'''private val ermakDiagnosticCategories = listOf(
    "Все",
    "Высоковольтные цепи",
    "Тяга",
    "Вспомогательные машины",
    "Тормоза",
    "Пневматика",
    "Ходовая часть",
    "Управление и защита",
    "Прочее"
)

private fun ermakScenarioText(scenario: ErmakDiagnosticScenario): String = listOf(
    scenario.category,
    scenario.title,
    scenario.symptom,
    scenario.immediateActions.joinToString(" "),
    scenario.probableCauses.joinToString(" "),
    scenario.reportFields.joinToString(" ")
).joinToString(" ").lowercase().replace('ё', 'е')

private fun String.containsAny(vararg needles: String): Boolean = needles.any(::contains)

private fun ermakCategory(scenario: ErmakDiagnosticScenario): String {
    val text = ermakScenarioText(scenario)
    return when {
        text.containsAny(
            "токоприем", "главный выключател", "высоковольт", "ввк", "трансформатор",
            "перенапряж", "изоляц", "крышев", "силовая цеп"
        ) -> "Высоковольтные цепи"
        text.containsAny(
            "тяга", "тягов", "тэд", "экг", "позици", "боксован", "юз"
        ) -> "Тяга"
        text.containsAny(
            "вспомогатель", "вентилятор", "фазорасщеп", "компрессор", "масляный насос", "маслонасос"
        ) -> "Вспомогательные машины"
        text.containsAny(
            "тормоз", "квт", "кран машиниста", "тормозных цилиндр", "тормозного цилиндр", "эпт"
        ) -> "Тормоза"
        text.containsAny(
            "пневм", "давлен", "тормозная магистрал", "питательная магистрал", "главных резервуар",
            "утечк воздуха", "воздухораспредел"
        ) -> "Пневматика"
        text.containsAny(
            "ходов", "тележ", "колес", "букс", "рессор", "редуктор", "подвес", "стук", "вибрац"
        ) -> "Ходовая часть"
        text.containsAny(
            "защит", "блокиров", "сигнализац", "управлен", "контроллер", "бортовой"
        ) -> "Управление и защита"
        else -> "Прочее"
    }
}

private fun ermakMatchesQuery(scenario: ErmakDiagnosticScenario, query: String): Boolean =
    query.isBlank() || ermakScenarioText(scenario).contains(query.trim().lowercase().replace('ё', 'е'))

private fun ermakQuickCandidate(scenario: ErmakDiagnosticScenario): Boolean {
    val severity = scenario.severity.trim().uppercase()
    val text = ermakScenarioText(scenario)
    return severity in setOf("ATTENTION", "WARNING", "RESTRICT_OPERATION", "RESTRICT", "STOP_AND_REPORT", "STOP") ||
        text.containsAny(
            "не включ", "не запуска", "отключ", "нет тяги", "тормоз", "давлен", "дым", "огонь",
            "нагрев", "стук", "вибрац", "защит", "токоприем"
        )
}

@Composable
fun ErmakDiagnosticsScreen(initialScenarioId: String? = null, initialEquipmentId: String? = null) {
    val context = LocalContext.current
    val repository = remember { ErmakDiagnosticRepository(context.applicationContext) }
    val scenarios by produceState<List<ErmakDiagnosticScenario>?>(null) {
        value = withContext(Dispatchers.IO) { repository.scenarios() }
    }
    var selectedId by rememberSaveable(initialScenarioId, initialEquipmentId) { mutableStateOf(initialScenarioId) }
    var query by rememberSaveable { mutableStateOf("") }
    var category by rememberSaveable { mutableStateOf("Все") }
    var catalogMode by rememberSaveable { mutableStateOf("scenarios") }
    var historyVersion by remember { mutableIntStateOf(0) }
    val sessionRepository = remember { DiagnosticSessionRepository(context) }
    val sessions = remember(historyVersion) {
        sessionRepository.loadForProfile(DiagnosticSessionRepository.PROFILE_ERMAK)
    }
    val selected = scenarios?.firstOrNull { it.id == selectedId }

    BackHandler(enabled = selected != null) { selectedId = null }
    if (selected != null) {
        ErmakDiagnosticRoute(selected, onBack = { selectedId = null }, onSaved = { historyVersion++ })
        return
    }

    val baseScenarios = scenarios.orEmpty().filter { scenario ->
        (initialEquipmentId == null || initialEquipmentId in scenario.equipmentIds) && ermakMatchesQuery(scenario, query)
    }
    val visible = when (catalogMode) {
        "scenarios" -> baseScenarios.filter { category == "Все" || ermakCategory(it) == category }
        "observations" -> baseScenarios.sortedBy { it.symptom.lowercase() }
        "quick" -> baseScenarios.filter(::ermakQuickCandidate).sortedBy { ermakCategory(it) + it.title }
        else -> emptyList()
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        item {
            RailSectionHeader("Диагностика Ермак", "Выберите неисправность или наблюдаемый симптом")
            DiagnosticSafetyNotice()
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                item { FilterChip(catalogMode == "scenarios", { catalogMode = "scenarios" }, label = { Text("Неисправность") }) }
                item { FilterChip(catalogMode == "observations", { catalogMode = "observations" }, label = { Text("Что я вижу?") }) }
                item { FilterChip(catalogMode == "quick", { catalogMode = "quick" }, label = { Text("В пути") }) }
                item { FilterChip(catalogMode == "history", { catalogMode = "history" }, label = { Text("Журнал") }) }
            }
            if (catalogMode != "history") {
                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = {
                        Text(
                            when (catalogMode) {
                                "observations" -> "Лампа, прибор, звук или симптом"
                                "quick" -> "Поиск во вкладке «В пути»"
                                else -> "Симптом или аппарат"
                            }
                        )
                    },
                    singleLine = true,
                    shape = RoundedCornerShape(16.dp)
                )
            }
        }

        if (catalogMode == "scenarios") {
            item {
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(ermakDiagnosticCategories) { item ->
                        FilterChip(
                            selected = category == item,
                            onClick = { category = item },
                            label = { Text(item) }
                        )
                    }
                }
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
            item {
                Row(Modifier.fillMaxWidth().padding(24.dp), horizontalArrangement = Arrangement.Center) {
                    CircularProgressIndicator()
                }
            }
        } else if (catalogMode == "quick") {
            item {
                BorderedCautionCard(
                    "Быстрая оценка",
                    listOf(
                        "Здесь собраны сценарии, которые полезно быстро открыть в пути. Это только безопасное первичное направление поиска.",
                        "При дыме, огне, дуге, повреждении токоведущих частей или неясном срабатывании защиты прекратите диагностические действия и доложите."
                    )
                )
            }
            if (visible.isEmpty()) {
                item { InfoCard("Ничего не найдено", listOf("Измените запрос или очистите строку поиска."), MaterialTheme.colorScheme.surfaceVariant) }
            }
            items(visible, key = { "quick-${it.id}" }) { scenario ->
                Card(
                    onClick = { selectedId = scenario.id },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Text(ermakCategory(scenario), color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                        Text(ermakSeverityTitle(scenario.severity), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                        Text(scenario.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                        Text(scenario.symptom, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text("Открыть безопасный маршрут →", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    }
                }
            }
        } else if (catalogMode == "observations") {
            if (visible.isEmpty()) {
                item { InfoCard("Ничего не найдено", listOf("Попробуйте описать то, что видно или слышно: лампу, показание, звук, запах или поведение аппарата."), MaterialTheme.colorScheme.surfaceVariant) }
            }
            items(visible, key = { "observation-${it.id}" }) { scenario ->
                Card(
                    onClick = { selectedId = scenario.id },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Text(ermakCategory(scenario), color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                        Text("Наблюдаемый признак", style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                        Text(scenario.symptom, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                        Text(scenario.title, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text("Открыть безопасный алгоритм →", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    }
                }
            }
        } else if (visible.isEmpty()) {
            item { InfoCard("Сценарии не найдены", listOf("Измените запрос, выберите категорию «Все» или вернитесь к общему списку."), MaterialTheme.colorScheme.surfaceVariant) }
        } else {
            items(visible, key = { it.id }) { scenario ->
                Card(
                    onClick = { selectedId = scenario.id },
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Text(ermakCategory(scenario), color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                        Text(ermakSeverityTitle(scenario.severity), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                        Text(scenario.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                        Text(scenario.symptom, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text("Открыть алгоритм →", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
'''

for path in ERMAK_PATHS:
    text = path.read_text(encoding="utf-8")
    start_marker = "@Composable\nfun ErmakDiagnosticsScreen"
    end_marker = "\nprivate fun ermakSeverityTitle"
    start = text.find(start_marker)
    end = text.find(end_marker)
    if start < 0 or end < 0 or end <= start:
        raise SystemExit(f"Ermak catalog markers not found in {path}")
    updated = text[:start] + replacement + text[end:]
    path.write_text(updated, encoding="utf-8")

print("Aligned home diagnostics label and Ermak diagnostic catalog UX")
