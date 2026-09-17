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


rel = "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"
t = read(rel)

# Pneumatic training-reference benchmarks are canonical content, not metadata.
t = rep(t, '''        id.startsWith("VL-EQ-") -> listOf(TechnicalFamily.VL80S to TechnicalSection.EQUIPMENT)
        id.startsWith("VL-SCH-") -> listOf(TechnicalFamily.VL80S to TechnicalSection.ELECTRICAL, TechnicalFamily.VL80S to TechnicalSection.PNEUMATIC)''', '''        id.startsWith("VL-EQ-") -> listOf(TechnicalFamily.VL80S to TechnicalSection.EQUIPMENT)
        id.startsWith("VL-PN-REF-") -> listOf(TechnicalFamily.VL80S to TechnicalSection.PNEUMATIC)
        id.startsWith("VL-SCH-") -> listOf(TechnicalFamily.VL80S to TechnicalSection.ELECTRICAL, TechnicalFamily.VL80S to TechnicalSection.PNEUMATIC)''', "pneumatic reference routing")

old_pneumatic = '''    private fun loadVl80sPneumatic(): List<TechnicalEntry> {
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
    }'''
new_pneumatic = '''    private fun loadVl80sPneumatic(): List<TechnicalEntry> {
        val root = json("technical/vl80s_pneumatic.json")
        val states = root.array("states").objects()
        val views = root.array("views").objects().map { item ->
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
        val references = root.array("referenceBenchmarks").objects().map { item ->
            entry(
                item, TechnicalFamily.VL80S, TechnicalSection.PNEUMATIC,
                title = item.optString("label"),
                subtitle = item.optString("value"),
                status = item.optString("status"),
                blocks = listOfNotEmpty(
                    block("Учебный ориентир", item.optString("value")),
                    block("Статус применимости", item.optString("status")),
                    block("Источники", item.array("sourceRefs").strings())
                )
            )
        }
        return views + references
    }'''
t = rep(t, old_pneumatic, new_pneumatic, "VL80 pneumatic references")

# Ermak system map has canonical critical cross-system links and extra system facets.
old_systems = '''    private fun loadErmakSystems(): List<TechnicalEntry> =
        json("technical/ermak_system_map.json").array("systems").objects().map { item ->
            entry(
                item, TechnicalFamily.ERMAK, TechnicalSection.SYSTEMS,
                title = item.optString("name").ifBlank { item.optString("title") },
                subtitle = item.optString("purpose").ifBlank { item.optString("description") },
                status = item.optString("evidenceStatus").ifBlank { item.optString("status") },
                blocks = listOfNotEmpty(
                    block("Назначение", item.optString("purpose").ifBlank { item.optString("description") }),
                    block("Состав", item.array("components").strings() + item.array("equipmentRefs").strings()),
                    block("Входы", item.array("inputs").strings()),
                    block("Выходы", item.array("outputs").strings()),
                    block("Защиты", item.array("protections").strings()),
                    block("Связи", item.array("relations").stringsOrSummaries()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
                ),
                relatedIds = (item.array("equipmentRefs").strings() +
                    item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) } +
                    ermakCanonicalRelated(item.optString("id"))).distinct()
            )
        }'''
new_systems = '''    private fun loadErmakSystems(): List<TechnicalEntry> {
        val root = json("technical/ermak_system_map.json")
        val criticalLinks = root.array("criticalLinks")
        return root.array("systems").objects().map { item ->
            val itemId = item.optString("id")
            val criticalLines = mutableListOf<String>()
            val criticalTargets = mutableListOf<String>()
            for (index in 0 until criticalLinks.length()) {
                val link = criticalLinks.optJSONArray(index) ?: continue
                val from = link.optString(0)
                val to = link.optString(1)
                val relation = link.optString(2)
                when (itemId) {
                    from -> {
                        if (to.isNotBlank()) criticalTargets.add(to)
                        criticalLines.add(listOf(from, "→", to, relation).filter(String::isNotBlank).joinToString(" "))
                    }
                    to -> {
                        if (from.isNotBlank()) criticalTargets.add(from)
                        criticalLines.add(listOf(from, "→", to, relation).filter(String::isNotBlank).joinToString(" "))
                    }
                }
            }
            entry(
                item, TechnicalFamily.ERMAK, TechnicalSection.SYSTEMS,
                title = item.optString("name").ifBlank { item.optString("title") },
                subtitle = item.optString("purpose").ifBlank { item.optString("description") },
                status = item.optString("evidenceStatus").ifBlank { item.optString("status") },
                blocks = listOfNotEmpty(
                    block("Назначение", item.optString("purpose").ifBlank { item.optString("description") }),
                    block("Область", item.optString("scope")),
                    block("Состав", item.array("components").strings() + item.array("equipmentRefs").strings()),
                    block("Базовый состав", item.array("baseComponents").strings()),
                    block("Функции", item.array("functions").strings()),
                    block("Входы", item.array("inputs").strings()),
                    block("Выходы", item.array("outputs").strings()),
                    block("Защиты", item.array("protections").strings()),
                    block("Профили исполнения", item.array("profiles").strings()),
                    block("Зависимости", item.array("dependencies").strings()),
                    block("Интерфейсы", item.array("interfaces").stringsOrSummaries()),
                    block("Домены", item.array("domains").strings()),
                    block("Действия", item.array("actions").stringsOrSummaries()),
                    block("Базовая система", item.optString("baseSystem")),
                    block("Цели", item.array("targets").strings()),
                    block("Связи", item.array("relations").stringsOrSummaries()),
                    block("Критические межсистемные связи", criticalLines),
                    block("Доказательная оговорка", item.optString("evidenceNote")),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
                ),
                relatedIds = (item.array("equipmentRefs").strings() +
                    item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) } +
                    item.array("dependencies").strings() + criticalTargets +
                    ermakCanonicalRelated(itemId)).distinct()
            )
        }
    }'''
t = rep(t, old_systems, new_systems, "Ermak system facets and critical links")

write(rel, t)

gradle_rel = "app/build.gradle.kts"
g = read(gradle_rel)
g, count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.2.2-beta-recovery8"', g, count=1)
if count != 1:
    raise SystemExit("versionName not found")
write(gradle_rel, g)

print("Recovery patch 8 applied")
