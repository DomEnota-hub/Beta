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
}
