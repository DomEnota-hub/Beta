from pathlib import Path

path = Path('app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt')
text = path.read_text(encoding='utf-8')

old_import = 'import androidx.compose.ui.text.font.FontWeight\nimport androidx.compose.ui.unit.dp\n'
new_import = 'import androidx.compose.ui.text.font.FontWeight\nimport androidx.compose.ui.text.style.TextOverflow\nimport androidx.compose.ui.unit.dp\n'
if old_import not in text:
    raise SystemExit('Text import anchor not found')
text = text.replace(old_import, new_import, 1)

old_card = '''                    Text(technicalEntryTitle(entry), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)\n                    technicalEntrySubtitle(entry)?.let { subtitle ->\n                        Text(subtitle, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)\n                    }\n                    Text(if (interactive) "Открыть интерактивную схему →" else "Открыть карточку →", color = if (interactive) InteractiveSchemeAccent else accent, fontWeight = FontWeight.Bold)'''
new_card = '''                    Text(technicalEntryTitle(entry), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)\n                    technicalEntrySubtitle(entry)?.let { subtitle ->\n                        Text(\n                            subtitle,\n                            style = MaterialTheme.typography.bodyMedium,\n                            color = MaterialTheme.colorScheme.onSurfaceVariant,\n                            maxLines = if (entry.family == TechnicalFamily.ERMAK) 2 else Int.MAX_VALUE,\n                            overflow = TextOverflow.Ellipsis\n                        )\n                    }\n                    Text(if (interactive) "Открыть интерактивную схему →" else "Открыть карточку →", color = if (interactive) InteractiveSchemeAccent else accent, fontWeight = FontWeight.Bold)'''
if old_card not in text:
    raise SystemExit('Compact list anchor not found')
text = text.replace(old_card, new_card, 1)

start = text.index('@Composable\nprivate fun TechnicalEntryDetail(')
end = text.index('\ninternal fun technicalNavigationIds', start)
replacement = r'''@Composable
private fun TechnicalEntryDetail(
    entry: TechnicalEntry,
    repository: TechnicalDataRepository,
    backLabel: String,
    onBack: () -> Unit,
    onOpen: (TechnicalEntry) -> Unit
) {
    val accent = technicalSectionAccent(entry.section, entry.status)
    val isErmakLayout = isErmakLayoutEntry(entry.id)
    val compactErmak = entry.family == TechnicalFamily.ERMAK && entry.section != TechnicalSection.ACCEPTANCE
    val detailBlocks = remember(entry.id) {
        if (isErmakLayout) entry.blocks.filterNot { it.title == "Оборудование" } else entry.blocks
    }
    val renderableDetailBlocks = remember(entry.id, repository) {
        detailBlocks.filter { block ->
            repository.displayLines(block.lines).mapNotNull(::technicalPresentationLine).any() ||
                repository.referencedEntries(block.lines).isNotEmpty() ||
                (block.title.startsWith("Таблица —") && block.lines.any { it.split("¦", limit = 3).size == 3 })
        }
    }
    var expandedErmakBlocks by rememberSaveable(entry.id) {
        mutableStateOf(
            renderableDetailBlocks
                .filter { ermakCompactBlockStartsExpanded(it.title) }
                .joinToString("\n") { it.title }
        )
    }
    var selectedErmakRelatedSection by rememberSaveable(entry.id) { mutableStateOf<String?>(null) }
    val expandedErmakBlockTitles = remember(expandedErmakBlocks) {
        ermakExpandedBlockTitles(expandedErmakBlocks)
    }
    val allErmakBlocksExpanded = compactErmak && renderableDetailBlocks.isNotEmpty() &&
        renderableDetailBlocks.all { it.title in expandedErmakBlockTitles }
    val referencedIds = remember(entry.id, repository) {
        if (isErmakLayout) {
            emptySet()
        } else {
            entry.blocks
                .flatMap { repository.referencedEntries(it.lines) }
                .map { it.id }
                .toSet()
        }
    }
    val relatedEntries = remember(entry.id, repository) {
        if (isErmakLayout) {
            emptyList()
        } else {
            entry.relatedIds
                .distinct()
                .mapNotNull(repository::entry)
                .filterNot { it.id == entry.id || it.id in referencedIds }
                .sortedWith(
                    compareBy<TechnicalEntry> { technicalRelatedSectionOrder(it.section) }
                        .thenBy { technicalEntryTitle(it).lowercase() }
                )
        }
    }
    val relatedGroups = remember(entry.id, repository) {
        relatedEntries.groupBy(TechnicalEntry::section)
            .toList()
            .sortedBy { (section, _) -> technicalRelatedSectionOrder(section) }
    }
    val schemeLinkContext by produceState<ru.railbrake.calculator.core.ErmakSchemeLinkContext?>(
        initialValue = null,
        entry.id,
        repository
    ) {
        value = withContext(Dispatchers.Default) {
            repository.ermakSchemeLinkContext(entry.id)
        }
    }

    LazyColumn(
        modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            ChildBackButton(backLabel, onBack)
            Text(technicalEntryTitle(entry), style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Black)
            technicalEntrySubtitle(entry)?.let { subtitle ->
                Text(
                    subtitle,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = if (compactErmak) 3 else Int.MAX_VALUE,
                    overflow = TextOverflow.Ellipsis
                )
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
        schemeLinkContext
            ?.takeIf { it.diagnosticLinks.isNotEmpty() }
            ?.let { linkContext ->
                item(key = "scheme-diagnostics-${entry.id}") {
                    ErmakSchemeDiagnostics(entry, linkContext, repository, onOpen)
                }
            }
        if (compactErmak && renderableDetailBlocks.isNotEmpty()) {
            item(key = "ermak-details-control-${entry.id}") {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("Подробности", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                        Text(
                            "${renderableDetailBlocks.size} разделов • открывайте только нужное",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    TextButton(
                        onClick = {
                            expandedErmakBlocks = if (allErmakBlocksExpanded) {
                                ""
                            } else {
                                renderableDetailBlocks.joinToString("\n") { it.title }
                            }
                        }
                    ) {
                        Text(if (allErmakBlocksExpanded) "Свернуть всё" else "Показать всё")
                    }
                }
            }
        }
        items(renderableDetailBlocks, key = { it.title }) { block ->
            val displayLines = repository.displayLines(block.lines)
                .mapNotNull(::technicalPresentationLine)
                .distinct()
            val references = repository.referencedEntries(block.lines)
            val referenceTableRows = if (block.title.startsWith("Таблица —")) {
                block.lines.mapNotNull { line ->
                    line.split("¦", limit = 3).takeIf { it.size == 3 }
                }
            } else emptyList()
            val expanded = !compactErmak || block.title in expandedErmakBlockTitles
            val contentCount = if (referenceTableRows.isNotEmpty()) {
                referenceTableRows.size
            } else {
                displayLines.size + references.size
            }
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = technicalBlockContainer(entry.section, block.title)),
                border = BorderStroke(1.dp, accent.copy(alpha = 0.38f)),
                shape = RoundedCornerShape(18.dp)
            ) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text(block.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                            if (compactErmak && !expanded) {
                                Text(
                                    "$contentCount пунктов",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                        if (compactErmak) {
                            TextButton(
                                onClick = {
                                    expandedErmakBlocks = ermakToggleExpandedBlock(expandedErmakBlocks, block.title)
                                }
                            ) {
                                Text(if (expanded) "Свернуть" else "Раскрыть")
                            }
                        }
                    }
                    if (expanded) {
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
        }
        if (relatedGroups.isNotEmpty()) {
            if (compactErmak) {
                item(key = "compact-related-${entry.id}") {
                    val selectedGroup = relatedGroups.firstOrNull { (section, _) ->
                        section.name == selectedErmakRelatedSection
                    }
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        border = BorderStroke(1.dp, accent.copy(alpha = 0.38f)),
                        shape = RoundedCornerShape(18.dp)
                    ) {
                        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text("Связанные материалы", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                                Text("${relatedEntries.size}", color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                items(relatedGroups) { (section, targets) ->
                                    FilterChip(
                                        selected = selectedErmakRelatedSection == section.name,
                                        onClick = {
                                            selectedErmakRelatedSection = if (selectedErmakRelatedSection == section.name) null else section.name
                                        },
                                        label = { Text("${section.title} · ${targets.size}") }
                                    )
                                }
                            }
                            if (selectedGroup == null) {
                                Text(
                                    "Выберите группу, чтобы открыть связанные карточки.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            } else {
                                selectedGroup.second.forEach { target ->
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
            } else {
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
}

internal fun ermakCompactBlockStartsExpanded(title: String): Boolean {
    val normalized = title.trim().lowercase()
    return normalized.startsWith("назнач") ||
        normalized.startsWith("располож") ||
        normalized.startsWith("кратк") ||
        normalized.startsWith("важно") ||
        normalized.startsWith("главное") ||
        normalized.contains("опас") ||
        normalized.contains("предупреж")
}

internal fun ermakExpandedBlockTitles(serialized: String): Set<String> =
    serialized.lineSequence().map(String::trim).filter(String::isNotBlank).toSet()

internal fun ermakToggleExpandedBlock(serialized: String, title: String): String {
    val titles = ermakExpandedBlockTitles(serialized).toMutableSet()
    if (!titles.add(title)) titles.remove(title)
    return titles.sorted().joinToString("\n")
}
'''
text = text[:start] + replacement + text[end:]
path.write_text(text, encoding='utf-8')

patch_path = Path('patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt')
patch_path.write_text(text, encoding='utf-8')

test = Path('app/src/test/java/ru/railbrake/calculator/ui/ErmakCompactPresentationTest.kt')
test.write_text(r'''package ru.railbrake.calculator.ui

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ErmakCompactPresentationTest {
    @Test
    fun primary_and_safety_blocks_start_expanded() {
        assertTrue(ermakCompactBlockStartsExpanded("Назначение"))
        assertTrue(ermakCompactBlockStartsExpanded("Расположение"))
        assertTrue(ermakCompactBlockStartsExpanded("Кратко"))
        assertTrue(ermakCompactBlockStartsExpanded("Важно"))
        assertTrue(ermakCompactBlockStartsExpanded("Опасные признаки"))
        assertFalse(ermakCompactBlockStartsExpanded("Признаки неисправности"))
        assertFalse(ermakCompactBlockStartsExpanded("Связанные системы"))
    }

    @Test
    fun block_toggle_round_trips_without_duplicates() {
        val expanded = ermakToggleExpandedBlock("Назначение", "Неисправности")
        assertTrue("Назначение" in ermakExpandedBlockTitles(expanded))
        assertTrue("Неисправности" in ermakExpandedBlockTitles(expanded))

        val collapsed = ermakToggleExpandedBlock(expanded, "Неисправности")
        assertTrue("Назначение" in ermakExpandedBlockTitles(collapsed))
        assertFalse("Неисправности" in ermakExpandedBlockTitles(collapsed))
    }
}
''', encoding='utf-8')

for gradle_name in ['app/build.gradle.kts', 'patch/app/build.gradle.kts']:
    gradle = Path(gradle_name)
    value = gradle.read_text(encoding='utf-8')
    value = value.replace('// Beta20: top-level acceptance controls and disabled-step manager.', '// Beta21: compact progressive-disclosure presentation for Ermak.')
    value = value.replace('versionCode = 165', 'versionCode = 166')
    value = value.replace('versionName = "1.2.2-dev14-beta20"', 'versionName = "1.2.2-dev14-beta21"')
    if 'versionCode = 166' not in value or '1.2.2-dev14-beta21' not in value:
        raise SystemExit(f'Version bump failed for {gradle_name}')
    gradle.write_text(value, encoding='utf-8')
