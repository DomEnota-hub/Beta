from pathlib import Path

TARGETS = [
    Path("app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt"),
]

OLD = 'text = if (isBulletedAnswer) "• $answer" else answer'
NEW = 'text = if (isBulletedAnswer) "- $answer" else answer'

for path in TARGETS:
    text = path.read_text(encoding="utf-8")
    if NEW in text:
        continue
    if OLD not in text:
        raise SystemExit(f"Expected list marker not found in {path}")
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")

print("Exam answer list marker changed to dash")
