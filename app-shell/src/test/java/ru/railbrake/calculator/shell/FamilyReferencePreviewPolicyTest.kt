package ru.railbrake.calculator.shell

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.assertEquals
import org.junit.Test
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination

class FamilyReferencePreviewPolicyTest {
    private val tem2 = FamilyProfiles.forModel(ModelId("tem2"))!!
    private val base = FamilyReferencePreview(
        id = "donor-summary.tem2", modelId = "tem2", executionId = "tem2",
        scope = ReferenceScope.DONOR_VARIANT, title = "Маслоотделитель",
        summary = "Подготовка воздуха", donorPath = "app/src/main/assets/technical/tem2_tem2_catalog.json",
        donorBlobSha = "c7a94c1cd2687b84de4358b80773e3156c6b93d7",
    )
    private fun show(
        entry: FamilyReferencePreview = base,
        model: FamilyModelProfile = tem2,
        execution: VariantId? = VariantId("tem2"),
        destination: ShellHomeDestination = ShellHomeDestination.ATLAS,
    ) = FamilyReferencePreviewPolicy.canShow(entry, model, execution, destination)

    @Test fun exactDonorVariantIsReferenceOnlyAfterExplicitSelection() {
        assertTrue(show())
        assertFalse(show(execution = null))
        assertFalse(show(execution = VariantId("tem2u")))
        assertFalse(show(model = FamilyProfiles.forModel(ModelId("tem2u"))!!))
        assertFalse(show(destination = ShellHomeDestination.DIAGNOSTICS))
        assertFalse(show(destination = ShellHomeDestination.ACCEPTANCE))
    }

    @Test fun unknownExecutionAndForeignModelFailClosed() {
        assertFalse(show(execution = VariantId("not-a-variant")))
        assertFalse(show(entry = base.copy(modelId = "chme3")))
        assertFalse(show(entry = base.copy(executionId = "tem2u")))
        assertFalse(show(entry = base.copy(donorBlobSha = "unverified")))
        assertFalse(show(entry = base.copy(summary = "")))
    }

    @Test fun searchIsScopedBeforeMatchingAndDoesNotLeakOtherModels() {
        val other = base.copy(id = "donor-summary.tem2u", modelId = "tem2u",
            executionId = "tem2u", title = "Скрытый реверсор")
        val candidates = listOf(base, other, base.copy(id = "donor-summary.tem2.second",
            title = "Тормозной резервуар", summary = "Пневматическая система"))
        val matches = FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "масло")
        assertEquals(listOf(base.id), matches.map { it.id })
        assertTrue(FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "скрытый").isEmpty())
        assertTrue(FamilyReferencePreviewPolicy.search(candidates, tem2,
            null, ShellHomeDestination.ATLAS, "").isEmpty())
        assertTrue(FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ACCEPTANCE, "").isEmpty())
        assertEquals(2, FamilyReferencePreviewPolicy.search(candidates, tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "").size)
    }

    @Test fun normalizedMultiwordSearchUsesOnlyVisibleSummaryAndKeepsExecutionGate() {
        val matches = FamilyReferencePreviewPolicy.search(listOf(base), tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS, "воздуха подготовка")
        assertEquals(listOf(base.id), matches.map { it.id })
        assertTrue(FamilyReferencePreviewPolicy.search(listOf(base), tem2,
            VariantId("tem2"), ShellHomeDestination.ATLAS,
            "подготовка воздуха несуществующий").isEmpty())
        assertTrue(FamilyReferencePreviewPolicy.search(listOf(base), tem2,
            VariantId("tem2u"), ShellHomeDestination.ATLAS,
            "воздуха подготовка").isEmpty())
    }


    @Test fun singleExecutionReferenceReadableBeforeSelectionButNotExecutable() {
        assertTrue(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base, tem2, ShellHomeDestination.ATLAS))
        assertFalse(show(execution = null)) // Published/execution-scoped path stays closed.
        assertFalse(FamilyCatalogLoadPolicy.shouldLoad(
            tem2, null, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base, tem2, ShellHomeDestination.ACCEPTANCE))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base.copy(modelId = "tem2u"), tem2, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            base.copy(donorBlobSha = "unverified"), tem2, ShellHomeDestination.ATLAS))
        assertEquals(listOf(base.id), FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(base), tem2, ShellHomeDestination.ATLAS, "воздуха подготовка"
        ).map { it.id })
    }

    @Test fun multiExecutionUnknownOnlyExposesGeneralUnverifiedSummaries() {
        val ermak = FamilyProfiles.forModel(ModelId("2es5k"))!!
        val general = base.copy(
            id = "ermak-general", modelId = "2es5k", executionId = null,
            scope = ReferenceScope.EXECUTION_UNVERIFIED,
        )
        val msudN = general.copy(
            id = "ermak-n", scope = ReferenceScope.DONOR_VARIANT,
            executionId = "2es5k_msud_n",
        )
        assertTrue(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            general, ermak, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            msudN, ermak, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            general.copy(modelId = "3es5k"), ermak, ShellHomeDestination.ATLAS))
        assertFalse(FamilyReferencePreviewPolicy.canReadBeforeExecution(
            general.copy(executionId = "2es5k_msud_n"), ermak,
            ShellHomeDestination.ATLAS))
        assertEquals(listOf(general.id), FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(general, msudN), ermak, ShellHomeDestination.ATLAS, ""
        ).map { it.id })
        assertFalse(FamilyReferencePreviewPolicy.canShow(
            general, ermak, null, ShellHomeDestination.ATLAS))
        assertFalse(FamilyCatalogLoadPolicy.shouldLoad(
            ermak, null, ShellHomeDestination.ATLAS))
    }

    @Test fun chme3tSerialSplitCannotLeakVariantSummaryWithoutSelection() {
        val chme3t = FamilyProfiles.forModel(ModelId("chme3t"))!!
        val before = base.copy(
            id = "chme3t-before", modelId = "chme3t",
            executionId = "chme3t_pre6245",
        )
        val after = before.copy(
            id = "chme3t-after", executionId = "chme3t_from6245",
        )
        assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(before, after), chme3t, ShellHomeDestination.ATLAS, ""
        ).isEmpty())
        assertEquals(listOf(before.id), FamilyReferencePreviewPolicy.search(
            listOf(before, after), chme3t, VariantId("chme3t_pre6245"),
            ShellHomeDestination.ATLAS, ""
        ).map { it.id })
    }

    @Test fun familyGeneralReferenceIsNeverPresentedAsVerifiedExecution() {
        val ermak = FamilyProfiles.forModel(ModelId("2es5k"))!!
        val general = base.copy(
            modelId = "2es5k", executionId = null,
            scope = ReferenceScope.EXECUTION_UNVERIFIED,
        )
        assertTrue(show(general, ermak, VariantId("2es5k_msud_n")))
        assertTrue(show(general, ermak, VariantId("2es5k_msud_015")))
        assertFalse(show(general, ermak, VariantId("3es5k_msud_n")))
        assertFalse(show(general.copy(executionId = "2es5k_msud_n"),
            ermak, VariantId("2es5k_msud_n")))
        assertFalse(show(general.copy(scope = ReferenceScope.DONOR_VARIANT),
            ermak, VariantId("2es5k_msud_n")))
    }
    @Test fun ermakSystemDetailsRemainReferenceOnlyAndSearchable() {
        val profile = FamilyProfiles.forModel(ModelId("2es5k"))!!
        val entry = base.copy(modelId = "2es5k", executionId = null,
            scope = ReferenceScope.EXECUTION_UNVERIFIED,
            donorPath = "app/src/main/assets/technical/ermak_knowledge.json.gz",
            donorBlobSha = "08d164fc11c33c241d04ad6ad60c13a3aec996c8",
            donorId = "ER-KB-SYS-20")
        assertTrue(FamilyReferenceDetails.forEntry(entry)!!.sourceIds.contains("ER-SRC-001"))
        assertEquals(null, FamilyReferenceDetails.forEntry(entry.copy(modelId = "tem2")))
        assertEquals(null, FamilyReferenceDetails.forEntry(entry.copy(donorBlobSha = "wrong")))
        assertEquals(null, FamilyReferenceDetails.forEntry(entry.copy(executionId = "2es5k_msud_n")))
        assertEquals(listOf(entry.id), FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(entry), profile, ShellHomeDestination.ATLAS, "реакторы").map { it.id })
        assertTrue(FamilyReferencePreviewPolicy.searchBeforeExecution(
            listOf(entry), profile, ShellHomeDestination.DIAGNOSTICS, "реакторы").isEmpty())
    }
}
