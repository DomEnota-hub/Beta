package ru.railbrake.calculator.diagnostics

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.PublicationStatus

/** Pure state transitions used by the Compose warning. No emulator assumptions. */
class DiagnosticExtendedWarningConsentTest {
    @Test
    fun freshAndCheckboxOnlyCannotEnableHistoricalEvidence() {
        val initial = DiagnosticExtendedWarningConsent()
        assertFalse(initial.canEnableInformation)
        assertFalse(initial.acknowledge(true).canEnableInformation)
        assertFalse(initial.acknowledge(true).asPresentationSettings().extendedEnabled)
    }

    @Test
    fun drawingBeforeLayoutCannotClaimReadToEnd() {
        val state = DiagnosticExtendedWarningConsent()
        assertFalse(state.reachedViewportEnd(120, 120, false).readToEnd)
        assertFalse(state.reachedViewportEnd(0, 0, true).readToEnd)
        assertFalse(state.reachedViewportEnd(110, 120, true).readToEnd)
        assertFalse(state.reachedViewportEnd(-1, 120, true).readToEnd)
        assertFalse(state.reachedViewportEnd(50, -1, true).readToEnd)
    }

    @Test
    fun readingEndAloneCannotEnableHistoricalEvidence() {
        val read = DiagnosticExtendedWarningConsent()
            .reachedViewportEnd(120, 120, true)
        assertTrue(read.readToEnd)
        assertFalse(read.acknowledged)
        assertFalse(read.asPresentationSettings().extendedEnabled)
        assertFalse(read.asPresentationSettings().warningAcknowledged)
    }

    @Test
    fun actualEndAndExplicitAcknowledgmentAreBothRequired() {
        val read = DiagnosticExtendedWarningConsent()
            .reachedViewportEnd(121, 120, true)
        val accepted = read.acknowledge(true)
        assertTrue(accepted.canEnableInformation)
        assertTrue(accepted.asPresentationSettings().extendedEnabled)
        assertTrue(accepted.asPresentationSettings().warningReadToEnd)
        assertTrue(accepted.asPresentationSettings().warningAcknowledged)
        assertFalse(accepted.acknowledge(false).canEnableInformation)
    }

    @Test
    fun freshDialogSessionNeverKeepsPreviousConsent() {
        val old = DiagnosticExtendedWarningConsent()
            .reachedViewportEnd(200, 200, true).acknowledge(true)
        assertTrue(old.canEnableInformation)
        val newSession = DiagnosticExtendedWarningConsent()
        assertFalse(newSession.canEnableInformation)
        assertFalse(newSession.readToEnd)
        assertFalse(newSession.acknowledged)
    }

    @Test
    fun explicitlyConsentingStillCannotApproveAnUnverifiedRepair() {
        val accepted = DiagnosticExtendedWarningConsent()
            .reachedViewportEnd(200, 200, true).acknowledge(true)
        assertTrue(accepted.asPresentationSettings().extendedEnabled)

        val input = DiagnosticActionInputs(
            publicationStatus = PublicationStatus.CANDIDATE,
            actionDisposition = ActionDisposition.INFORMATION_ONLY,
            runtimeAvailability = DiagnosticRuntimeAvailability.EXECUTABLE_FLOW_AVAILABLE,
            sourceAuthorityVerified = false,
            exactProfileConfirmed = false,
            installedEquipmentConfirmed = false,
        )
        assertFalse(DiagnosticActionGate.permits(input))
    }

    @Test
    fun earlierScrollWithoutReachingEndDoesNotAuthorizeConfirmation() {
        val prior = DiagnosticExtendedWarningConsent()
            .reachedViewportEnd(50, 200, true)
            .acknowledge(true)
        assertEquals(DiagnosticExtendedWarningConsent(), prior)
    }
}
