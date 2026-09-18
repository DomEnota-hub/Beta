package ru.railbrake.calculator.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.core.KnowledgeRepository
import ru.railbrake.calculator.core.TechnicalFamily
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
}
