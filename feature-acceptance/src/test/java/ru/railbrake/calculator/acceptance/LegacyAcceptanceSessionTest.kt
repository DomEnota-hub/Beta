package ru.railbrake.calculator.acceptance

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class LegacyAcceptanceSessionTest {
    private val id = "VL80-ROUTE-route_canonical"
    private val prefix = "session:VL80S:"
    private val valid = mapOf<String, Any>(
        prefix + "route_id" to id,
        prefix + "started_at" to 100L,
        prefix + "updated_at" to 200L,
    )

    @Test fun resumesOnlyAvailableExactRoute() {
        assertEquals(id, LegacyAcceptanceSession.resumeRouteId(valid, setOf(id)))
        assertNull(LegacyAcceptanceSession.resumeRouteId(valid, emptySet()))
        assertNull(LegacyAcceptanceSession.resumeRouteId(valid + (prefix + "route_id" to "route_canonical"), setOf("route_canonical")))
    }

    @Test fun rejectsCompletedMalformedAndOtherFamily() {
        assertNull(LegacyAcceptanceSession.resumeRouteId(valid + (prefix + "completed_at" to 200L), setOf(id)))
        assertNull(LegacyAcceptanceSession.resumeRouteId(valid + (prefix + "updated_at" to 99L), setOf(id)))
        assertNull(LegacyAcceptanceSession.resumeRouteId(valid + (prefix + "started_at" to "100"), setOf(id)))
        assertNull(LegacyAcceptanceSession.resumeRouteId(valid.mapKeys { it.key.replace("VL80S", "ERMAK") }, setOf(id)))
    }

    @Test fun betaSelectionWinsAndDismissalDoesNotResurrectLegacy() {
        val other = "VL80-ROUTE-required"
        val available = setOf(id, other)
        val handled = LegacyAcceptanceSession.handledKey
        val route = LegacyAcceptanceSession.currentRouteKey
        assertEquals(id, LegacyAcceptanceSession.currentResumeRouteId(emptyMap<String, Any>(), valid, available))
        assertEquals(other, LegacyAcceptanceSession.currentResumeRouteId(mapOf(handled to true, route to other), valid, available))
        assertNull(LegacyAcceptanceSession.currentResumeRouteId(mapOf(handled to true), valid, available))
        assertNull(LegacyAcceptanceSession.currentResumeRouteId(mapOf(handled to false, route to other), valid, available))
        assertNull(LegacyAcceptanceSession.currentResumeRouteId(mapOf(route to other), valid, available))
        assertNull(LegacyAcceptanceSession.currentResumeRouteId(mapOf(handled to true, route to "ER-ROUTE-required"), valid, available))
        assertNull(LegacyAcceptanceSession.currentResumeRouteId(mapOf(handled to true, route to other), valid, setOf(id)))
    }
}
