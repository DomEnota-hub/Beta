package ru.railbrake.calculator.shell

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.Applicability
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentPackManifest
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.PackId
import ru.railbrake.calculator.domain.ProvenanceClass
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.runtime.ContentPack
import ru.railbrake.calculator.runtime.ContentRegistry

class Vl80sEntryGateTest {
    private val vl = ModelId("vl80s")
    private val unknown = VariantId("vl80s_unknown")

    private fun entry(id: String, type: ContentType = ContentType.EQUIPMENT) = ContentEntry(
        id = CanonicalId(id), type = type,
        owner = ContentOwner.Model(vl),
        applicability = Applicability(modelIds = setOf(vl)),
        provenance = ProvenanceClass.MANUFACTURER,
        sourceStatus = SourceStatus.UNKNOWN,
        actionDisposition = ActionDisposition.INFORMATION_ONLY,
        title = id,
    )

    private fun registry(vararg entries: ContentEntry): ContentRegistry =
        ContentRegistry().also { registry ->
            assertTrue(registry.install(ContentPack(
                manifest = ContentPackManifest(
                    schemaVersion = 1, packId = PackId("vl80s.gate.test"),
                    packVersion = "1", family = "ELECTRIC",
                    modelIds = setOf(vl), variantIds = emptySet(),
                    locale = "ru-RU", entries = entries.map { it.id }.toSet(),
                    requiresRuntime = "1", sourceCatalogVersion = "test", checksums = emptyMap(),
                ),
                entries = entries.toList(),
            )).isEmpty())
        }

    @Test
    fun onlyPublishedInformationalVl80sCardOpens() {
        val active = entry("published")
        val candidate = entry("candidate").copy(publicationStatus = PublicationStatus.CANDIDATE)
        val restricted = entry("restricted").copy(layer = ContentLayer.RESTRICTED)
        val action = entry("action").copy(actionDisposition = ActionDisposition.CONDITIONAL_ACTION)
        val source = entry("source", ContentType.SOURCE)
        val scenario = entry("scenario", ContentType.DIAGNOSTIC_SCENARIO)
        val variant = entry("variant").copy(
            applicability = Applicability(
                modelIds = setOf(vl), variantIds = setOf(VariantId("vl80s_pre697")),
            ),
        )
        val wrongOwner = entry("foreign").copy(owner = ContentOwner.Model(ModelId("chme3")))
        val registry = registry(active, candidate, restricted, action, source, scenario, variant, wrongOwner)
        val context = RuntimeContext(workingModelId = vl, activeVariantId = unknown)
        assertEquals(active, Vl80sEntryGate.open(registry, active.id, context))
        for (blocked in listOf(candidate, restricted, action, source, scenario, variant, wrongOwner)) {
            assertNull("Must reject " + blocked.id.value, Vl80sEntryGate.open(registry, blocked.id, context))
        }
        assertNull(Vl80sEntryGate.open(registry, active.id, RuntimeContext()))
        assertNull(Vl80sEntryGate.open(registry, active.id, RuntimeContext(workingModelId = ModelId("chme3"))))
        assertNull(Vl80sEntryGate.open(registry, CanonicalId("missing"), context))
    }

    @Test
    fun exactVariantCardOnlyOpensWithMatchingExplicitVariant() {
        val card = entry("serial-specific").copy(
            applicability = Applicability(
                modelIds = setOf(vl), variantIds = setOf(VariantId("vl80s_pre697")),
            ),
        )
        val registry = registry(card)
        assertNull(Vl80sEntryGate.open(registry, card.id, RuntimeContext(workingModelId = vl)))
        assertNull(Vl80sEntryGate.open(registry, card.id,
            RuntimeContext(workingModelId = vl, activeVariantId = unknown)))
        assertEquals(card, Vl80sEntryGate.open(registry, card.id,
            RuntimeContext(workingModelId = vl, activeVariantId = VariantId("vl80s_pre697"))))
    }
}
