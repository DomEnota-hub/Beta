from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_PATHS = [
    ROOT / "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
    ROOT / "patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
]
UI_PATHS = [
    ROOT / "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt",
    ROOT / "patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, got {count}")
    return text.replace(old, new, 1)


DATA_CLASSES_ANCHOR = '''data class TechnicalEntry(
    val id: String,
    val family: TechnicalFamily,
    val section: TechnicalSection,
    val title: String,
    val subtitle: String,
    val status: String,
    val blocks: List<TechnicalBlock>,
    val relatedIds: List<String> = emptyList(),
    val sequence: List<String> = emptyList(),
    val sequenceLabels: Map<String, String> = emptyMap(),
    val hotspots: List<TechnicalHotspot> = emptyList(),
    val searchText: String
)

class TechnicalDataRepository'''

DATA_CLASSES_REPLACEMENT = '''data class TechnicalEntry(
    val id: String,
    val family: TechnicalFamily,
    val section: TechnicalSection,
    val title: String,
    val subtitle: String,
    val status: String,
    val blocks: List<TechnicalBlock>,
    val relatedIds: List<String> = emptyList(),
    val sequence: List<String> = emptyList(),
    val sequenceLabels: Map<String, String> = emptyMap(),
    val hotspots: List<TechnicalHotspot> = emptyList(),
    val searchText: String
)

data class ErmakSchemeDiagnosticLink(
    val diagnosticId: String,
    val profileGateRequired: Boolean,
    val reason: String
)

data class ErmakSchemeLinkContext(
    val models: List<String>,
    val profiles: List<String>,
    val selectionRequired: Boolean,
    val notes: String,
    val diagnosticLinks: List<ErmakSchemeDiagnosticLink>
)

class TechnicalDataRepository'''

LINK_FUNCTION_ANCHOR = '''    private fun ermakKnowledgeLinks(article: JSONObject): JSONObject {
        val equipmentId = article.optString("equipmentId")
        if (equipmentId.isNotBlank()) return ermakEquipmentLinks(equipmentId)
        val articleId = article.optString("id")
        if (articleId.startsWith("ER-KB-SYS-")) {
            return ermakSystemLinks(articleId.removePrefix("ER-KB-"))
        }
        return JSONObject()
    }

    val entries: List<TechnicalEntry>'''

LINK_FUNCTION_REPLACEMENT = '''    private fun ermakKnowledgeLinks(article: JSONObject): JSONObject {
        val equipmentId = article.optString("equipmentId")
        if (equipmentId.isNotBlank()) return ermakEquipmentLinks(equipmentId)
        val articleId = article.optString("id")
        if (articleId.startsWith("ER-KB-SYS-")) {
            return ermakSystemLinks(articleId.removePrefix("ER-KB-"))
        }
        return JSONObject()
    }

    fun ermakSchemeLinkContext(schemeId: String): ErmakSchemeLinkContext? {
        val byScheme = ermakLinkIndexes.optJSONObject("byScheme") ?: return null
        val raw = byScheme.optJSONObject(schemeId) ?: return null
        val rules = raw.obj("variantRules")
        val diagnostics = raw.array("diagnosticLinks").objects().mapNotNull { item ->
            item.optString("diagnosticId").takeIf(String::isNotBlank)?.let { diagnosticId ->
                ErmakSchemeDiagnosticLink(
                    diagnosticId = diagnosticId,
                    profileGateRequired = item.optBoolean("profileGateRequired", false),
                    reason = item.optString("reason")
                )
            }
        }.distinctBy(ErmakSchemeDiagnosticLink::diagnosticId)
        return ErmakSchemeLinkContext(
            models = rules.array("models").strings(),
            profiles = rules.array("includeProfiles").strings(),
            selectionRequired = rules.optBoolean("selectionRequired", false),
            notes = rules.optString("notes"),
            diagnosticLinks = diagnostics
        )
    }

    val entries: List<TechnicalEntry>'''

DETAIL_ANCHOR = '''        } else if (entry.sequence.isNotEmpty()) {
            item { TechnicalSequenceLinks(entry, repository, onOpen) }
        }
        items(entry.blocks, key = { it.title }) { block ->'''

DETAIL_REPLACEMENT = '''        } else if (entry.sequence.isNotEmpty()) {
            item { TechnicalSequenceLinks(entry, repository, onOpen) }
        }
        repository.ermakSchemeLinkContext(entry.id)
            ?.takeIf { it.diagnosticLinks.isNotEmpty() }
            ?.let { linkContext ->
                item(key = "scheme-diagnostics-${entry.id}") {
                    ErmakSchemeDiagnostics(entry, linkContext, repository, onOpen)
                }
            }
        items(entry.blocks, key = { it.title }) { block ->'''

SCHEME_DIAGNOSTICS_ANCHOR = '''@Composable
private fun TechnicalSequenceLinks(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {'''

SCHEME_DIAGNOSTICS_REPLACEMENT = '''@Composable
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
private fun TechnicalSequenceLinks(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {'''


for path in REPO_PATHS:
    text = path.read_text(encoding="utf-8")
    if "data class ErmakSchemeLinkContext(" not in text:
        text = replace_once(text, DATA_CLASSES_ANCHOR, DATA_CLASSES_REPLACEMENT, f"{path}: data classes")
    if "fun ermakSchemeLinkContext(schemeId: String)" not in text:
        text = replace_once(text, LINK_FUNCTION_ANCHOR, LINK_FUNCTION_REPLACEMENT, f"{path}: scheme context")
    path.write_text(text, encoding="utf-8")

for path in UI_PATHS:
    text = path.read_text(encoding="utf-8")
    if "ErmakSchemeDiagnostics(entry, linkContext, repository, onOpen)" not in text:
        text = replace_once(text, DETAIL_ANCHOR, DETAIL_REPLACEMENT, f"{path}: detail integration")
    if "private fun ErmakSchemeDiagnostics(" not in text:
        text = replace_once(text, SCHEME_DIAGNOSTICS_ANCHOR, SCHEME_DIAGNOSTICS_REPLACEMENT, f"{path}: diagnostics UI")
    path.write_text(text, encoding="utf-8")

print("Ermak scheme diagnostic gating wired into app and patch mirrors")
