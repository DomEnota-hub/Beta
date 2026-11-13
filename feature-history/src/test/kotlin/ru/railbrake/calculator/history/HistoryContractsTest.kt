package ru.railbrake.calculator.history

import org.junit.Assert.assertTrue
import org.junit.Assert.assertEquals
import org.junit.Test

class HistoryContractsTest {
    @Test
    fun recordMatchesExistingCalculationHistoryShape() {
        val record = HistoryRecord(
            timestampMillis = 1L,
            mode = "По массе",
            title = "4000 т",
            summary = "8 ТБ",
            details = "Расчёт",
        )

        assertEquals("По массе", record.mode)
    }

    @Test
    fun legacyStorageMustBeVerifiedBeforeReplacement() {
        assertTrue(HistoryStorageMigrationGate.legacyFormatVerified)
    }
}
