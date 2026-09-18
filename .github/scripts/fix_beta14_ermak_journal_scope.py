from pathlib import Path

paths = [
    Path('app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt'),
]
old = '''    val visible = scenarios.orEmpty().filter { scenario ->
        (initialEquipmentId == null || initialEquipmentId in scenario.equipmentIds) &&
            (query.isBlank() || listOf(scenario.title, scenario.symptom, scenario.category)
                .any { it.contains(query, ignoreCase = true) })
    }
'''
new = '''    val visible = if (catalogMode == "scenarios") {
        scenarios.orEmpty().filter { scenario ->
            (initialEquipmentId == null || initialEquipmentId in scenario.equipmentIds) &&
                (query.isBlank() || listOf(scenario.title, scenario.symptom, scenario.category)
                    .any { it.contains(query, ignoreCase = true) })
        }
    } else {
        emptyList()
    }
'''
for path in paths:
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'Expected visible block not found in {path}')
    path.write_text(text.replace(old, new, 1))
