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

    @Test fun explicitOtherModelRequiresExecutionAndDoesNotChangeWorkingModel() {
        val query = AssistantFamilyReferencePolicy.resolveQuery("ТЭМ2 компрессор", vl, null)!!
        assertEquals("tem2", query.profile.workingModelId.value)
        assertEquals("компрессор", query.searchText)
        assertTrue(AssistantFamilyReferencePolicy.search(listOf(tem), query, null).isEmpty())
        assertEquals(listOf(tem.id), AssistantFamilyReferencePolicy.search(
            listOf(tem), query, VariantId("tem2")).map { it.id })
        assertTrue(AssistantFamilyReferencePolicy.search(
            listOf(tem), query, VariantId("tem2u")).isEmpty())
        assertEquals("vl80s", vl.value)
    }

    @Test fun noUnspecifiedErmakOrCrossFamilyOrFaultExecution() {
        assertNull(AssistantFamilyReferencePolicy.resolveQuery("Ермак компрессор", vl, null))
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
}
