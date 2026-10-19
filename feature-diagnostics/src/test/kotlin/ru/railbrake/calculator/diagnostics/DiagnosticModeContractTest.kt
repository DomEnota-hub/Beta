package ru.railbrake.calculator.diagnostics

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.PublicationStatus

class DiagnosticModeContractTest {
    private fun route(
        version: DiagnosticCardVersion,
        next: String,
        extended: List<DiagnosticEvidenceRoute> = emptyList(),
    ) = DiagnosticCardRoute(
        version = version,
        startNodeId = "start",
        nodes = listOf(
            DiagnosticRouteNode("start", mapOf(
                ExecutableDiagnosticResponse.YES to next,
                ExecutableDiagnosticResponse.NO to DIAGNOSTIC_END_OF_FLOW,
                ExecutableDiagnosticResponse.UNKNOWN to DIAGNOSTIC_END_OF_FLOW,
            )),
            DiagnosticRouteNode(next, emptyMap()),
        ),
        extendedRoutes = extended,
    )

    @Test
    fun eachCardVersionHasItsOwnRouteAndExtendedBranches() {
        val scenario = DiagnosticModeContract(
            scenarioId = "CHME3-DIAG-001",
            exactProfileId = "chme3-base",
            routes = listOf(
                route(DiagnosticCardVersion.SHORT, "short-end", listOf(
                    DiagnosticEvidenceRoute("EXT2-CHME3-DIAG-001", "chme3-base", false),
                )),
                route(DiagnosticCardVersion.DETAILED, "detailed-end", listOf(
                    DiagnosticEvidenceRoute("EXT2-CHME3-DIAG-001", "chme3-base", false),
                )),
            ),
        )
        val settings = DiagnosticPresentationSettings(
            knowledgeVolume = DiagnosticKnowledgeVolume.EXPANDED,
            displayDepth = DiagnosticDisplayDepth.DETAILED,
            extendedEnabled = true,
            warningAcknowledged = true,
        )

        val short = scenario.select(DiagnosticCardVersion.SHORT, "chme3-base", settings)
        val detailed = scenario.select(DiagnosticCardVersion.DETAILED, "chme3-base", settings)
        assertEquals("short-end", short.next("start", ExecutableDiagnosticResponse.YES))
        assertEquals("detailed-end", detailed.next("start", ExecutableDiagnosticResponse.YES))
        assertEquals(listOf("EXT2-CHME3-DIAG-001"), short.evidence.map { it.sourceId })
        assertEquals(listOf("EXT2-CHME3-DIAG-001"), detailed.evidence.map { it.sourceId })
        assertFalse(short.evidence.first().executable)
        assertEquals(DiagnosticKnowledgeVolume.EXPANDED, short.knowledgeVolume)
        assertEquals(DiagnosticDisplayDepth.DETAILED, short.displayDepth)
    }

    @Test
    fun evidenceRequiresWarningAndExactProfile() {
        val scenario = DiagnosticModeContract("CHME3-DIAG-001", "chme3-base", listOf(
            route(DiagnosticCardVersion.SHORT, "short-end", listOf(
                DiagnosticEvidenceRoute("EXT2-CHME3-DIAG-001", "chme3-base", false),
            )),
            route(DiagnosticCardVersion.DETAILED, "long-end"),
        ))
        val enabledWithoutWarning = DiagnosticPresentationSettings(extendedEnabled = true)
        assertTrue(scenario.select(DiagnosticCardVersion.SHORT, "chme3-base", enabledWithoutWarning).evidence.isEmpty())
        assertTrue(scenario.select(DiagnosticCardVersion.SHORT, "chme3t",
            enabledWithoutWarning.copy(warningAcknowledged = true)).evidence.isEmpty())
        assertEquals(listOf("EXT2-CHME3-DIAG-001"), scenario.select(DiagnosticCardVersion.SHORT, "chme3-base",
            enabledWithoutWarning.copy(warningAcknowledged = true)).evidence.map { it.sourceId })
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesMissingDetailedRoute() {
        DiagnosticModeContract("CHME3-DIAG-001", "chme3", listOf(
            route(DiagnosticCardVersion.SHORT, "short-end"),
        ))
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesExecutableHistoricalEvidence() {
        DiagnosticEvidenceRoute("archived", "chme3", true)
    }

    @Test
    fun showingEvidenceDoesNotGrantOperationalAction() {
        val candidate = DiagnosticActionInputs(
            publicationStatus = PublicationStatus.CANDIDATE,
            actionDisposition = ActionDisposition.INFORMATION_ONLY,
            runtimeAvailability = DiagnosticRuntimeAvailability.EXECUTABLE_FLOW_AVAILABLE,
            sourceAuthorityVerified = false,
            exactProfileConfirmed = true,
            installedEquipmentConfirmed = true,
        )
        assertFalse(DiagnosticActionGate.permits(candidate))
        assertFalse(DiagnosticActionGate.permits(candidate.copy(
            publicationStatus = PublicationStatus.ACTIVE,
            actionDisposition = ActionDisposition.PROHIBITED,
            sourceAuthorityVerified = true,
        )))
        assertFalse(DiagnosticActionGate.permits(candidate.copy(
            publicationStatus = PublicationStatus.ACTIVE,
            actionDisposition = ActionDisposition.CONDITIONAL_ACTION,
            sourceAuthorityVerified = true,
            installedEquipmentConfirmed = false,
        )))
        assertTrue(DiagnosticActionGate.permits(candidate.copy(
            publicationStatus = PublicationStatus.ACTIVE,
            actionDisposition = ActionDisposition.CONDITIONAL_ACTION,
            sourceAuthorityVerified = true,
        )))
    }
}
