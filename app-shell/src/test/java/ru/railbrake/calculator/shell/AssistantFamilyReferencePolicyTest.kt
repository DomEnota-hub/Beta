package ru.railbrake.calculator.shell

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId

class AssistantFamilyReferencePolicyTest {
    private val vl = ModelId("vl80s")
    private val tem = FamilyReferencePreview(
        id = "donor-summary.tem2", modelId = "tem2", executionId = "tem2",
        scope = ReferenceScope.DONOR_VARIANT, title = "Компрессор",
        summary = "Воздушная система", donorPath = "technical/tem2.json",
        donorBlobSha = "c7a94c1cd2687b84de4358b80773e3156c6b93d7",
    )

    @Test fun explicitOtherModelAllowsReadOnlyBeforeExecutionAndDoesNotChangeWorkingModel() {
        val query = AssistantFamilyReferencePolicy.resolveQuery("ТЭМ2 компрессор", vl, null)!!
        assertEquals("tem2", query.profile.workingModelId.value)
        assertEquals("компрессор", query.searchText)
        assertEquals(listOf(tem.id), AssistantFamilyReferencePolicy.search(
            listOf(tem), query, null).map { it.id })
        assertEquals(listOf(tem.id), AssistantFamilyReferencePolicy.search(
            listOf(tem), query, VariantId("tem2")).map { it.id })
        assertTrue(AssistantFamilyReferencePolicy.search(
            listOf(tem), query, VariantId("tem2u")).isEmpty())
        assertEquals("vl80s", vl.value)
    }

    @Test fun noUnspecifiedErmakOrCrossFamilyOrFaultExecution() {
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("Ермак компрессор", vl, null))
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("ВЛ80 компрессор", ModelId("tem2"), null))
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("VL80 компрессор", ModelId("tem2"), null))
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("2ЭС5К и 3ЭС5К компрессор", vl, null))
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("ТЭМ2 компрессор не работает", vl, null))
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("ТЭМ2 компрессор", vl,
            AssistantSearchCategory.FAULTS))
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("ВЛ80С компрессор", vl, null))
        val other = AssistantFamilyReferencePolicy.resolveQuery("ЧМЭ3Т компрессор", vl, null)!!
        assertEquals(2, other.profile.executions.size)
        assertTrue(AssistantFamilyReferencePolicy.search(listOf(tem), other,
            VariantId("chme3t_pre6245")).isEmpty())
    }

    @Test fun onlyPinnedSummaryWithMatchingSourceAndExactExecutionIsReadable() {
        val query = AssistantFamilyReferencePolicy.resolveQuery("ТЭМ2 компрессор", vl, null)!!
        val variants = listOf(tem,
            tem.copy(id = "other", modelId = "tem2u", executionId = "tem2u"),
            tem.copy(id = "bad-sha", donorBlobSha = "not-proven"),
            tem.copy(id = "unverified-execution", executionId = null,
                scope = ReferenceScope.EXECUTION_UNVERIFIED))
        assertEquals(listOf("donor-summary.tem2", "unverified-execution"),
            AssistantFamilyReferencePolicy.search(variants, query,
                VariantId("tem2")).map { it.id })
        assertTrue(AssistantFamilyReferencePolicy.search(variants, query,
            VariantId("unknown")).isEmpty())
    }

    @Test fun multiExecutionWithoutSelectionShowsOnlyUnverifiedKnowledge() {
        val query = AssistantFamilyReferencePolicy.resolveQuery(
            "2ЭС5К компрессор", vl, AssistantSearchCategory.EQUIPMENT)!!
        val general = tem.copy(
            id = "ermak-general", modelId = "2es5k", executionId = null,
            scope = ReferenceScope.EXECUTION_UNVERIFIED)
        val msudN = general.copy(
            id = "ermak-n", scope = ReferenceScope.DONOR_VARIANT,
            executionId = "2es5k_msud_n")
        val foreign = general.copy(id = "other-model", modelId = "3es5k")
        val badSource = general.copy(id = "bad-source", donorBlobSha = "unverified")
        val hits = AssistantFamilyReferencePolicy.search(
            listOf(general, msudN, foreign, badSource), query, null)
        assertEquals(listOf(general.id), hits.map { it.id })
        assertEquals(listOf(general.id, msudN.id),
            AssistantFamilyReferencePolicy.search(
                listOf(general, msudN), query, VariantId("2es5k_msud_n"))
                .map { it.id }.sorted())
        assertTrue(AssistantFamilyReferencePolicy.search(
            listOf(msudN), query, null).isEmpty())
        assertTrue(AssistantFamilyReferencePolicy.search(
            listOf(general), query, VariantId("3es5k_msud_n")).isEmpty())
    }

    @Test fun chme3tSerialVariantAndFaultsCannotLeakBeforeExecution() {
        val query = AssistantFamilyReferencePolicy.resolveQuery(
            "ЧМЭ3Т компрессор", vl, null)!!
        val before = tem.copy(
            id = "pre6245", modelId = "chme3t",
            executionId = "chme3t_pre6245")
        val after = before.copy(id = "from6245", executionId = "chme3t_from6245")
        assertTrue(AssistantFamilyReferencePolicy.search(
            listOf(before, after), query, null).isEmpty())
        assertEquals(listOf(before.id), AssistantFamilyReferencePolicy.search(
            listOf(before, after), query, VariantId("chme3t_pre6245")).map { it.id })
        assertNull(AssistantFamilyReferencePolicy.resolveQuery(
            "ЧМЭ3Т компрессор неисправен", vl, null))
    }
}
