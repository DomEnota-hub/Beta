#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(".")
CATALOG_PATHS = [
    ROOT / "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt",
    ROOT / "patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt",
]
APP_PATHS = [
    ROOT / "app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt",
    ROOT / "patch/app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, got {count}")
    return text.replace(old, new, 1)


def patch_catalog(text: str) -> str:
    text = replace_once(
        text,
        '''    initialEntryId: String? = null,
    onOpenLegacyArticle: ((String) -> Unit)? = null
) {''',
        '''    initialEntryId: String? = null,
    onOpenLegacyArticle: ((String) -> Unit)? = null,
    onOpenDiagnosticScenario: ((String, String, TechnicalSection) -> Unit)? = null
) {''',
        "catalog callback signature",
    )
    text = replace_once(
        text,
        '''    var query by rememberSaveable { mutableStateOf("") }
    var selectedId by rememberSaveable(initialEntryId) { mutableStateOf(initialEntryId) }
    var acceptanceStartChoice by rememberSaveable { mutableStateOf(false) }''',
        '''    var query by rememberSaveable { mutableStateOf("") }
    var selectedId by rememberSaveable(initialEntryId) { mutableStateOf(initialEntryId) }
    var navigationPath by rememberSaveable(initialEntryId) { mutableStateOf("") }
    var acceptanceStartChoice by rememberSaveable { mutableStateOf(false) }''',
        "catalog navigation state",
    )
    text = replace_once(
        text,
        '''    val selected = selectedId?.let(repository::entry)

    BackHandler(enabled = selected != null || acceptanceStartChoice) {
        if (selected != null) selectedId = null else acceptanceStartChoice = false
    }''',
        '''    val selected = selectedId?.let(repository::entry)

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
    }''',
        "catalog navigation handlers",
    )
    text = replace_once(
        text,
        '''            onSelect = { selectedId = it; acceptanceStartChoice = false }''',
        '''            onSelect = { selectedId = it; navigationPath = ""; acceptanceStartChoice = false }''',
        "acceptance reset",
    )
    text = replace_once(
        text,
        '''        TechnicalEntryDetail(
            entry = selected,
            repository = repository,
            onBack = { selectedId = null },
            onOpen = { target -> selectedId = target.id }
        )''',
        '''        val previousEntry = technicalNavigationIds(navigationPath).lastOrNull()?.let(repository::entry)
        TechnicalEntryDetail(
            entry = selected,
            repository = repository,
            backLabel = previousEntry?.let { "Назад к «${technicalEntryTitle(it).take(34)}»" } ?: selected.section.title,
            onBack = ::backFromSelected,
            onOpen = ::openTarget
        )''',
        "detail wiring",
    )
    text = replace_once(
        text,
        '''                    if (entry.id == "VL80-ROUTE-route_canonical") acceptanceStartChoice = true
                    else selectedId = entry.id''',
        '''                    if (entry.id == "VL80-ROUTE-route_canonical") acceptanceStartChoice = true
                    else {
                        navigationPath = ""
                        selectedId = entry.id
                    }''',
        "list open reset",
    )
    text = replace_once(
        text,
        '''private fun TechnicalEntryDetail(
    entry: TechnicalEntry,
    repository: TechnicalDataRepository,
    onBack: () -> Unit,
    onOpen: (TechnicalEntry) -> Unit
) {''',
        '''private fun TechnicalEntryDetail(
    entry: TechnicalEntry,
    repository: TechnicalDataRepository,
    backLabel: String,
    onBack: () -> Unit,
    onOpen: (TechnicalEntry) -> Unit
) {''',
        "detail signature",
    )
    text = replace_once(
        text,
        '''    val relatedEntries = entry.relatedIds
        .distinct()
        .mapNotNull(repository::entry)
        .filterNot { it.id in referencedIds }
        .take(40)''',
        '''    val relatedEntries = entry.relatedIds
        .distinct()
        .mapNotNull(repository::entry)
        .filterNot { it.id == entry.id || it.id in referencedIds }
        .sortedWith(
            compareBy<TechnicalEntry> { technicalRelatedSectionOrder(it.section) }
                .thenBy { technicalEntryTitle(it).lowercase() }
        )
    val relatedGroups = relatedEntries.groupBy(TechnicalEntry::section)
        .toList()
        .sortedBy { (section, _) -> technicalRelatedSectionOrder(section) }''',
        "related sorting",
    )
    text = replace_once(
        text,
        '''            ChildBackButton(entry.section.title, onBack)''',
        '''            ChildBackButton(backLabel, onBack)''',
        "detail back label",
    )
    text = replace_once(
        text,
        '''        if (relatedEntries.isNotEmpty()) {
            item {
                HorizontalDivider()
                Text("Связанные материалы", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
            }
            items(relatedEntries, key = { "related-${it.id}" }) { target ->
                OutlinedButton(
                    onClick = { onOpen(target) },
                    modifier = Modifier.fillMaxWidth(),
                    border = BorderStroke(1.dp, Color.Black)
                ) {
                    Text("${technicalEntryTitle(target)} →")
                }
            }
        }''',
        '''        if (relatedGroups.isNotEmpty()) {
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
        }''',
        "related grouping",
    )
    marker = '''internal fun isErmakLayoutEntry(id: String): Boolean = id.startsWith("ER-SCH-LAYOUT-")'''
    helpers = '''internal fun technicalNavigationIds(path: String): List<String> =
    path.lineSequence().map(String::trim).filter(String::isNotBlank).toList()

internal fun technicalNavigationPush(path: String, currentId: String): String =
    (technicalNavigationIds(path) + currentId).joinToString("\\n")

internal fun technicalNavigationPop(path: String): Pair<String?, String> {
    val ids = technicalNavigationIds(path)
    return ids.lastOrNull() to ids.dropLast(1).joinToString("\\n")
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

''' + marker
    text = replace_once(text, marker, helpers, "catalog helpers")
    return text


def patch_app(text: str) -> str:
    text = replace_once(
        text,
        '''    var diagnosticStartScenarioId by rememberSaveable { mutableStateOf<String?>(null) }
    var diagnosticStartEquipmentId by rememberSaveable { mutableStateOf<String?>(null) }''',
        '''    var diagnosticStartScenarioId by rememberSaveable { mutableStateOf<String?>(null) }
    var diagnosticStartEquipmentId by rememberSaveable { mutableStateOf<String?>(null) }
    var diagnosticReturnScreenName by rememberSaveable { mutableStateOf(AppScreen.HOME.name) }''',
        "app diagnostic return state",
    )
    text = replace_once(
        text,
        '''                                AppScreen.DIAGNOSTICS -> {
                                    diagnosticStartScenarioId = null
                                    diagnosticStartEquipmentId = null
                                    diagnosticRootVersion++
                                }''',
        '''                                AppScreen.DIAGNOSTICS -> {
                                    diagnosticStartScenarioId = null
                                    diagnosticStartEquipmentId = null
                                    diagnosticReturnScreenName = AppScreen.HOME.name
                                    diagnosticRootVersion++
                                }''',
        "drawer diagnostic reset",
    )
    text = replace_once(
        text,
        '''            screenName = when (screen) {
                AppScreen.MASS, AppScreen.APPENDIX -> AppScreen.CALCULATIONS.name
                AppScreen.LOCOMOTIVE_MATERIAL, AppScreen.LOCOMOTIVE_LEGACY -> AppScreen.LOCOMOTIVES.name
                else -> AppScreen.HOME.name
            }''',
        '''            screenName = when (screen) {
                AppScreen.MASS, AppScreen.APPENDIX -> AppScreen.CALCULATIONS.name
                AppScreen.LOCOMOTIVE_MATERIAL, AppScreen.LOCOMOTIVE_LEGACY -> AppScreen.LOCOMOTIVES.name
                AppScreen.DIAGNOSTICS -> diagnosticReturnScreenName
                else -> AppScreen.HOME.name
            }''',
        "app back target",
    )
    text = replace_once(
        text,
        '''                    onDiagnostics = {
                        diagnosticStartScenarioId = null
                        diagnosticStartEquipmentId = null
                        screenName = AppScreen.DIAGNOSTICS.name
                    },''',
        '''                    onDiagnostics = {
                        diagnosticStartScenarioId = null
                        diagnosticStartEquipmentId = null
                        diagnosticReturnScreenName = AppScreen.HOME.name
                        screenName = AppScreen.DIAGNOSTICS.name
                    },''',
        "home diagnostics",
    )
    text = replace_once(
        text,
        '''                    onOpenLegacyArticle = { articleId ->
                        locomotiveMaterialQuery = null
                        locomotiveMaterialArticleId = articleId
                        screenName = AppScreen.LOCOMOTIVE_LEGACY.name
                    }
                )''',
        '''                    onOpenLegacyArticle = { articleId ->
                        locomotiveMaterialQuery = null
                        locomotiveMaterialArticleId = articleId
                        screenName = AppScreen.LOCOMOTIVE_LEGACY.name
                    },
                    onOpenDiagnosticScenario = { scenarioId, sourceEntryId, sourceSection ->
                        technicalFamilyName = TechnicalFamily.ERMAK.name
                        technicalSectionName = sourceSection.name
                        technicalInitialEntryId = sourceEntryId
                        diagnosticStartScenarioId = scenarioId
                        diagnosticStartEquipmentId = null
                        diagnosticReturnScreenName = AppScreen.LOCOMOTIVE_MATERIAL.name
                        diagnosticRootVersion++
                        screenName = AppScreen.DIAGNOSTICS.name
                    }
                )''',
        "catalog diagnostic routing",
    )
    text = replace_once(
        text,
        '''                    onOpenScenario = { scenarioId ->
                        diagnosticStartScenarioId = scenarioId
                        diagnosticStartEquipmentId = null
                        screenName = AppScreen.DIAGNOSTICS.name
                    },''',
        '''                    onOpenScenario = { scenarioId ->
                        diagnosticStartScenarioId = scenarioId
                        diagnosticStartEquipmentId = null
                        diagnosticReturnScreenName = AppScreen.HOME.name
                        screenName = AppScreen.DIAGNOSTICS.name
                    },''',
        "exam scenario routing",
    )
    text = replace_once(
        text,
        '''                    onOpenEquipment = { equipmentId ->
                        diagnosticStartScenarioId = null
                        diagnosticStartEquipmentId = equipmentId
                        screenName = AppScreen.DIAGNOSTICS.name
                    },''',
        '''                    onOpenEquipment = { equipmentId ->
                        diagnosticStartScenarioId = null
                        diagnosticStartEquipmentId = equipmentId
                        diagnosticReturnScreenName = AppScreen.HOME.name
                        screenName = AppScreen.DIAGNOSTICS.name
                    },''',
        "exam equipment routing",
    )
    return text


def patch_file(path: Path, fn):
    original = path.read_text(encoding="utf-8")
    updated = fn(original)
    if updated == original:
        raise SystemExit(f"{path}: no changes")
    path.write_text(updated, encoding="utf-8")


for path in CATALOG_PATHS:
    patch_file(path, patch_catalog)
for path in APP_PATHS:
    patch_file(path, patch_app)

if CATALOG_PATHS[0].read_bytes() != CATALOG_PATHS[1].read_bytes():
    raise SystemExit("TechnicalCatalogScreen mirrors diverged")
if APP_PATHS[0].read_bytes() != APP_PATHS[1].read_bytes():
    raise SystemExit("BrakeCalculatorApp mirrors diverged")

print("Ermak cross-link UX patch applied")
