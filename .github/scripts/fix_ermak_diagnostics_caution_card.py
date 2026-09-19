from pathlib import Path

paths = [
    Path("app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt"),
]

old = '''                BorderedCautionCard(
                    "Быстрая оценка",
                    listOf(
                        "Здесь собраны сценарии, которые полезно быстро открыть в пути. Это только безопасное первичное направление поиска.",
                        "При дыме, огне, дуге, повреждении токоведущих частей или неясном срабатывании защиты прекратите диагностические действия и доложите."
                    )
                )'''
new = '''                InfoCard(
                    "Быстрая оценка",
                    listOf(
                        "Здесь собраны сценарии, которые полезно быстро открыть в пути. Это только безопасное первичное направление поиска.",
                        "При дыме, огне, дуге, повреждении токоведущих частей или неясном срабатывании защиты прекратите диагностические действия и доложите."
                    ),
                    MaterialTheme.colorScheme.surfaceVariant
                )'''

for path in paths:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Quick caution card marker not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

print("Replaced private VL80S caution card with shared InfoCard")
