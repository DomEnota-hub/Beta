package ru.railbrake.calculator.safety

import java.nio.file.Files
import java.nio.file.Path
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.ContentLayer
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
        val json = Files.readString(Path.of("..", "content-packs", "common", path))
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
}
