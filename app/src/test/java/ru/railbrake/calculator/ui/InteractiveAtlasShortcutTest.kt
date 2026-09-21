package ru.railbrake.calculator.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.core.KnowledgeRepository
import ru.railbrake.calculator.core.TechnicalFamily
import ru.railbrake.calculator.core.TechnicalHotspot
import ru.railbrake.calculator.core.TechnicalSection

class InteractiveAtlasShortcutTest {
    @Test
    fun vl80TechnicalSectionsExposeLegacyInteractiveMaterials() {
        assertEquals("vl80-layout", interactiveLegacyShortcuts(TechnicalFamily.VL80S, TechnicalSection.EQUIPMENT).single().articleId)
        assertEquals("vl80-pneumatic-simulator", interactiveLegacyShortcuts(TechnicalFamily.VL80S, TechnicalSection.PNEUMATIC).single().articleId)
        assertEquals("vl80-electrical-simulator", interactiveLegacyShortcuts(TechnicalFamily.VL80S, TechnicalSection.ELECTRICAL).single().articleId)
        listOf(TechnicalSection.EQUIPMENT, TechnicalSection.PNEUMATIC, TechnicalSection.ELECTRICAL)
            .flatMap { interactiveLegacyShortcuts(TechnicalFamily.VL80S, it) }
            .forEach { shortcut ->
                assertTrue("Missing article ${shortcut.articleId}", KnowledgeRepository.articleById(shortcut.articleId) != null)
            }
    }

    @Test
    fun ermakDoesNotPointToVl80LegacyMaterials() {
        TechnicalSection.entries.forEach { section ->
            assertTrue(interactiveLegacyShortcuts(TechnicalFamily.ERMAK, section).isEmpty())
        }
    }

    @Test
    fun ermakAtlasExposesAllSupportedSectionVariants() {
        assertEquals(
            listOf(
                "ER-SCH-LAYOUT-2ES5K-BASE",
                "ER-SCH-LAYOUT-3ES5K-HEAD",
                "ER-SCH-LAYOUT-3ES5K-BOOSTER"
            ),
            ErmakAtlasVariants.map { it.first }
        )
        assertTrue(ErmakAtlasVariants.all { isErmakLayoutEntry(it.first) })
    }

    @Test
    fun ermakAtlasHitTestChoosesSmallestOverlappingZone() {
        val large = TechnicalHotspot("large", "Большая зона", 0, 0, 200, 120)
        val small = TechnicalHotspot("small", "Малая зона", 40, 30, 40, 30)

        assertEquals("small", ermakAtlasHitTest(listOf(large, small), 50f, 40f)?.equipmentId)
        assertEquals("large", ermakAtlasHitTest(listOf(large, small), 150f, 80f)?.equipmentId)
        assertEquals(null, ermakAtlasHitTest(listOf(large, small), 250f, 200f))
    }
}
