#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
p = root / "app/src/main/java/ru/railbrake/calculator/ui/HomeScreen.kt"
text = p.read_text(encoding="utf-8")

text = text.replace("import ru.railbrake.calculator.core.DiagnosticRepository\n", "")
text = text.replace("import ru.railbrake.calculator.core.Vl80sObservationCatalog\n", "")

pattern = re.compile(
    r'''\s*RailInfoBand\(\s*"\$\{DiagnosticRepository\.scenarios\.size\} диагностических сценария • \$\{Vl80sObservationCatalog\.equipment\.size\} узлов оборудования"\s*\)''',
    re.MULTILINE,
)
replacement = '''\n        RailInfoBand(\n            "Диагностические сценарии • оборудование ВЛ80С • технические профили"\n        )'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit(f"HomeScreen startup-count block: expected 1 match, got {count}")
p.write_text(text, encoding="utf-8")

gp = root / "app/build.gradle.kts"
g = gp.read_text(encoding="utf-8")
g, count = re.subn(r'versionName\s*=\s*"[^"]+"', 'versionName = "1.2.2-beta-recovery4"', g, count=1)
if count != 1:
    raise SystemExit("versionName not found")
gp.write_text(g, encoding="utf-8")

print("Startup-light patch applied")
