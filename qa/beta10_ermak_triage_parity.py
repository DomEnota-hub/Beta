from pathlib import Path

ROOTS = [Path("app"), Path("patch/app")]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    assert count == 1, f"{label}: expected 1 occurrence, found {count}"
    return text.replace(old, new, 1)


def patch_screen(root: Path) -> None:
    path = root / "src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        "import androidx.compose.runtime.mutableStateOf\n",
        "import androidx.compose.runtime.mutableIntStateOf\nimport androidx.compose.runtime.mutableStateOf\n",
        f"mutableIntStateOf import in {path}",
    )

    text = replace_once(
        text,
        '    var uncertain by rememberSaveable(scenario.id) { mutableStateOf(false) }\n    val node = scenario.nodes[nodeId]\n',
        '    var uncertain by rememberSaveable(scenario.id) { mutableStateOf(false) }\n    var questionNumber by rememberSaveable(scenario.id) { mutableIntStateOf(1) }\n    val node = scenario.nodes[nodeId]\n',
        f"question number state in {path}",
    )

    old = '''        } else {
            item {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = if (node.type == "terminal") MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant
                    ),
                    shape = RoundedCornerShape(18.dp)
                ) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        Text(
                            when (node.type) {
                                "question" -> "Уточнение"
                                "finding" -> "Выявленный признак"
                                "source_action" -> "Подтверждённое действие"
                                "terminal" -> "Результат"
                                else -> "Шаг диагностики"
                            },
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Black
                        )
                        Text(node.text)
                        node.choices.forEach { choice ->
                            Button(
                                onClick = {
                                    history = history + "${node.text} — ${choice.label}"
                                    nodeId = choice.nextNodeId
                                },
                                modifier = Modifier.fillMaxWidth()
                            ) { Text(choice.label) }
                        }
                        if (node.type == "question" && node.choices.none { choice ->
                                choice.label.contains("не уверен", true) || choice.label.contains("не знаю", true) ||
                                    choice.label.contains("недостаточно", true)
                            }) {
                            TextButton(
                                onClick = {
                                    history = history + "${node.text} — Не уверен"
                                    uncertain = true
                                },
                                modifier = Modifier.fillMaxWidth()
                            ) { Text("Не уверен — записать и завершить") }
                        }
                        if (node.choices.isEmpty() && node.nextNodeId != null) {
                            Button(
                                onClick = {
                                    if (node.text.isNotBlank()) history = history + node.text
                                    nodeId = node.nextNodeId
                                },
                                modifier = Modifier.fillMaxWidth()
                            ) { Text("Продолжить") }
                        }
                    }
                }
            }
        }
'''

    new = '''        } else {
            item {
                if (node.type == "question") {
                    val uncertaintyChoice = node.choices.firstOrNull { choice ->
                        choice.label.contains("не уверен", true) ||
                            choice.label.contains("не знаю", true) ||
                            choice.label.contains("недостаточно", true)
                    }
                    val answerChoices = node.choices.filterNot { it == uncertaintyChoice }
                    Card(
                        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.secondary.copy(alpha = 0.42f)),
                        shape = RoundedCornerShape(17.dp),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Text("Уточнение симптома", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
                            Text("Шаг $questionNumber; дальнейший вопрос зависит от ответа")
                            Text(node.text, fontWeight = FontWeight.Bold)
                            if (answerChoices.isNotEmpty()) {
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
                            TextButton(
                                onClick = {
                                    history = history + "${node.text} — ${uncertaintyChoice?.label ?: "Не уверен"}"
                                    if (uncertaintyChoice != null) {
                                        questionNumber += 1
                                        nodeId = uncertaintyChoice.nextNodeId
                                    } else {
                                        uncertain = true
                                    }
                                }
                            ) { Text("Не уверен — записать и завершить") }
                            history.filter { " — " in it }.forEach {
                                Text("• $it", style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                } else {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = if (node.type == "terminal") MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant
                        ),
                        shape = RoundedCornerShape(18.dp)
                    ) {
                        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                            Text(
                                when (node.type) {
                                    "finding" -> "Выявленный признак"
                                    "source_action" -> "Подтверждённое действие"
                                    "terminal" -> "Результат"
                                    else -> "Шаг диагностики"
                                },
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.Black
                            )
                            Text(node.text)
                            node.choices.forEach { choice ->
                                Button(
                                    onClick = {
                                        history = history + "${node.text} — ${choice.label}"
                                        nodeId = choice.nextNodeId
                                    },
                                    modifier = Modifier.fillMaxWidth()
                                ) { Text(choice.label) }
                            }
                            if (node.choices.isEmpty() && node.nextNodeId != null) {
                                Button(
                                    onClick = {
                                        if (node.text.isNotBlank()) history = history + node.text
                                        nodeId = node.nextNodeId
                                    },
                                    modifier = Modifier.fillMaxWidth()
                                ) { Text("Продолжить") }
                            }
                        }
                    }
                }
            }
        }
'''
    text = replace_once(text, old, new, f"Ermak triage card in {path}")

    text = replace_once(
        text,
        '''                    OutlinedButton(onClick = {
                        nodeId = scenario.startNodeId
                        history = emptyList()
                        uncertain = false
                    }) { Text("Начать заново") }
''',
        '''                    OutlinedButton(onClick = {
                        nodeId = scenario.startNodeId
                        history = emptyList()
                        uncertain = false
                        questionNumber = 1
                    }) { Text("Начать заново") }
''',
        f"Ermak triage reset in {path}",
    )

    path.write_text(text, encoding="utf-8")


def patch_version(root: Path) -> None:
    path = root / "build.gradle.kts"
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, "        versionCode = 154", "        versionCode = 155", f"versionCode in {path}")
    text = replace_once(
        text,
        '        versionName = "1.2.2-dev14-beta9"',
        '        versionName = "1.2.2-dev14-beta10"',
        f"versionName in {path}",
    )
    path.write_text(text, encoding="utf-8")


for root in ROOTS:
    patch_screen(root)
    patch_version(root)

for rel in (
    "build.gradle.kts",
    "src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt",
):
    a = Path("app") / rel
    b = Path("patch/app") / rel
    assert a.read_bytes() == b.read_bytes(), f"mirror mismatch: {rel}"

screen = Path("app/src/main/java/ru/railbrake/calculator/ui/ErmakDiagnosticsScreen.kt").read_text(encoding="utf-8")
assert 'Text("Уточнение симптома"' in screen
assert 'Text("Шаг $questionNumber; дальнейший вопрос зависит от ответа")' in screen
assert 'Text("Не уверен — записать и завершить")' in screen
assert '"question" -> "Уточнение"' not in screen
print("Beta10 Ermak triage parity patched and mirrors verified")
