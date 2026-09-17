#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")


def read(rel):
    return (root / rel).read_text(encoding="utf-8")


def write(rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def rep(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, got {count}")
    return text.replace(old, new, 1)


runtime = r'''package ru.railbrake.calculator.ui

import android.content.Context
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import org.json.JSONArray
import org.json.JSONObject
import ru.railbrake.calculator.core.TechnicalDataRepository
import ru.railbrake.calculator.core.TechnicalEntry

internal data class ErmakDiagChoice(
    val label: String,
    val nextNodeId: String = "",
    val nextScenarioId: String = ""
)

internal data class ErmakDiagNode(
    val id: String,
    val type: String,
    val prompt: String = "",
    val text: String = "",
    val result: String = "",
    val nextNodeId: String = "",
    val terminalStatus: String = "",
    val riskClass: String = "",
    val userFacingPolicy: String = "",
    val sourceBound: Boolean = false,
    val choices: List<ErmakDiagChoice> = emptyList()
)

internal data class ErmakDiagScenarioRuntime(
    val id: String,
    val title: String,
    val startNodeId: String,
    val nodes: Map<String, ErmakDiagNode>,
    val families: List<String>,
    val profiles: List<String>,
    val lateProfiles: String,
    val explicitVariantSelectionRequired: Boolean
) {
    val profileSelectionRequired: Boolean
        get() = explicitVariantSelectionRequired || (profiles.isNotEmpty() && "all_confirmed_profiles" !in profiles)
}

internal class ErmakDiagnosticRuntimeRepository(context: Context) {
    private val appContext = context.applicationContext
    private val root by lazy {
        appContext.assets.open("technical/ermak_diagnostics.json").bufferedReader().use { JSONObject(it.readText()) }
    }

    fun scenario(id: String): ErmakDiagScenarioRuntime? {
        val scenarios = root.optJSONArray("scenarios") ?: return null
        val source = (0 until scenarios.length())
            .mapNotNull { scenarios.optJSONObject(it) }
            .firstOrNull { it.optString("id") == id }
            ?: return null
        val applicability = source.optJSONObject("applicability") ?: JSONObject()
        val graph = source.optJSONObject("graph") ?: return null
        val nodeArray = graph.optJSONArray("nodes") ?: JSONArray()
        val nodes = buildMap {
            for (i in 0 until nodeArray.length()) {
                val n = nodeArray.optJSONObject(i) ?: continue
                val choicesArray = n.optJSONArray("choices") ?: JSONArray()
                val choices = buildList {
                    for (j in 0 until choicesArray.length()) {
                        val c = choicesArray.optJSONObject(j) ?: continue
                        add(ErmakDiagChoice(c.optString("label"), c.optString("nextNodeId"), c.optString("nextScenarioId")))
                    }
                }
                val node = ErmakDiagNode(
                    id = n.optString("id"),
                    type = n.optString("type"),
                    prompt = n.optString("prompt"),
                    text = n.optString("text"),
                    result = n.optString("result"),
                    nextNodeId = n.optString("nextNodeId"),
                    terminalStatus = n.optString("terminalStatus"),
                    riskClass = n.optString("riskClass"),
                    userFacingPolicy = n.optString("userFacingPolicy"),
                    sourceBound = n.optBoolean("sourceBound", false),
                    choices = choices
                )
                if (node.id.isNotBlank()) put(node.id, node)
            }
        }
        return ErmakDiagScenarioRuntime(
            id = source.optString("id"),
            title = source.optString("title"),
            startNodeId = graph.optString("startNodeId"),
            nodes = nodes,
            families = applicability.optJSONArray("families").strings(),
            profiles = applicability.optJSONArray("profiles").strings(),
            lateProfiles = applicability.optString("lateProfiles"),
            explicitVariantSelectionRequired = applicability.optBoolean("variantSelectionRequired", false)
        )
    }
}

private fun JSONArray?.strings(): List<String> {
    if (this == null) return emptyList()
    return buildList {
        for (i in 0 until length()) optString(i).takeIf(String::isNotBlank)?.let(::add)
    }
}

private fun ermakFamilyLabel(value: String): String = when (value) {
    "2ES5K" -> "2ЭС5К"
    "3ES5K" -> "3ЭС5К"
    else -> value
}

private fun ermakProfileLabel(value: String): String = when (value) {
    "base_early" -> "Базовое раннее"
    "all_confirmed_profiles" -> "Подтверждённое исполнение"
    else -> value.replace('_', ' ')
}

private fun ermakRiskLabel(value: String): String = when (value) {
    "stop_and_report" -> "Остановиться и доложить"
    "fire_emergency" -> "Пожар / аварийный порядок"
    "emergency_source_bound" -> "Аварийное действие по источнику"
    "manual_power_apparatus" -> "Силовой аппарат: ручное действие"
    "hv_manual" -> "Высокое напряжение"
    "roof_hv" -> "Крышевое ВВ оборудование"
    else -> value.replace('_', ' ')
}

@Composable
internal fun ErmakDiagnosticRuntime(
    entry: TechnicalEntry,
    technicalRepository: TechnicalDataRepository,
    onOpen: (TechnicalEntry) -> Unit
) {
    val context = androidx.compose.ui.platform.LocalContext.current
    val runtimeRepository = remember { ErmakDiagnosticRuntimeRepository(context) }
    val scenario = remember(entry.id) { runtimeRepository.scenario(entry.id) } ?: return

    var family by rememberSaveable(entry.id) { mutableStateOf("") }
    var profile by rememberSaveable("${entry.id}-profile") { mutableStateOf("") }
    var currentNodeId by rememberSaveable("${entry.id}-node") { mutableStateOf(scenario.startNodeId) }
    var history by rememberSaveable("${entry.id}-history") { mutableStateOf("") }
    val node = scenario.nodes[currentNodeId]
    var safetyConfirmed by rememberSaveable("${entry.id}-${currentNodeId}-gate") { mutableStateOf(false) }

    val familyReady = scenario.families.isEmpty() || family in scenario.families
    val profileReady = !scenario.profileSelectionRequired || profile in scenario.profiles || "all_confirmed_profiles" in scenario.profiles
    val variantReady = familyReady && profileReady
    val actionNeedsProfile = node?.userFacingPolicy in setOf("SOURCE_AND_PROFILE_REQUIRED", "SAFETY_GATE_REQUIRED")
    val actionUnlocked = !actionNeedsProfile || variantReady

    fun move(next: String) {
        if (next.isBlank() || next !in scenario.nodes) return
        history = (history.split('|').filter(String::isNotBlank) + currentNodeId).joinToString("|")
        currentNodeId = next
    }
    fun back() {
        val items = history.split('|').filter(String::isNotBlank)
        if (items.isNotEmpty()) {
            currentNodeId = items.last()
            history = items.dropLast(1).joinToString("|")
        }
    }
    fun reset() {
        currentNodeId = scenario.startNodeId
        history = ""
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(18.dp),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.secondary.copy(alpha = .45f)),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
    ) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("Интерактивный маршрут диагностики", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
            Text("Граф и ограничения читаются напрямую из канонического ermak_diagnostics.json.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)

            if (scenario.families.isNotEmpty()) {
                Text("Модель", fontWeight = FontWeight.Bold)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    scenario.families.forEach { value ->
                        FilterChip(selected = family == value, onClick = { family = value }, label = { Text(ermakFamilyLabel(value)) })
                    }
                }
            }
            if (scenario.profileSelectionRequired && scenario.profiles.isNotEmpty()) {
                Text("Исполнение", fontWeight = FontWeight.Bold)
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    scenario.profiles.forEach { value ->
                        FilterChip(selected = profile == value, onClick = { profile = value }, label = { Text(ermakProfileLabel(value)) })
                    }
                    FilterChip(selected = profile == "__unknown__", onClick = { profile = "__unknown__" }, label = { Text("Не подтверждено / другое") })
                }
                if (scenario.lateProfiles.isNotBlank()) Text(scenario.lateProfiles, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }

            if (scenario.profileSelectionRequired && !variantReady) {
                Text("Профиль-зависимые действия заблокированы до подтверждения модели и исполнения.", color = MaterialTheme.colorScheme.error, fontWeight = FontWeight.Bold)
            }

            if (node == null) {
                Text("Узел маршрута не найден: $currentNodeId", color = MaterialTheme.colorScheme.error)
                OutlinedButton(onClick = ::reset) { Text("Начать заново") }
            } else {
                if (node.riskClass.isNotBlank()) {
                    RailStatusPill(ermakRiskLabel(node.riskClass), accent = MaterialTheme.colorScheme.error)
                }
                when (node.type) {
                    "question" -> {
                        Text(node.prompt, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
                        node.choices.forEach { choice ->
                            Button(
                                onClick = {
                                    when {
                                        choice.nextNodeId.isNotBlank() -> move(choice.nextNodeId)
                                        choice.nextScenarioId.isNotBlank() -> technicalRepository.entry(choice.nextScenarioId)?.let(onOpen)
                                    }
                                },
                                modifier = Modifier.fillMaxWidth()
                            ) { Text(choice.label) }
                        }
                    }
                    "finding", "info" -> {
                        Text(node.text, style = MaterialTheme.typography.bodyLarge)
                        if (node.nextNodeId.isNotBlank()) Button(onClick = { move(node.nextNodeId) }, modifier = Modifier.fillMaxWidth()) { Text("Продолжить") }
                    }
                    "safety_gate" -> {
                        Text(node.text, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                        FilterChip(
                            selected = safetyConfirmed,
                            onClick = { safetyConfirmed = !safetyConfirmed },
                            label = { Text(if (safetyConfirmed) "Условие безопасности подтверждено" else "Подтвердить условие безопасности") }
                        )
                        if (!actionUnlocked) Text("Продолжение также требует подтверждённого исполнения.", color = MaterialTheme.colorScheme.error)
                        if (node.nextNodeId.isNotBlank()) Button(
                            onClick = { move(node.nextNodeId) },
                            enabled = safetyConfirmed && actionUnlocked,
                            modifier = Modifier.fillMaxWidth()
                        ) { Text("Продолжить") }
                    }
                    "source_action", "emergency_action" -> {
                        if (actionUnlocked) {
                            Text(node.text, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                            if (node.sourceBound) Text("Действие привязано к источнику и выбранному исполнению.", style = MaterialTheme.typography.bodySmall)
                            if (node.nextNodeId.isNotBlank()) Button(onClick = { move(node.nextNodeId) }, modifier = Modifier.fillMaxWidth()) { Text("Продолжить") }
                        } else {
                            Text("Действие не показывается как исполнимое для неподтверждённого профиля. Выберите применимое исполнение или вернитесь к диагностике.", color = MaterialTheme.colorScheme.error)
                        }
                    }
                    "terminal" -> {
                        Text(node.result, style = MaterialTheme.typography.bodyLarge, fontWeight = FontWeight.Bold)
                        if (node.terminalStatus.isNotBlank()) Text("Результат: ${node.terminalStatus.replace('_', ' ')}", style = MaterialTheme.typography.labelLarge)
                        OutlinedButton(onClick = ::reset, modifier = Modifier.fillMaxWidth()) { Text("Начать маршрут заново") }
                    }
                    else -> Text("Неподдерживаемый тип узла: ${node.type}", color = MaterialTheme.colorScheme.error)
                }

                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = ::back, enabled = history.isNotBlank()) { Text("Шаг назад") }
                    OutlinedButton(onClick = ::reset) { Text("Сбросить маршрут") }
                }
            }
        }
    }
}
'''
write("app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticRuntime.kt", runtime)

rel = "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
t = read(rel)
t = rep(
    t,
    '''        if (entry.sequence.isNotEmpty()) {
            item {''',
    '''        if (entry.family == TechnicalFamily.ERMAK && entry.section == TechnicalSection.DIAGNOSTICS) {
            item { ErmakDiagnosticRuntime(entry, repository, onOpen) }
        }
        if (entry.sequence.isNotEmpty()) {
            item {''',
    "Ermak diagnostic runtime injection",
)
write(rel, t)

gradle_rel = "app/build.gradle.kts"
g = read(gradle_rel)
g, count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.2.2-beta-recovery6"', g, count=1)
if count != 1:
    raise SystemExit("versionName not found")
write(gradle_rel, g)

print("Recovery patch 6 applied")
