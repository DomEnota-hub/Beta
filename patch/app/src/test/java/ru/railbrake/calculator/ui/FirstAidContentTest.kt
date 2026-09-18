package ru.railbrake.calculator.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class FirstAidContentTest {
    @Test
    fun hypothermiaAndFrostbiteAreIndependentTopics() {
        val hypothermia = firstAidTopics.single { it.id == "hypothermia" }
        val frostbite = firstAidTopics.single { it.id == "frostbite" }

        assertEquals("Переохлаждение", hypothermia.title)
        assertEquals("Обморожение", frostbite.title)
        assertNotEquals(hypothermia.actions, frostbite.actions)
        assertNotEquals(hypothermia.dont, frostbite.dont)
        assertFalse(firstAidTopics.any { it.title.contains("Переохлаждение / обморожение") })
    }

    @Test
    fun coldInjuryTopicsKeepTheirCriticalSafetyRules() {
        val hypothermia = firstAidTopics.single { it.id == "hypothermia" }
        val frostbite = firstAidTopics.single { it.id == "frostbite" }

        assertTrue(hypothermia.actions.any { it.contains("112/103") })
        assertTrue(hypothermia.actions.any { it.contains("дыхани") })
        assertTrue(frostbite.dont.any { it.contains("Не растирайте") })
        assertTrue(frostbite.dont.any { it.contains("повторного замерзания") })
    }
}
