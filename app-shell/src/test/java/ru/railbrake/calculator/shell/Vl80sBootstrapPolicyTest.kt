package ru.railbrake.calculator.shell

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
    fun onlyExplicitPublishedVl80sTriggersRuntimeLoad() {
        assertTrue(Vl80sBootstrapPolicy.shouldLoad("vl80s"))
        listOf("2es5k", "3es5k", "chme3", "chme3t", "chme3e", "tem2", "tem2u")
            .forEach { id ->
                assertFalse("Reference-only model must not parse VL80S: $id",
                    Vl80sBootstrapPolicy.shouldLoad(id))
            }
    }
}
