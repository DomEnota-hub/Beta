package ru.railbrake.calculator.acceptance

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AcceptanceStateTest {
    @Test
    fun summaryKeepsFourUserFacingStatesSeparate() {
        val summary = acceptanceSummary(
            listOf(
                AcceptanceItemState(AcceptanceCheckState.CHECKED),
                AcceptanceItemState(AcceptanceCheckState.NOTE, "Осмотр"),
                AcceptanceItemState(AcceptanceCheckState.NOT_APPLICABLE),
                AcceptanceItemState(AcceptanceCheckState.NOT_CHECKED),
            )
        )

        assertEquals(4, summary.total)
        assertEquals(1, summary.checked)
        assertEquals(1, summary.notes)
        assertEquals(1, summary.notApplicable)
        assertEquals(1, summary.notChecked)
        assertFalse(summary.complete)
    }

    @Test
    fun completedSingleItemIsComplete() {
        assertTrue(
            acceptanceSummary(
                listOf(AcceptanceItemState(AcceptanceCheckState.CHECKED))
            ).complete
        )
    }

    @Test
    fun legacyExactIdsAndBlockingNoteArePreserved() {
        val id = "VL80-ACC-001"
        assertEquals(AcceptanceItemState(AcceptanceCheckState.NOTE, "секция 2"),
            LegacyAcceptanceMigration.decode(id, mapOf(id to "BLOCKING", "note:$id" to "секция 2")))
        assertEquals(AcceptanceCheckState.CHECKED,
            LegacyAcceptanceMigration.decode(id, mapOf(id to "OK"))?.state)
        assertEquals(AcceptanceCheckState.NOT_APPLICABLE,
            LegacyAcceptanceMigration.decode(id, mapOf(id to "NOT_APPLICABLE"))?.state)
    }

    @Test
    fun legacyUnknownIdsAndMalformedValuesAreNotImported() {
        val id = "VL80-ACC-001"
        assertEquals(null, LegacyAcceptanceMigration.decode("VL80-ACC-067", mapOf("VL80-ACC-067" to "OK")))
        assertEquals(null, LegacyAcceptanceMigration.decode("CHME3-ACC-001", mapOf("CHME3-ACC-001" to "OK")))
        assertEquals(null, LegacyAcceptanceMigration.decode(id, mapOf(id to 1)))
        assertEquals(null, LegacyAcceptanceMigration.decode(id, mapOf(id to "OK", "note:$id" to 1)))
        assertEquals(null, LegacyAcceptanceMigration.decode(id, mapOf(id to "UNKNOWN")))
        assertEquals(null, LegacyAcceptanceMigration.decode(id, emptyMap<String, Any>()))
    }

    @Test
    fun noteWithoutMarkDoesNotInventCompletedCheck() {
        val id = "VL80-ACC-066"
        assertEquals(AcceptanceItemState(AcceptanceCheckState.NOT_CHECKED, "замечание"),
            LegacyAcceptanceMigration.decode(id, mapOf("note:$id" to "замечание")))
    }
    @Test
    fun existingBetaValuesAndClearMarkerPreventLegacyImport() {
        val id = "VL80-ACC-001"
        val legacy = mapOf(id to "OK", "note:$id" to "old")
        assertEquals(AcceptanceCheckState.CHECKED,
            LegacyAcceptanceMigration.pending(id, emptyMap<String, Any>(), legacy)?.state)
        for (current in listOf(
            mapOf("state:$id" to "NOTE"),
            mapOf("note:$id" to "new"),
            mapOf("state:$id" to 42),
            mapOf("legacy_imported:$id" to true),
        )) {
            assertEquals(null, LegacyAcceptanceMigration.pending(id, current, legacy))
        }
        assertEquals("old", legacy["note:$id"])
    }

    @Test
    fun clearMarkerForOneItemDoesNotSuppressAnother() {
        val id = "VL80-ACC-002"
        assertEquals(AcceptanceCheckState.CHECKED,
            LegacyAcceptanceMigration.pending(id, mapOf("legacy_imported:VL80-ACC-001" to true),
                mapOf(id to "OK"))?.state)
    }
}
