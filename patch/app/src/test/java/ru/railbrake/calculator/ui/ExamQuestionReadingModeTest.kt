package ru.railbrake.calculator.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ExamQuestionReadingModeTest {
    @Test
    fun emptySearchAndFiltersDoNotCreateMisleadingIndicator() {
        assertNull(examActiveFilterLabel("   ", null, null))
    }

    @Test
    fun readingModeIndicatorKeepsEveryActiveFilter() {
        val label = examActiveFilterLabel(
            query = "тормозная магистраль",
            block = "Блок 2",
            category = "Тормоза"
        )

        assertEquals("поиск: «тормозная магистраль» • Блок 2 • Тормоза", label)
    }

    @Test
    fun longQueryIsShortenedOnlyInCompactIndicator() {
        val label = examActiveFilterLabel(
            query = "очень длинный поисковый запрос который не должен растянуть панель",
            block = null,
            category = null
        )

        assertTrue(label.orEmpty().endsWith("…»"))
        assertTrue(label.orEmpty().length < 40)
    }
}
