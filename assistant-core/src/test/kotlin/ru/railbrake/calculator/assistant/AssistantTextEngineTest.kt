package ru.railbrake.calculator.assistant

import org.junit.Assert.*
import org.junit.Test
import ru.railbrake.calculator.domain.*
import ru.railbrake.calculator.runtime.*

class AssistantTextEngineTest {
    private val vl = ModelId("vl80s")
    private fun entry(
        id: String,
        status: PublicationStatus = PublicationStatus.ACTIVE,
        type: ContentType = ContentType.EQUIPMENT,
        disposition: ActionDisposition = ActionDisposition.INFORMATION_ONLY,
        variants: Set<VariantId> = emptySet(),
        refs: Set<String> = emptySet(),
        provenance: ProvenanceClass = ProvenanceClass.UNKNOWN,
        sourceStatus: SourceStatus = SourceStatus.UNKNOWN,
    ) = ContentEntry(
        id = CanonicalId(id), type = type, owner = ContentOwner.Model(vl),
        applicability = Applicability(variantIds = variants),
        publicationStatus = status, provenance = provenance, sourceStatus = sourceStatus,
        actionDisposition = disposition, title = "Главный выключатель",
        searchTerms = setOf("ГВ"), sourceRefs = refs,
    )
    private fun engine(vararg entries: ContentEntry): AssistantTextEngine {
        val registry = ContentRegistry()
        val pack = ContentPack(ContentPackManifest(1, PackId("test"), "1.0", null,
            emptySet(), emptySet(), "ru-RU", entries.map { it.id }.toSet(),
            "1", "test", emptyMap()), entries.toList())
        assertTrue(registry.install(pack).isEmpty())
        return AssistantTextEngine(registry, setOf(vl))
    }
    @Test fun parserPreservesNegationAndSeries() {
        val parsed = TextQueryParser.parse("На ВЛ80С не включается ГВ")
        assertEquals(setOf(vl), parsed.explicitModels)
        assertEquals(TextIntent.DIAGNOSTICS, parsed.intent)
        assertTrue(parsed.searchText.contains("не включается"))
        assertNotEquals(TextQueryParser.normalize("не включается"),
            TextQueryParser.normalize("не выключается"))
    }
    @Test fun missingModelFailsClosed() {
        assertEquals(TextAssistantResult.WorkingModelRequired,
            engine(entry("gv")).query("главный выключатель", null))
    }
    @Test fun activeReferenceIsFoundButUnknownSourceCannotAutoOpen() {
        val result = engine(entry("gv")).query("главный выключатель", vl)
        assertTrue(result is TextAssistantResult.Matches)
        result as TextAssistantResult.Matches
        assertEquals("gv", result.hits.first().entry.id.value)
        assertFalse(result.hits.first().sourceVerified)
        assertNull(result.recommended)
    }
    @Test fun candidateAndConditionalActionAreExcluded() {
        assertTrue(engine(entry("candidate", status = PublicationStatus.CANDIDATE),
            entry("action", disposition = ActionDisposition.CONDITIONAL_ACTION))
            .query("главный выключатель", vl) is TextAssistantResult.NoMatches)
    }
    @Test fun faultCannotReturnEquipmentAsRepairAdvice() {
        assertTrue(engine(entry("gv")).query("не включается главный выключатель", vl)
            is TextAssistantResult.NoMatches)
    }
    @Test fun variantRequiresExplicitProfile() {
        assertTrue(engine(entry("gv", variants = setOf(VariantId("vl80s_697_1260"))))
            .query("главный выключатель", vl) is TextAssistantResult.NoMatches)
    }
    @Test fun unpublishedOtherModelNeverBorrowsVl80s() {
        assertEquals(TextAssistantResult.UnpublishedModel(ModelId("2es5k")),
            engine(entry("gv")).query("главный выключатель 2ЭС5К", vl))
    }
    @Test fun ermakWithoutSeriesClarifies() {
        val result = engine(entry("gv")).query("главный выключатель Ермак", vl)
        assertTrue(result is TextAssistantResult.ClarifyModel)
        assertEquals(setOf(ModelId("2es5k"), ModelId("3es5k")),
            (result as TextAssistantResult.ClarifyModel).choices)
    }
    @Test fun conflictingSeriesClarifies() {
        assertTrue(engine(entry("gv")).query("главный выключатель ВЛ80С ЧМЭ3", vl)
            is TextAssistantResult.ClarifyModel)
    }
    @Test fun sourceIsVerifiedOnlyWithCurrentPublishedManufacturer() {
        val source = entry("src", type = ContentType.SOURCE,
            provenance = ProvenanceClass.MANUFACTURER, sourceStatus = SourceStatus.CURRENT)
        val result = engine(entry("gv", refs = setOf("src")), source)
            .query("главный выключатель", vl)
        assertTrue((result as TextAssistantResult.Matches).hits.first().sourceVerified)
    }
    @Test fun missingSourceDoesNotCountAsVerified() {
        val result = engine(entry("gv", refs = setOf("missing")))
            .query("главный выключатель", vl)
        assertFalse((result as TextAssistantResult.Matches).hits.first().sourceVerified)
    }
    @Test fun clarificationNeverChangesWorkingModel() {
        val conversation = AssistantTextConversation(engine(entry("gv")))
        assertTrue(conversation.submit("главный выключатель Ермак", vl)
            is TextAssistantResult.ClarifyModel)
        assertEquals(TextAssistantResult.UnpublishedModel(ModelId("2es5k")),
            conversation.clarify(ModelId("2es5k"), vl))
    }

    @Test fun categoryFilterDoesNotLeakOtherContentTypes() {
        val result = engine(entry("equipment"), entry("knowledge", type = ContentType.KNOWLEDGE))
            .query("главный выключатель", vl, limit = 50,
                intentOverride = TextIntent.REFERENCE,
                allowedTypes = setOf(ContentType.KNOWLEDGE))
        assertEquals(listOf("knowledge"),
            (result as TextAssistantResult.Matches).hits.map { it.entry.id.value })
    }

    @Test fun resultLimitSupportsPaginationWithoutUnboundedQueries() {
        val entries = (1..55).map { entry("equipment" + it) }
        val result = engine(*entries.toTypedArray())
            .query("главный выключатель", vl, limit = 100)
        assertEquals(50, (result as TextAssistantResult.Matches).hits.size)
    }
}
