#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def read(rel):
    return (root / rel).read_text(encoding="utf-8")


def write(rel, text):
    (root / rel).write_text(text, encoding="utf-8")


def rep(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Recovery pass 2: make acceptance behavior follow the canonical data model.
# ---------------------------------------------------------------------------
rel = "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"
t = read(rel)

t = rep(t, '''    val sequence: List<String> = emptyList(),
    val sequenceKind: String = "",
    val searchText: String
)''', '''    val sequence: List<String> = emptyList(),
    val sequenceKind: String = "",
    val sequenceMode: String = "",
    val requiredGates: List<String> = emptyList(),
    val zoneId: String = "",
    val searchText: String
)''', "TechnicalEntry acceptance metadata")

t = rep(t, '''    private val vl80sStage6 by lazy { json("technical/vl80s_diagnostics.json") }
    private val ermakStage7 by lazy { json("technical/ermak_links.json") }
''', '''    private val vl80sStage6 by lazy { json("technical/vl80s_diagnostics.json") }
    private val vl80Acceptance by lazy { json("technical/vl80s_acceptance.json") }
    private val ermakStage7 by lazy { json("technical/ermak_links.json") }
''', "canonical acceptance root")

t = rep(t, '''    fun count(family: TechnicalFamily, section: TechnicalSection): Int = sectionEntries(family, section).size

    private fun vl80CanonicalRelated''', '''    fun count(family: TechnicalFamily, section: TechnicalSection): Int = sectionEntries(family, section).size

    fun acceptanceStateIds(): List<String> =
        vl80Acceptance.obj("checkStateModel").array("states").strings().ifEmpty {
            listOf("NOT_CHECKED", "OK", "NOTE", "BLOCKING", "NOT_APPLICABLE")
        }

    fun acceptanceStateRules(): List<String> =
        vl80Acceptance.obj("checkStateModel").array("rules").strings()

    fun acceptanceGateMeaning(id: String): String =
        vl80Acceptance.array("gates").objects().firstOrNull { it.optString("id") == id }
            ?.optString("meaning").orEmpty()

    private fun vl80CanonicalRelated''', "acceptance contract accessors")

t = rep(t, '''        val root = json("technical/vl80s_acceptance.json")
''', '''        val root = vl80Acceptance
''', "reuse canonical acceptance root")

t = rep(t, '''                    addAll(vl80CanonicalRelated(item.optString("id")))
                }.distinct()
            )
        }
        val routes = root.array("routes")''', '''                    addAll(vl80CanonicalRelated(item.optString("id")))
                }.distinct(),
                requiredGates = item.array("preconditions").strings(),
                zoneId = item.optString("zoneId")
            )
        }
        val routes = root.array("routes")''', "acceptance item gate metadata")

t = rep(t, '''                blocks=listOf(TechnicalBlock("Режим",listOf("Последовательное прохождение пунктов приёмки с пятью состояниями проверки, комментариями и сохранением прогресса."))),
                sequence=ids, sequenceKind="ACCEPTANCE", searchText=(route.optString("title")+" "+mode).lowercase()
''', '''                blocks=listOfNotEmpty(
                    block("Режим", mode),
                    block("Условия маршрута", route.optString("note")),
                    block("Правила состояний", root.obj("checkStateModel").array("rules").strings())
                ),
                sequence=ids, sequenceKind="ACCEPTANCE", sequenceMode=route.optString("mode"),
                searchText=(route.optString("title")+" "+mode+" "+route.optString("note")).lowercase()
''', "acceptance route mode")

t = rep(t, '''            sequence=items.map(TechnicalEntry::id), sequenceKind="ACCEPTANCE", searchText="полная приёмка пошагово"
''', '''            sequence=items.map(TechnicalEntry::id), sequenceKind="ACCEPTANCE", sequenceMode="step_by_step", searchText="полная приёмка пошагово"
''', "acceptance fallback mode")

t = rep(t, '''        sequence: List<String> = emptyList(),
        sequenceKind: String = ""
    ): TechnicalEntry {''', '''        sequence: List<String> = emptyList(),
        sequenceKind: String = "",
        sequenceMode: String = "",
        requiredGates: List<String> = emptyList(),
        zoneId: String = ""
    ): TechnicalEntry {''', "entry factory metadata signature")

t = rep(t, '''            sequence = sequence.filter(String::isNotBlank).distinct(),
            sequenceKind = sequenceKind,
            searchText = search
''', '''            sequence = sequence.filter(String::isNotBlank).distinct(),
            sequenceKind = sequenceKind,
            sequenceMode = sequenceMode,
            requiredGates = requiredGates.filter(String::isNotBlank).distinct(),
            zoneId = zoneId,
            searchText = search
''', "entry factory metadata result")

write(rel, t)

# ---------------------------------------------------------------------------
# Acceptance UI: canonical states + explicit safety gates + route semantics.
# ---------------------------------------------------------------------------
rel = "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
t = read(rel)

t = rep(t, '''                if (entry.sequenceKind == "ACCEPTANCE") AcceptanceSequence(entry, repository, onOpen)
                else TechnicalSequence(entry, repository, onOpen)
''', '''                if (entry.sequenceKind == "ACCEPTANCE") {
                    when (entry.sequenceMode) {
                        "checklist", "area" -> AcceptanceChecklist(entry, repository, onOpen)
                        else -> AcceptanceSequence(entry, repository, onOpen)
                    }
                } else TechnicalSequence(entry, repository, onOpen)
''', "acceptance route dispatcher")

start = t.index('@Composable\nprivate fun AcceptanceSequence')
end = t.index('\n@Composable\nprivate fun TechnicalSequence', start)
new = r'''@Composable
private fun AcceptanceSequence(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {
    val context = LocalContext.current
    val prefs = remember(entry.id) { context.getSharedPreferences("vl80s_acceptance_progress", android.content.Context.MODE_PRIVATE) }
    var step by rememberSaveable(entry.id) { mutableIntStateOf(prefs.getInt("${entry.id}:step", 0).coerceIn(entry.sequence.indices)) }
    var gateRevision by remember(entry.id) { mutableIntStateOf(0) }
    val currentId = entry.sequence[step.coerceIn(entry.sequence.indices)]
    val target = repository.entry(currentId)
    val stateKey = "${entry.id}:$currentId:state"
    val noteKey = "${entry.id}:$currentId:note"
    val resolutionKey = "${entry.id}:$currentId:resolution"
    val availableStates = remember(entry.id) { repository.acceptanceStateIds() }
    var state by remember(currentId) {
        mutableStateOf((prefs.getString(stateKey, "NOT_CHECKED") ?: "NOT_CHECKED").takeIf { it in availableStates } ?: "NOT_CHECKED")
    }
    var note by remember(currentId) { mutableStateOf(prefs.getString(noteKey, "") ?: "") }
    var resolution by remember(currentId) { mutableStateOf(prefs.getString(resolutionKey, "") ?: "") }
    val accent = technicalSectionAccent(entry.section, entry.status)
    val completed = entry.sequence.count { id -> (prefs.getString("${entry.id}:$id:state", "NOT_CHECKED") ?: "NOT_CHECKED") != "NOT_CHECKED" }
    val requiredGates = target?.requiredGates.orEmpty()
    val gateStates = remember(currentId, gateRevision) {
        requiredGates.associateWith { gate -> prefs.getBoolean("${entry.id}:gate:$gate", false) }
    }
    val gatesSatisfied = gateStates.values.all { it }
    val requiresNote = state == "NOTE" || state == "NOT_APPLICABLE"
    val requiresResolution = state == "BLOCKING"
    val stateComplete = (!requiresNote || note.isNotBlank()) && (!requiresResolution || (note.isNotBlank() && resolution.isNotBlank()))
    val canAdvance = stateComplete && gatesSatisfied

    fun persistState(newState: String) {
        state = newState
        prefs.edit().putString(stateKey, newState).apply()
    }
    fun move(newStep: Int) {
        step = newStep.coerceIn(entry.sequence.indices)
        prefs.edit().putInt("${entry.id}:step", step).apply()
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer),
        border = BorderStroke(1.dp, accent.copy(alpha = .45f)),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Пошаговая приёмка", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
            Text("Шаг ${step + 1} из ${entry.sequence.size} • отмечено $completed", color = accent)
            if (entry.sequenceMode == "route") {
                Text("Маршрут с контролем условий перехода", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            }
            Text(target?.let(::technicalEntryTitle) ?: "Пункт приёмки", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
            target?.let { item ->
                technicalEntrySubtitle(item)?.let { Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                item.blocks.forEach { block ->
                    val lines = repository.displayLines(block.lines).mapNotNull(::technicalPresentationLine).distinct()
                    if (lines.isNotEmpty()) Card(
                        colors = CardDefaults.cardColors(containerColor = technicalBlockContainer(item.section, block.title)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                            Text(block.title, fontWeight = FontWeight.Black)
                            lines.forEach { Text("• $it") }
                        }
                    }
                }
            }

            if (requiredGates.isNotEmpty()) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer.copy(alpha = .34f)),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.error.copy(alpha = .35f))
                ) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Условия безопасности перед этим пунктом", fontWeight = FontWeight.Black)
                        requiredGates.forEach { gate ->
                            val confirmed = gateStates[gate] == true
                            val meaning = repository.acceptanceGateMeaning(gate)
                            if (meaning.isNotBlank()) Text(meaning, style = MaterialTheme.typography.bodySmall)
                            FilterChip(
                                selected = confirmed,
                                onClick = {
                                    prefs.edit().putBoolean("${entry.id}:gate:$gate", !confirmed).apply()
                                    gateRevision++
                                },
                                label = { Text(if (confirmed) "Условие подтверждено" else "Подтвердить условие") }
                            )
                        }
                        Text(
                            "Отметка в приложении фиксирует подтверждение пользователя и не заменяет допуск, распоряжение или установленный порядок работ.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            fun stateLabel(value: String): String = when (value) {
                "OK" -> "Проверено"
                "NOTE" -> "Замечание"
                "BLOCKING" -> "Блокирующее замечание"
                "NOT_APPLICABLE" -> "Не применяется"
                else -> "Не проверено"
            }
            Text("Состояние: ${stateLabel(state)}", color = accent, fontWeight = FontWeight.Bold)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(availableStates) { stateId ->
                    FilterChip(
                        selected = state == stateId,
                        onClick = { persistState(stateId) },
                        label = { Text(stateLabel(stateId)) }
                    )
                }
            }
            if (state == "NOTE" || state == "BLOCKING" || state == "NOT_APPLICABLE") {
                OutlinedTextField(
                    value = note,
                    onValueChange = { note = it; prefs.edit().putString(noteKey, it).apply() },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text(if (state == "NOT_APPLICABLE") "Причина применимости / варианта" else "Комментарий и локализация") },
                    minLines = 2
                )
            }
            if (state == "BLOCKING") {
                OutlinedTextField(
                    value = resolution,
                    onValueChange = { resolution = it; prefs.edit().putString(resolutionKey, it).apply() },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Оформленное решение / дальнейшее действие") },
                    minLines = 2
                )
            }
            if (!gatesSatisfied) Text("Переход дальше заблокирован: не подтверждены обязательные условия безопасности.", color = MaterialTheme.colorScheme.error)
            else if (!stateComplete) Text(
                if (state == "BLOCKING") "Блокирующее замечание нельзя закрыть без комментария и оформленного решения."
                else "Для этого состояния требуется комментарий.",
                color = MaterialTheme.colorScheme.error
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { move(step - 1) }, enabled = step > 0) { Text("Назад") }
                Button(onClick = { move(step + 1) }, enabled = step < entry.sequence.lastIndex && canAdvance) { Text("Далее") }
            }
            if (target != null) OutlinedButton(onClick = { onOpen(target) }, modifier = Modifier.fillMaxWidth()) { Text("Открыть полную карточку") }
        }
    }
}

@Composable
private fun AcceptanceChecklist(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {
    val context = LocalContext.current
    val prefs = remember(entry.id) { context.getSharedPreferences("vl80s_acceptance_progress", android.content.Context.MODE_PRIVATE) }
    var revision by remember(entry.id) { mutableIntStateOf(0) }
    val targets = remember(entry.id) { entry.sequence.mapNotNull(repository::entry) }
    val groups = remember(entry.id) { targets.groupBy { it.zoneId.ifBlank { "OTHER" } } }
    val stateLabels = mapOf(
        "OK" to "Проверено",
        "NOTE" to "Замечание",
        "BLOCKING" to "Блокирующее",
        "NOT_APPLICABLE" to "Не применяется",
        "NOT_CHECKED" to "Не проверено"
    )
    val completed = remember(revision) {
        targets.count { item -> (prefs.getString("${entry.id}:${item.id}:state", "NOT_CHECKED") ?: "NOT_CHECKED") != "NOT_CHECKED" }
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(if (entry.sequenceMode == "area") "Приёмка по зоне" else "Контрольный список", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
            Text("Отмечено $completed из ${targets.size}", color = MaterialTheme.colorScheme.primary)
            groups.forEach { (zone, itemsInZone) ->
                Text(zone.replace('_', ' '), style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Black)
                itemsInZone.forEach { item ->
                    val stateKey = "${entry.id}:${item.id}:state"
                    val state = prefs.getString(stateKey, "NOT_CHECKED") ?: "NOT_CHECKED"
                    OutlinedButton(
                        onClick = {
                            val states = repository.acceptanceStateIds()
                            val next = if (state == "NOT_CHECKED" && "OK" in states) "OK" else "NOT_CHECKED"
                            prefs.edit().putString(stateKey, next).apply()
                            revision++
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(Modifier.fillMaxWidth()) {
                            Text(technicalEntryTitle(item), fontWeight = FontWeight.Bold)
                            Text(stateLabels[state] ?: state, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                    TextButton(onClick = { onOpen(item) }) { Text("Открыть пункт") }
                }
            }
            Text(
                "Быстрая отметка в списке переключает только «Не проверено ↔ Проверено». Для замечания, блокирующего состояния, причины неприменимости и полного содержания откройте пункт.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
'''
t = t[:start] + new + t[end:]
write(rel, t)

# Distinguish the second functional recovery pass.
gradle_rel = "app/build.gradle.kts"
g = read(gradle_rel).replace('versionName = "1.2.2-beta-recovery1"', 'versionName = "1.2.2-beta-recovery2"', 1)
write(gradle_rel, g)

print("Recovery patch 2 applied")
