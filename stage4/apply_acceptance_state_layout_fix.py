#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
path = root / "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt"
text = path.read_text(encoding="utf-8")

first = text.find('state == "NOT_CHECKED"')
last = text.find('state == "NOT_APPLICABLE"', first + 1)
if first < 0 or last < 0:
    raise SystemExit("acceptance state chips not found")
start = text.rfind("LazyRow", max(0, first - 1500), first)
if start < 0:
    raise SystemExit("acceptance LazyRow not found before state chips")
end = text.find("\n            }", last)
if end < 0:
    raise SystemExit("acceptance LazyRow closing brace not found")
end += len("\n            }")
old = text[start:end]
for token in ('NOT_CHECKED','OK','NOTE','BLOCKING','NOT_APPLICABLE'):
    if f'state == "{token}"' not in old:
        raise SystemExit(f"state {token} missing from located LazyRow")

new = '''Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
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
path.write_text(text[:start] + new + text[end:], encoding="utf-8")
print("Stage 4 acceptance state layout fix applied")
