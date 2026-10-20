package ru.railbrake.calculator.atlas

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.CanonicalId

class AtlasCandidatePairTest {
    @Test
    fun overlappingAreasPickTheSmallerNodeAndUnknownVariantHasNoEquipmentLink() {
        val route = AtlasPairRoute(
            "sequence", "layout", "chme3-family", setOf("chme3t"), "Training",
            "Functional training view", listOf(
                AtlasPairNode("outer", "Outer", AtlasPairBounds(0f, 0f, 100f, 80f), null),
                AtlasPairNode("inner", "Inner", AtlasPairBounds(10f, 10f, 20f, 20f),
                    CanonicalId("chme3.catalog.chme3t-eq-edb-control")),
            ), listOf(AtlasPairStep("Step", "Explanation", setOf("inner"))),
        )
        assertEquals("inner", route.hitTest(15f, 15f)?.key)
        assertNull(route.equipmentTarget("inner", null))
        assertNull(route.equipmentTarget("inner", "chme3"))
        assertEquals("chme3.catalog.chme3t-eq-edb-control",
            route.equipmentTarget("inner", "chme3t")?.id?.value)
        assertNull(route.step(1))
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsMissingActiveLayoutNode() {
        AtlasPairRoute("sequence", "layout", "tem2-family", setOf("tem2"), "Training",
            "Functional training view",
            listOf(AtlasPairNode("one", "One", AtlasPairBounds(0f, 0f, 20f, 20f), null)),
            listOf(AtlasPairStep("Step", "Explanation", setOf("absent"))))
    }

    @Test
    fun candidateLoaderJoinsOnlyExactPair() {
        val sequence = """{
          "id":"tem2.sequences.example","publicationStatus":"CANDIDATE",
          "actionDisposition":"INFORMATION_ONLY","owner":{"modelId":"tem2-family"},
          "sourceObject":{"object":{"id":"TEM2-STEP","sourceSchemeRef":"TEM2-INT-SCH",
          "title":"Training",
          "functionalDisclaimer":"Functional view, not a physical route",
          "steps":[{"title":"Step","explanation":"Source explanation",
          "edges":[{"fromEquipmentId":"TEM2-EQ-COMP","toEquipmentId":"TEM2-EQ-MAIN-RES"}]}]}}
        }""".trimIndent()
        val layout = """{
          "id":"tem2.layouts.example","publicationStatus":"CANDIDATE",
          "actionDisposition":"INFORMATION_ONLY","owner":{"modelId":"tem2-family"},
          "sourceObject":{"object":{"sequenceId":"TEM2-STEP","nodes":[
          {"nodeKey":"TEM2-EQ-COMP","label":"Compressor","position":{"x":0,"y":0,"width":20,"height":20}},
          {"nodeKey":"TEM2-EQ-MAIN-RES","label":"Reservoir","position":{"x":30,"y":0,"width":20,"height":20}}]}}
        }""".trimIndent()
        val bindings = """{"publicationStatus":"CANDIDATE",
          "actionDisposition":"INFORMATION_ONLY","runtimeImport":false,"rows":[{
          "modelId":"tem2-family","variantIds":["tem2"],"sourceSequenceId":"TEM2-STEP",
          "sourceSchemeRef":"TEM2-INT-SCH",
          "sequenceEntryId":"tem2.sequences.example","layoutEntryId":"tem2.layouts.example",
          "nodeTargets":{"TEM2-EQ-COMP":"tem2.catalog.tem2-eq-comp",
          "TEM2-EQ-MAIN-RES":"tem2.catalog.tem2-eq-main-res"},
          "stepCount":1,"nodeCount":2}]}""".trimIndent()

        val route = AtlasCandidatePairLoader().parse(sequence, layout, bindings)
        assertEquals(setOf("TEM2-EQ-COMP", "TEM2-EQ-MAIN-RES"), route.step(0)?.activeNodeKeys)
        assertTrue(route.equipmentTarget("TEM2-EQ-COMP", "tem2") != null)
        assertNull(route.equipmentTarget("TEM2-EQ-COMP", "tem2u"))
    }
}
