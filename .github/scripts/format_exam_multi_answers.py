from pathlib import Path

TARGETS = [
    Path("app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/ui/ExamQuestionScreen.kt"),
]

OLD = '''            androidx.compose.material3.Surface(
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.42f)
            ) {
                Text(item.correctAnswer, modifier = Modifier.fillMaxWidth().padding(12.dp), style = MaterialTheme.typography.bodyLarge)
            }
'''

NEW = '''            androidx.compose.material3.Surface(
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.42f)
            ) {
                val answerParts = item.correctAnswer
                    .split('•')
                    .map(String::trim)
                    .filter(String::isNotBlank)
                val isBulletedAnswer = '•' in item.correctAnswer
                Column(
                    modifier = Modifier.fillMaxWidth().padding(12.dp),
                    verticalArrangement = Arrangement.spacedBy(if (isBulletedAnswer) 6.dp else 0.dp)
                ) {
                    answerParts.forEach { answer ->
                        Text(
                            text = if (isBulletedAnswer) "• $answer" else answer,
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
'''

for path in TARGETS:
    text = path.read_text(encoding="utf-8")
    if NEW in text:
        continue
    if OLD not in text:
        raise SystemExit(f"Expected answer block not found in {path}")
    path.write_text(text.replace(OLD, NEW, 1), encoding="utf-8")

print("Exam multi-answer formatting applied")
