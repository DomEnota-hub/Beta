#!/usr/bin/env python3
from pathlib import Path
import re, sys

root = Path(sys.argv[1])

def ms(rel):
    return [root / rel, root / "patch" / rel]

def rep(rel, old, new):
    for p in ms(rel):
        s = p.read_text(encoding="utf-8")
        if s.count(old) != 1:
            raise SystemExit(f"{p}: expected exactly one match for {old[:80]!r}")
        p.write_text(s.replace(old, new, 1), encoding="utf-8")

rep("app/build.gradle.kts", "versionCode = 145", "versionCode = 146")
rep("app/build.gradle.kts", 'versionName = "1.2.2-dev14-hotfix3"', 'versionName = "1.2.2-dev14-beta1"')

rel = "app/src/main/java/ru/railbrake/calculator/ui/HomeScreen.kt"
for p in ms(rel):
    s = p.read_text(encoding="utf-8")
    s = s.replace("import ru.railbrake.calculator.core.DiagnosticRepository\n", "")
    s = s.replace("import ru.railbrake.calculator.core.Vl80sObservationCatalog\n", "")
    s2, c = re.subn(
        r'\n\s*RailInfoBand\(\n\s*"\$\{DiagnosticRepository\.scenarios\.size\} диагностических сценария • \$\{Vl80sObservationCatalog\.equipment\.size\} узлов оборудования"\n\s*\)\n',
        "\n", s, count=1
    )
    if c != 1:
        raise SystemExit(f"{p}: home counter not found")
    p.write_text(s2, encoding="utf-8")

rel = "app/src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt"
rep(rel,
    '                "${DiagnosticRepository.scenarios.size} сценариев • ветвящиеся уточнения • безопасные проверки"',
    '                "Выберите неисправность, наблюдаемый признак или быстрый маршрут"')
rep(rel,
    '                item { FilterChip(catalogMode == "training", { catalogMode = "training" }, label = { Text("Тренажёр") }) }\n',
    "")
rep(rel, '''        if (catalogMode == "scenarios" || catalogMode == "observations") item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text(if (catalogMode == "scenarios") "Симптом или аппарат" else "Лампа, прибор, звук или аппарат") },
                placeholder = { Text(if (catalogMode == "scenarios") "Например: ЭКГ, №395, БУРТ, АЛСН" else "Например: выбило ГВ, ТМ падает, стук, боксование") },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        }
''', '''        if (catalogMode == "scenarios" || catalogMode == "observations" || catalogMode == "quick") item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                label = { Text(when (catalogMode) {
                    "scenarios" -> "Симптом или аппарат"
                    "quick" -> "Поиск по быстрому маршруту"
                    else -> "Лампа, прибор, звук или аппарат"
                }) },
                placeholder = { Text(when (catalogMode) {
                    "scenarios" -> "Например: ЭКГ, №395, БУРТ, АЛСН"
                    "quick" -> "Например: тормоза, ГВ, дым"
                    else -> "Например: выбило ГВ, ТМ падает, стук, боксование"
                }) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth()
            )
        }
''')
rep(rel, '''                quickRouteItems.filter { item ->
                    DiagnosticRepository.scenario(item.scenarioId)?.let { scenario ->
                        LocomotiveProfiles.appliesToVariant(selectedVariantId, scenario.applicableVariantIds)
                    } == true
                },
''', '''                quickRouteItems.filter { item ->
                    val matchesQuery = query.isBlank() ||
                        item.title.contains(query, ignoreCase = true) ||
                        item.subtitle.contains(query, ignoreCase = true)
                    matchesQuery && DiagnosticRepository.scenario(item.scenarioId)?.let { scenario ->
                        LocomotiveProfiles.appliesToVariant(selectedVariantId, scenario.applicableVariantIds)
                    } == true
                },
''')
rep(rel,
    '                        Text("Связано: ${observation.equipmentIds.joinToString()}", style = MaterialTheme.typography.bodySmall)\n',
    '''                        val linkedTitles = observation.equipmentIds
                            .mapNotNull(Vl80sObservationCatalog::equipment)
                            .map { it.title }
                            .distinct()
                        if (linkedTitles.isNotEmpty()) {
                            Text("Связано: ${linkedTitles.joinToString()}", style = MaterialTheme.typography.bodySmall)
                        }
''')
rep(rel, '''@Composable
private fun SafetyNotice() {
    BorderedCautionCard(
        title = "Важно: это не допуск к работам",
        lines = listOf(DiagnosticRepository.safetyNotice)
    )
}
''', '''@Composable
internal fun SafetyNotice() {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.error),
        shape = RoundedCornerShape(17.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
            Text(
                "Важно: это не допуск к работам",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Black,
                color = MaterialTheme.colorScheme.error
            )
            Text(DiagnosticRepository.safetyNotice)
        }
    }
}
''')

rel = "app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt"
rep(rel, '''            InfoCard(
                "Важно: это не допуск к работам",
                listOf(
                    "Диагностика помогает локализовать отказ и подготовить доклад.",
                    "Она не заменяет местную инструкцию, установленный допуск и требования безопасности."
                ),
                MaterialTheme.colorScheme.errorContainer
            )
''', "            SafetyNotice()\n")

rel = "app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt"
anchor = '''private fun examBlockDisplayTitle(sourceTitle: String): String = when (sourceTitle) {
    "Тест 1" -> "Блок 1"
    "Тест 2 - блок 1" -> "Блок 2"
    "Тест 2 - блок 2" -> "Блок 3"
    "Тест 2 - блок 3" -> "Блок 4"
    else -> sourceTitle
}
'''
rep(rel, anchor, anchor + '''
internal fun formatExamCorrectAnswer(answer: String): String {
    val parts = answer.split('•').map { it.trim() }.filter { it.isNotEmpty() }
    return if (parts.size > 1) parts.joinToString("\\n") { "- $it" } else answer
}
''')
rep(rel,
    "Text(item.correctAnswer, modifier = Modifier.fillMaxWidth().padding(12.dp), style = MaterialTheme.typography.bodyLarge)",
    "Text(formatExamCorrectAnswer(item.correctAnswer), modifier = Modifier.fillMaxWidth().padding(12.dp), style = MaterialTheme.typography.bodyLarge)")

rel = "app/src/main/java/ru/railbrake/calculator/ui/KnowledgeBaseScreen.kt"
rep(rel,
    "import ru.railbrake.calculator.data.FavoriteArticleRepository\n",
    "import ru.railbrake.calculator.data.FavoriteArticleRepository\nimport ru.railbrake.calculator.data.SecretAccessRepository\n")
rep(rel,
    "    val examQuestionRepository = remember { ExamQuestionRepository(context) }\n",
    "    val examQuestionRepository = remember { ExamQuestionRepository(context) }\n    val examQuestionsUnlocked = remember { SecretAccessRepository(context).isUnlocked() }\n")
rep(rel,
    "            examQuestionRepository = examQuestionRepository,\n            onOpenArticle = { selectedArticleId = it.id },",
    "            examQuestionRepository = examQuestionRepository,\n            examQuestionsUnlocked = examQuestionsUnlocked,\n            onOpenArticle = { selectedArticleId = it.id },")
rep(rel,
    "    examQuestionRepository: ExamQuestionRepository,\n    onOpenArticle: (KnowledgeArticle) -> Unit,",
    "    examQuestionRepository: ExamQuestionRepository,\n    examQuestionsUnlocked: Boolean,\n    onOpenArticle: (KnowledgeArticle) -> Unit,")
rep(rel, '''    val categories = remember {
        (KnowledgeRepository.categories + examQuestionRepository.categories).distinct()
    }
    val thematicFacts = remember(query, category, onlyFavorites) {
        if (onlyFavorites) emptyList() else examQuestionRepository.thematicFacts(
''', '''    val categories = remember(examQuestionsUnlocked) {
        if (examQuestionsUnlocked) {
            (KnowledgeRepository.categories + examQuestionRepository.categories).distinct()
        } else {
            KnowledgeRepository.categories
        }
    }
    val thematicFacts = remember(query, category, onlyFavorites, examQuestionsUnlocked) {
        if (onlyFavorites || !examQuestionsUnlocked) emptyList() else examQuestionRepository.thematicFacts(
''')
rep(rel, '        RailInfoBand("Внешние первоисточники открываются в браузере.")\n\n', "")

print("BETA_PATCH_APPLIED")
