package ru.railbrake.calculator.data

import org.junit.Assert.assertEquals
import org.junit.Test

class TechnicalRecentRepositoryTest {
    @Test
    fun openedMaterialMovesToFrontWithoutDuplicates() {
        assertEquals(
            listOf("B", "A", "C"),
            updateRecentTechnicalIds(listOf("A", "B", "C"), "B")
        )
    }

    @Test
    fun recentMaterialsKeepBoundedStableHistory() {
        assertEquals(
            listOf("N", "A", "B"),
            updateRecentTechnicalIds(listOf("A", "B", "C", "D"), "N", limit = 3)
        )
    }

    @Test
    fun blankIdsNeverEnterHistory() {
        assertEquals(
            listOf("A", "B"),
            updateRecentTechnicalIds(listOf("A", "", "A", "B"), " ")
        )
    }
}
