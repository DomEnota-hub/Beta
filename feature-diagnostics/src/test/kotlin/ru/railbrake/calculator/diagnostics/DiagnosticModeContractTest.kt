package ru.railbrake.calculator.diagnostics

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.PublicationStatus

class DiagnosticModeContractTest {
    private fun extension(end: String) = DiagnosticEvidenceRoute(
        sourceId = "EXT2-CHME3-DIAG-001",
        scenarioId = "CHME3-DIAG-001",
        exactProfileId = "chme3-base",
        startNodeId = "extended-start",
        nodes = listOf(
            DiagnosticRouteNode("extended-start", mapOf(
                ExecutableDiagnosticResponse.YES to end,
                ExecutableDiagnosticResponse.NO to DIAGNOSTIC_END_OF_FLOW,
                ExecutableDiagnosticResponse.UNKNOWN to DIAGNOSTIC_END_OF_FLOW,
            )),
            DiagnosticRouteNode(end, emptyMap()),
        ),
    )

    private fun route(
        version: DiagnosticCardVersion,
        next: String,
        extended: List<DiagnosticEvidenceRoute> = listOf(extension("extended-$next")),
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
                    extension("short-extended-end"),
                )),
                route(DiagnosticCardVersion.DETAILED, "detailed-end", listOf(
                    extension("detailed-extended-end"),
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
        assertEquals("short-extended-end", short.nextExtended("EXT2-CHME3-DIAG-001",
            "extended-start", ExecutableDiagnosticResponse.YES))
        assertEquals("detailed-extended-end", detailed.nextExtended("EXT2-CHME3-DIAG-001",
            "extended-start", ExecutableDiagnosticResponse.YES))
        assertFalse(short.evidence.first().executable)
        assertEquals(DiagnosticKnowledgeVolume.EXPANDED, short.knowledgeVolume)
        assertEquals(DiagnosticDisplayDepth.DETAILED, short.displayDepth)
    }

    @Test
    fun evidenceRequiresWarningAndExactProfile() {
        val scenario = DiagnosticModeContract("CHME3-DIAG-001", "chme3-base", listOf(
            route(DiagnosticCardVersion.SHORT, "short-end", listOf(
                extension("short-extended-end"),
            )),
            route(DiagnosticCardVersion.DETAILED, "long-end"),
        ))
        val enabledWithoutWarning = DiagnosticPresentationSettings(extendedEnabled = true)
        assertTrue(scenario.select(DiagnosticCardVersion.SHORT, "chme3-base", enabledWithoutWarning).evidence.isEmpty())
        assertEquals(null, scenario.select(DiagnosticCardVersion.SHORT, "chme3-base", enabledWithoutWarning)
            .nextExtended("EXT2-CHME3-DIAG-001", "extended-start", ExecutableDiagnosticResponse.YES))
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
        extension("end").copy(executable = true)
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesAbsentExtendedBranch() {
        route(DiagnosticCardVersion.SHORT, "short-end", emptyList())
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesSharedExtendedGraphAcrossVersions() {
        DiagnosticModeContract("CHME3-DIAG-001", "chme3-base", listOf(
            route(DiagnosticCardVersion.SHORT, "short-end", listOf(extension("same-end"))),
            route(DiagnosticCardVersion.DETAILED, "detailed-end", listOf(extension("same-end"))),
        ))
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesBranchFromAnotherScenario() {
        DiagnosticModeContract("CHME3-DIAG-002", "chme3-base", listOf(
            route(DiagnosticCardVersion.SHORT, "short-end"),
            route(DiagnosticCardVersion.DETAILED, "detailed-end"),
        ))
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
    @Test
    fun distinctApproachesFromOneHistoricalSourceRemainSelectableOnlyAfterWarning() {
        val first = extension("archive-air-end").copy(
            sourceId = "historical-book",
            approachId = "pneumatic-interpretation",
            origin = DiagnosticEvidenceOrigin.HISTORICAL_PUBLICATION,
            sourceLabel = "Историческое пособие, раздел А",
            applicabilityCaveat = "Точная секция не установлена",
        )
        val second = extension("archive-command-end").copy(
            sourceId = "historical-book",
            approachId = "control-chain-interpretation",
            origin = DiagnosticEvidenceOrigin.HISTORICAL_PUBLICATION,
            sourceLabel = "Историческое пособие, раздел Б",
            applicabilityCaveat = "Комплектация аппаратов требует сверки",
        )
        val scenario = DiagnosticModeContract("CHME3-DIAG-001", "chme3-base", listOf(
            route(DiagnosticCardVersion.SHORT, "short-end", listOf(first, second)),
            route(DiagnosticCardVersion.DETAILED, "detailed-end", listOf(
                extension("different-detailed-end"),
            )),
        ))
        val disabled = scenario.select(DiagnosticCardVersion.SHORT, "chme3-base",
            DiagnosticPresentationSettings(extendedEnabled = true, warningAcknowledged = false))
        assertTrue(disabled.evidence.isEmpty())
        val enabled = scenario.select(DiagnosticCardVersion.SHORT, "chme3-base",
            DiagnosticPresentationSettings(extendedEnabled = true, warningAcknowledged = true))
        assertEquals(listOf("pneumatic-interpretation", "control-chain-interpretation"),
            enabled.evidence.map { it.approachId })
        assertEquals(listOf("historical-book", "historical-book"), enabled.evidence.map { it.sourceId })
        assertEquals("archive-air-end", enabled.nextExtended("pneumatic-interpretation",
            "extended-start", ExecutableDiagnosticResponse.YES))
        assertEquals("archive-command-end", enabled.nextExtended("control-chain-interpretation",
            "extended-start", ExecutableDiagnosticResponse.YES))
        assertEquals(null, enabled.nextExtended("historical-book",
            "extended-start", ExecutableDiagnosticResponse.YES))
        assertFalse(first.executable)
        assertFalse(second.executable)
        assertTrue(scenario.select(DiagnosticCardVersion.SHORT, "another-model",
            DiagnosticPresentationSettings(extendedEnabled = true, warningAcknowledged = true))
            .evidence.isEmpty())
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsDuplicateApproachEvenWhenSourceIsShared() {
        DiagnosticCardRoute(DiagnosticCardVersion.SHORT, "start",
            route(DiagnosticCardVersion.SHORT, "end").nodes,
            listOf(extension("a").copy(sourceId = "book", approachId = "same"),
                   extension("b").copy(sourceId = "book", approachId = "same")))
    }

    @Test(expected = IllegalArgumentException::class)
    fun historicalBranchCannotBecomeConditionalAction() {
        extension("end").copy(actionDisposition = ActionDisposition.CONDITIONAL_ACTION)
    }

    @Test
    fun acknowledgedWarningStillDoesNotGrantAuthority() {
        val inputs = DiagnosticActionInputs(
            publicationStatus = PublicationStatus.CANDIDATE,
            actionDisposition = ActionDisposition.INFORMATION_ONLY,
            runtimeAvailability = DiagnosticRuntimeAvailability.EXECUTABLE_FLOW_AVAILABLE,
            exactProfileConfirmed = true,
            sourceAuthorityVerified = false,
            installedEquipmentConfirmed = true,
        )
        assertFalse(DiagnosticActionGate.permits(inputs))
    }
}
