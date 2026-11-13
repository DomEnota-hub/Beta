package ru.railbrake.calculator.navigation

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.CommonSection
import ru.railbrake.calculator.domain.ModelId

class ShellNavigationTest {
    @Test fun noImplicitWorkingLocomotive() {
        val state = ShellNavigationState()
        assertNull(state.workingModelId)
        assertEquals(ShellDestination.ChooseWorkingModel, state.destination)
        assertEquals(WorkingModelResolution.NotSelected, ShellNavigationPolicy.resolve(null))
        assertNull(ShellNavigationPolicy.enterWorkspace(state))
    }

    @Test fun onlyPublishedVl80sCanEnterExistingRuntime() {
        val state = ShellNavigationPolicy.select(ShellNavigationState(), ModelId("vl80s"))!!
        assertEquals(ShellDestination.ModelWorkspace(ModelId("vl80s")), state.destination)
        assertEquals(state, ShellNavigationPolicy.enterWorkspace(state))
        assertTrue((ShellNavigationPolicy.resolve("vl80s") as WorkingModelResolution.Selected).model.runtimePublished)
    }

    @Test fun everyOtherModelIsSelectableButNotPublished() {
        WorkingModelCatalog.models.filterNot { it.id.value == "vl80s" }.forEach { model ->
            val state = ShellNavigationPolicy.select(ShellNavigationState(), model.id)!!
            assertEquals(model.id, state.workingModelId)
            assertEquals(ShellDestination.ModelUnavailable(model.id), state.destination)
            assertNull(ShellNavigationPolicy.enterWorkspace(state))
            assertFalse(model.runtimePublished)
        }
    }

    @Test fun ermakAndDieselExecutionsRemainDistinct() {
        assertEquals(8, WorkingModelCatalog.models.size)
        assertEquals(8, WorkingModelCatalog.models.map { it.id }.distinct().size)
        assertTrue(WorkingModelCatalog.find(ModelId("2es5k")) != WorkingModelCatalog.find(ModelId("3es5k")))
        assertTrue(WorkingModelCatalog.find(ModelId("chme3t")) != WorkingModelCatalog.find(ModelId("chme3e")))
        assertTrue(WorkingModelCatalog.find(ModelId("tem2")) != WorkingModelCatalog.find(ModelId("tem2u")))
    }

    @Test fun unknownOrMalformedModelFailsClosed() {
        assertNull(ShellNavigationPolicy.select(ShellNavigationState(), ModelId("vl80sk")))
        assertNull(ShellNavigationPolicy.select(ShellNavigationState(), ModelId("VL80S")))
        assertTrue(ShellNavigationPolicy.resolve("vl80sk") is WorkingModelResolution.Unknown)
        assertTrue(ShellNavigationPolicy.resolve("") is WorkingModelResolution.Unknown)
    }

    @Test fun changingWorkingModelDoesNotCarryOldRoute() {
        val first = ShellNavigationPolicy.select(ShellNavigationState(), ModelId("vl80s"))!!
        val next = ShellNavigationPolicy.select(first, ModelId("chme3t"))!!
        assertEquals(ShellDestination.ModelUnavailable(ModelId("chme3t")), next.destination)
        assertNull(ShellNavigationPolicy.enterWorkspace(next))
        assertEquals(ShellNavigationState(), ShellNavigationPolicy.returnToModelSelection())
    }

    @Test fun commonContentDoesNotInventWorkingModel() {
        val state = ShellNavigationPolicy.openCommon(ShellNavigationState(), CommonSection.FIRST_AID)
        assertNull(state.workingModelId)
        assertEquals(ShellDestination.CommonContent(CommonSection.FIRST_AID), state.destination)
    }
}
