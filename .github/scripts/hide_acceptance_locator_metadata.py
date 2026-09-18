from pathlib import Path

PATHS = [
    Path("app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalPresentation.kt"),
]

OLD = '''private val rangeTitle = Regex("^(\\\\d+)-(\\\\d+)$")
'''
NEW = '''private val rangeTitle = Regex("^(\\\\d+)-(\\\\d+)$")

private val hiddenServiceLocators = setOf(
    "search by symptom/equipment",
    "applicable brake rules"
)
'''

ATOM_OLD = '''    if (key in hiddenMetadata) return null
    exactLabels[key]?.let { return it }
'''
ATOM_NEW = '''    if (key in hiddenMetadata || key in hiddenServiceLocators || key.startsWith("search by ")) return null
    exactLabels[key]?.let { return it }
'''

for path in PATHS:
    text = path.read_text(encoding="utf-8")
    if "hiddenServiceLocators" not in text:
        if OLD not in text:
            raise SystemExit(f"rangeTitle anchor not found in {path}")
        text = text.replace(OLD, NEW, 1)
    if 'key.startsWith("search by ")' not in text:
        if ATOM_OLD not in text:
            raise SystemExit(f"presentation atom anchor not found in {path}")
        text = text.replace(ATOM_OLD, ATOM_NEW, 1)
    path.write_text(text, encoding="utf-8")

print("Acceptance service locators are hidden from user-facing presentation.")
