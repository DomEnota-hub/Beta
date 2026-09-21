package ru.railbrake.calculator.ui

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ErmakCompactPresentationTest {
    @Test
    fun primary_and_safety_blocks_start_expanded() {
        assertTrue(ermakCompactBlockStartsExpanded("Назначение"))
        assertTrue(ermakCompactBlockStartsExpanded("Расположение"))
        assertTrue(ermakCompactBlockStartsExpanded("Кратко"))
        assertTrue(ermakCompactBlockStartsExpanded("Важно"))
        assertTrue(ermakCompactBlockStartsExpanded("Опасные признаки"))
        assertFalse(ermakCompactBlockStartsExpanded("Признаки неисправности"))
        assertFalse(ermakCompactBlockStartsExpanded("Связанные системы"))
    }

    @Test
    fun block_toggle_round_trips_without_duplicates() {
        val expanded = ermakToggleExpandedBlock("Назначение", "Неисправности")
        assertTrue("Назначение" in ermakExpandedBlockTitles(expanded))
        assertTrue("Неисправности" in ermakExpandedBlockTitles(expanded))

        val collapsed = ermakToggleExpandedBlock(expanded, "Неисправности")
        assertTrue("Назначение" in ermakExpandedBlockTitles(collapsed))
        assertFalse("Неисправности" in ermakExpandedBlockTitles(collapsed))
    }
}
