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

data class CommonReferenceCard(
    val title: String,
    val summary: String,
    val details: List<String>,
    val sources: List<String>,
    val id: String,
    val sourceEvidence: List<CommonReferenceSourceEvidence> = emptyList(),
    val relatedCards: List<CommonReferenceRelatedCard> = emptyList(),
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
                searchTerms = entry.searchTerms,
            )
        }
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
