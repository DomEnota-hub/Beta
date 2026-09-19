package ru.railbrake.calculator.ui

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.data.matchesLocalFeatureSignature

class DeveloperEasterEggTest {
    @Test
    fun exactDeveloperCombinationTriggersEasterEgg() {
        assertTrue(isDeveloperEasterEgg(massTons = 2381.0, axleCount = 999))
    }

    @Test
    fun anyDifferentValueDoesNotTriggerEasterEgg() {
        assertFalse(isDeveloperEasterEgg(massTons = 2381.001, axleCount = 999))
        assertFalse(isDeveloperEasterEgg(massTons = 2381.0, axleCount = 998))
        assertFalse(isDeveloperEasterEgg(massTons = 2381.0, axleCount = null))
    }

    @Test
    fun localFeatureSignatureIsSeparateAndExact() {
        assertTrue(matchesLocalFeatureSignature(massTons = 1000.0, axleCount = 2381))
        assertFalse(matchesLocalFeatureSignature(massTons = 2381.0, axleCount = 999))
        assertFalse(matchesLocalFeatureSignature(massTons = 1000.0, axleCount = 2380))
        assertFalse(matchesLocalFeatureSignature(massTons = 999.9, axleCount = 2381))
        assertFalse(matchesLocalFeatureSignature(massTons = Double.NaN, axleCount = 2381))
        assertFalse(matchesLocalFeatureSignature(massTons = 1000.0, axleCount = null))
    }
}
