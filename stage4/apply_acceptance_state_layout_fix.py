#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
rel = Path("app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt")
path = root / rel
text = path.read_text(encoding="utf-8")

old = '''            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                item { FilterChip(state == "NOT_CHECKED", { persistState("NOT_CHECKED") }, label = { Text("Не проверено") }) }
                item { FilterChip(state == "OK", { persistState("OK") }, label = { Text("Проверено") }) }
                item { FilterChip(state == "NOTE", { persistState("NOTE") }, label = { Text("Замечание") }) }
                item { FilterChip(state == "BLOCKING", { persistState("BLOCKING") }, label = { Text("Блокирующее") }) }
                item { FilterChip(state == "NOT_APPLICABLE", { persistState("NOT_APPLICABLE") }, label = { Text("Не применяется") }) }
            }'''

new = '''            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(state == "NOT_CHECKED", { persistState("NOT_CHECKED") }, label = { Text("Не проверено") })
                    FilterChip(state == "OK", { persistState("OK") }, label = { Text("Проверено") })
                    FilterChip(state == "NOTE", { persistState("NOTE") }, label = { Text("Замечание") })
                }
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(state == "BLOCKING", { persistState("BLOCKING") }, label = { Text("Блокирующее замечание") })
                    FilterChip(state == "NOT_APPLICABLE", { persistState("NOT_APPLICABLE") }, label = { Text("Не применяется") })
                }
            }'''

count = text.count(old)
if count != 1:
    raise SystemExit(f"acceptance state row: expected exactly one match, got {count}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Stage 4 acceptance state layout fix applied")
