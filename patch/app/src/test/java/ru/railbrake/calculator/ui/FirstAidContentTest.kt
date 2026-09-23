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

    @Test
    fun cprMakesAirwayCheckExplicitWithoutDelayingCompressions() {
        val cpr = firstAidTopics.single { it.id == "cpr" }
        val text = (cpr.actions + cpr.dont).joinToString(" ")

        assertTrue(text.contains("маску"))
        assertTrue(text.contains("шарф"))
        assertTrue(text.contains("не более 10 секунд"))
        assertTrue(text.contains("видимое"))
        assertTrue(text.contains("слепое"))
        assertTrue(text.contains("100–120"))
        assertTrue(text.contains("5–6 см"))
        assertTrue(text.contains("Не откладывайте СЛР"))
    }

    @Test
    fun chokingCoversPregnancyObesityAndLossOfConsciousness() {
        val airway = firstAidTopics.single { it.id == "airway" }
        val text = (airway.actions + airway.dont).joinToString(" ")

        assertTrue(text.contains("Беременной"))
        assertTrue(text.contains("ожирением"))
        assertTrue(text.contains("грудной клетки"))
        assertTrue(text.contains("потере сознания"))
        assertTrue(text.contains("СЛР"))
    }

    @Test
    fun poisoningAndChemicalExposureAreSeparateSourcedTopics() {
        assertTrue(firstAidTopics.any { it.id == "poisoning" && it.title == "Отравление" })
        assertTrue(firstAidTopics.any { it.id == "chemical" && it.title == "Химическое поражение" })
        assertTrue(firstAidTopics.all { it.source.contains("Минздрава России") && it.source.contains("2025") })
    }
}
