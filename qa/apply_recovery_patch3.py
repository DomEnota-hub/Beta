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


rel = "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
t = read(rel)

# Import used by the checklist item drill-down.
t = rep(t, '''import androidx.compose.material3.Text
''', '''import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
''', "TextButton import")

start = t.index('@Composable\nprivate fun AcceptanceChecklist')
end = t.index('\n@Composable\nprivate fun TechnicalSequence', start)
new = r'''@Composable
private fun AcceptanceChecklist(entry: TechnicalEntry, repository: TechnicalDataRepository, onOpen: (TechnicalEntry) -> Unit) {
    val context = LocalContext.current
    val prefs = remember(entry.id) { context.getSharedPreferences("vl80s_acceptance_progress", android.content.Context.MODE_PRIVATE) }
    var revision by remember(entry.id) { mutableIntStateOf(0) }
    var gateRevision by remember(entry.id) { mutableIntStateOf(0) }
    val targets = remember(entry.id) { entry.sequence.mapNotNull(repository::entry) }
    val groups = remember(entry.id) { targets.groupBy { it.zoneId.ifBlank { "OTHER" } } }
    val routeGates = remember(entry.id) { targets.flatMap { it.requiredGates }.distinct() }
    val gateStates = remember(entry.id, gateRevision) {
        routeGates.associateWith { gate -> prefs.getBoolean("${entry.id}:gate:$gate", false) }
    }
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
    fun zoneLabel(zone: String): String = when (zone) {
        "DOCS" -> "Документы"
        "SAFETY" -> "Безопасность"
        "OUTSIDE" -> "Наружный осмотр"
        "RUNNING_GEAR" -> "Экипажная часть"
        "BRAKE_PNEUMATIC" -> "Тормоза и пневматика"
        "BODY_VVK" -> "Кузов и ВВК"
        "CAB" -> "Кабина"
        "FUNCTIONAL" -> "Функциональные проверки"
        "DECISION" -> "Итоговое решение"
        else -> "Прочее"
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(if (entry.sequenceMode == "area") "Приёмка по зоне" else "Контрольный список", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
            Text("Отмечено $completed из ${targets.size}", color = MaterialTheme.colorScheme.primary)

            if (routeGates.isNotEmpty()) {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer.copy(alpha = .28f)),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.error.copy(alpha = .35f))
                ) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("Условия безопасности маршрута", fontWeight = FontWeight.Black)
                        routeGates.forEach { gate ->
                            val confirmed = gateStates[gate] == true
                            val meaning = repository.acceptanceGateMeaning(gate)
                            if (meaning.isNotBlank()) Text(meaning, style = MaterialTheme.typography.bodySmall)
                            FilterChip(
                                selected = confirmed,
                                onClick = {
                                    prefs.edit().putBoolean("${entry.id}:gate:$gate", !confirmed).apply()
                                    gateRevision++
                                    revision++
                                },
                                label = { Text(if (confirmed) "Условие подтверждено" else "Подтвердить условие") }
                            )
                        }
                        Text(
                            "Эти отметки не являются допуском к работе и не заменяют установленный порядок действий.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }

            groups.forEach { (zone, itemsInZone) ->
                Text(zoneLabel(zone), style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.Black)
                itemsInZone.forEach { item ->
                    val stateKey = "${entry.id}:${item.id}:state"
                    val state = prefs.getString(stateKey, "NOT_CHECKED") ?: "NOT_CHECKED"
                    val itemGatesSatisfied = item.requiredGates.all { gate -> gateStates[gate] == true }
                    OutlinedButton(
                        onClick = {
                            val states = repository.acceptanceStateIds()
                            val next = if (state == "NOT_CHECKED" && "OK" in states) "OK" else "NOT_CHECKED"
                            prefs.edit().putString(stateKey, next).apply()
                            revision++
                        },
                        enabled = itemGatesSatisfied,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(Modifier.fillMaxWidth()) {
                            Text(technicalEntryTitle(item), fontWeight = FontWeight.Bold)
                            Text(stateLabels[state] ?: state, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            if (!itemGatesSatisfied) Text("Требуется подтверждение обязательных условий", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.error)
                        }
                    }
                    TextButton(onClick = { onOpen(item) }) { Text("Открыть пункт") }
                }
            }
            Text(
                "Быстрая отметка переключает только «Не проверено ↔ Проверено». Для замечания, блокирующего состояния, причины неприменимости и полного содержания используйте пошаговый маршрут или откройте пункт.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
'''
t = t[:start] + new + t[end:]
write(rel, t)

# Distinguish this stricter acceptance pass in build identity.
gradle_rel = "app/build.gradle.kts"
g = read(gradle_rel).replace('versionName = "1.2.2-beta-recovery2"', 'versionName = "1.2.2-beta-recovery3"', 1)
write(gradle_rel, g)

print("Recovery patch 3 applied")
