package ru.railbrake.calculator.shell

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.Applicability
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.ProvenanceClass
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.domain.VariantId

class FamilyPublicationGateTest {
    private val profile = FamilyProfiles.forModel(ModelId("tem2"))!!
    private val variant = VariantId("tem2")
    private val allowed = setOf(ContentType.EQUIPMENT)
    private fun entry(
        status: PublicationStatus = PublicationStatus.ACTIVE,
        variantIds: Set<VariantId> = setOf(variant),
        model: ModelId = ModelId("tem2-family"),
        refs: Set<String> = setOf("source.ok"),
        type: ContentType = ContentType.EQUIPMENT,
        provenance: ProvenanceClass = ProvenanceClass.MANUFACTURER,
        sourceStatus: SourceStatus = SourceStatus.CURRENT,
        disposition: ActionDisposition = ActionDisposition.INFORMATION_ONLY,
        layer: ContentLayer = ContentLayer.STANDARD,
    ) = ContentEntry(
        id = CanonicalId("tem2.eq.sample"), type = type,
        owner = ContentOwner.Model(model),
        applicability = Applicability(modelIds = setOf(model), variantIds = variantIds),
        publicationStatus = status, provenance = provenance, sourceStatus = sourceStatus,
        actionDisposition = disposition, layer = layer, sourceRefs = refs,
        title = "Тестовая карточка",
    )
    private fun permitted(e: ContentEntry, v: VariantId? = variant, sources: Set<String> = setOf("source.ok")) =
        FamilyPublicationGate.canDisplay(e, profile, v, sources, allowed)

    @Test fun onlyExplicitVerifiedInformationalEntryCanPass() {
        assertTrue(permitted(entry()))
        assertFalse(permitted(entry(), null))
        assertFalse(permitted(entry(), VariantId("tem2u")))
    }
    @Test fun candidatesAndUnknownSourcesNeverPublish() {
        assertFalse(permitted(entry(status = PublicationStatus.CANDIDATE)))
        assertFalse(permitted(entry(sourceStatus = SourceStatus.UNKNOWN)))
        assertFalse(permitted(entry(provenance = ProvenanceClass.UNKNOWN)))
    }
    @Test fun familyOnlyAndCrossFamilyCardsFailClosed() {
        assertFalse(permitted(entry(variantIds = emptySet())))
        assertFalse(permitted(entry(model = ModelId("chme3-family"))))
        assertFalse(permitted(entry(variantIds = setOf(VariantId("tem2u")))))
    }
    @Test fun missingOrUntrustedSourcesFailClosed() {
        assertFalse(permitted(entry(refs = emptySet())))
        assertFalse(permitted(entry(), sources = emptySet()))
        assertFalse(permitted(entry(refs = setOf("source.ok", "source.missing"))))
    }
    @Test fun diagnosticsAndUnsafeContentNeverEnterInformationalCatalog() {
        assertFalse(permitted(entry(type = ContentType.DIAGNOSTIC_SCENARIO)))
        assertFalse(permitted(entry(disposition = ActionDisposition.CONDITIONAL_ACTION)))
        assertFalse(permitted(entry(disposition = ActionDisposition.PROHIBITED)))
        assertFalse(permitted(entry(layer = ContentLayer.RESTRICTED)))
    }
    @Test fun sourceNeedsIndependentPublicationAndProvenance() {
        assertTrue(FamilyPublicationGate.trustedSource(entry(type = ContentType.SOURCE), profile))
        assertFalse(FamilyPublicationGate.trustedSource(
            entry(type = ContentType.SOURCE, status = PublicationStatus.CANDIDATE), profile))
    }
    @Test fun distinctSeriesAndExecutionsNeverMerge() {
        val a = FamilyProfiles.forModel(ModelId("2es5k"))!!
        val b = FamilyProfiles.forModel(ModelId("3es5k"))!!
        assertTrue(a.executions.map { it.id }.intersect(b.executions.map { it.id }.toSet()).isEmpty())
        val chme3t = FamilyProfiles.forModel(ModelId("chme3t"))!!
        assertTrue(chme3t.executions.map { it.id.value }.containsAll(
            listOf("chme3t_pre6245", "chme3t_from6245")))
        assertTrue(FamilyProfiles.forModel(ModelId("unknown")) == null)
    }
}
