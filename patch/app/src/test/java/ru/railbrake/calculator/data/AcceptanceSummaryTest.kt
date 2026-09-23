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

    @Test
    fun reportContainsSessionSummaryAndNotes() {
        val report = acceptanceReportText(
            familyTitle = "ВЛ80С",
            routeTitle = "Обязательная приёмка",
            startedAt = "23.09.2026 10:00",
            updatedAt = "23.09.2026 10:15",
            summary = acceptanceSummary(
                listOf(AcceptanceCheckState.OK, AcceptanceCheckState.NOTE, AcceptanceCheckState.NOT_CHECKED)
            ),
            notes = listOf("Тормозное оборудование" to "Утечка воздуха")
        )

        assertTrue(report.contains("Приёмка: ВЛ80С"))
        assertTrue(report.contains("Режим: Обязательная приёмка"))
        assertTrue(report.contains("Не проверено: 1"))
        assertTrue(report.contains("Тормозное оборудование: Утечка воздуха"))
    }
}
