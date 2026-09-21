from pathlib import Path

ROOTS = [Path('app'), Path('patch/app')]

HOME_OLD = '''        Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
            Text("ВЛ80С • Ермак", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Black)
            Text("Два технических профиля локомотивной бригады", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }

'''
HOME_OLD_SUBTITLE = 'subtitle = "ВЛ80С и Ермак: поиск неисправности по наблюдаемым признакам, ветвящиеся уточнения и безопасные проверки.",'
HOME_NEW_SUBTITLE = 'subtitle = "ВЛ80С и Ермак: поиск неисправности по наблюдаемым признакам и безопасные проверки.",'

LINK_ANCHOR = '''    private fun ermakKnowledgeLinks(article: JSONObject): JSONObject {
        val equipmentId = article.optString("equipmentId")
        if (equipmentId.isNotBlank()) return ermakEquipmentLinks(equipmentId)
        val articleId = article.optString("id")
        if (articleId.startsWith("ER-KB-SYS-")) {
            return ermakSystemLinks(articleId.removePrefix("ER-KB-"))
        }
        return JSONObject()
    }

'''
LINK_INSERT = LINK_ANCHOR + '''    // VL80S assets already contain canonical equipment IDs in scheme nodes. Build the
    // reverse index at runtime so equipment cards can navigate back to the current
    // electrical/pneumatic schemes instead of exposing legacy schemeNodeIds tokens.
    private val vl80sSchemeIdsByEquipment by lazy {
        val result = linkedMapOf<String, MutableList<String>>()
        val schemes = buildList {
            addAll(json("technical/vl80s_electrical.json").array("baseSchemes").objects())
            addAll(json("technical/vl80s_pneumatic.json").array("views").objects())
        }
        schemes.forEach { scheme ->
            val schemeId = scheme.optString("id")
            if (schemeId.isBlank()) return@forEach
            val equipmentIds = buildList {
                addAll(scheme.array("equipmentIds").strings())
                addAll(scheme.array("nodes").objects().mapNotNull { node ->
                    node.optString("equipmentId").takeIf(String::isNotBlank)
                })
            }.distinct()
            equipmentIds.forEach { equipmentId ->
                result.getOrPut(equipmentId) { mutableListOf() }.add(schemeId)
            }
        }
        result.mapValues { (_, ids) -> ids.distinct() }
    }

'''

EQUIP_OLD = '''    private fun loadVl80sEquipment(): List<TechnicalEntry> =
        json("technical/vl80s_equipment.json").array("records").objects().map { item ->
            val related = buildList {
                addAll(item.array("diagnosticScenarioIds").strings())
                addAll(item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) })
            }.distinct()
            entry(
'''
EQUIP_NEW = '''    private fun loadVl80sEquipment(): List<TechnicalEntry> =
        json("technical/vl80s_equipment.json").array("records").objects().map { item ->
            val equipmentId = item.optString("id")
            val canonicalSchemeIds = vl80sSchemeIdsByEquipment[equipmentId].orEmpty()
            val related = buildList {
                addAll(item.array("diagnosticScenarioIds").strings())
                addAll(item.array("relations").objects().mapNotNull { it.optString("targetId").takeIf(String::isNotBlank) })
                addAll(canonicalSchemeIds)
            }.distinct()
            entry(
'''

ALIASES_OLD = '                    block("Обозначения", item.array("aliases").strings() + item.array("schemeNodeIds").strings()),\n'
ALIASES_NEW = '                    block("Обозначения", item.array("aliases").strings()),\n'
SYSTEMS_LINE = '                    block("Системы", item.array("systemIds").strings()),\n'
SYSTEMS_WITH_SCHEMES = SYSTEMS_LINE + '                    block("Схемы", canonicalSchemeIds),\n'

for root in ROOTS:
    home = root / 'src/main/java/ru/railbrake/calculator/ui/HomeScreen.kt'
    text = home.read_text(encoding='utf-8')
    assert text.count(HOME_OLD) == 1, home
    assert text.count(HOME_OLD_SUBTITLE) == 1, home
    text = text.replace(HOME_OLD, '', 1).replace(HOME_OLD_SUBTITLE, HOME_NEW_SUBTITLE, 1)
    home.write_text(text, encoding='utf-8')

    repo = root / 'src/main/java/ru/railbrake/calculator/core/TechnicalDataRepository.kt'
    text = repo.read_text(encoding='utf-8')
    assert text.count(LINK_ANCHOR) == 1, repo
    assert 'private val vl80sSchemeIdsByEquipment by lazy' not in text, repo
    assert text.count(EQUIP_OLD) == 1, repo
    assert text.count(ALIASES_OLD) == 1, repo
    assert text.count(SYSTEMS_LINE) >= 1, repo
    text = text.replace(LINK_ANCHOR, LINK_INSERT, 1)
    text = text.replace(EQUIP_OLD, EQUIP_NEW, 1)
    text = text.replace(ALIASES_OLD, ALIASES_NEW, 1)
    # Only the first Systems block after loadVl80sEquipment is targeted by anchoring on the nearby alias line.
    marker = ALIASES_NEW + SYSTEMS_LINE
    assert text.count(marker) >= 1, repo
    text = text.replace(marker, ALIASES_NEW + SYSTEMS_WITH_SCHEMES, 1)
    repo.write_text(text, encoding='utf-8')

print('VL80S audit fixes applied to app/patch mirrors')
