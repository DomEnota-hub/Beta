from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

DATA_FILES = [
    REPO / "app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
    REPO / "patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
]
UI_FILES = [
    REPO / "app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt",
    REPO / "patch/app/src/main/java/ru/railbrake/calculator/ui/TechnicalCatalogScreen.kt",
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


wheel_helper = r'''
    private fun loadWheelFlatReference(family: TechnicalFamily): List<TechnicalEntry> {
        val id = if (family == TechnicalFamily.VL80S) "vl80-wheel-flats" else "ER-KB-WHEEL-FLATS"
        return listOf(
            TechnicalEntry(
                id = id,
                family = family,
                section = TechnicalSection.KNOWLEDGE,
                title = "Ползуны колесных пар: скорость и действия",
                subtitle = "Порядок следования при обнаружении ползуна (выбоины) в пути",
                status = "INFORMATION",
                blocks = listOf(
                    TechnicalBlock("Важно", listOf(
                        "Таблица ниже относится к порядку следования после обнаружения ползуна в пути. Она не заменяет браковочные нормы для штатной эксплуатации колесных пар.",
                        "Размер ползуна в таблице — его глубина. Приоритет имеют действующие ПТЭ, распоряжения владельца инфраструктуры и указания ДСП/ДНЦ в конкретной ситуации."
                    )),
                    TechnicalBlock("Таблица — локомотив", listOf(
                        "> 1–2 мм¦Не более 15 км/ч¦До ближайшей железнодорожной станции; колесная пара должна быть заменена.",
                        "> 2–4 мм¦Не более 10 км/ч¦До ближайшей железнодорожной станции; колесная пара должна быть заменена.",
                        "> 4 мм¦Не более 10 км/ч¦До ближайшей станции только при вывешивании колесной пары или исключении возможности вращения колеса."
                    )),
                    TechnicalBlock("При ползуне более 4 мм на локомотиве", listOf(
                        "Локомотив должен быть отцеплен от поезда.",
                        "Тормозные цилиндры и тяговый электродвигатель (группа электродвигателей) поврежденной колесной пары должны быть отключены.",
                        "Осевой редуктор поврежденной колесной пары должен быть отключен."
                    )),
                    TechnicalBlock("Таблица — пассажирские и грузовые вагоны", listOf(
                        "> 1–2 мм¦Пассажирский: не более 100 км/ч; грузовой: не более 70 км/ч¦До ближайшего ПТО, имеющего средства для замены колесных пар.",
                        "> 2–6 мм¦Не более 15 км/ч¦До ближайшей железнодорожной станции; колесная пара должна быть заменена.",
                        "> 6–12 мм¦Не более 10 км/ч¦До ближайшей железнодорожной станции; колесная пара должна быть заменена.",
                        "> 12 мм¦Не более 10 км/ч¦До ближайшей станции при вывешивании колесной пары или исключении возможности вращения колеса."
                    )),
                    TechnicalBlock("Нормативная основа", listOf(
                        "Приказ Минтранса России от 23.06.2022 № 250 «Об утверждении Правил технической эксплуатации железных дорог Российской Федерации», пункт 155."
                    ))
                ),
                searchText = "ползун ползуны выбоина колесная пара колесные пары скорость 15 10 100 70 локомотив вагон птэ пункт 155".lowercase()
            )
        )
    }
'''

for path in DATA_FILES:
    text = path.read_text(encoding="utf-8")
    if "Ползуны колесных пар: скорость и действия" in text:
        continue
    text = replace_once(
        text,
        "TechnicalSection.KNOWLEDGE -> loadVl80sKnowledge()",
        "TechnicalSection.KNOWLEDGE -> loadVl80sKnowledge() + loadWheelFlatReference(TechnicalFamily.VL80S)",
        f"{path}: VL80S knowledge hook",
    )
    text = replace_once(
        text,
        "TechnicalSection.KNOWLEDGE -> loadErmakKnowledge()",
        "TechnicalSection.KNOWLEDGE -> loadErmakKnowledge() + loadWheelFlatReference(TechnicalFamily.ERMAK)",
        f"{path}: Ermak knowledge hook",
    )
    marker = "\n\n    private fun loadSafety(family: TechnicalFamily): List<TechnicalEntry> {"
    if marker not in text:
        raise SystemExit(f"{path}: loadSafety marker not found")
    text = text.replace(marker, "\n" + wheel_helper + marker, 1)
    path.write_text(text, encoding="utf-8")

old_import = "import androidx.compose.foundation.layout.width\n"
new_import = "import androidx.compose.foundation.layout.width\nimport androidx.compose.foundation.layout.weight\n"

old_block = '''        items(entry.blocks, key = { it.title }) { block ->
            val displayLines = repository.displayLines(block.lines)
                .mapNotNull(::technicalPresentationLine)
                .distinct()
            val references = repository.referencedEntries(block.lines)
            if (displayLines.isEmpty() && references.isEmpty()) return@items
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = technicalBlockContainer(entry.section, block.title)),
                border = BorderStroke(1.dp, accent.copy(alpha = 0.38f)),
                shape = RoundedCornerShape(18.dp)
            ) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                    Text(block.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                    displayLines.forEach { line -> Text("• $line") }
                    references.forEach { target ->
                        OutlinedButton(
                            onClick = { onOpen(target) },
                            modifier = Modifier.fillMaxWidth(),
                            border = BorderStroke(1.dp, Color.Black)
                        ) { Text("${technicalEntryTitle(target)} →") }
                    }
                }
            }
        }
'''

new_block = '''        items(entry.blocks, key = { it.title }) { block ->
            val displayLines = repository.displayLines(block.lines)
                .mapNotNull(::technicalPresentationLine)
                .distinct()
            val references = repository.referencedEntries(block.lines)
            val referenceTableRows = if (block.title.startsWith("Таблица —")) {
                block.lines.mapNotNull { line ->
                    line.split("¦", limit = 3).takeIf { it.size == 3 }
                }
            } else emptyList()
            if (displayLines.isEmpty() && references.isEmpty() && referenceTableRows.isEmpty()) return@items
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = technicalBlockContainer(entry.section, block.title)),
                border = BorderStroke(1.dp, accent.copy(alpha = 0.38f)),
                shape = RoundedCornerShape(18.dp)
            ) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                    Text(block.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
                    if (referenceTableRows.isNotEmpty()) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text("Размер", modifier = Modifier.weight(0.75f), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Black)
                            Text("Скорость", modifier = Modifier.weight(0.9f), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Black)
                            Text("Действие", modifier = Modifier.weight(1.55f), style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Black)
                        }
                        HorizontalDivider()
                        referenceTableRows.forEachIndexed { index, cells ->
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(cells[0], modifier = Modifier.weight(0.75f), style = MaterialTheme.typography.bodySmall, fontWeight = FontWeight.Bold)
                                Text(cells[1], modifier = Modifier.weight(0.9f), style = MaterialTheme.typography.bodySmall)
                                Text(cells[2], modifier = Modifier.weight(1.55f), style = MaterialTheme.typography.bodySmall)
                            }
                            if (index != referenceTableRows.lastIndex) HorizontalDivider()
                        }
                    } else {
                        displayLines.forEach { line -> Text("• $line") }
                        references.forEach { target ->
                            OutlinedButton(
                                onClick = { onOpen(target) },
                                modifier = Modifier.fillMaxWidth(),
                                border = BorderStroke(1.dp, Color.Black)
                            ) { Text("${technicalEntryTitle(target)} →") }
                        }
                    }
                }
            }
        }
'''

for path in UI_FILES:
    text = path.read_text(encoding="utf-8")
    if "referenceTableRows" in text:
        continue
    text = replace_once(text, old_import, new_import, f"{path}: weight import")
    text = replace_once(text, old_block, new_block, f"{path}: detail block renderer")
    path.write_text(text, encoding="utf-8")

print("Wheel-flat reference patch applied")
