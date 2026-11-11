package ru.railbrake.calculator.safety

import java.nio.file.Files
import java.nio.file.Path
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ContentLink
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.LinkScope
import ru.railbrake.calculator.domain.LinkType
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.runtime.ContentPackJsonLoader

class CommonReferencePolicyTest {
    private fun donorEntries() = listOf(
        "first-aid/topics.pack.json",
        "knowledge/articles.pack.json",
        "safety/articles.pack.json",
    ).flatMap { path ->
        val json = Files.readAllBytes(Path.of("..", "content-packs", "common", path)).toString(Charsets.UTF_8)
        ContentPackJsonLoader().parse(json).entries
    }

    @Test fun fourCommonSectionsShowAllSixtySixReferenceSummaries() {
        val entries = donorEntries()
        assertEquals(87, entries.size)
        val knowledge = CommonReferencePolicy.cards(entries, ShellHomeDestination.KNOWLEDGE)
        val traffic = CommonReferencePolicy.cards(entries, ShellHomeDestination.TRAFFIC_SAFETY)
        val occupational = CommonReferencePolicy.cards(entries, ShellHomeDestination.OCCUPATIONAL_SAFETY)
        val firstAid = CommonReferencePolicy.cards(entries, ShellHomeDestination.FIRST_AID)
        assertEquals(13, knowledge.size)
        assertEquals(13, traffic.size)
        assertEquals(22, occupational.size)
        assertEquals(18, firstAid.size)
        val all = knowledge + traffic + occupational + firstAid
        assertEquals(66, all.map { it.id }.distinct().size)
        assertTrue(all.all { it.title.isNotBlank() && it.summary.isNotBlank() && it.sources.isNotEmpty() })
        assertTrue(CommonReferencePolicy.cards(entries, ShellHomeDestination.ATLAS).isEmpty())
    }

    @Test fun firstAidNeverProjectsUnverifiedProceduralBlocks() {
        val entries = donorEntries()
        assertTrue(entries.any { it.type == ContentType.FIRST_AID && it.blocks.isNotEmpty() })
        val cards = CommonReferencePolicy.cards(entries, ShellHomeDestination.FIRST_AID)
        assertEquals(18, cards.size)
        assertTrue(cards.all { it.details.isEmpty() })
        assertFalse(cards.any { it.title.contains("SOURCE") })
    }

    @Test fun referenceGateRejectsActionPromotionCrossModelAndUnprovenSources() {
        val entries = donorEntries()
        val article = entries.first { it.id.value == "common.knowledge.brakes-automatic-principle" }
        val sources = entries.filter { it.type == ContentType.SOURCE }
        val section = ShellHomeDestination.KNOWLEDGE
        assertEquals(1, CommonReferencePolicy.cards(sources + article, section).size)
        val unsafe = listOf(
            article.copy(publicationStatus = PublicationStatus.ACTIVE),
            article.copy(actionDisposition = ActionDisposition.CONDITIONAL_ACTION),
            article.copy(actionDisposition = ActionDisposition.PROHIBITED),
            article.copy(owner = ContentOwner.Model(ModelId("vl80s"))),
            article.copy(layer = ContentLayer.EXTENDED),
            article.copy(sourceRefs = emptySet()),
        )
        unsafe.forEach { candidate ->
            assertTrue(CommonReferencePolicy.cards(sources + candidate, section).isEmpty())
        }
        assertTrue(CommonReferencePolicy.cards(listOf(article), section).isEmpty())
    }

    @Test fun commonSearchUsesDonorSynonymsButNeverHiddenFirstAidSteps() {
        val entries = donorEntries()
        val aid = CommonReferencePolicy.cards(entries, ShellHomeDestination.FIRST_AID)
        assertEquals(listOf("common.first-aid.cpr"),
            CommonReferencePolicy.search(aid, "слр").map { it.id })
        assertTrue(CommonReferencePolicy.search(aid, "Жгут должен оставаться видимым").isEmpty())
        assertEquals(aid, CommonReferencePolicy.search(aid, "  "))
        val knowledge = CommonReferencePolicy.cards(entries, ShellHomeDestination.KNOWLEDGE)
        assertTrue(CommonReferencePolicy.search(knowledge, "автотормоза").isNotEmpty())
        assertTrue(CommonReferencePolicy.search(knowledge, "несуществующее слово").isEmpty())
    }

    @Test fun internalLinksAreLimitedToSameSectionAndEligibleTargets() {
        val entries = donorEntries()
        val occupational = CommonReferencePolicy.cards(entries, ShellHomeDestination.OCCUPATIONAL_SAFETY)
        val ppe = occupational.first { it.id == "common.safety.safety-ppe-types" }
        assertEquals(
            setOf("common.safety.safety-ppe-before-use", "common.safety.safety-electrical-protection"),
            ppe.relatedCards.map { it.id }.toSet(),
        )
        val article = entries.first { it.id.value == "common.knowledge.brakes-automatic-principle" }
        val valid = entries.first { it.id.value == "common.knowledge.brakes-pressure-units" }
        val otherSection = entries.first { it.id.value == "common.knowledge.signals-reading-principle" }
        val links = listOf(
            ContentLink(LinkType.KNOWLEDGE, valid.id, scope = LinkScope.COMMON_INTERNAL),
            ContentLink(LinkType.KNOWLEDGE, otherSection.id, scope = LinkScope.COMMON_INTERNAL),
            ContentLink(LinkType.KNOWLEDGE, CanonicalId("missing.id"), scope = LinkScope.COMMON_INTERNAL),
            ContentLink(LinkType.KNOWLEDGE, valid.id, scope = LinkScope.SAME_MODEL),
        )
        val sourceEntries = entries.filter { it.type == ContentType.SOURCE }
        val cards = CommonReferencePolicy.cards(
            sourceEntries + article.copy(links = links) + valid + otherSection,
            ShellHomeDestination.KNOWLEDGE,
        )
        assertEquals(listOf(valid.id.value),
            cards.first { it.id == article.id.value }.relatedCards.map { it.id })
        assertTrue(cards.none { it.id == otherSection.id.value })
    }

    @Test fun firstAidOfficialReferencesStaySourceBoundAndNeverAuthorizeActions() {
        val entries = donorEntries()
        val cards = CommonReferencePolicy.cards(entries, ShellHomeDestination.FIRST_AID)
        assertEquals(18, cards.size)
        val procedures = cards.filter { it.id != "common.first-aid.worker-kit" }
        assertEquals(17, procedures.size)
        assertTrue(procedures.all { it.officialResources.size == 2 })
        val kit = cards.single { it.id == "common.first-aid.worker-kit" }
        assertEquals(1, kit.officialResources.size)
        assertTrue(kit.officialResources.single().title.contains("262н"))
        assertTrue(procedures.all { it.officialResources.first().title.contains("220н") })
        assertTrue(cards.all { it.details.isEmpty() && it.relatedCards.isEmpty() })
        assertTrue(cards.flatMap { it.officialResources }.all { resource ->
            resource.url.startsWith("https://") &&
                (resource.url.contains(".mchs.gov.ru/") ||
                    resource.url.contains("://mchs.gov.ru/") ||
                    resource.url.contains("://minzdrav.gov.ru/")) &&
                resource.limitation.isNotBlank()
        })
        val cpr = entries.single { it.id.value == "common.first-aid.cpr" }
        val donorSource = entries.single { it.id.value == "common.source.first-aid-donor" }
        val injectedSource = donorSource.copy(details = listOf("https://untrusted.example/unsafe"))
        val card = CommonReferencePolicy.cards(
            listOf(injectedSource, cpr), ShellHomeDestination.FIRST_AID,
        ).single()
        assertEquals(2, card.officialResources.size)
        assertTrue(card.officialResources.none { "untrusted" in it.url })
        assertEquals(SourceStatus.UNKNOWN, card.sourceEvidence.single().sourceStatus)
        assertTrue(CommonReferencePolicy.cards(
            listOf(donorSource, cpr.copy(sourceRefs = emptySet())),
            ShellHomeDestination.FIRST_AID,
        ).isEmpty())
    }

    @Test fun onlyTwoFirstAidCardsExposeIndependentlyReviewedAdultGuidance() {
        val entries = donorEntries()
        val cards = CommonReferencePolicy.cards(entries, ShellHomeDestination.FIRST_AID)
        val reviewed = cards.filter { it.reviewedAid != null }
        assertEquals(
            setOf("common.first-aid.unconscious", "common.first-aid.cpr"),
            reviewed.map { it.id }.toSet(),
        )
        assertTrue(reviewed.all { it.reviewedAid!!.steps.size == 6 })
        assertTrue(reviewed.all {
            it.reviewedAid!!.sourceUrl == "https://minzdrav.gov.ru/special/pervaya-pomosch" &&
                it.reviewedAid!!.sourceTitle.contains("220н") &&
                it.reviewedAid!!.scopeNote.contains("взрослого")
        })
        assertTrue(cards.all { it.details.isEmpty() })
        assertTrue(cards.filter { it.reviewedAid == null }.size == 16)
        assertTrue(reviewed.all { card ->
            card.sourceEvidence.all { it.sourceStatus == SourceStatus.UNKNOWN }
        })
        val cpr = entries.single { it.id.value == "common.first-aid.cpr" }
        val donorSource = entries.single { it.id.value == "common.source.first-aid-donor" }
        assertTrue(CommonReferencePolicy.cards(
            listOf(cpr), ShellHomeDestination.FIRST_AID,
        ).isEmpty())
        assertTrue(CommonReferencePolicy.cards(
            listOf(donorSource, cpr.copy(sourceRefs = emptySet())),
            ShellHomeDestination.FIRST_AID,
        ).isEmpty())
        val nonAid = entries.single { it.id.value == "common.knowledge.brakes-automatic-principle" }
        assertTrue(CommonReferencePolicy.cards(
            listOf(donorSource, nonAid), ShellHomeDestination.FIRST_AID,
        ).isEmpty())
    }

    @Test fun sourcesRetainUnverifiedProvenanceWithoutImplyingApproval() {
        val entries = donorEntries()
        val cards = listOf(
            ShellHomeDestination.KNOWLEDGE,
            ShellHomeDestination.TRAFFIC_SAFETY,
            ShellHomeDestination.OCCUPATIONAL_SAFETY,
            ShellHomeDestination.FIRST_AID,
        ).flatMap { CommonReferencePolicy.cards(entries, it) }
        assertEquals(66, cards.size)
        assertTrue(cards.all { it.sourceEvidence.isNotEmpty() })
        assertTrue(cards.flatMap { it.sourceEvidence }.all { it.sourceStatus == SourceStatus.UNKNOWN })
        assertTrue(cards.all { it.sources == it.sourceEvidence.map { s -> s.title } })
        assertTrue(cards.filter { it.id.startsWith("common.first-aid.") }.all {
            it.details.isEmpty() && it.relatedCards.isEmpty()
        })
    }
}
