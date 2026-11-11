package ru.railbrake.calculator.diagnostics

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
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

class DiagnosticReferenceCatalogTest {
    private val scenario = ExecutableDiagnosticScenario(
        legacyId = "pantograph-no-rise",
        id = "vl80s.diag.pantograph-no-rise",
        category = "Высоковольтные цепи",
        title = "Токоприёмник не поднимается",
        summary = "Симптом из донорской базы",
        profileId = "vl80s",
        applicableVariantIds = setOf("vl80s.general"),
        informationConfidence = "REFERENCE",
        severity = "ATTENTION",
        applicability = "ВЛ80С",
        startQuestionKey = null,
        questions = emptyList(),
        diagnosticCauses = emptyList(),
        probableCauses = emptyList(),
        immediateActions = listOf("DO_NOT_EXPOSE_UNVERIFIED_ACTION"),
        dangerSigns = listOf("DO_NOT_EXPOSE_UNVERIFIED_DANGER"),
        checks = emptyList(),
        prohibited = listOf("DO_NOT_EXPOSE_UNVERIFIED_PROHIBITION"),
        stopConditions = emptyList(),
        reportFields = emptyList(),
        relatedEquipment = emptyList(),
        sourceNote = "DO_NOT_EXPOSE_UNVERIFIED_SOURCE_CLAIM",
        observableSigns = emptyList(),
        systemExplanation = emptyList(),
        operationalConsequences = emptyList(),
        trainingNotes = emptyList(),
        feedbackPrompts = emptyList(),
        relatedScenarioIds = emptyList(),
    )
    private val runtime = ExecutableDiagnosticRuntime(
        schemaVersion = 1,
        modelId = "vl80s",
        sourceRepository = "DomEnota-hub/Test-",
        sourceCommit = "3176d6ee228f0ed4b78371f45209e10c1c724eff",
        runtimeSource = "DiagnosticRepository.scenarios",
        scenarioCount = 1,
        questionCount = 0,
        responseEdgeCount = 0,
        scenarios = listOf(scenario),
    )

    private fun registry(
        status: PublicationStatus = PublicationStatus.CANDIDATE,
        layer: ContentLayer = ContentLayer.STANDARD,
        model: String = "vl80s",
        variants: Set<VariantId> = emptySet(),
        type: ContentType = ContentType.DIAGNOSTIC_SCENARIO,
    ): ContentRegistry {
        val id = CanonicalId(scenario.id)
        val entry = ContentEntry(
            id = id,
            type = type,
            owner = ContentOwner.Model(ModelId(model)),
            applicability = Applicability(
                modelIds = setOf(ModelId(model)),
                variantIds = variants,
            ),
            layer = layer,
            publicationStatus = status,
            provenance = ProvenanceClass.UNKNOWN,
            sourceStatus = SourceStatus.UNKNOWN,
            actionDisposition = ActionDisposition.CONDITIONAL_ACTION,
            title = scenario.title,
            summary = scenario.summary,
        )
        val manifest = ContentPackManifest(
            schemaVersion = 1,
            packId = PackId("vl80s.diagnostic.reference.test"),
            packVersion = "1",
            family = "electric",
            modelIds = setOf(ModelId(model)),
            variantIds = emptySet(),
            locale = "ru",
            entries = setOf(id),
            requiresRuntime = "test",
            sourceCatalogVersion = "test",
            checksums = emptyMap(),
        )
        return ContentRegistry().also {
            assertTrue(it.install(ContentPack(manifest, listOf(entry))).isEmpty())
        }
    }

    private fun context(
        model: String = "vl80s",
        variant: String = "vl80s.unknown",
    ) = RuntimeContext(
        viewedModelId = ModelId(model),
        activeVariantId = VariantId(variant),
    )

    @Test
    fun candidateDescriptionIsReadableWithoutPublishingDonorActions() {
        val catalog = DiagnosticReferenceCatalog(runtime, registry(), context())
        val preview = requireNotNull(catalog.open(scenario.id))
        assertEquals(scenario.title, preview.title)
        assertEquals(scenario.summary, preview.summary)
        assertTrue(preview.sourceNotice.contains("требуют проверки"))
        assertTrue(preview.variantNotice!!.contains("не подтверждена"))
        assertEquals(1, catalog.search("ТОКОПРИЁМНИК").size)
        assertEquals(1, catalog.search("симптом").size)
        assertEquals(0, catalog.search("неизвестный запрос").size)
        val exposed = preview.toString()
        assertFalse(exposed.contains("DO_NOT_EXPOSE_UNVERIFIED_ACTION"))
        assertFalse(exposed.contains("DO_NOT_EXPOSE_UNVERIFIED_DANGER"))
        assertFalse(exposed.contains("DO_NOT_EXPOSE_UNVERIFIED_PROHIBITION"))
        assertFalse(exposed.contains("DO_NOT_EXPOSE_UNVERIFIED_SOURCE_CLAIM"))
        // No executable question or route is exposed by the reference type.
        assertEquals(6, DiagnosticReferencePreview::class.java.declaredFields.count {
            !it.isSynthetic
        })
    }

    @Test
    fun referenceIsScopedToExactModelAndRegistryApplicability() {
        assertTrue(DiagnosticReferenceCatalog(runtime, registry(), context("ermak")).search("").isEmpty())
        assertTrue(DiagnosticReferenceCatalog(runtime, registry(model = "ermak"), context()).search("").isEmpty())
        assertTrue(
            DiagnosticReferenceCatalog(
                runtime,
                registry(variants = setOf(VariantId("vl80s.other"))),
                context(),
            ).search("").isEmpty(),
        )
        val confirmedVariant = DiagnosticReferenceCatalog(
            runtime,
            registry(),
            context(variant = "vl80s.general"),
        ).open(scenario.id)
        assertNull(requireNotNull(confirmedVariant).variantNotice)
    }

    @Test
    fun activeOrRestrictedOrWrongTypeNeverAppearsAsCandidateReference() {
        assertTrue(
            DiagnosticReferenceCatalog(runtime, registry(status = PublicationStatus.ACTIVE), context())
                .search("").isEmpty(),
        )
        assertTrue(
            DiagnosticReferenceCatalog(runtime, registry(layer = ContentLayer.EXTENDED), context())
                .search("").isEmpty(),
        )
        assertTrue(
            DiagnosticReferenceCatalog(runtime, registry(type = ContentType.EQUIPMENT), context())
                .search("").isEmpty(),
        )
    }
}
