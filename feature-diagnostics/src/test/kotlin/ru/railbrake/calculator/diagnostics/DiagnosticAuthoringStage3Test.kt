package ru.railbrake.calculator.diagnostics

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/** Synthetic contract fixtures only. No railway actions or locomotive claims. */
class DiagnosticAuthoringStage3Test {
    private fun graph(endId: String): List<DiagnosticRouteNode> = listOf(
        DiagnosticRouteNode("start", mapOf(
            ExecutableDiagnosticResponse.YES to endId,
            ExecutableDiagnosticResponse.NO to DIAGNOSTIC_END_OF_FLOW,
            ExecutableDiagnosticResponse.UNKNOWN to DIAGNOSTIC_END_OF_FLOW,
        )),
        DiagnosticRouteNode(endId, emptyMap()),
    )

    private fun route(
        version: DiagnosticCardVersion,
        endId: String,
        evidence: List<DiagnosticEvidenceRoute> = emptyList(),
        gap: String? = "SOURCE_GAP: source and exact profile not verified",
    ) = DiagnosticCardRoute(version, "start", graph(endId), evidence, gap)

    private fun evidence(endId: String) = DiagnosticEvidenceRoute(
        sourceId = "SYNTHETIC-NON-OPERATIONAL-REFERENCE",
        scenarioId = "synthetic-scenario",
        exactProfileId = "synthetic-profile",
        startNodeId = "start",
        nodes = graph(endId),
    )

    @Test
    fun bothVersionsCanRemainUnboundWithoutInventedExtendedNodes() {
        val contract = DiagnosticModeContract(
            "synthetic-scenario", "synthetic-profile", listOf(
                route(DiagnosticCardVersion.SHORT, "short-end"),
                route(DiagnosticCardVersion.DETAILED, "detailed-end"),
            ),
        )
        val settings = DiagnosticPresentationSettings(
            knowledgeVolume = DiagnosticKnowledgeVolume.EXPANDED,
            extendedEnabled = true,
            warningAcknowledged = true,
        )
        val short = contract.select(DiagnosticCardVersion.SHORT, "synthetic-profile", settings)
        val detailed = contract.select(DiagnosticCardVersion.DETAILED, "synthetic-profile", settings)
        assertTrue(short.available)
        assertTrue(detailed.available)
        assertTrue(short.evidence.isEmpty())
        assertTrue(detailed.evidence.isEmpty())
        assertEquals("short-end", short.next("start", ExecutableDiagnosticResponse.YES))
        assertEquals("detailed-end", detailed.next("start", ExecutableDiagnosticResponse.YES))
        assertEquals(DIAGNOSTIC_END_OF_FLOW,
            short.next("start", ExecutableDiagnosticResponse.UNKNOWN))
    }

    @Test
    fun oneVersionMayHaveEvidenceWhileOtherRemainsSourceBlocked() {
        val contract = DiagnosticModeContract(
            "synthetic-scenario", "synthetic-profile", listOf(
                route(DiagnosticCardVersion.SHORT, "short-end",
                    listOf(evidence("short-evidence-end")), gap = null),
                route(DiagnosticCardVersion.DETAILED, "detailed-end"),
            ),
        )
        val settings = DiagnosticPresentationSettings(
            extendedEnabled = true, warningAcknowledged = true,
        )
        assertEquals(1, contract.select(DiagnosticCardVersion.SHORT,
            "synthetic-profile", settings).evidence.size)
        assertTrue(contract.select(DiagnosticCardVersion.DETAILED,
            "synthetic-profile", settings).evidence.isEmpty())
        assertFalse(contract.select(DiagnosticCardVersion.SHORT,
            "wrong-profile", settings).available)
        assertTrue(contract.select(DiagnosticCardVersion.SHORT,
            "wrong-profile", settings).evidence.isEmpty())
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesMainGraphCopiedBetweenVersions() {
        DiagnosticModeContract("synthetic-scenario", "synthetic-profile", listOf(
            route(DiagnosticCardVersion.SHORT, "same-end"),
            route(DiagnosticCardVersion.DETAILED, "same-end"),
        ))
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesAbsentEvidenceWithoutExplicitGap() {
        route(DiagnosticCardVersion.SHORT, "end", gap = null)
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesSimultaneousBoundEvidenceAndSourceGap() {
        route(DiagnosticCardVersion.SHORT, "end", listOf(evidence("ext-end")))
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesUnreachableAuthoringNode() {
        DiagnosticCardRoute(
            DiagnosticCardVersion.SHORT, "start",
            graph("end") + DiagnosticRouteNode("unreachable", emptyMap()),
            emptyList(), "SOURCE_GAP",
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesGraphWithNoReachableTerminal() {
        val loop = DiagnosticRouteNode("start", mapOf(
            ExecutableDiagnosticResponse.YES to "start",
            ExecutableDiagnosticResponse.NO to "start",
            ExecutableDiagnosticResponse.UNKNOWN to "start",
        ))
        DiagnosticCardRoute(
            DiagnosticCardVersion.SHORT, "start",
            listOf(loop), emptyList(), "SOURCE_GAP",
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesClosedCycleEvenWhenOtherBranchTerminates() {
        val start = DiagnosticRouteNode("start", mapOf(
            ExecutableDiagnosticResponse.YES to "loop",
            ExecutableDiagnosticResponse.NO to "end",
            ExecutableDiagnosticResponse.UNKNOWN to "end",
        ))
        val loop = DiagnosticRouteNode("loop", mapOf(
            ExecutableDiagnosticResponse.YES to "loop",
            ExecutableDiagnosticResponse.NO to "loop",
            ExecutableDiagnosticResponse.UNKNOWN to "loop",
        ))
        DiagnosticCardRoute(
            DiagnosticCardVersion.SHORT, "start",
            listOf(start, loop, DiagnosticRouteNode("end", emptyMap())),
            emptyList(), "SOURCE_GAP",
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesMissingUnknownBranch() {
        DiagnosticCardRoute(
            DiagnosticCardVersion.SHORT, "start",
            listOf(DiagnosticRouteNode("start", mapOf(
                ExecutableDiagnosticResponse.YES to DIAGNOSTIC_END_OF_FLOW,
                ExecutableDiagnosticResponse.NO to DIAGNOSTIC_END_OF_FLOW,
            ))),
            emptyList(), "SOURCE_GAP",
        )
    }

    @Test(expected = IllegalArgumentException::class)
    fun refusesExtendedEvidenceWithoutExit() {
        val loop = DiagnosticRouteNode("start", mapOf(
            ExecutableDiagnosticResponse.YES to "start",
            ExecutableDiagnosticResponse.NO to "start",
            ExecutableDiagnosticResponse.UNKNOWN to "start",
        ))
        DiagnosticEvidenceRoute(
            sourceId = "SYNTHETIC", scenarioId = "synthetic-scenario",
            exactProfileId = "synthetic-profile", startNodeId = "start",
            nodes = listOf(loop),
        )
    }
}
