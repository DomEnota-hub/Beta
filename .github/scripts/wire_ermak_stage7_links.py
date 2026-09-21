#!/usr/bin/env python3
from pathlib import Path

PATHS = [
    Path('app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'),
    Path('patch/app/src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'),
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, got {count}')
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    text = replace_once(
        text,
        '''    private val legacyEquipmentIds by lazy {
        json("technical/vl80s_equipment.json").array("records").objects()
            .mapNotNull { item ->
                item.optString("legacyId").takeIf(String::isNotBlank)?.let { legacy ->
                    "vl80-eq-$legacy" to item.optString("id")
                }
            }.toMap()
    }

''',
        '''    private val legacyEquipmentIds by lazy {
        json("technical/vl80s_equipment.json").array("records").objects()
            .mapNotNull { item ->
                item.optString("legacyId").takeIf(String::isNotBlank)?.let { legacy ->
                    "vl80-eq-$legacy" to item.optString("id")
                }
            }.toMap()
    }

    // Stage 7 is the canonical Ermak cross-link graph. Equipment/system/article
    // cards consume these indexes directly instead of duplicating link lists.
    private val ermakLinkIndexes by lazy {
        json("technical/ermak_links.json").obj("indexes")
    }

    private fun ermakEquipmentLinks(equipmentId: String): JSONObject =
        ermakLinkIndexes.obj("byEquipment").obj(equipmentId)

    private fun ermakSystemLinks(systemId: String): JSONObject =
        ermakLinkIndexes.obj("bySystem").obj(systemId)

    private fun ermakKnowledgeLinks(article: JSONObject): JSONObject {
        val equipmentId = article.optString("equipmentId")
        if (equipmentId.isNotBlank()) return ermakEquipmentLinks(equipmentId)
        val articleId = article.optString("id")
        if (articleId.startsWith("ER-KB-SYS-")) {
            return ermakSystemLinks(articleId.removePrefix("ER-KB-"))
        }
        return JSONObject()
    }

''',
        'insert Stage 7 helpers'
    )

    text = replace_once(
        text,
        '''            val relatedSystems = systemArticle?.array("relatedSystems")?.strings().orEmpty()

            entry(
''',
        '''            val relatedSystems = systemArticle?.array("relatedSystems")?.strings().orEmpty()
            val canonicalLinks = ermakSystemLinks(systemId)

            entry(
''',
        'system canonical links'
    )

    text = replace_once(
        text,
        '''                    block("Справочные материалы", supportingArticles.mapNotNull { article ->
                        article.optString("title").takeIf(String::isNotBlank)
                    }),
                    block("Требует уточнения по исполнению", systemArticle?.array("openQuestions")?.strings().orEmpty())
''',
        '''                    block("Справочные материалы", supportingArticles.mapNotNull { article ->
                        article.optString("title").takeIf(String::isNotBlank)
                    }),
                    block("Диагностика", canonicalLinks.array("diagnosticIds").strings()),
                    block("Схемы", canonicalLinks.array("schemeIds").strings()),
                    block("Требует уточнения по исполнению", systemArticle?.array("openQuestions")?.strings().orEmpty())
''',
        'system blocks'
    )

    text = replace_once(
        text,
        '''                    addAll(relatedSystems)
                    addAll(item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) })
''',
        '''                    addAll(relatedSystems)
                    addAll(canonicalLinks.array("diagnosticIds").strings())
                    addAll(canonicalLinks.array("schemeIds").strings())
                    addAll(item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) })
''',
        'system related ids'
    )

    text = replace_once(
        text,
        '''            val equipmentId = item.optString("id")
            val knowledge = knowledgeByEquipment[equipmentId]
            val relationIds = item.array("relations").objects()
''',
        '''            val equipmentId = item.optString("id")
            val knowledge = knowledgeByEquipment[equipmentId]
            val canonicalLinks = ermakEquipmentLinks(equipmentId)
            val relationIds = item.array("relations").objects()
''',
        'equipment canonical links'
    )

    text = replace_once(
        text,
        '''                    block("Применимость", item.obj("applicability").summary()),
                    block("Системы", item.array("systemIds").strings()),
                    block("Примечания", item.array("notes").stringsOrSummaries()),
''',
        '''                    block("Применимость", item.obj("applicability").summary()),
                    block("Системы", item.array("systemIds").strings()),
                    block("Статья", listOfNotNull(canonicalLinks.optString("equipmentArticleId").takeIf(String::isNotBlank))),
                    block("Диагностика", canonicalLinks.array("diagnosticIds").strings()),
                    block("Схемы", canonicalLinks.array("schemeIds").strings()),
                    block("Примечания", item.array("notes").stringsOrSummaries()),
''',
        'equipment blocks'
    )

    text = replace_once(
        text,
        '''                    addAll(item.array("systemIds").strings())
                    knowledge?.optString("id")?.takeIf(String::isNotBlank)?.let(::add)
''',
        '''                    addAll(item.array("systemIds").strings())
                    canonicalLinks.optString("equipmentArticleId").takeIf(String::isNotBlank)?.let(::add)
                    addAll(canonicalLinks.array("diagnosticIds").strings())
                    addAll(canonicalLinks.array("schemeIds").strings())
                    knowledge?.optString("id")?.takeIf(String::isNotBlank)?.let(::add)
''',
        'equipment related ids'
    )

    text = replace_once(
        text,
        '''    private fun loadErmakKnowledge(): List<TechnicalEntry> =
        json("technical/ermak_knowledge.json").array("articles").objects().map { item ->
            entry(
''',
        '''    private fun loadErmakKnowledge(): List<TechnicalEntry> =
        json("technical/ermak_knowledge.json").array("articles").objects().map { item ->
            val canonicalLinks = ermakKnowledgeLinks(item)
            entry(
''',
        'knowledge canonical links'
    )

    text = replace_once(
        text,
        '''                    block("Применимость", item.obj("scope").summary()),
                    block("Особенности исполнения", item.array("variantRules").strings()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
''',
        '''                    block("Применимость", item.obj("scope").summary()),
                    block("Особенности исполнения", item.array("variantRules").strings()),
                    block("Диагностика", canonicalLinks.array("diagnosticIds").strings()),
                    block("Схемы", canonicalLinks.array("schemeIds").strings()),
                    block("Источники", item.array("sourceRefs").stringsOrSummaries())
''',
        'knowledge blocks'
    )

    text = replace_once(
        text,
        '''                    addAll(item.array("relatedSystems").strings())
                    addAll(item.obj("futureLinks").allStrings())
''',
        '''                    addAll(item.array("relatedSystems").strings())
                    addAll(canonicalLinks.array("diagnosticIds").strings())
                    addAll(canonicalLinks.array("schemeIds").strings())
                    addAll(item.obj("futureLinks").allStrings())
''',
        'knowledge related ids'
    )

    return text


originals = [p.read_text(encoding='utf-8') for p in PATHS]
if originals[0] != originals[1]:
    raise SystemExit('app/patch TechnicalDataRepository.kt were not identical before patch')
patched = patch(originals[0])
for path in PATHS:
    path.write_text(patched, encoding='utf-8')

print('Wired canonical Ermak Stage 7 links into systems, equipment and knowledge cards')
