package ru.railbrake.calculator.safety

import android.content.res.AssetManager
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.LinkScope
import ru.railbrake.calculator.domain.ProvenanceClass
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.domain.expectedTargetType
import java.util.Locale
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.runtime.ContentPackJsonLoader
import ru.railbrake.calculator.runtime.ContentRegistry

/**
 * A READ-ONLY view of donor reference material. A CANDIDATE can be read as
 * clearly labelled evidence; it is never resolved as a published action.
 * Blocks (including donor "Действия" procedures) and links are deliberately
 * not exposed by this projection. This is NOT a new publication gate.
 */
data class CommonReferenceSourceEvidence(
    val id: String,
    val title: String,
    val sourceStatus: SourceStatus,
    val provenance: ProvenanceClass,
)

data class CommonReferenceRelatedCard(val id: String, val title: String)

/**
 * Independently reviewed, narrowly scoped first-aid content. Never populated
 * from the donor's unreviewed blocks. This is information for immediate aid,
 * not a promotion of donor source status or an occupational authorization.
 */
data class CommonReferenceReviewedAid(
    val steps: List<String>,
    val sourceTitle: String,
    val sourceUrl: String,
    val scopeNote: String,
)

/**
 * A link to an independently located government resource, NOT evidence that
 * the donor summary or its hidden procedures match the current regulation.
 * The URL is chosen by code, never taken from unreviewed donor content.
 */
data class CommonReferenceOfficialResource(
    val title: String,
    val url: String,
    val limitation: String,
)

data class CommonReferenceCard(
    val title: String,
    val summary: String,
    val details: List<String>,
    val sources: List<String>,
    val id: String,
    val sourceEvidence: List<CommonReferenceSourceEvidence> = emptyList(),
    val relatedCards: List<CommonReferenceRelatedCard> = emptyList(),
    val officialResources: List<CommonReferenceOfficialResource> = emptyList(),
    val reviewedAid: CommonReferenceReviewedAid? = null,
    val searchTerms: Set<String> = emptySet(),
)

object CommonReferencePolicy {
    private val commonDestinations = setOf(
        ShellHomeDestination.KNOWLEDGE,
        ShellHomeDestination.TRAFFIC_SAFETY,
        ShellHomeDestination.OCCUPATIONAL_SAFETY,
        ShellHomeDestination.FIRST_AID,
    )

    /**
     * Source titles and same-section references are navigable evidence, not
     * permission to execute the original donor's procedures.
     */
    fun cards(entries: List<ContentEntry>, destination: ShellHomeDestination): List<CommonReferenceCard> {
        if (destination !in commonDestinations) return emptyList()
        val sourceEntries = entries.filter {
            it.type == ContentType.SOURCE && it.owner == ContentOwner.Common &&
                it.layer == ContentLayer.STANDARD
        }.associateBy { it.id.value }
        val eligible = entries.filter { entry ->
            entry.owner == ContentOwner.Common &&
                entry.publicationStatus == PublicationStatus.CANDIDATE &&
                entry.layer == ContentLayer.STANDARD &&
                entry.actionDisposition == ActionDisposition.INFORMATION_ONLY &&
                entry.applicability.modelIds.isEmpty() &&
                entry.applicability.variantIds.isEmpty() &&
                entry.summary?.isNotBlank() == true &&
                entry.sourceRefs.isNotEmpty() &&
                entry.sourceRefs.all { it in sourceEntries } &&
                belongsToSection(entry, destination)
        }
        val byId = eligible.associateBy { it.id.value }
        return eligible.map { entry ->
            val evidence = entry.sourceRefs.mapNotNull(sourceEntries::get)
                .distinctBy { it.id.value }.sortedBy { it.title }
                .map { source ->
                    CommonReferenceSourceEvidence(
                        id = source.id.value,
                        title = source.title,
                        sourceStatus = source.sourceStatus,
                        provenance = source.provenance,
                    )
                }
            val related = entry.links.asSequence()
                .filter { it.scope == LinkScope.COMMON_INTERNAL }
                .filter {
                    it.applicability.modelIds.isEmpty() && it.applicability.variantIds.isEmpty()
                }
                .mapNotNull { link ->
                    byId[link.targetId.value]?.takeIf {
                        it.type == link.type.expectedTargetType() && it.id != entry.id
                    }
                }
                .distinctBy { it.id.value }
                .map { CommonReferenceRelatedCard(it.id.value, it.title) }
                .toList()
            CommonReferenceCard(
                id = entry.id.value,
                title = entry.title,
                summary = requireNotNull(entry.summary),
                // Unverified first-aid steps stay in the donor pack for later
                // source review; never project them into the reader.
                details = if (entry.type == ContentType.FIRST_AID) emptyList()
                    else entry.details.filter { it.isNotBlank() },
                sources = evidence.map { it.title },
                sourceEvidence = evidence,
                relatedCards = related,
                officialResources = officialFirstAidResources(entry, evidence),
                reviewedAid = reviewedFirstAid(entry, evidence),
                searchTerms = entry.searchTerms,
            )
        }
    }

    private val firstAidOrder = CommonReferenceOfficialResource(
        title = "Приказ Минздрава России №220н от 03.05.2024 (МЧС России)",
        url = "https://55.mchs.gov.ru/deyatelnost/napravleniya-deyatelnosti/dobrovolnaya-pozharnaya-ohrana/normativnye-akty-i-inye-dokumenty-dobrovolchestva-volonterstva-v-oblasti-zashchity-ot-chrezvychaynyh-situaciy-prirodnogo-i-tehnogennogo-haraktera-grazhdanskoy-oborony-pozharnoy-bezopasnosti-i-bezopasnosti-lyudey-na-vodnyh-obektah/prikaz-ministerstva-zdravoohraneniya-rossiyskoy-federacii-ot-3-maya-2024-g-220n-ob-utverzhdenii-poryadka-okazaniya-pervoy-pomoshchi",
        limitation = "Официальный текст для сверки; соответствие донорских действий не установлено.",
    )
    private val firstAidAlgorithms = CommonReferenceOfficialResource(
        title = "Алгоритмы первой помощи, Минздрав России (2024)",
        url = "https://minzdrav.gov.ru/special/documents/9801-algoritmy-okazaniya-pervoy-pomoschi",
        limitation = "Материал ведомства для сверки; не разрешает скрытые процедуры из Test-.",
    )
    private val workerKitSource = CommonReferenceOfficialResource(
        title = "Аптечки первой помощи, МЧС России (ссылка на приказ №262н)",
        url = "https://mchs.gov.ru/deyatelnost/bezopasnost-grazhdan/aptechki-pervoy-pomoshchi",
        limitation = "Ведомственное разъяснение; состав аптечки из донора не сверен по позициям.",
    )

    private fun officialFirstAidResources(
        entry: ContentEntry,
        evidence: List<CommonReferenceSourceEvidence>,
    ): List<CommonReferenceOfficialResource> {
        if (entry.type != ContentType.FIRST_AID) return emptyList()
        val sourceIds = evidence.map { it.id }.toSet()
        return when {
            entry.id.value == "common.first-aid.worker-kit" &&
                "common.source.worker-kit-262n-donor" in sourceIds -> listOf(workerKitSource)
            entry.id.value.startsWith("common.first-aid.") &&
                "common.source.first-aid-donor" in sourceIds ->
                listOf(firstAidOrder, firstAidAlgorithms)
            else -> emptyList()
        }
    }

    /**
     * Checked against Order 220n (03.05.2024), annex 2 §§1–4,9 and the
     * Ministry of Health first-aid posters published on its page updated
     * 05.03.2026. Only explicitly listed adult cases have a reviewed UI procedure.
     * No donor procedural block is copied or exposed by this function.
     */
    private fun reviewedFirstAid(
        entry: ContentEntry,
        evidence: List<CommonReferenceSourceEvidence>,
    ): CommonReferenceReviewedAid? {
        if (entry.type != ContentType.FIRST_AID ||
            evidence.none { it.id == "common.source.first-aid-donor" }) return null
        val steps = when (entry.id.value) {
            "common.first-aid.unconscious" -> listOf(
                "Убедитесь в безопасности места. Не подвергайте себя опасности.",
                "Проверьте, нет ли продолжающегося наружного кровотечения; при наличии остановите его.",
                "Проверьте сознание. При отсутствии реакции откройте дыхательные пути запрокидыванием головы с подъёмом подбородка и проверьте дыхание не более 10 секунд.",
                "Если дыхание нормальное, придайте устойчивое боковое положение. Если это невозможно из-за травмы или иных причин, удерживайте голову запрокинутой с поднятым подбородком.",
                "Вызовите 103 или 112 и постоянно контролируйте дыхание до прибытия помощи.",
                "Если нормального дыхания нет, немедленно переходите к сердечно-лёгочной реанимации.",
            )
            "common.first-aid.cpr" -> listOf(
                "Убедитесь в безопасности. Проверьте сознание и нормальное дыхание; редкие судорожные вдохи не считайте нормальным дыханием.",
                "Если пострадавший без сознания и не дышит нормально, вызовите 103 или 112 либо поручите вызов помощнику. Попросите принести автоматический наружный дефибриллятор (АНД).",
                "Уложите взрослого пострадавшего на твёрдую ровную поверхность. Надавливайте на центр грудной клетки с частотой 100–120 в минуту и глубиной 5–6 см.",
                "Если обучены и можете безопасно делать искусственное дыхание, чередуйте 30 надавливаний с 2 вдохами. Иначе выполняйте непрерывные надавливания.",
                "При наличии АНД включите его и следуйте голосовым указаниям, сводя перерывы в надавливаниях к минимуму.",
                "Продолжайте до появления явных признаков жизни, передачи бригаде скорой помощи, невозможности продолжать или возникновения опасности.",
            )
            "common.first-aid.bleeding" -> listOf(
                "Убедитесь в безопасности. Используйте перчатки, если они под рукой; не откладывайте помощь при угрожающей жизни кровопотере.",
                "При сильном кровотечении немедленно поручите вызов 103 или 112. Прижмите рану салфеткой или чистой тканью и удерживайте давление.",
                "Если в ране застрял предмет или выступает костный отломок, не давите на него и не извлекайте его. Давите вокруг раны и зафиксируйте предмет повязкой.",
                "После остановки крови прямым давлением закрепите давящую повязку. При угрожающем жизни кровотечении из конечности, которое не удаётся остановить, либо при её обширном повреждении или отрыве примените кровоостанавливающий жгут.",
                "Жгут размещайте на конечности выше раны примерно на 5–7 см, не на суставе. Затяните до прекращения кровотечения, запишите время, оставьте жгут видимым и не ослабляйте самостоятельно.",
                "Оставайтесь рядом, контролируйте сознание и дыхание, защищайте от охлаждения. При подозрении на внутреннее кровотечение срочно вызовите помощь; наружное давление не устраняет внутреннюю кровопотерю.",
            )
            "common.first-aid.airway" -> listOf(
                "Если взрослый способен эффективно кашлять, предложите ему продолжать кашель и наблюдайте. Не наносите удары, пока кашель эффективен.",
                "Если человек не может говорить, эффективно кашлять или дышать, поручите вызов 103 или 112. Поддерживая пострадавшего, наклоните его вперёд и нанесите до пяти ударов основанием ладони между лопатками, проверяя эффект после каждого.",
                "Если это не помогло, встаньте сзади, поместите кулак выше пупка и ниже грудины, обхватите его другой рукой и выполните до пяти резких толчков внутрь и вверх.",
                "Чередуйте до пяти ударов по спине и до пяти толчков, прекращая их при восстановлении проходимости. При беременности или невозможности обхватить живот вместо толчков в живот выполняйте толчки в нижнюю часть грудной клетки.",
                "Если человек потерял сознание, осторожно опустите его на пол, убедитесь, что помощь вызвана, и начните СЛР с надавливаний на грудную клетку.",
                "При открытии дыхательных путей удаляйте только хорошо видимый предмет. Не обследуйте рот пальцами вслепую. После успешного устранения тяжёлой непроходимости необходима медицинская оценка, особенно после толчков.",
            )
            else -> return null
        }
        return CommonReferenceReviewedAid(
            steps = steps,
            sourceTitle = "Минздрав России: приказ №220н, приложение №2, пункты 1–4, 9; материалы первой помощи (страница обновлена 05.03.2026)" + when (entry.id.value) {
                "common.first-aid.bleeding" -> "; дополнительно: American Red Cross, Bleeding / Tourniquet"
                "common.first-aid.airway" -> "; дополнительно: МЧС России, «Человек подавился. Что делать?»"
                else -> ""
            },
            sourceUrl = "https://minzdrav.gov.ru/special/pervaya-pomosch",
            scopeNote = "Сверены только указанные действия для взрослого. Донорские процедуры, особенности помощи детям и иные состояния не подтверждены этой карточкой.",
        )
    }

    /** Search only visible title, summary and donor keywords; never hidden procedures. */
    fun search(cards: List<CommonReferenceCard>, query: String): List<CommonReferenceCard> {
        val tokens = query.trim().lowercase(Locale.ROOT).split(Regex("\\s+"))
            .filter { it.isNotBlank() }
        if (tokens.isEmpty()) return cards
        return cards.filter { card ->
            val visible = (listOf(card.title, card.summary) + card.searchTerms)
                .joinToString(" ").lowercase(Locale.ROOT)
            tokens.all { it in visible }
        }
    }

    private fun belongsToSection(entry: ContentEntry, destination: ShellHomeDestination): Boolean {
        val traffic = entry.id.value.startsWith("common.knowledge.signals-") ||
            entry.id.value.startsWith("common.knowledge.movement-")
        return when (destination) {
            ShellHomeDestination.FIRST_AID -> entry.type == ContentType.FIRST_AID
            ShellHomeDestination.OCCUPATIONAL_SAFETY -> entry.type == ContentType.SAFETY
            ShellHomeDestination.TRAFFIC_SAFETY -> entry.type == ContentType.KNOWLEDGE && traffic
            ShellHomeDestination.KNOWLEDGE -> entry.type == ContentType.KNOWLEDGE && !traffic
            else -> false
        }
    }
}

/** Read only the three pinned common packs; no candidate is installed into published runtime. */
class CommonReferenceCatalog(private val assets: AssetManager) {
    private val packs = listOf(
        "common/first-aid/topics.pack.json" to "common.first-aid.topics-001",
        "common/knowledge/articles.pack.json" to "common.knowledge.articles-001",
        "common/safety/articles.pack.json" to "common.safety.articles-001",
    )

    fun load(): List<ContentEntry> {
        val registry = ContentRegistry()
        val parser = ContentPackJsonLoader()
        packs.forEach { (path, expectedId) ->
            val json = assets.open(path).bufferedReader().use { it.readText() }
            val pack = parser.parse(json)
            require(pack.manifest.packId.value == expectedId)
            require(pack.manifest.family == null &&
                pack.manifest.modelIds.isEmpty() && pack.manifest.variantIds.isEmpty())
            require(pack.manifest.entries == pack.entries.map { it.id }.toSet())
            require(pack.entries.all {
                it.owner == ContentOwner.Common && it.publicationStatus == PublicationStatus.CANDIDATE
            })
            require(registry.install(pack).isEmpty()) { "Invalid common reference pack: $expectedId" }
        }
        require(registry.validateGlobalLinks().isEmpty()) { "Broken common reference links" }
        return registry.allEntries()
    }
}
