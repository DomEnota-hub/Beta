package ru.railbrake.calculator.shell

import ru.railbrake.calculator.navigation.ShellHomeDestination
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class Vl80sBootstrapPolicyTest {
    @Test
    fun modelPickerAndUnknownModelNeverTriggerRuntimeLoad() {
        assertFalse(Vl80sBootstrapPolicy.shouldLoad(null))
        assertFalse(Vl80sBootstrapPolicy.shouldLoad(""))
        assertFalse(Vl80sBootstrapPolicy.shouldLoad("VL80S"))
        assertFalse(Vl80sBootstrapPolicy.shouldLoad("unknown"))
    }

    @Test
    fun homeAndIndependentSectionsNeverRequestExpensiveVl80sRuntime() {
        listOf(
            ShellHomeDestination.HOME,
            ShellHomeDestination.CALCULATIONS,
            ShellHomeDestination.RECORDS,
            ShellHomeDestination.KNOWLEDGE,
            ShellHomeDestination.TRAFFIC_SAFETY,
            ShellHomeDestination.OCCUPATIONAL_SAFETY,
            ShellHomeDestination.FIRST_AID,
            ShellHomeDestination.SETTINGS,
            ShellHomeDestination.APPEARANCE,
            ShellHomeDestination.ABOUT,
        ).forEach { destination ->
            assertFalse("VL80S must not bootstrap in $destination",
                Vl80sBootstrapPolicy.shouldRequest("vl80s", destination))
        }
    }

    @Test
    fun onlyPublishedVl80sFeatureDestinationsRequestRuntime() {
        listOf(
            ShellHomeDestination.ASSISTANT,
            ShellHomeDestination.ATLAS,
            ShellHomeDestination.DIAGNOSTICS,
            ShellHomeDestination.ACCEPTANCE,
        ).forEach { destination ->
            assertTrue("VL80S must load for $destination",
                Vl80sBootstrapPolicy.shouldRequest("vl80s", destination))
            assertFalse("Unknown profile must not load for $destination",
                Vl80sBootstrapPolicy.shouldRequest("VL80S", destination))
            assertFalse("No model must not load for $destination",
                Vl80sBootstrapPolicy.shouldRequest(null, destination))
            listOf("2es5k", "3es5k", "chme3", "chme3t", "chme3e", "tem2", "tem2u")
                .forEach { other ->
                    assertFalse("Foreign model $other must not load VL80S in $destination",
                        Vl80sBootstrapPolicy.shouldRequest(other, destination))
                }
        }
    }

    @Test
    fun explicitAssistantQueryLoadsPublishedReferenceWithoutChangingWorkingModel() {
        val assistant = ShellHomeDestination.ASSISTANT
        assertTrue(Vl80sBootstrapPolicy.shouldRequest("tem2", assistant, "ВЛ80С главника"))
        assertTrue(Vl80sBootstrapPolicy.shouldRequest("chme3", assistant, "в эл 80 с главника"))
        listOf("главника", "ВЛ80 главника", "ВЛ80С ТЭМ2 главника",
            "ВЛ80С Ермак главника", "ВЛ80С").forEach { query ->
            assertFalse(query, Vl80sBootstrapPolicy.shouldRequest("tem2", assistant, query))
        }
        assertFalse(Vl80sBootstrapPolicy.shouldRequest(null, assistant, "ВЛ80С главника"))
        assertFalse(Vl80sBootstrapPolicy.shouldRequest("unknown", assistant, "ВЛ80С главника"))
        assertFalse(Vl80sBootstrapPolicy.shouldRequest("tem2", ShellHomeDestination.ATLAS, "ВЛ80С главника"))
    }

    @Test
    fun onlyExplicitPublishedVl80sTriggersRuntimeLoad() {
        assertTrue(Vl80sBootstrapPolicy.shouldLoad("vl80s"))
        listOf("2es5k", "3es5k", "chme3", "chme3t", "chme3e", "tem2", "tem2u")
            .forEach { id ->
                assertFalse("Reference-only model must not parse VL80S: $id",
                    Vl80sBootstrapPolicy.shouldLoad(id))
            }
    }
}
