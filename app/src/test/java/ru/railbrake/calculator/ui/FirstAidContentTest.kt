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
        assertTrue(text.contains("судорожные вдохи"))
        assertTrue(text.contains("видимое"))
        assertTrue(text.contains("слепое"))
        assertTrue(text.contains("100–120"))
        assertTrue(text.contains("5–6 см"))
        assertTrue(text.contains("Не откладывайте СЛР"))
        assertTrue(text.contains("дефибриллятор"))
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
        val poisoning = firstAidTopics.single { it.id == "poisoning" && it.title == "Отравление" }
        val chemical = firstAidTopics.single { it.id == "chemical" && it.title == "Химическое поражение" }

        assertTrue(poisoning.actions.any { it.contains("не едким") })
        assertTrue(poisoning.dont.any { it.contains("неизвестного вещества") })
        assertTrue(chemical.actions.any { it.contains("не менее 20 минут") })
        assertTrue(firstAidTopics.all { it.source.contains("Минздрава России") && it.source.contains("2025") })
    }

    @Test
    fun auditedTopicsCoverOrder220nCriticalConditions() {
        val ids = firstAidTopics.map { it.id }.toSet()

        assertTrue("heat" in ids)
        assertTrue("nosebleed" in ids)
        assertTrue("chest_abdomen" in ids)
        assertTrue(firstAidTopics.single { it.id == "seizure" }.actions.any { it.contains("вызовите 112/103") })
        assertTrue(firstAidTopics.single { it.id == "bites" }.dont.any { it.contains("не отсасывайте") })
    }

    @Test
    fun bleedingKeepsOrder220nTourniquetRules() {
        val bleeding = firstAidTopics.single { it.id == "bleeding" }
        val text = (bleeding.actions + bleeding.dont).joinToString(" ")

        assertTrue(text.contains("5–7 см выше раны"))
        assertTrue(text.contains("не на сустав"))
        assertTrue(text.contains("точное время"))
        assertTrue(text.contains("не ослабляйте"))
    }

    @Test
    fun thermalBurnUsesVerifiedCoolingDuration() {
        val burn = firstAidTopics.single { it.id == "burn" }
        assertTrue(burn.actions.any { it.contains("не менее 20 минут") })
        assertTrue(burn.actions.any { it.contains("комнатной температуры") })
    }
}
