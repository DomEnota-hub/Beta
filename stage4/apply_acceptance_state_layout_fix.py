#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
path = root / "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
text = path.read_text(encoding="utf-8")

old = '''            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(availableStates) { stateId ->
                    FilterChip(
                        selected = state == stateId,
                        onClick = { persistState(stateId) },
                        label = { Text(stateLabel(stateId)) }
                    )
                }
            }'''
new = '''            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    availableStates.filter { it in listOf("NOT_CHECKED", "OK", "NOTE") }.forEach { stateId ->
                        FilterChip(
                            selected = state == stateId,
                            onClick = { persistState(stateId) },
                            label = { Text(stateLabel(stateId)) }
                        )
                    }
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    availableStates.filter { it in listOf("BLOCKING", "NOT_APPLICABLE") }.forEach { stateId ->
                        FilterChip(
                            selected = state == stateId,
                            onClick = { persistState(stateId) },
                            label = { Text(stateLabel(stateId)) }
                        )
                    }
                }
            }'''
if text.count(old) != 1:
    raise SystemExit(f"dynamic acceptance state row: expected one match, got {text.count(old)}")
text = text.replace(old, new, 1)

old_reason = 'label = { Text(if (state == "NOT_APPLICABLE") "Причина применимости / варианта" else "Комментарий и локализация") },'
new_reason = 'label = { Text(if (state == "NOT_APPLICABLE") "Причина неприменимости / вариант" else "Комментарий и локализация") },'
if text.count(old_reason) != 1:
    raise SystemExit(f"not-applicable reason label: expected one match, got {text.count(old_reason)}")
text = text.replace(old_reason, new_reason, 1)

path.write_text(text, encoding="utf-8")
print("Stage 4 acceptance state layout fix applied")
