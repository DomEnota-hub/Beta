package ru.railbrake.calculator.acceptance

/** Legacy session is a navigation hint, never evidence of current completion. */
internal object LegacyAcceptanceSession {
    private const val prefix = "session:VL80S:"
    private val knownRoutes = setOf(
        "VL80-ROUTE-required", "VL80-ROUTE-route_canonical", "VL80-ROUTE-route_list",
        "VL80-ROUTE-route_from_outside", "VL80-ROUTE-route_from_cab",
        "VL80-ROUTE-route_running_gear", "VL80-ROUTE-route_machine_room",
        "VL80-ROUTE-route_functional",
    )

    fun resumeRouteId(legacy: Map<String, *>, availableIds: Set<String>): String? {
        val id = legacy[prefix + "route_id"] as? String ?: return null
        if (id !in knownRoutes || id !in availableIds) return null
        val started = legacy[prefix + "started_at"] as? Long ?: return null
        val updated = legacy[prefix + "updated_at"] as? Long ?: return null
        if (started <= 0L || updated < started) return null
        // Completed or malformed sessions are not offered as unfinished work.
        val completed = legacy[prefix + "completed_at"]
        if (completed != null && completed != 0L) return null
        return id
    }
}
