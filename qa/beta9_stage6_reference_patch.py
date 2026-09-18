from pathlib import Path
import re

ROOTS = [Path("app"), Path("patch/app")]


def replace_function(text: str, start: str, end: str, replacement: str, label: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?(?=" + re.escape(end) + r")", re.S)
    match = pattern.search(text)
    assert match, f"{label}: function block not found"
    assert len(pattern.findall(text)) == 1, f"{label}: expected one function block"
    return text[:match.start()] + replacement.rstrip() + "\n\n" + text[match.end():]


def patch_repository(root: Path) -> None:
    path = root / "src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt"
    text = path.read_text(encoding="utf-8")

    systems = r'''    private fun loadErmakSystems(): List<TechnicalEntry> {
        val equipmentRecords = json("technical/ermak_equipment.json").array("records").objects()
        val equipmentBySystem = equipmentRecords
            .flatMap { equipment -> equipment.array("systemIds").strings().map { it to equipment } }
            .groupBy({ it.first }, { it.second })
        val knowledgeArticles = json("technical/ermak_knowledge.json").array("articles").objects()
        val articlesBySystem = knowledgeArticles
            .flatMap { article -> article.array("relatedSystems").strings().map { it to article } }
            .groupBy({ it.first }, { it.second })
        val systemArticleById = knowledgeArticles.mapNotNull { article ->
            article.optString("id")
                .takeIf { it.startsWith("ER-KB-SYS-") }
                ?.removePrefix("ER-KB-")
                ?.let { systemId -> systemId to article }
        }.toMap()

        return json("technical/ermak_system_map.json").array("systems").objects().map { item ->
            val systemId = item.optString("id")
            val equipment = equipmentBySystem[systemId].orEmpty()
            val systemArticle = systemArticleById[systemId]
            val supportingArticles = articlesBySystem[systemId].orEmpty()
                .filter { article ->
                    article.optString("articleType") != "equipment" &&
                        article.optString("id") != systemArticle?.optString("id")
                }
                .distinctBy { it.optString("id") }
            val summary = systemArticle?.optString("summary").orEmpty()
                .ifBlank { item.optString("purpose").ifBlank { item.optString("description") } }
            val relatedSystems = systemArticle?.array("relatedSystems")?.strings().orEmpty()

            entry(
                item, TechnicalFamily.ERMAK, TechnicalSection.SYSTEMS,
                title = item.optString("name").ifBlank { item.optString("title") },
                subtitle = summary,
                status = item.optString("evidenceStatus").ifBlank { item.optString("status") },
                blocks = listOfNotEmpty(
                    block("Назначение", summary),
                    block("Как работает", systemArticle?.optString("principle").orEmpty()),
                    block("Нормальное состояние", systemArticle?.array("normalState")?.strings().orEmpty()),
                    block("Признаки отклонения", systemArticle?.array("deviationSigns")?.strings().orEmpty()),
                    block("Ключевые параметры", systemArticle?.array("keyParameters")?.stringsOrSummaries().orEmpty()),
                    block("Оборудование системы", equipment.mapNotNull { record ->
                        record.optString("name").takeIf(String::isNotBlank)
                    }),
                    block("Связанные системы", relatedSystems),
                    block("Эксплуатационные особенности", systemArticle?.array("variantRules")?.strings().orEmpty()),
                    block("Справочные материалы", supportingArticles.mapNotNull { article ->
                        article.optString("title").takeIf(String::isNotBlank)
                    }),
                    block("Требует уточнения по исполнению", systemArticle?.array("openQuestions")?.strings().orEmpty())
                ),
                relatedIds = buildList {
                    addAll(equipment.mapNotNull { it.optString("id").takeIf(String::isNotBlank) })
                    systemArticle?.optString("id")?.takeIf(String::isNotBlank)?.let(::add)
                    addAll(supportingArticles.mapNotNull { it.optString("id").takeIf(String::isNotBlank) })
                    addAll(relatedSystems)
                    addAll(item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) })
                }.distinct()
            )
        }
    }'''

    equipment = r'''    private fun loadErmakEquipment(): List<TechnicalEntry> {
        val records = json("technical/ermak_equipment.json").array("records").objects()
        val equipmentById = records.associateBy { it.optString("id") }
        val knowledgeByEquipment = json("technical/ermak_knowledge.json").array("articles").objects()
            .mapNotNull { article ->
                article.optString("equipmentId").takeIf(String::isNotBlank)?.let { it to article }
            }.toMap()

        return records.map { item ->
            val equipmentId = item.optString("id")
            val knowledge = knowledgeByEquipment[equipmentId]
            val relationIds = item.array("relations").objects()
                .mapNotNull { relation -> relation.optString("targetId").takeIf(String::isNotBlank) }
                .distinct()
            val relatedEquipmentNames = relationIds.mapNotNull { targetId ->
                equipmentById[targetId]?.optString("name")?.takeIf(String::isNotBlank)
            }.distinct()

            entry(
                item, TechnicalFamily.ERMAK, TechnicalSection.EQUIPMENT,
                title = item.optString("name"),
                subtitle = item.optString("purpose"),
                status = item.optString("evidenceStatus"),
                blocks = listOfNotEmpty(
                    block("Назначение", item.optString("purpose")),
                    block("Как работает", knowledge?.optString("principle").orEmpty()),
                    block("Расположение", item.obj("location").summary()),
                    block("Количество", item.optString("quantity")),
                    block("Обозначения", item.array("schemeDesignations").strings() + item.array("modelNames").strings()),
                    block("Параметры", item.array("parameters").stringsOrSummaries()),
                    block("Нормальное состояние", knowledge?.array("normalState")?.strings().orEmpty()),
                    block("Признаки отклонения", knowledge?.array("deviationSigns")?.strings().orEmpty()),
                    block("Связанное оборудование", relatedEquipmentNames),
                    block("Применимость", item.obj("applicability").summary()),
                    block("Системы", item.array("systemIds").strings()),
                    block("Примечания", item.array("notes").stringsOrSummaries()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
                ),
                relatedIds = buildList {
                    addAll(relationIds)
                    addAll(item.array("systemIds").strings())
                    knowledge?.optString("id")?.takeIf(String::isNotBlank)?.let(::add)
                }.distinct()
            )
        }
    }'''

    text = replace_function(
        text,
        "    private fun loadErmakSystems(): List<TechnicalEntry> {",
        "    private fun loadErmakEquipment()",
        systems,
        f"Ermak systems in {path}",
    )
    text = replace_function(
        text,
        "    private fun loadErmakEquipment(): List<TechnicalEntry> =",
        "    private fun loadErmakKnowledge()",
        equipment,
        f"Ermak equipment in {path}",
    )
    path.write_text(text, encoding="utf-8")


def patch_identity(root: Path) -> None:
    path = root / "build.gradle.kts"
    text = path.read_text(encoding="utf-8")
    assert text.count("        versionCode = 153") == 1, f"versionCode baseline missing in {path}"
    assert text.count('        versionName = "1.2.2-dev14-beta8"') == 1, f"versionName baseline missing in {path}"
    text = text.replace("        versionCode = 153", "        versionCode = 154", 1)
    text = text.replace('        versionName = "1.2.2-dev14-beta8"', '        versionName = "1.2.2-dev14-beta9"', 1)
    path.write_text(text, encoding="utf-8")


for root in ROOTS:
    patch_repository(root)
    patch_identity(root)

for rel in (
    "build.gradle.kts",
    "src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt",
):
    a = Path("app") / rel
    b = Path("patch/app") / rel
    assert a.read_bytes() == b.read_bytes(), f"mirror mismatch: {rel}"

repo = Path("app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt").read_text(encoding="utf-8")
assert 'block("Как работает", systemArticle?.optString("principle").orEmpty())' in repo
assert 'block("Нормальное состояние", knowledge?.array("normalState")?.strings().orEmpty())' in repo
assert 'block("Связанное оборудование", relatedEquipmentNames)' in repo
assert 'block("Связи с оборудованием", item.array("relations").stringsOrSummaries())' not in repo
assert 'subtitle = "Оборудование: ${equipment.size} • Материалы: ${articles.size}"' not in repo

print("Beta9 Ermak reference deepening patched and mirrors verified")
