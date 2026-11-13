package ru.railbrake.calculator.assistant

import org.junit.Assert.*
import org.junit.Test
import ru.railbrake.calculator.domain.*
import ru.railbrake.calculator.runtime.*

class AssistantUiNavigationGateTest {
    private val model = ModelId("vl80s")
    private fun entry(id: String, status: PublicationStatus = PublicationStatus.ACTIVE,
        disposition: ActionDisposition = ActionDisposition.INFORMATION_ONLY,
        type: ContentType = ContentType.EQUIPMENT, refs: Set<String> = emptySet(),
    ) = ContentEntry(id = CanonicalId(id), type = type, owner = ContentOwner.Model(model),
        publicationStatus = status, provenance = ProvenanceClass.UNKNOWN,
        sourceStatus = SourceStatus.UNKNOWN, actionDisposition = disposition,
        title = "Главный выключатель", sourceRefs = refs)
    private fun registry(vararg entries: ContentEntry): ContentRegistry {
        val registry = ContentRegistry()
        val pack = ContentPack(ContentPackManifest(1, PackId("gate-test"), "1", null,
            emptySet(), emptySet(), "ru-RU", entries.map { it.id }.toSet(),
            "1", "test", emptyMap()), entries.toList())
        assertTrue(registry.install(pack).isEmpty())
        return registry
    }
    private fun result(entry: ContentEntry) = TextAssistantResult.Matches(
        AssistantScope(model, AssistantQueryMode.WORKING_MODEL, model),
        TextIntent.REFERENCE,
        listOf(TextAssistantHit(entry, 120, emptySet(), false)), null)
    private fun context() = RuntimeContext(model, model,
        allowedLayers = setOf(ContentLayer.STANDARD))

    @Test fun opensOnlyActualSearchHits() {
        val item = entry("gv")
        val other = entry("other")
        val registry = registry(item, other)
        assertEquals(item, AssistantUiNavigationGate.openHit(
            result(item), ContentTarget(item.id, item.type), registry, setOf(model)))
        assertNull(AssistantUiNavigationGate.openHit(
            result(item), ContentTarget(other.id, other.type), registry, setOf(model)))
    }
    @Test fun unpublishedAndActionTargetsRemainClosed() {
        val candidate = entry("candidate", PublicationStatus.CANDIDATE)
        val action = entry("action", disposition = ActionDisposition.CONDITIONAL_ACTION)
        val registry = registry(candidate, action)
        assertNull(AssistantUiNavigationGate.resolveSafeTarget(
            ContentTarget(candidate.id, candidate.type), registry, context(), setOf(model)))
        assertNull(AssistantUiNavigationGate.resolveSafeTarget(
            ContentTarget(action.id, action.type), registry, context(), setOf(model)))
    }
    @Test fun unknownModelCannotBorrowVl80s() {
        val item = entry("gv")
        assertNull(AssistantUiNavigationGate.resolveSafeTarget(
            ContentTarget(item.id, item.type), registry(item),
            RuntimeContext(ModelId("chme3"), ModelId("chme3")), setOf(model)))
    }
    @Test fun diagnosticsNeedCurrentVerifiedSource() {
        val diagnostic = entry("diag", type = ContentType.DIAGNOSTIC_SCENARIO,
            refs = setOf("missing"))
        assertNull(AssistantUiNavigationGate.resolveSafeTarget(
            ContentTarget(diagnostic.id, diagnostic.type), registry(diagnostic),
            context(), setOf(model)))
    }
    @Test fun typeMismatchAndSourceDirectAccessAreDenied() {
        val source = entry("source", type = ContentType.SOURCE)
        val registry = registry(source)
        assertNull(AssistantUiNavigationGate.resolveSafeTarget(
            ContentTarget(source.id, source.type), registry, context(), setOf(model)))
        assertNull(AssistantUiNavigationGate.resolveSafeTarget(
            ContentTarget(source.id, ContentType.EQUIPMENT), registry, context(), setOf(model)))
    }
}
