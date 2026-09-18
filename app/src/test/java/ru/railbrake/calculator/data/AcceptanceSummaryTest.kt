package ru.railbrake.calculator.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AcceptanceSummaryTest {
    @Test
    fun incompleteChecklistReportsRemainingItems() {
        val summary = acceptanceSummary(listOf(AcceptanceCheckState.OK, AcceptanceCheckState.NOT_CHECKED))
        assertFalse(summary.complete)
        assertEquals(1, summary.notChecked)
        assertEquals("Проверка не завершена", summary.result)
    }

    @Test
    fun completedChecklistKeepsNotesVisible() {
        val summary = acceptanceSummary(listOf(AcceptanceCheckState.OK, AcceptanceCheckState.NOTE, AcceptanceCheckState.NOT_APPLICABLE))
        assertTrue(summary.complete)
        assertEquals(1, summary.notes)
        assertEquals("Проверка завершена: есть замечания", summary.result)
    }

    @Test
    fun cleanChecklistProducesCleanResult() {
        val summary = acceptanceSummary(listOf(AcceptanceCheckState.OK, AcceptanceCheckState.OK))
        assertEquals("Проверка завершена: замечаний нет", summary.result)
    }
}
