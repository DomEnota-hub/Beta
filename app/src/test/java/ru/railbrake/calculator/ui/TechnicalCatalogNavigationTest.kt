package ru.railbrake.calculator.ui

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class TechnicalCatalogNavigationTest {
    @Test
    fun breadcrumbCanJumpToAnyKnownAncestor() {
        val path = technicalNavigationPush(
            technicalNavigationPush("", "equipment"),
            "system"
        )

        assertEquals("equipment" to "", technicalBreadcrumbSelection(path, "article", "equipment"))
        assertEquals("system" to "equipment", technicalBreadcrumbSelection(path, "article", "system"))
        assertEquals("article" to "equipment\nsystem", technicalBreadcrumbSelection(path, "article", "article"))
    }

    @Test
    fun breadcrumbIgnoresUnknownTarget() {
        assertNull(technicalBreadcrumbSelection("equipment", "article", "missing"))
    }
}
