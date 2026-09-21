#!/usr/bin/env python3
from pathlib import Path

REPO_FILES = [
    Path("app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"),
]
UI_FILES = [
    Path("app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"),
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_repository(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '''    companion object {
        private val sharedSectionCache = mutableMapOf<Pair<TechnicalFamily, TechnicalSection>, List<TechnicalEntry>>()
    }
''',
        '''    companion object {
        private val sharedSectionCache = mutableMapOf<Pair<TechnicalFamily, TechnicalSection>, List<TechnicalEntry>>()
        private val sharedEntryCache = mutableMapOf<String, TechnicalEntry>()
    }
''',
        f"{path}: companion cache",
    )

    text = replace_once(
        text,
        '''    fun entry(id: String): TechnicalEntry? {
        val canonicalId = legacyEquipmentIds[id.lowercase()] ?: id
        synchronized(sharedSectionCache) {
            sharedSectionCache.values.asSequence().flatten().firstOrNull { it.id == canonicalId }?.let { return it }
        }
        candidateSections(canonicalId).forEach { (family, section) ->
            sectionEntries(family, section).firstOrNull { it.id == canonicalId }?.let { return it }
        }
        return null
    }
''',
        '''    fun entry(id: String): TechnicalEntry? {
        val canonicalId = legacyEquipmentIds[id.lowercase()] ?: id
        synchronized(sharedSectionCache) {
            sharedEntryCache[canonicalId]?.let { return it }
        }
        candidateSections(canonicalId).forEach { (family, section) ->
            sectionEntries(family, section)
            synchronized(sharedSectionCache) {
                sharedEntryCache[canonicalId]?.let { return it }
            }
        }
        return null
    }
''',
        f"{path}: entry lookup",
    )

    text = replace_once(
        text,
        '''    private fun sectionEntries(family: TechnicalFamily, section: TechnicalSection): List<TechnicalEntry> {
        val key = family to section
        synchronized(sharedSectionCache) { sharedSectionCache[key]?.let { return it } }
        val loaded = loadSection(family, section)
        synchronized(sharedSectionCache) { return sharedSectionCache.getOrPut(key) { loaded } }
    }
''',
        '''    private fun sectionEntries(family: TechnicalFamily, section: TechnicalSection): List<TechnicalEntry> {
        val key = family to section
        synchronized(sharedSectionCache) {
            sharedSectionCache[key]?.let { return it }
        }
        val loaded = loadSection(family, section)
        synchronized(sharedSectionCache) {
            val cached = sharedSectionCache.getOrPut(key) { loaded }
            cached.forEach { entry -> sharedEntryCache.putIfAbsent(entry.id, entry) }
            return cached
        }
    }
''',
        f"{path}: section index",
    )

    path.write_text(text, encoding="utf-8")


def patch_ui(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '''    val accent = technicalSectionAccent(entry.section, entry.status)
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
''',
        '''    val accent = technicalSectionAccent(entry.section, entry.status)
    val isErmakLayout = isErmakLayoutEntry(entry.id)
    val detailBlocks = remember(entry.id) {
        if (isErmakLayout) entry.blocks.filterNot { it.title == "Оборудование" } else entry.blocks
    }
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
''',
        f"{path}: detail precomputation",
    )

    text = replace_once(
        text,
        '''        repository.ermakSchemeLinkContext(entry.id)
            ?.takeIf { it.diagnosticLinks.isNotEmpty() }
            ?.let { linkContext ->
''',
        '''        schemeLinkContext
            ?.takeIf { it.diagnosticLinks.isNotEmpty() }
            ?.let { linkContext ->
''',
        f"{path}: async scheme links",
    )

    text = replace_once(
        text,
        '''        items(entry.blocks, key = { it.title }) { block ->
''',
        '''        items(detailBlocks, key = { it.title }) { block ->
''',
        f"{path}: filtered detail blocks",
    )

    text = replace_once(
        text,
        '''    var selectedId by rememberSaveable(entry.id) { mutableStateOf(entry.hotspots.firstOrNull()?.equipmentId) }
    var query by rememberSaveable(entry.id) { mutableStateOf("") }
    val selectedHotspot = entry.hotspots.firstOrNull { it.equipmentId == selectedId }
    val selectedEquipment = selectedHotspot?.let { repository.entry(it.equipmentId) }
    val visible = entry.hotspots.filter {
        query.isBlank() || it.label.contains(query, ignoreCase = true) || it.equipmentId.contains(query, ignoreCase = true)
    }
    val maxX = entry.hotspots.maxOfOrNull { it.x + it.width }?.coerceAtLeast(1) ?: 1
    val maxY = entry.hotspots.maxOfOrNull { it.y + it.height }?.coerceAtLeast(1) ?: 1
''',
        '''    var selectedId by rememberSaveable(entry.id) { mutableStateOf(entry.hotspots.firstOrNull()?.equipmentId) }
    var query by rememberSaveable(entry.id) { mutableStateOf("") }
    val selectedHotspot = remember(entry.id, selectedId) {
        entry.hotspots.firstOrNull { it.equipmentId == selectedId }
    }
    val selectedEquipmentState by produceState<Pair<Boolean, TechnicalEntry?>>(
        initialValue = false to null,
        selectedId,
        repository
    ) {
        val equipmentId = selectedId
        value = if (equipmentId == null) {
            true to null
        } else {
            withContext(Dispatchers.Default) {
                true to repository.entry(equipmentId)
            }
        }
    }
    val selectedEquipmentLoaded = selectedEquipmentState.first
    val selectedEquipment = selectedEquipmentState.second
    val visible = remember(entry.id, query) {
        entry.hotspots.filter {
            query.isBlank() || it.label.contains(query, ignoreCase = true) || it.equipmentId.contains(query, ignoreCase = true)
        }
    }
    val maxX = remember(entry.id) { entry.hotspots.maxOfOrNull { it.x + it.width }?.coerceAtLeast(1) ?: 1 }
    val maxY = remember(entry.id) { entry.hotspots.maxOfOrNull { it.y + it.height }?.coerceAtLeast(1) ?: 1 }
''',
        f"{path}: async selected equipment",
    )

    text = replace_once(
        text,
        '''            selectedHotspot?.let { hotspot ->
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
''',
        '''            selectedHotspot?.let { hotspot ->
                Text(hotspot.label, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                val equipment = selectedEquipment
                when {
                    !selectedEquipmentLoaded -> Text(
                        "Карточка оборудования загружается…",
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    equipment != null -> {
                        technicalEntrySubtitle(equipment)?.let {
                            Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        OutlinedButton(
                            onClick = { onOpen(equipment) },
                            modifier = Modifier.fillMaxWidth(),
                            border = BorderStroke(1.dp, Color.Black)
                        ) { Text("Подробнее") }
                    }
                    else -> Text(
                        "Для выбранной зоны отдельная карточка оборудования пока отсутствует.",
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
''',
        f"{path}: loading state",
    )

    path.write_text(text, encoding="utf-8")


for file in REPO_FILES:
    patch_repository(file)
for file in UI_FILES:
    patch_ui(file)

print("Patched Ermak interactive atlas ANR hot path in app and patch mirrors.")
