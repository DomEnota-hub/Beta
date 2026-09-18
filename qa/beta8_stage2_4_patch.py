from pathlib import Path

ROOTS = [Path("app"), Path("patch/app")]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"{label}: expected 1 occurrence, found {count}"
    return text.replace(old, new, 1)


def patch_diagnostics(root: Path) -> None:
    path = root / "src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt"
    text = path.read_text(encoding="utf-8")

    old = '                        Text("Связано: ${observation.equipmentIds.joinToString()}", style = MaterialTheme.typography.bodySmall)\n'
    new = '''                        val relatedEquipmentTitles = observation.equipmentIds
                            .mapNotNull { id -> Vl80sObservationCatalog.equipment(id)?.title }
                            .distinct()
                        if (relatedEquipmentTitles.isNotEmpty()) {
                            Text("Связано: ${relatedEquipmentTitles.joinToString()}", style = MaterialTheme.typography.bodySmall)
                        }
'''
    text = replace_once(text, old, new, f"observation raw equipment ids in {path}")

    path.write_text(text, encoding="utf-8")


def patch_theme(root: Path) -> None:
    path = root / "src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt"
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    BLUE("Янтарный", RailAmber, RailAmberSoft),',
        '    BLUE("Холодный синий", Color(0xFF82A9FF), Color(0xFF182947)),',
        f"historical blue palette in {path}",
    )
    path.write_text(text, encoding="utf-8")


def patch_app_shell(root: Path) -> None:
    path = root / "src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '                        Text("ВЛ80С • Ермак", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.primary)',
        '                        Text("Пользовательский профиль", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.primary)',
        f"drawer profile label in {path}",
    )

    text = replace_once(
        text,
        '                    AccentPalette.BLUE -> "Основной янтарный акцент нового интерфейса"',
        '                    AccentPalette.BLUE -> "Классический холодный синий акцент приложения"',
        f"blue palette description in {path}",
    )

    text = replace_once(
        text,
        '    RailInfoBand("Основная тема dev8: графитовый фон, металлические вторичные элементы и янтарный рабочий акцент. Красный зарезервирован для опасности и ОПП.")',
        '    RailInfoBand("Графитовая основа постоянна; выбранная палитра меняет рабочий акцент. Красный зарезервирован для опасности и ОПП.")',
        f"palette info band in {path}",
    )

    old_head = '''private fun PaletteScreen(
    palette: AccentPalette,
    onPaletteChange: (AccentPalette) -> Unit
) {
'''
    new_head = '''private fun PaletteScreen(
    palette: AccentPalette,
    onPaletteChange: (AccentPalette) -> Unit
) {
    val context = LocalContext.current
    val packageInfo = remember(context) {
        context.packageManager.getPackageInfo(context.packageName, 0)
    }
    val actualVersionCode = if (android.os.Build.VERSION.SDK_INT >= 28) {
        packageInfo.longVersionCode
    } else {
        @Suppress("DEPRECATION")
        packageInfo.versionCode.toLong()
    }
'''
    text = replace_once(text, old_head, new_head, f"palette screen version source in {path}")

    text = replace_once(
        text,
        '        Metric("Версия", "1.2.2-dev10 (138)")',
        '        Metric("Версия", "${packageInfo.versionName ?: "—"} ($actualVersionCode)")',
        f"hardcoded version in {path}",
    )

    path.write_text(text, encoding="utf-8")


def patch_identity(root: Path) -> None:
    path = root / "build.gradle.kts"
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, "        versionCode = 152", "        versionCode = 153", f"versionCode in {path}")
    text = replace_once(
        text,
        '        versionName = "1.2.2-dev14-beta7"',
        '        versionName = "1.2.2-dev14-beta8"',
        f"versionName in {path}",
    )
    path.write_text(text, encoding="utf-8")


for root in ROOTS:
    patch_diagnostics(root)
    patch_theme(root)
    patch_app_shell(root)
    patch_identity(root)

# app/patch source mirrors touched in this stage must remain byte-identical.
for rel in (
    "build.gradle.kts",
    "src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt",
    "src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt",
    "src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt",
):
    a = Path("app") / rel
    b = Path("patch/app") / rel
    assert a.read_bytes() == b.read_bytes(), f"mirror mismatch: {rel}"

# Guard the specific user-facing regressions this stage is intended to remove.
screen = Path("app/src/main/java/ru/railbrake/calculator/ui/DiagnosticScreen.kt").read_text(encoding="utf-8")
shell = Path("app/src/main/java/ru/railbrake/calculator/ui/BrakeCalculatorApp.kt").read_text(encoding="utf-8")
theme = Path("app/src/main/java/ru/railbrake/calculator/ui/theme/Theme.kt").read_text(encoding="utf-8")
assert 'observation.equipmentIds.joinToString()' not in screen
assert '1.2.2-dev10 (138)' not in shell
assert 'Text("ВЛ80С • Ермак"' not in shell
assert 'BLUE("Холодный синий", Color(0xFF82A9FF), Color(0xFF182947))' in theme

print("Beta8 stages 2-4 patched and mirrors verified")
