package ru.railbrake.calculator.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.produceState
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import ru.railbrake.calculator.core.TechnicalDataRepository
import ru.railbrake.calculator.core.TechnicalEntry
import ru.railbrake.calculator.core.TechnicalFamily
import ru.railbrake.calculator.core.TechnicalSection
import ru.railbrake.calculator.core.technicalEntrySubtitle
import ru.railbrake.calculator.core.technicalEntryTitle
import ru.railbrake.calculator.core.technicalPresentationLine
import ru.railbrake.calculator.core.technicalStatusPresentation
import ru.railbrake.calculator.data.AcceptanceCheckState
import ru.railbrake.calculator.data.AcceptanceStateRepository
import ru.railbrake.calculator.data.acceptanceSummary

@Composable
fun TechnicalCatalogScreen(
    initialFamily: TechnicalFamily = TechnicalFamily.VL80S,
    initialSection: TechnicalSection = TechnicalSection.EQUIPMENT,
    sectionBackLabel: String = "Локомотивы / атлас",
    onSectionBack: () -> Unit,
    lockFamily: Boolean = false,
    lockSection: Boolean = false,
    initialEntryId: String? = null,
    onOpenLegacyArticle: ((String) -> Unit)? = null,
    onOpenDiagnosticScenario: ((String, String, TechnicalSection) -> Unit)? = null
) {
    val context = LocalContext.current
    val repository = remember { TechnicalDataRepository(context.applicationContext) }
    var familyName by rememberSaveable { mutableStateOf(initialFamily.name) }
    var sectionName by rememberSaveable { mutableStateOf(initialSection.name) }
    var query by rememberSaveable { mutableStateOf("") }
    var selectedId by rememberSaveable(initialEntryId) { mutableStateOf(initialEntryId) }
    var navigationPath by rememberSaveable(initialEntryId) { mutableStateOf("") }
    var acceptanceStartChoice by rememberSaveable { mutableStateOf(false) }
    val family = runCatching { TechnicalFamily.valueOf(familyName) }.getOrDefault(TechnicalFamily.VL80S)
    val availableSections = remember(family, lockSection, initialSection) { if (lockSection) listOf(initialSection) else repository.sections(family) }
    val selectedSection = runCatching { TechnicalSection.valueOf(sectionName) }.getOrNull()?.takeIf(availableSections::contains)
        ?: availableSections.first()
    val selected = selectedId?.let(repository::entry)

    fun openTarget(target: TechnicalEntry) {
        val source = selected
        if (
            target.family == TechnicalFamily.ERMAK &&
            target.section == TechnicalSection.DIAGNOSTICS &&
            source != null &&
            onOpenDiagnosticScenario != null
        ) {
            onOpenDiagnosticScenario(target.id, source.id, source.section)
            return
        }
        source?.id?.let { navigationPath = technicalNavigationPush(navigationPath, it) }
        selectedId = target.id
    }

    fun backFromSelected() {
        val (previousId, remainingPath) = technicalNavigationPop(navigationPath)
        navigationPath = remainingPath
        selectedId = previousId
    }

    BackHandler(enabled = selected != null || acceptanceStartChoice) {
        if (selected != null) backFromSelected() else acceptanceStartChoice = false
    }

    if (acceptanceStartChoice) {
        AcceptanceStartChoice(
            onBack = { acceptanceStartChoice = false },
            onSelect = { selectedId = it; navigationPath = ""; acceptanceStartChoice = false }
        )
        return
    }

    if (selected != null) {
        val previousEntry = technicalNavigationIds(navigationPath).lastOrNull()?.let(repository::entry)
        TechnicalEntryDetail(
            entry = selected,
            repository = repository,
            backLabel = previousEntry?.let { "Назад к «${technicalEntryTitle(it).take(34)}»" } ?: selected.section.title,
            onBack = ::backFromSelected,
            onOpen = ::openTarget
        )
        return
    }

    val visible by produceState<List<TechnicalEntry>?>(initialValue = null, family, selectedSection, query) {
        value = withContext(Dispatchers.Default) {
            val loaded = repository.entries(family, selectedSection, query)
            val filtered = if (selectedSection == TechnicalSection.ACCEPTANCE && query.isBlank()) {
                loaded.filter { it.status == "ROUTE" }
            } else loaded
            filtered.sortedWith(
                compareByDescending<TechnicalEntry> { isErmakLayoutEntry(it.id) }
                    .thenByDescending { it.sequence.isNotEmpty() }
            )
        }
    }
    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        item {
            ChildBackButton(sectionBackLabel, onSectionBack)
            RailSectionHeader(
                "Техническая база ${family.title}",
                "Материалы и связи между разделами"
            )
        }
        item {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(if (lockFamily) listOf(family) else listOf(TechnicalFamily.VL80S, TechnicalFamily.ERMAK)) { option ->
                    FilterChip(
                        selected = family == option,
                        onClick = {
                            familyName = option.name
                            val sections = repository.sections(option)
                            if (runCatching { TechnicalSection.valueOf(sectionName) }.getOrNull() !in sections) sectionName = sections.first().name
                            query = ""
                        },
                        label = { Text(option.title) }
                    )
                }
            }
        }
        item {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(availableSections) { option ->
                    val accent = technicalSectionAccent(option, "")
                    FilterChip(
                        selected = selectedSection == option,
                        onClick = { sectionName = option.name; query = "" },
                        colors = FilterChipDefaults.filterChipColors(selectedContainerColor = accent.copy(alpha = 0.22f), selectedLabelColor = accent),
                        label = { Text(option.title, color = if (selectedSection == option) accent else MaterialTheme.colorScheme.onSurfaceVariant) }
                    )
                }
            }
        }
        item {
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Поиск по названию, аппарату или признаку") },
                trailingIcon = {
                    if (query.isNotEmpty()) {
                        IconButton(onClick = { query = "" }) {
                            Text("×", style = MaterialTheme.typography.titleLarge)
                        }
                    }
                },
                shape = RoundedCornerShape(16.dp)
            )
        }
        item {
            Text(
                if (visible == null) "${selectedSection.title}: загрузка…" else "${selectedSection.title}: ${visible!!.size}",
                style = MaterialTheme.typography.labelLarge,
                color = technicalSectionAccent(selectedSection, ""),
                fontWeight = FontWeight.Bold
            )
        }
        if (visible == null) {
            item { LinearProgressIndicator(modifier = Modifier.fillMaxWidth()) }
        } else if (visible!!.isEmpty()) {
            item {
                InfoCard(
                    "Ничего не найдено",
                    listOf("Измените запрос или выберите другой раздел."),
                    MaterialTheme.colorScheme.surfaceVariant
                )
            }
        }
        interactiveLegacyShortcuts(family, selectedSection).forEach { shortcut ->
            item(key = "interactive-${shortcut.articleId}") {
                Card(
                    onClick = { onOpenLegacyArticle?.invoke(shortcut.articleId) },
                    enabled = onOpenLegacyArticle != null,
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(18.dp),
                    colors = CardDefaults.cardColors(containerColor = InteractiveSchemeContainer),
                    border = BorderStroke(2.dp, InteractiveSchemeAccent)
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                        Text("ИНТЕРАКТИВНАЯ СХЕМА", style = MaterialTheme.typography.labelSmall, color = InteractiveSchemeAccent, fontWeight = FontWeight.Black)
                        Text(shortcut.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                        Text(shortcut.subtitle, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        Text("Открыть интерактивную схему →", color = InteractiveSchemeAccent, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
        items(visible.orEmpty(), key = { it.id }) { entry ->
            val accent = technicalSectionAccent(entry.section, entry.status)
            val interactive = entry.sequence.isNotEmpty() && entry.section != TechnicalSection.ACCEPTANCE
            Card(
                onClick = {
                    if (entry.id == "VL80-ROUTE-route_canonical") acceptanceStartChoice = true
                    else {
                        navigationPath = ""
                        selectedId = entry.id
                    }
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = if (interactive) InteractiveSchemeContainer else technicalSectionContainer(entry.section)),
                border = BorderStroke(if (interactive) 2.dp else 1.dp, if (interactive) InteractiveSchemeAccent else accent.copy(alpha = 0.52f))
            ) {
                Column(Modifier.padding(15.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    if (interactive) {
                        Text("ИНТЕРАКТИВНАЯ СХЕМА", style = MaterialTheme.typography.labelSmall, color = InteractiveSchemeAccent, fontWeight = FontWeight.Black)
                    } else technicalStatusLabel(entry.status)?.let { status ->
                        Text(status, style = MaterialTheme.typography.labelSmall, color = accent)
                    }
                    Text(technicalEntryTitle(entry), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                    technicalEntrySubtitle(entry)?.let { subtitle ->
                        Text(subtitle, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    Text(if (interactive) "Открыть интерактивную схему →" else "Открыть карточку →", color = if (interactive) InteractiveSchemeAccent else accent, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

private val InteractiveSchemeContainer = Color(0xFF17363A)
private val InteractiveSchemeAccent = Color(0xFF65E3D2)

internal data class InteractiveLegacyShortcut(val articleId: String, val title: String, val subtitle: String)

internal fun interactiveLegacyShortcuts(family: TechnicalFamily, section: TechnicalSection): List<InteractiveLegacyShortcut> = when {
    family == TechnicalFamily.VL80S && section == TechnicalSection.EQUIPMENT -> listOf(
        InteractiveLegacyShortcut(
            articleId = "vl80-layout",
            title = "Расположение оборудования ВЛ80С",
            subtitle = "Схема секции с кликабельными зонами, краткой сводкой и переходом к подробному описанию."
        )
    )
    family == TechnicalFamily.VL80S && section == TechnicalSection.PNEUMATIC -> listOf(
        InteractiveLegacyShortcut(
            articleId = "vl80-pneumatic-simulator",
            title = "Интерактивная пневмосхема ВЛ80С",
            subtitle = "Пошаговое движение воздуха, указатели маршрута и кликабельные приборы."
        )
    )
    family == TechnicalFamily.VL80S && section == TechnicalSection.ELECTRICAL -> listOf(
        InteractiveLegacyShortcut(
            articleId = "vl80-electrical-simulator",
            title = "Интерактивная электросхема ВЛ80С",
            subtitle = "Пошаговый разбор цепи с переходами между связанными элементами."
        )
    )
    else -> emptyList()
}

@Composable
private fun AcceptanceStartChoice(onBack: () -> Unit, onSelect: (String) -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        ChildBackButton("Приёмка", onBack)
        RailSectionHeader("Полная приёмка", "Выберите точку начала маршрута")
        Card(
            onClick = { onSelect("VL80-ROUTE-route_from_outside") },
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                Text("Начать снаружи", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
                Text("Последовательный маршрут от наружного осмотра к кабине.")
            }
        }
        Card(
            onClick = { onSelect("VL80-ROUTE-route_from_cab") },
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer),
            shape = RoundedCornerShape(18.dp)
        ) {
            Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                Text("Начать из кабины", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
                Text("Последовательный маршрут от органов управления к наружным зонам.")
            }
        }
    }
}

@Composable
private fun TechnicalEntryDetail(
    entry: TechnicalEntry,
    repository: TechnicalDataRepository,
    backLabel: String,
    onBack: () -> Unit,
    onOpen: (TechnicalEntry) -> Unit
) {
    val accent = technicalSectionAccent(entry.section, entry.status)
    val referencedIds = entry.blocks
        .flatMap { repository.referencedEntries(it.lines) }
        .map { it.id }
        .toSet()
    val relatedEntries = entry.relatedIds
        .distinct()
        .mapNotNull(repository::entry)
        .filterNot { it.id == entry.id || it.id in referencedIds }
        .sortedWith(
            compareBy<TechnicalEntry> { technicalRelatedSectionOrder(it.section) }
                .thenBy { technicalEntryTitle(it).lowercase() }
        )
    val relatedGroups = relatedEntries.groupBy(TechnicalEntry::section)
        .toList()
        .sortedBy { (section, _) -> technicalRelatedSectionOrder(section) }

    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            ChildBackButton(backLabel, onBack)
            Text(technicalEntryTitle(entry), style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Black)
            technicalEntrySubtitle(entry)?.let { subtitle ->
                Text(subtitle, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            technicalStatusLabel(entry.status)?.let { status ->
                RailStatusPill(status, accent = accent)
            }
        }
        if (entry.id.startsWith("ER-SCH-LAYOUT-") && entry.hotspots.isNotEmpty()) {
            item { ErmakInteractiveAtlas(entry, repository, onOpen) }
        } else if (entry.section == TechnicalSection.ACCEPTANCE && entry.sequence.isNotEmpty()) {
            item { TechnicalSequence(entry, repository) }
        } else if (entry.sequence.isNotEmpty()) {
            item { TechnicalSequenceLinks(entry, repository, onOpen) }
        }
        repository.ermakSchemeLinkContext(entry.id)
            ?.takeIf { it.diagnosticLinks.isNotEmpty() }
            ?.let { linkContext ->
                item(key = "scheme-diagnostics-${entry.id}") {
                    ErmakSchemeDiagnostics(entry, linkContext, repository, onOpen)
                }
            }
        items(entry.blocks, key = { it.title }) { block ->
            val displayLines = repository.displayLines(block.lines)
                .mapNotNull(::technicalPresentationLine)
                .distinct()
            val references = repository.referencedEntries(block.lines)
            val referenceTableRows = if (block.title.startsWith("Таблица —")) {
                block.lines.mapNotNull { line ->
                    line.split("¦", limit = 3).takeIf { it.size == 3 }
                }
            } else emptyList()
            if (displayLines.isEmpty() && references.isEmpty() && referenceTableRows.isEmpty()) return@items
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = technicalBlockContainer(entry.section, block.title)),
                border = BorderStroke(1.dp, accent.copy(alpha = 0.38f)),
                shape = RoundedCornerShape(18.dp)
            ) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                    Text(block.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                    if (referenceTableRows.isNotEmpty()) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Размер", modifier = Modifier.weight(0.75f), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Black)
                            Text("Скорость", modifier = Modifier.weight(0.9f), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Black)
                            Text("Действие", modifier = Modifier.weight(1.55f), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Black)
                        }
                        HorizontalDivider()
                        referenceTableRows.forEachIndexed { index, cells ->
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(cells[0], modifier = Modifier.weight(0.75f), style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
                                Text(cells[1], modifier = Modifier.weight(0.9f), style = MaterialTheme.typography.bodySmall)
                                Text(cells[2], modifier = Modifier.weight(1.55f), style = MaterialTheme.typography.bodySmall)
                            }
                            if (index != referenceTableRows.lastIndex) HorizontalDivider()
                        }
                    } else {
                        displayLines.forEach { line -> Text("• $line") }
                        references.forEach { target ->
                            OutlinedButton(
                                onClick = { onOpen(target) },
                                modifier = Modifier.fillMaxWidth(),
                                border = BorderStroke(1.dp, Color.Black)
                            ) { Text("${technicalEntryTitle(target)} →") }
                        }
                    }
                }
            }
        }
        if (relatedGroups.isNotEmpty()) {
            item {
                HorizontalDivider()
                Text("Связанные материалы", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
                Text(
                    "Материалы сгруппированы по назначению; уже показанные внутри карточки ссылки здесь не повторяются.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            relatedGroups.forEach { (section, targets) ->
                item(key = "related-header-${entry.id}-${section.name}") {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(section.title, fontWeight = FontWeight.Bold, color = technicalSectionAccent(section, ""))
                        Text("${targets.size}", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
                items(targets, key = { "related-${section.name}-${it.id}" }) { target ->
                    OutlinedButton(
                        onClick = { onOpen(target) },
                        modifier = Modifier.fillMaxWidth(),
                        border = BorderStroke(1.dp, Color.Black)
                    ) {
                        Text("${technicalEntryTitle(target)} →")
                    }
                }
            }
        }
    }
}

internal fun technicalNavigationIds(path: String): List<String> =
    path.lineSequence().map(String::trim).filter(String::isNotBlank).toList()

internal fun technicalNavigationPush(path: String, currentId: String): String =
    (technicalNavigationIds(path) + currentId).joinToString("\n")

internal fun technicalNavigationPop(path: String): Pair<String?, String> {
    val ids = technicalNavigationIds(path)
    return ids.lastOrNull() to ids.dropLast(1).joinToString("\n")
}

internal fun technicalRelatedSectionOrder(section: TechnicalSection): Int = when (section) {
    TechnicalSection.SYSTEMS -> 0
    TechnicalSection.EQUIPMENT -> 1
    TechnicalSection.KNOWLEDGE -> 2
    TechnicalSection.DIAGNOSTICS -> 3
    TechnicalSection.ELECTRICAL, TechnicalSection.PNEUMATIC -> 4
    TechnicalSection.SAFETY -> 5
    TechnicalSection.PROFILES -> 6
    TechnicalSection.ACCEPTANCE -> 7
}

internal fun isErmakLayoutEntry(id: String): Boolean = id.startsWith("ER-SCH-LAYOUT-")

internal val ErmakAtlasVariants = listOf(
    "ER-SCH-LAYOUT-2ES5K-BASE" to "2ЭС5К",
    "ER-SCH-LAYOUT-3ES5K-HEAD" to "3ЭС5К · головная",
    "ER-SCH-LAYOUT-3ES5K-BOOSTER" to "3ЭС5К · бустерная"
)

@Composable
private fun ErmakInteractiveAtlas(
    entry: TechnicalEntry,
    repository: TechnicalDataRepository,
    onOpen: (TechnicalEntry) -> Unit
) {
    var selectedId by rememberSaveable(entry.id) { mutableStateOf(entry.hotspots.firstOrNull()?.equipmentId) }
    var query by rememberSaveable(entry.id) { mutableStateOf("") }
    val selectedHotspot = entry.hotspots.firstOrNull { it.equipmentId == selectedId }
    val selectedEquipment = selectedHotspot?.let { repository.entry(it.equipmentId) }
    val visible = entry.hotspots.filter {
        query.isBlank() || it.label.contains(query, ignoreCase = true) || it.equipmentId.contains(query, ignoreCase = true)
    }
    val maxX = entry.hotspots.maxOfOrNull { it.x + it.width }?.coerceAtLeast(1) ?: 1
    val maxY = entry.hotspots.maxOfOrNull { it.y + it.height }?.coerceAtLeast(1) ?: 1
    val scale = 0.62f
    val mapWidth = maxX * scale
    val mapHeight = maxY * scale
    val horizontal = rememberScrollState()

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = InteractiveSchemeContainer),
        border = BorderStroke(2.dp, InteractiveSchemeAccent),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Интерактивный атлас «Ермак»", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
            Text(
                "Функциональная карта по встроенным данным компоновки. Зоны показывают принадлежность оборудования, но не заменяют заводской монтажный чертёж.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text("Исполнение и секция", color = InteractiveSchemeAccent, fontWeight = FontWeight.Bold)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(ErmakAtlasVariants) { (id, label) ->
                    val target = repository.entry(id)
                    FilterChip(
                        selected = entry.id == id,
                        onClick = { target?.let(onOpen) },
                        enabled = target != null,
                        label = { Text(label) }
                    )
                }
            }
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Найти аппарат на карте") }
            )
            Text("Элементов: ${entry.hotspots.size}", style = MaterialTheme.typography.labelMedium, color = InteractiveSchemeAccent)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(horizontal)
                    .background(Color(0xFF0D1F22), RoundedCornerShape(14.dp))
            ) {
                Box(Modifier.width(mapWidth.dp).height(mapHeight.dp)) {
                    entry.hotspots.forEach { hotspot ->
                        val selected = hotspot.equipmentId == selectedId
                        val matched = hotspot in visible
                        Box(
                            modifier = Modifier
                                .offset(x = (hotspot.x * scale).dp, y = (hotspot.y * scale).dp)
                                .size(width = (hotspot.width * scale).dp, height = (hotspot.height * scale).dp)
                                .background(
                                    color = when {
                                        selected -> InteractiveSchemeAccent.copy(alpha = 0.72f)
                                        matched -> InteractiveSchemeAccent.copy(alpha = 0.20f)
                                        else -> Color(0xFF243336)
                                    },
                                    shape = RoundedCornerShape(7.dp)
                                )
                                .clickable { selectedId = hotspot.equipmentId }
                                .padding(horizontal = 5.dp, vertical = 3.dp)
                        ) {
                            Text(
                                hotspot.label,
                                style = MaterialTheme.typography.labelSmall,
                                color = if (selected) Color(0xFF071313) else MaterialTheme.colorScheme.onSurface,
                                maxLines = 2,
                                overflow = TextOverflow.Ellipsis
                            )
                        }
                    }
                }
            }
            selectedHotspot?.let { hotspot ->
                Text(hotspot.label, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                selectedEquipment?.let { equipment ->
                    technicalEntrySubtitle(equipment)?.let {
                        Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                    OutlinedButton(
                        onClick = { onOpen(equipment) },
                        modifier = Modifier.fillMaxWidth(),
                        border = BorderStroke(1.dp, Color.Black)
                    ) { Text("Подробнее") }
                } ?: Text(
                    "Для выбранной зоны отдельная карточка оборудования пока отсутствует.",
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            if (query.isNotBlank()) {
                Text("Результаты поиска", fontWeight = FontWeight.Bold)
                visible.take(20).forEach { hotspot ->
                    OutlinedButton(
                        onClick = { selectedId = hotspot.equipmentId },
                        modifier = Modifier.fillMaxWidth(),
                        border = BorderStroke(1.dp, Color.Black)
                    ) { Text(hotspot.label) }
                }
                if (visible.size > 20) Text("Показаны первые 20 из ${visible.size}", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun ErmakSchemeDiagnostics(
    entry: TechnicalEntry,
    linkContext: ru.railbrake.calculator.core.ErmakSchemeLinkContext,
    repository: TechnicalDataRepository,
    onOpen: (TechnicalEntry) -> Unit
) {
    var executionConfirmed by rememberSaveable(entry.id, "ermak-scheme-execution") { mutableStateOf(false) }
    var query by rememberSaveable(entry.id, "ermak-scheme-diagnostics-query") { mutableStateOf("") }
    val gatedCount = linkContext.diagnosticLinks.count { it.profileGateRequired }
    val directCount = linkContext.diagnosticLinks.size - gatedCount
    val available = linkContext.diagnosticLinks
        .filter { !it.profileGateRequired || executionConfirmed }
        .mapNotNull { link -> repository.entry(link.diagnosticId) }
        .distinctBy(TechnicalEntry::id)
    val visible = available.filter { target ->
        query.isBlank() || target.searchText.contains(query.trim(), ignoreCase = true)
    }
    val modelText = linkContext.models.map(::ermakSchemeModelLabel).distinct().joinToString(" / ")

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = technicalBlockContainer(entry.section, "Диагностика")),
        border = BorderStroke(1.dp, InteractiveSchemeAccent.copy(alpha = 0.65f)),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(9.dp)) {
            Text("Диагностика по схеме", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
            Text(
                "Сразу доступно: $directCount • после подтверждения исполнения: $gatedCount",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            if (gatedCount > 0) {
                if (!executionConfirmed) {
                    if (modelText.isNotBlank()) {
                        Text("Серия схемы: $modelText", fontWeight = FontWeight.Bold)
                    }
                    Text(
                        "Часть переходов зависит от фактического исполнения. Подтверждайте только если открытая схема соответствует установленному на локомотиве оборудованию. Подтверждение действует только для этой схемы.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    OutlinedButton(
                        onClick = { executionConfirmed = true },
                        modifier = Modifier.fillMaxWidth(),
                        border = BorderStroke(1.dp, InteractiveSchemeAccent)
                    ) {
                        Text("Подтвердить соответствие исполнения")
                    }
                    Text(
                        "Скрыто до подтверждения: $gatedCount",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } else {
                    Text(
                        "Исполнение подтверждено для этой схемы. Профильные диагностические переходы разблокированы.",
                        color = InteractiveSchemeAccent,
                        fontWeight = FontWeight.Bold
                    )
                    TextButton(onClick = { executionConfirmed = false }) {
                        Text("Сбросить подтверждение")
                    }
                }
            }
            if (available.isNotEmpty()) {
                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text("Найти диагностический сценарий") }
                )
                visible.take(20).forEach { target ->
                    OutlinedButton(
                        onClick = { onOpen(target) },
                        modifier = Modifier.fillMaxWidth(),
                        border = BorderStroke(1.dp, Color.Black)
                    ) {
                        Text("${technicalEntryTitle(target)} →")
                    }
                }
                if (visible.size > 20) {
                    Text(
                        "Показаны первые 20 из ${visible.size}; уточните поиск.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            } else {
                Text(
                    "Для текущего состояния доступных диагностических переходов нет.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

internal fun ermakSchemeModelLabel(value: String): String = when (value) {
    "2ES5K" -> "2ЭС5К"
    "3ES5K" -> "3ЭС5К"
    else -> value
}

@Composable
private fun TechnicalSequenceLinks(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {
    if (entry.sequence.isEmpty()) return
    var step by rememberSaveable(entry.id) { mutableIntStateOf(0) }
    var query by rememberSaveable(entry.id) { mutableStateOf("") }
    val steps = entry.sequence.map { id ->
        val target = repository.entry(id)
        val label = target?.let(::technicalEntryTitle)
            ?: entry.sequenceLabels[id]?.let(::technicalPresentationLine)
            ?: "Узел схемы"
        Triple(id, label, target)
    }
    val visible = steps.filter { (_, label, _) -> query.isBlank() || label.contains(query, ignoreCase = true) }
    val safeStep = step.coerceIn(steps.indices)
    val current = steps[safeStep]
    val accent = technicalSectionAccent(entry.section, entry.status)
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, accent.copy(alpha = 0.55f)),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Интерактивная схема", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
            Text("Узел ${safeStep + 1} из ${steps.size}", color = accent, fontWeight = FontWeight.Bold)
            Text(current.second, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
            current.third?.let { target ->
                technicalEntrySubtitle(target)?.let { Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                OutlinedButton(
                    onClick = { onOpen(target) },
                    modifier = Modifier.fillMaxWidth(),
                    border = BorderStroke(1.dp, Color.Black)
                ) {
                    Text("Открыть карточку оборудования")
                }
            } ?: Text(
                "Служебный узел маршрута; отдельная карточка оборудования не предусмотрена.",
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { step-- }, enabled = safeStep > 0) { Text("Назад") }
                Button(onClick = { step++ }, enabled = safeStep < steps.lastIndex) { Text("Далее") }
                TextButton(onClick = { step = 0 }) { Text("Сбросить") }
            }
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text("Найти узел или аппарат") }
            )
            visible.forEach { (id, label, target) ->
                OutlinedButton(
                    onClick = {
                        step = steps.indexOfFirst { it.first == id }.coerceAtLeast(0)
                        query = ""
                    },
                    modifier = Modifier.fillMaxWidth(),
                    border = BorderStroke(1.dp, Color.Black)
                ) {
                    Text(if (target == null) label else "$label →")
                }
            }
        }
    }
}

@Composable
private fun TechnicalSequence(entry: TechnicalEntry, repository: TechnicalDataRepository) {
    val context = LocalContext.current
    val acceptanceRepository = remember(context) { AcceptanceStateRepository(context.applicationContext) }
    var step by rememberSaveable(entry.id) { mutableIntStateOf(0) }
    var stateVersion by rememberSaveable(entry.id) { mutableIntStateOf(0) }
    var showFullChecklist by rememberSaveable(entry.id) { mutableStateOf(false) }
    var checklistQuery by rememberSaveable(entry.id) { mutableStateOf("") }
    val currentId=entry.sequence[step.coerceIn(entry.sequence.indices)]
    val target=repository.entry(currentId)
    val accent=technicalSectionAccent(entry.section,entry.status)
    val currentState = stateVersion.let { acceptanceRepository.state(currentId) }
    val checklistItems = entry.sequence.mapNotNull { id -> repository.entry(id)?.let { id to it } }
    val states = stateVersion.let { entry.sequence.map(acceptanceRepository::state) }
    val summary = acceptanceSummary(states)
    val visibleItems = checklistItems.filter { (_, item) ->
        checklistQuery.isBlank() || technicalEntryTitle(item).contains(checklistQuery, ignoreCase = true) ||
            technicalEntrySubtitle(item)?.contains(checklistQuery, ignoreCase = true) == true
    }
    Card(modifier=Modifier.fillMaxWidth(),colors=CardDefaults.cardColors(containerColor=MaterialTheme.colorScheme.secondaryContainer),border=BorderStroke(1.dp,accent.copy(alpha=.45f)),shape=RoundedCornerShape(18.dp)) {
        Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(10.dp)) {
            Text("Пошаговая приёмка",style=MaterialTheme.typography.titleMedium,fontWeight=FontWeight.Black)
            Text("${summary.checked + summary.notes + summary.notApplicable} из ${summary.total} пунктов обработано",color=accent)
            if (showFullChecklist) {
                OutlinedTextField(
                    value = checklistQuery,
                    onValueChange = { checklistQuery = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text("Поиск по названию") }
                )
                visibleItems.forEach { (id, item) ->
                    val itemState = stateVersion.let { acceptanceRepository.state(id) }
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        border = BorderStroke(1.dp, accent.copy(alpha = 0.35f)),
                        shape = RoundedCornerShape(14.dp)
                    ) {
                        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(technicalEntryTitle(item), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                            technicalEntrySubtitle(item)?.let { Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                            AcceptanceStatusSelector(
                                itemTitle = technicalEntryTitle(item),
                                currentState = itemState,
                                onSelect = { option -> acceptanceRepository.setState(id, option); stateVersion++ }
                            )
                        }
                    }
                }
                if (visibleItems.isEmpty()) Text("Ничего не найдено", color = MaterialTheme.colorScheme.onSurfaceVariant)
                AcceptanceResultCard(summary)
                OutlinedButton(onClick = { showFullChecklist = false }, modifier = Modifier.fillMaxWidth()) { Text("Вернуться к пошаговой проверке") }
            } else {
                Text("Шаг ${step+1} из ${entry.sequence.size}",color=accent)
                Text(target?.let(::technicalEntryTitle)?:"Пункт приёмки",style=MaterialTheme.typography.titleLarge,fontWeight=FontWeight.Black)
                target?.let { item ->
                    technicalEntrySubtitle(item)?.let { Text(it,color=MaterialTheme.colorScheme.onSurfaceVariant) }
                    item.blocks.forEach { block ->
                        val lines=repository.displayLines(block.lines).mapNotNull(::technicalPresentationLine).distinct()
                        if(lines.isNotEmpty()) Card(colors=CardDefaults.cardColors(containerColor=technicalBlockContainer(item.section,block.title)),modifier=Modifier.fillMaxWidth()) {
                            Column(Modifier.padding(12.dp),verticalArrangement=Arrangement.spacedBy(5.dp)) { Text(block.title,fontWeight=FontWeight.Black); lines.forEach { Text("• $it") } }
                        }
                    }
                    AcceptanceStatusSelector(
                        itemTitle = technicalEntryTitle(item),
                        currentState = currentState,
                        onSelect = { option -> acceptanceRepository.setState(currentId, option); stateVersion++ }
                    )
                }
                Row(horizontalArrangement=Arrangement.spacedBy(8.dp)) { OutlinedButton(onClick={if(step>0)step--},enabled=step>0){Text("Назад")}; Button(onClick={if(step<entry.sequence.lastIndex)step++},enabled=step<entry.sequence.lastIndex && currentState != AcceptanceCheckState.NOT_CHECKED){Text("Далее")} }
                OutlinedButton(onClick={showFullChecklist=true},modifier=Modifier.fillMaxWidth()){Text("Открыть полную карточку")}
                if (summary.complete) AcceptanceResultCard(summary)
            }
        }
    }
}

@Composable
private fun AcceptanceStatusSelector(
    itemTitle: String,
    currentState: AcceptanceCheckState,
    onSelect: (AcceptanceCheckState) -> Unit
) {
    Text("Статус: ${currentState.label}", color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.Bold)
    Text(itemTitle, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Black)
    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        items(AcceptanceCheckState.entries) { option ->
            FilterChip(selected = currentState == option, onClick = { onSelect(option) }, label = { Text(option.label) })
        }
    }
}

@Composable
private fun AcceptanceResultCard(summary: ru.railbrake.calculator.data.AcceptanceSummary) {
    val tone = if (summary.complete && summary.notes == 0) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.tertiaryContainer
    InfoCard(
        summary.result,
        listOf(
            "Проверено: ${summary.checked}",
            "Замечания: ${summary.notes}",
            "Не применяется: ${summary.notApplicable}",
            "Не проверено: ${summary.notChecked}"
        ),
        tone
    )
}

@Composable
private fun technicalBlockContainer(section: TechnicalSection,title:String):Color=when {
    title.contains("Опас",true)->MaterialTheme.colorScheme.errorContainer
    title.contains("Неисправ",true)->MaterialTheme.colorScheme.secondaryContainer
    title.contains("Нормаль",true)->MaterialTheme.colorScheme.primaryContainer
    title.contains("Провер",true)->MaterialTheme.colorScheme.tertiaryContainer
    else->technicalSectionContainer(section)
}

@Composable
private fun technicalSectionContainer(section:TechnicalSection):Color =
    MaterialTheme.colorScheme.primaryContainer

@Composable
private fun technicalSectionAccent(section: TechnicalSection, status: String): Color {
    if (status.equals("STOP_AND_REPORT", true) || status.equals("RESTRICT_OPERATION", true)) {
        return MaterialTheme.colorScheme.error
    }
    return MaterialTheme.colorScheme.primary
}

internal fun technicalStatusLabel(status: String): String? = technicalStatusPresentation(status)
