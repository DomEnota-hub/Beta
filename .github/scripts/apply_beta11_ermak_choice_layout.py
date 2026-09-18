from pathlib import Path

paths = [
    Path('app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt'),
]

old = '''                            if (answerChoices.isNotEmpty()) {
                                Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                    answerChoices.getOrNull(0)?.let { choice ->
                                        Button(onClick = {
                                            history = history + "${node.text} — ${choice.label}"
                                            questionNumber += 1
                                            nodeId = choice.nextNodeId
                                        }) { Text(choice.label) }
                                    }
                                    answerChoices.getOrNull(1)?.let { choice ->
                                        OutlinedButton(onClick = {
                                            history = history + "${node.text} — ${choice.label}"
                                            questionNumber += 1
                                            nodeId = choice.nextNodeId
                                        }) { Text(choice.label) }
                                    }
                                }
                                answerChoices.drop(2).forEach { choice ->
                                    OutlinedButton(
                                        onClick = {
                                            history = history + "${node.text} — ${choice.label}"
                                            questionNumber += 1
                                            nodeId = choice.nextNodeId
                                        },
                                        modifier = Modifier.fillMaxWidth()
                                    ) { Text(choice.label) }
                                }
                            }
'''

new = '''                            if (answerChoices.isNotEmpty()) {
                                val compactBinaryChoices = answerChoices.size == 2 &&
                                    answerChoices.all { it.label.length <= 14 }
                                if (compactBinaryChoices) {
                                    Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                                        answerChoices.getOrNull(0)?.let { choice ->
                                            Button(onClick = {
                                                history = history + "${node.text} — ${choice.label}"
                                                questionNumber += 1
                                                nodeId = choice.nextNodeId
                                            }) { Text(choice.label) }
                                        }
                                        answerChoices.getOrNull(1)?.let { choice ->
                                            OutlinedButton(onClick = {
                                                history = history + "${node.text} — ${choice.label}"
                                                questionNumber += 1
                                                nodeId = choice.nextNodeId
                                            }) { Text(choice.label) }
                                        }
                                    }
                                } else {
                                    answerChoices.forEachIndexed { index, choice ->
                                        if (index == 0) {
                                            Button(
                                                onClick = {
                                                    history = history + "${node.text} — ${choice.label}"
                                                    questionNumber += 1
                                                    nodeId = choice.nextNodeId
                                                },
                                                modifier = Modifier.fillMaxWidth()
                                            ) { Text(choice.label) }
                                        } else {
                                            OutlinedButton(
                                                onClick = {
                                                    history = history + "${node.text} — ${choice.label}"
                                                    questionNumber += 1
                                                    nodeId = choice.nextNodeId
                                                },
                                                modifier = Modifier.fillMaxWidth()
                                            ) { Text(choice.label) }
                                        }
                                    }
                                }
                            }
'''

for path in paths:
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'Expected choice block not found in {path}')
    path.write_text(text.replace(old, new, 1))

for path in [Path('app/build.gradle.kts'), Path('patch/app/build.gradle.kts')]:
    text = path.read_text()
    text = text.replace('versionCode = 155', 'versionCode = 156')
    text = text.replace('versionName = "1.2.2-dev14-beta10"', 'versionName = "1.2.2-dev14-beta11"')
    path.write_text(text)

for path in paths:
    text = path.read_text()
    assert 'compactBinaryChoices' in text
    assert 'answerChoices.forEachIndexed' in text
