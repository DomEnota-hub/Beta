#!/usr/bin/env python3
from pathlib import Path
import re
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
# Technical data adapter: restore canonical links and expose prepared layers.
# ---------------------------------------------------------------------------
rel = "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"
t = read(rel)

t = rep(t, '''data class TechnicalEntry(
    val id: String,
    val family: TechnicalFamily,
    val section: TechnicalSection,
    val title: String,
    val subtitle: String,
    val status: String,
    val blocks: List<TechnicalBlock>,
    val relatedIds: List<String> = emptyList(),
    val sequence: List<String> = emptyList(),
    val searchText: String
)''', '''data class TechnicalEntry(
    val id: String,
    val family: TechnicalFamily,
    val section: TechnicalSection,
    val title: String,
    val subtitle: String,
    val status: String,
    val blocks: List<TechnicalBlock>,
    val relatedIds: List<String> = emptyList(),
    val sequence: List<String> = emptyList(),
    val sequenceKind: String = "",
    val searchText: String
)''', "TechnicalEntry.sequenceKind")

t = rep(t, '''class TechnicalDataRepository(private val context: Context) {
    companion object {
        private val sharedSectionCache = mutableMapOf<Pair<TechnicalFamily, TechnicalSection>, List<TechnicalEntry>>()
    }
''', '''class TechnicalDataRepository(private val context: Context) {
    companion object {
        private val sharedSectionCache = mutableMapOf<Pair<TechnicalFamily, TechnicalSection>, List<TechnicalEntry>>()
    }

    private val vl80sStage6 by lazy { json("technical/vl80s_diagnostics.json") }
    private val ermakStage7 by lazy { json("technical/ermak_links.json") }
''', "canonical roots")

anchor = '''    fun count(family: TechnicalFamily, section: TechnicalSection): Int = sectionEntries(family, section).size

    private fun sectionEntries'''
insert = '''    fun count(family: TechnicalFamily, section: TechnicalSection): Int = sectionEntries(family, section).size

    private fun vl80CanonicalRelated(id: String): List<String> = buildList {
        vl80sStage6.array("edges").objects().forEach { edge ->
            val from = edge.optString("from")
            val to = edge.optString("to")
            when (id) {
                from -> to.takeIf(String::isNotBlank)?.let(::add)
                to -> from.takeIf(String::isNotBlank)?.let(::add)
            }
        }
    }.distinct()

    private fun ermakStableRef(value: String): Boolean =
        value.startsWith("ER-EQ-") || value.startsWith("ER-KB-") ||
            value.startsWith("ER-DIAG-") || value.startsWith("ER-SCH-") ||
            value.startsWith("ER-VARIANT-") || value.startsWith("SYS-")

    private fun stableRefs(value: Any?): List<String> = buildList {
        when (value) {
            is String -> if (ermakStableRef(value)) add(value)
            is JSONArray -> for (index in 0 until value.length()) addAll(stableRefs(value.opt(index)))
            is JSONObject -> {
                val keys = value.keys()
                while (keys.hasNext()) addAll(stableRefs(value.opt(keys.next())))
            }
        }
    }

    private fun ermakCanonicalRelated(id: String): List<String> {
        val indexes = ermakStage7.obj("indexes")
        val result = linkedSetOf<String>()
        listOf("byEquipment", "bySystem", "byDiagnostic", "byScheme").forEach { bucketName ->
            val bucket = indexes.obj(bucketName)
            val keys = bucket.keys()
            while (keys.hasNext()) {
                val key = keys.next()
                val refs = stableRefs(bucket.opt(key)).toSet()
                if (key == id) result.addAll(refs)
                if (id in refs && ermakStableRef(key)) result.add(key)
            }
        }
        result.remove(id)
        return result.toList()
    }

    private fun sectionEntries'''
t = rep(t, anchor, insert, "canonical link helpers")

# VЛ80 equipment: expose applicability/crosslinks and use Stage 6 graph.
t = rep(t, '''                    block("Системы", item.array("systemIds").strings()),
                    block("Диагностика", item.array("diagnosticScenarioIds").strings()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
                ),
                relatedIds = related
''', '''                    block("Системы", item.array("systemIds").strings()),
                    block("Диагностика", item.array("diagnosticScenarioIds").strings()),
                    block("Применимость", item.obj("applicability").summary()),
                    block("Связанные материалы", item.obj("crosslinks").allStrings()),
                    block("Особенности исполнения", item.array("featureRules").stringsOrSummaries() + item.array("equipmentOverrides").stringsOrSummaries()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
                ),
                relatedIds = (related + item.obj("crosslinks").allStrings() + vl80CanonicalRelated(item.optString("id"))).distinct()
''', "VL80 equipment enrichment")

# Acceptance: include Stage 6 reverse links.
t = rep(t, '''                    addAll(item.array("diagnosticHints").objects().mapNotNull { hint -> hint.optString("scenarioId").takeIf(String::isNotBlank) ?: hint.optString("id").takeIf(String::isNotBlank) })
                }.distinct()
''', '''                    addAll(item.array("diagnosticHints").objects().mapNotNull { hint -> hint.optString("scenarioId").takeIf(String::isNotBlank) ?: hint.optString("id").takeIf(String::isNotBlank) })
                    addAll(vl80CanonicalRelated(item.optString("id")))
                }.distinct()
''', "VL80 acceptance links")

t = rep(t, '''                blocks=listOf(TechnicalBlock("Режим",listOf("Последовательное прохождение пунктов приёмки с отметками «проверено» и «замечание»."))),
                sequence=ids, searchText=(route.optString("title")+" "+mode).lowercase()
''', '''                blocks=listOf(TechnicalBlock("Режим",listOf("Последовательное прохождение пунктов приёмки с пятью состояниями проверки, комментариями и сохранением прогресса."))),
                sequence=ids, sequenceKind="ACCEPTANCE", searchText=(route.optString("title")+" "+mode).lowercase()
''', "acceptance route kind")

t = rep(t, '''            title="Полная приёмка", subtitle="${items.size} пунктов • пошагово", status="ROUTE", blocks=emptyList(),
            sequence=items.map(TechnicalEntry::id), searchText="полная приёмка пошагово"
''', '''            title="Полная приёмка", subtitle="${items.size} пунктов • пошагово", status="ROUTE", blocks=emptyList(),
            sequence=items.map(TechnicalEntry::id), sequenceKind="ACCEPTANCE", searchText="полная приёмка пошагово"
''', "acceptance fallback kind")

# Electrical and pneumatic canonical modes/states must reach the UI.
t = rep(t, '''    private fun loadVl80sElectrical(): List<TechnicalEntry> =
        json("technical/vl80s_electrical.json").array("baseSchemes").objects().map { item ->
            schemeEntry(item, TechnicalFamily.VL80S, TechnicalSection.ELECTRICAL, "semanticEdges")
        }

    private fun loadVl80sPneumatic(): List<TechnicalEntry> =
        json("technical/vl80s_pneumatic.json").array("views").objects().map { item ->
            schemeEntry(item, TechnicalFamily.VL80S, TechnicalSection.PNEUMATIC, "edges")
        }
''', '''    private fun loadVl80sElectrical(): List<TechnicalEntry> {
        val root = json("technical/vl80s_electrical.json")
        val modes = root.array("modeOverlays").objects()
        val variants = root.array("variantOverlays").objects()
        return root.array("baseSchemes").objects().map { item ->
            val schemeId = item.optString("id")
            val schemeModes = modes.filter { it.optString("schemeId") == schemeId }
            val schemeVariants = variants.filter { schemeId in it.array("appliesTo").strings() }
            schemeEntry(
                item, TechnicalFamily.VL80S, TechnicalSection.ELECTRICAL, "semanticEdges",
                extraBlocks = listOfNotEmpty(
                    block("Режимы работы", schemeModes.map { mode ->
                        listOf(mode.optString("title"), mode.optString("note")).filter(String::isNotBlank).joinToString(" — ")
                    }),
                    block("Особенности исполнения", schemeVariants.map { it.optString("title") })
                )
            )
        }
    }

    private fun loadVl80sPneumatic(): List<TechnicalEntry> {
        val root = json("technical/vl80s_pneumatic.json")
        val states = root.array("states").objects()
        return root.array("views").objects().map { item ->
            val viewId = item.optString("id")
            val viewStates = states.filter { it.optString("viewId") == viewId }
            schemeEntry(
                item, TechnicalFamily.VL80S, TechnicalSection.PNEUMATIC, "edges",
                extraBlocks = listOfNotEmpty(
                    block("Рабочие состояния", viewStates.map { state ->
                        listOf(state.optString("title"), state.optString("summary")).filter(String::isNotBlank).joinToString(" — ")
                    })
                )
            )
        }
    }
''', "VL80 scheme overlays")

# Stage 6 links are authoritative for the internal technical graph.
t = rep(t, '''                    addAll(item.obj("pneumaticViews").allStrings())
                }.distinct()
''', '''                    addAll(item.obj("pneumaticViews").allStrings())
                    addAll(item.array("articleTargets").strings())
                    addAll(vl80CanonicalRelated(item.optString("id")))
                }.distinct()
''', "VL80 diagnostic canonical links")

# Ermak: use Stage 7 canonical link indexes, not raw candidate-only relations.
t = rep(t, '''                relatedIds = item.array("equipmentRefs").strings() +
                    item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) }
''', '''                relatedIds = (item.array("equipmentRefs").strings() +
                    item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) } +
                    ermakCanonicalRelated(item.optString("id"))).distinct()
''', "Ermak systems links")

t = rep(t, '''                    block("Системы", item.array("systemIds").strings()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
                ),
                relatedIds = item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) } +
                    item.array("systemIds").strings()
''', '''                    block("Системы", item.array("systemIds").strings()),
                    block("Покрытие параметров", item.obj("parameterCoverage").summary()),
                    block("Покрытие связей", item.obj("relationCoverage").summary()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
                ),
                relatedIds = (item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) } +
                    item.array("systemIds").strings() + ermakCanonicalRelated(item.optString("id"))).distinct()
''', "Ermak equipment links")

t = rep(t, '''                    addAll(item.obj("futureLinks").allStrings())
                }.distinct()
''', '''                    addAll(item.obj("futureLinks").allStrings())
                    addAll(ermakCanonicalRelated(item.optString("id")))
                }.distinct()
''', "Ermak knowledge links")

# Ermak diagnostics: surface the actual prepared graph/content instead of a small projection only.
t = rep(t, '''                    block("Симптом", item.optString("symptom")),
                    block("Немедленные действия", projection.array("immediateActions").strings()),
                    block("Опасные признаки", projection.array("dangerSigns").strings()),
                    block("Уточнения", projection.array("questions").stringsOrSummaries()),
                    block("Возможные причины", projection.array("probableCauses").strings()),
                    block("Безопасные проверки", projection.array("checks").stringsOrSummaries()),
                    block("Запрещено", projection.array("prohibited").strings()),
                    block("Условия прекращения", projection.array("stopConditions").strings()),
                    block("Что доложить", projection.array("reportFields").strings()),
                    block("Применимость", projection.optString("applicability")),
                    block("Источник", projection.optString("sourceNote"))
''', '''                    block("Симптом", item.optString("symptom")),
                    block("Наблюдаемые признаки", projection.array("observableSigns").strings()),
                    block("Немедленные действия", projection.array("immediateActions").strings()),
                    block("Опасные признаки", projection.array("dangerSigns").strings()),
                    block("Уточнения", projection.array("questions").stringsOrSummaries()),
                    block("Возможные причины", (item.array("possibleCauses").stringsOrSummaries() + projection.array("probableCauses").strings()).distinct()),
                    block("Безопасные проверки", projection.array("checks").stringsOrSummaries()),
                    block("Подтверждённые действия", item.array("actions").stringsOrSummaries()),
                    block("Результат / дальнейшая оценка", item.optString("outcome")),
                    block("Объяснение системы", projection.array("systemExplanation").strings()),
                    block("Эксплуатационные последствия", projection.array("operationalConsequences").strings()),
                    block("Ветвление диагностики", item.obj("graph").array("nodes").stringsOrSummaries()),
                    block("Запрещено", projection.array("prohibited").strings()),
                    block("Условия прекращения", projection.array("stopConditions").strings()),
                    block("Что доложить", projection.array("reportFields").strings()),
                    block("Учебные заметки", projection.array("trainingNotes").strings()),
                    block("Контрольные вопросы", projection.array("feedbackPrompts").strings()),
                    block("Применимость", item.obj("applicability").summary()),
                    block("Ограничение по возрасту источника", item.optString("sourceAgeNote")),
                    block("Источник", projection.optString("sourceNote"))
''', "Ermak diagnostics content")

t = rep(t, '''                    addAll(item.array("relatedScenarioIds").strings())
                }.distinct()
''', '''                    addAll(item.array("relatedScenarioIds").strings())
                    addAll(ermakCanonicalRelated(item.optString("id")))
                }.distinct()
''', "Ermak diagnostic canonical links")

# Ermak schemes: expose hotspots/flows and Stage 7 vetted links.
t = rep(t, '''                    block("Тип", type),
                    block("Системы", item.array("systemIds").strings()),
                    block("Применимость", item.obj("variantRules").summary()),
                    block("Оборудование", item.array("equipmentRefs").strings()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries()),
                    block("Покрытие", item.obj("coverage").summary())
                ),
                relatedIds = item.array("equipmentRefs").strings(),
                sequence = sequence.distinct()
''', '''                    block("Тип", type),
                    block("Системы", item.array("systemIds").strings()),
                    block("Применимость", item.obj("variantRules").summary()),
                    block("Оборудование", item.array("equipmentRefs").strings()),
                    block("Узлы схемы", hotspots.map { hotspot ->
                        listOf(hotspot.optString("label"), hotspot.optString("schemeDesignation"), hotspot.optString("equipmentId"))
                            .filter(String::isNotBlank).joinToString(" • ")
                    }),
                    block("Режимы / потоки", flow.map { flowStep ->
                        listOf(flowStep.optString("title"), flowStep.optString("note")).filter(String::isNotBlank).joinToString(" — ")
                    }),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries()),
                    block("Покрытие", item.obj("coverage").summary())
                ),
                relatedIds = (item.array("equipmentRefs").strings() + ermakCanonicalRelated(item.optString("id"))).distinct(),
                sequence = sequence.distinct(),
                sequenceKind = "SCHEME"
''', "Ermak scheme content")

# Generic scheme adapter: distinguish scheme navigation from acceptance and merge canonical links.
t = rep(t, '''    private fun schemeEntry(
        item: JSONObject,
        family: TechnicalFamily,
        section: TechnicalSection,
        edgeKey: String
    ): TechnicalEntry {
        val nodes = item.array("nodes").objects()
        val sequence = nodes.mapNotNull { node ->
            node.optString("equipmentId").takeIf(String::isNotBlank)
                ?: node.optString("virtualNodeId").takeIf(String::isNotBlank)
        }
''', '''    private fun schemeEntry(
        item: JSONObject,
        family: TechnicalFamily,
        section: TechnicalSection,
        edgeKey: String,
        extraBlocks: List<TechnicalBlock> = emptyList()
    ): TechnicalEntry {
        val nodes = item.array("nodes").objects()
        val sequence = nodes.mapNotNull { node -> node.optString("equipmentId").takeIf(String::isNotBlank) }
''', "schemeEntry signature")

t = rep(t, '''                block("Связи", item.array(edgeKey).stringsOrSummaries()),
                block("Источники", item.array("sourceRefs").stringsOrSummaries())
            ),
            relatedIds = sequence,
            sequence = sequence
''', '''                block("Связи", item.array(edgeKey).stringsOrSummaries()),
                block("Источники", item.array("sourceRefs").stringsOrSummaries())
            ) + extraBlocks,
            relatedIds = (sequence + if (family == TechnicalFamily.VL80S) vl80CanonicalRelated(item.optString("id")) else ermakCanonicalRelated(item.optString("id"))).distinct(),
            sequence = sequence,
            sequenceKind = "SCHEME"
''', "schemeEntry result")

# Thread sequence kind through the normal entry factory.
t = rep(t, '''        relatedIds: List<String> = emptyList(),
        sequence: List<String> = emptyList()
    ): TechnicalEntry {''', '''        relatedIds: List<String> = emptyList(),
        sequence: List<String> = emptyList(),
        sequenceKind: String = ""
    ): TechnicalEntry {''', "entry factory signature")

t = rep(t, '''            relatedIds = relatedIds.filter(String::isNotBlank).distinct(),
            sequence = sequence.filter(String::isNotBlank).distinct(),
            searchText = search
''', '''            relatedIds = relatedIds.filter(String::isNotBlank).distinct(),
            sequence = sequence.filter(String::isNotBlank).distinct(),
            sequenceKind = sequenceKind,
            searchText = search
''', "entry factory result")

write(rel, t)

# ---------------------------------------------------------------------------
# Technical UI: routes/list mode, 5-state persisted acceptance, scheme sequence.
# ---------------------------------------------------------------------------
rel = "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
t = read(rel)

t = rep(t, '''    var query by rememberSaveable { mutableStateOf("") }
    var selectedId by rememberSaveable(initialEntryId) { mutableStateOf(initialEntryId) }
''', '''    var query by rememberSaveable { mutableStateOf("") }
    var acceptanceShowAll by rememberSaveable { mutableStateOf(false) }
    var selectedId by rememberSaveable(initialEntryId) { mutableStateOf(initialEntryId) }
''', "acceptance list state")

t = rep(t, '''    val visible = remember(family, selectedSection, query) {
        val loaded = repository.entries(family, selectedSection, query)
        if (selectedSection == TechnicalSection.ACCEPTANCE && query.isBlank()) loaded.filter { it.status == "ROUTE" } else loaded
    }
''', '''    val visible = remember(family, selectedSection, query, acceptanceShowAll) {
        val loaded = repository.entries(family, selectedSection, query)
        if (selectedSection == TechnicalSection.ACCEPTANCE && query.isBlank() && !acceptanceShowAll) {
            loaded.filter { it.status == "ROUTE" }
        } else if (selectedSection == TechnicalSection.ACCEPTANCE && acceptanceShowAll) {
            loaded.filterNot { it.status == "ROUTE" }
        } else loaded
    }
''', "acceptance visible")

marker = '''        item {
            OutlinedTextField(
                value = query,
'''
replacement = '''        if (selectedSection == TechnicalSection.ACCEPTANCE) {
            item {
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    item {
                        FilterChip(
                            selected = !acceptanceShowAll,
                            onClick = { acceptanceShowAll = false; query = "" },
                            label = { Text("Маршруты") }
                        )
                    }
                    item {
                        FilterChip(
                            selected = acceptanceShowAll,
                            onClick = { acceptanceShowAll = true; query = "" },
                            label = { Text("Все пункты") }
                        )
                    }
                }
            }
        }
        item {
            OutlinedTextField(
                value = query,
'''
t = rep(t, marker, replacement, "acceptance mode chips")

t = rep(t, '''                "${selectedSection.title}: ${visible.size}",
''', '''                "${selectedSection.title}: показано ${visible.size} из ${repository.count(family, selectedSection)}",
''', "section count")

t = rep(t, '''    val relatedEntries = entry.relatedIds
        .distinct()
        .mapNotNull(repository::entry)
        .filterNot { it.id in referencedIds }
        .take(40)
''', '''    val relatedEntries = entry.relatedIds
        .distinct()
        .mapNotNull(repository::entry)
        .filterNot { it.id in referencedIds }
''', "remove link truncation")

t = rep(t, '''        if (entry.sequence.isNotEmpty()) {
            item { TechnicalSequence(entry, repository, onOpen) }
        }
''', '''        if (entry.sequence.isNotEmpty()) {
            item {
                if (entry.sequenceKind == "ACCEPTANCE") AcceptanceSequence(entry, repository, onOpen)
                else TechnicalSequence(entry, repository, onOpen)
            }
        }
''', "sequence dispatcher")

start = t.index('@Composable\nprivate fun TechnicalSequence')
end = t.index('\n@Composable\nprivate fun technicalBlockContainer', start)
old = t[start:end]
new = r'''@Composable
private fun AcceptanceSequence(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {
    val context = LocalContext.current
    val prefs = remember(entry.id) { context.getSharedPreferences("vl80s_acceptance_progress", android.content.Context.MODE_PRIVATE) }
    var step by rememberSaveable(entry.id) { mutableIntStateOf(prefs.getInt("${entry.id}:step", 0).coerceIn(entry.sequence.indices)) }
    val currentId = entry.sequence[step.coerceIn(entry.sequence.indices)]
    val target = repository.entry(currentId)
    val stateKey = "${entry.id}:$currentId:state"
    val noteKey = "${entry.id}:$currentId:note"
    val resolutionKey = "${entry.id}:$currentId:resolution"
    var state by remember(currentId) { mutableStateOf(prefs.getString(stateKey, "NOT_CHECKED") ?: "NOT_CHECKED") }
    var note by remember(currentId) { mutableStateOf(prefs.getString(noteKey, "") ?: "") }
    var resolution by remember(currentId) { mutableStateOf(prefs.getString(resolutionKey, "") ?: "") }
    val accent = technicalSectionAccent(entry.section, entry.status)
    val completed = entry.sequence.count { id -> (prefs.getString("${entry.id}:$id:state", "NOT_CHECKED") ?: "NOT_CHECKED") != "NOT_CHECKED" }
    val requiresNote = state == "NOTE" || state == "NOT_APPLICABLE"
    val requiresResolution = state == "BLOCKING"
    val canAdvance = (!requiresNote || note.isNotBlank()) && (!requiresResolution || (note.isNotBlank() && resolution.isNotBlank()))

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
            val stateLabel = when (state) {
                "OK" -> "Проверено"
                "NOTE" -> "Замечание"
                "BLOCKING" -> "Блокирующее замечание"
                "NOT_APPLICABLE" -> "Не применяется"
                else -> "Не проверено"
            }
            Text("Состояние: $stateLabel", color = accent, fontWeight = FontWeight.Bold)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                item { FilterChip(state == "NOT_CHECKED", { persistState("NOT_CHECKED") }, label = { Text("Не проверено") }) }
                item { FilterChip(state == "OK", { persistState("OK") }, label = { Text("Проверено") }) }
                item { FilterChip(state == "NOTE", { persistState("NOTE") }, label = { Text("Замечание") }) }
                item { FilterChip(state == "BLOCKING", { persistState("BLOCKING") }, label = { Text("Блокирующее") }) }
                item { FilterChip(state == "NOT_APPLICABLE", { persistState("NOT_APPLICABLE") }, label = { Text("Не применяется") }) }
            }
            if (state == "NOTE" || state == "BLOCKING" || state == "NOT_APPLICABLE") {
                OutlinedTextField(
                    value = note,
                    onValueChange = { note = it; prefs.edit().putString(noteKey, it).apply() },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text(if (state == "NOT_APPLICABLE") "Причина" else "Комментарий и локализация") },
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
                if (!canAdvance) Text("Блокирующее замечание нельзя закрыть без комментария и оформленного решения.", color = MaterialTheme.colorScheme.error)
            } else if (!canAdvance) {
                Text("Для этого состояния требуется комментарий.", color = MaterialTheme.colorScheme.error)
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { move(step - 1) }, enabled = step > 0) { Text("Назад") }
                Button(onClick = { move(step + 1) }, enabled = step < entry.sequence.lastIndex && canAdvance) { Text("Далее") }
            }
            if (target != null) OutlinedButton(onClick = { onOpen(target) }, modifier = Modifier.fillMaxWidth()) { Text("Открыть полную карточку") }
        }
    }
}

@Composable
private fun TechnicalSequence(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {
    var step by rememberSaveable(entry.id) { mutableIntStateOf(0) }
    val currentId = entry.sequence[step.coerceIn(entry.sequence.indices)]
    val target = repository.entry(currentId)
    val accent = technicalSectionAccent(entry.section, entry.status)
    val heading = when (entry.section) {
        TechnicalSection.ELECTRICAL -> "Узлы электрической схемы"
        TechnicalSection.PNEUMATIC -> "Узлы пневматической схемы"
        else -> "Связанные элементы"
    }
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = technicalSectionContainer(entry.section)),
        border = BorderStroke(1.dp, accent.copy(alpha = .45f)),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text(heading, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
            Text("Элемент ${step + 1} из ${entry.sequence.size}", color = accent)
            Text(target?.let(::technicalEntryTitle) ?: "Элемент схемы", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
            target?.let { item ->
                technicalEntrySubtitle(item)?.let { Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                OutlinedButton(onClick = { onOpen(item) }, modifier = Modifier.fillMaxWidth()) { Text("Открыть карточку оборудования") }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { if (step > 0) step-- }, enabled = step > 0) { Text("Назад") }
                Button(onClick = { if (step < entry.sequence.lastIndex) step++ }, enabled = step < entry.sequence.lastIndex) { Text("Далее") }
            }
        }
    }
}
'''
t = t[:start] + new + t[end:]

write(rel, t)

# Give beta builds a unique identity in screenshots/artifacts without touching production.
gradle_rel = "app/build.gradle.kts"
g = read(gradle_rel)
g = re.sub(r'versionName\s*=\s*"1\.2\.2-dev18"', 'versionName = "1.2.2-beta-recovery1"', g, count=1)
write(gradle_rel, g)

print("Recovery patch applied")
