package ru.railbrake.calculator.shell

import java.nio.file.Files
import java.nio.file.Path
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.runtime.ContentPackJsonLoader

class AssistantCommonReferencePolicyTest {
    private fun realDonorEntries() = listOf(
        "first-aid/topics.pack.json",
        "knowledge/articles.pack.json",
        "safety/articles.pack.json",
    ).flatMap { path ->
        val file = Path.of("..", "content-packs", "common", path)
        ContentPackJsonLoader().parse(Files.readAllBytes(file).toString(Charsets.UTF_8)).entries
    }

    @Test fun assistantCanFindAlreadyReadableDonorReferencesWithoutPublishingActions() {
        val entries = realDonorEntries()
        val aid = AssistantCommonReferencePolicy.search(entries, "слр", null)
        assertEquals(listOf("common.first-aid.cpr"), aid.map { it.card.id })
        assertEquals(ShellHomeDestination.FIRST_AID, aid.single().destination)
        assertTrue(aid.single().card.details.isEmpty())
        assertTrue(aid.single().card.sourceEvidence.all { it.sourceStatus == SourceStatus.UNKNOWN })
        assertTrue(AssistantCommonReferencePolicy.search(entries, "автотормоза", null)
            .any { it.destination == ShellHomeDestination.KNOWLEDGE })
        assertTrue(AssistantCommonReferencePolicy.search(entries, "автотормоза",
            AssistantSearchCategory.KNOWLEDGE).all {
                it.destination in setOf(ShellHomeDestination.KNOWLEDGE,
                    ShellHomeDestination.TRAFFIC_SAFETY)
            })
    }

    @Test fun noCrossModelSubstitutionOrProceduralLeak() {
        val entries = realDonorEntries()
        listOf("ВЛ80С автотормоза", "ВЛ80 автотормоза", "VL80 автотормоза",
            "ЧМЭ3 слр", "Ермак автотормоза",
            "2ЭС5К и 3ЭС5К автотормоза", "пожарная сигнализация не работает",
            "жгут должен оставаться видимым").forEach { query ->
            assertTrue(query, AssistantCommonReferencePolicy.search(entries, query, null).isEmpty())
        }
        assertTrue(AssistantCommonReferencePolicy.search(entries, "слр",
            AssistantSearchCategory.FAULTS).isEmpty())
        assertTrue(AssistantCommonReferencePolicy.search(entries, "слр",
            AssistantSearchCategory.SCHEMES).isEmpty())
        assertTrue(AssistantCommonReferencePolicy.search(entries, "слр",
            AssistantSearchCategory.EQUIPMENT).isEmpty())
        assertTrue(AssistantCommonReferencePolicy.search(entries, "слр",
            AssistantSearchCategory.KNOWLEDGE).isEmpty())
    }

    @Test fun sourceAndActionGatesStillApplyToAssistantReferenceLane() {
        val entries = realDonorEntries()
        val aid = entries.first { it.id.value == "common.first-aid.cpr" }
        val sources = entries.filter { it.type == ContentType.SOURCE }
        assertEquals(1, AssistantCommonReferencePolicy.search(sources + aid, "слр", null).size)
        assertTrue(AssistantCommonReferencePolicy.search(listOf(aid), "слр", null).isEmpty())
        assertTrue(AssistantCommonReferencePolicy.search(sources +
            aid.copy(actionDisposition = ActionDisposition.CONDITIONAL_ACTION),
            "слр", null).isEmpty())
        assertTrue(AssistantCommonReferencePolicy.search(sources +
            aid.copy(publicationStatus = PublicationStatus.ACTIVE),
            "слр", null).isEmpty())
        assertTrue(AssistantCommonReferencePolicy.search(entries, "слр", null, limit = 0).size <= 1)
    }
}
