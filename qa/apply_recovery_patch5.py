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


def rep_n(text, old, new, label, expected):
    count = text.count(old)
    if count != expected:
        raise SystemExit(f"{label}: expected {expected} matches, got {count}")
    return text.replace(old, new)


# Recovery pass 5: acceptance state is canonical per item, not per route/UI mode.
rel = "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"
t = read(rel)
t = rep(
    t,
    '''                    block("Условия маршрута", route.optString("note")),''',
    '''                    block("Условия маршрута", route.optString("notes").ifBlank { route.optString("note") }),''',
    "route notes field",
)
t = rep(
    t,
    '''                searchText=(route.optString("title")+" "+mode+" "+route.optString("note")).lowercase()''',
    '''                searchText=(route.optString("title")+" "+mode+" "+route.optString("notes").ifBlank { route.optString("note") }).lowercase()''',
    "route notes search",
)
write(rel, t)

rel = "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
t = read(rel)

# Route position is route-specific; inspection results are canonical per item.
t = rep(t, '''    val stateKey = "${entry.id}:$currentId:state"
    val noteKey = "${entry.id}:$currentId:note"
    val resolutionKey = "${entry.id}:$currentId:resolution"''', '''    val stateKey = "item:$currentId:state"
    val noteKey = "item:$currentId:note"
    val resolutionKey = "item:$currentId:resolution"''', "canonical item keys")

t = rep(t, '''    val completed = entry.sequence.count { id -> (prefs.getString("${entry.id}:$id:state", "NOT_CHECKED") ?: "NOT_CHECKED") != "NOT_CHECKED" }''', '''    val completed = entry.sequence.count { id -> (prefs.getString("item:$id:state", "NOT_CHECKED") ?: "NOT_CHECKED") != "NOT_CHECKED" }''', "step completed count")

t = rep(t, '''        requiredGates.associateWith { gate -> prefs.getBoolean("${entry.id}:gate:$gate", false) }''', '''        requiredGates.associateWith { gate -> prefs.getBoolean("gate:$gate", false) }''', "step gate keys")

t = rep(t, '''    val requiresNote = state == "NOTE" || state == "NOT_APPLICABLE"
    val requiresResolution = state == "BLOCKING"
    val stateComplete = (!requiresNote || note.isNotBlank()) && (!requiresResolution || (note.isNotBlank() && resolution.isNotBlank()))
    val canAdvance = stateComplete && gatesSatisfied''', '''    val requiresNote = state == "NOTE" || state == "NOT_APPLICABLE"
    val requiresResolution = state == "BLOCKING"
    val stateSelected = state != "NOT_CHECKED"
    val stateComplete = stateSelected && (!requiresNote || note.isNotBlank()) && (!requiresResolution || (note.isNotBlank() && resolution.isNotBlank()))
    val canAdvance = stateComplete && gatesSatisfied''', "require explicit state")

# This line intentionally exists in both the sequential and checklist implementations.
t = rep_n(t, '''                                    prefs.edit().putBoolean("${entry.id}:gate:$gate", !confirmed).apply()''', '''                                    prefs.edit().putBoolean("gate:$gate", !confirmed).apply()''', "shared gate persistence", 2)

t = rep(t, '''            if (!gatesSatisfied) Text("Переход дальше заблокирован: не подтверждены обязательные условия безопасности.", color = MaterialTheme.colorScheme.error)
            else if (!stateComplete) Text(
                if (state == "BLOCKING") "Блокирующее замечание нельзя закрыть без комментария и оформленного решения."
                else "Для этого состояния требуется комментарий.",
                color = MaterialTheme.colorScheme.error
            )''', '''            if (!gatesSatisfied) Text("Переход дальше заблокирован: не подтверждены обязательные условия безопасности.", color = MaterialTheme.colorScheme.error)
            else if (!stateComplete) Text(
                when {
                    state == "NOT_CHECKED" -> "Перед переходом выберите результат проверки этого пункта."
                    state == "BLOCKING" -> "Блокирующее замечание нельзя закрыть без комментария и оформленного решения."
                    else -> "Для этого состояния требуется комментарий."
                },
                color = MaterialTheme.colorScheme.error
            )''', "explicit state message")

# Checklist/area views share exactly the same item and gate state as sequential views.
t = rep(t, '''        routeGates.associateWith { gate -> prefs.getBoolean("${entry.id}:gate:$gate", false) }''', '''        routeGates.associateWith { gate -> prefs.getBoolean("gate:$gate", false) }''', "checklist gate keys")

t = rep(t, '''        targets.count { item -> (prefs.getString("${entry.id}:${item.id}:state", "NOT_CHECKED") ?: "NOT_CHECKED") != "NOT_CHECKED" }''', '''        targets.count { item -> (prefs.getString("item:${item.id}:state", "NOT_CHECKED") ?: "NOT_CHECKED") != "NOT_CHECKED" }''', "checklist completed count")

t = rep(t, '''                    val stateKey = "${entry.id}:${item.id}:state"''', '''                    val stateKey = "item:${item.id}:state"''', "checklist item key")

write(rel, t)

# Distinguish the stricter acceptance semantics in the Beta build identity.
gradle_rel = "app/build.gradle.kts"
g = read(gradle_rel)
g, count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.2.2-beta-recovery5"', g, count=1)
if count != 1:
    raise SystemExit("versionName not found")
write(gradle_rel, g)

print("Recovery patch 5 applied")
