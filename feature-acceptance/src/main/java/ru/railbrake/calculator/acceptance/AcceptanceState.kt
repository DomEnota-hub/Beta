package ru.railbrake.calculator.acceptance

import android.content.Context
import ru.railbrake.calculator.domain.CanonicalId

enum class AcceptanceCheckState(val label: String) {
    NOT_CHECKED("Не проверено"),
    CHECKED("Проверено"),
    NOTE("Замечание"),
    NOT_APPLICABLE("Не применяется"),
}

data class AcceptanceItemState(
    val state: AcceptanceCheckState = AcceptanceCheckState.NOT_CHECKED,
    val note: String = "",
)

data class AcceptanceSummary(
    val total: Int,
    val checked: Int,
    val notes: Int,
    val notApplicable: Int,
    val notChecked: Int,
) {
    val complete: Boolean get() = total > 0 && notChecked == 0
}

fun acceptanceSummary(states: Collection<AcceptanceItemState>): AcceptanceSummary =
    AcceptanceSummary(
        total = states.size,
        checked = states.count { it.state == AcceptanceCheckState.CHECKED },
        notes = states.count { it.state == AcceptanceCheckState.NOTE },
        notApplicable = states.count { it.state == AcceptanceCheckState.NOT_APPLICABLE },
        notChecked = states.count { it.state == AcceptanceCheckState.NOT_CHECKED },
    )

interface AcceptanceStateStore {
    fun read(id: CanonicalId): AcceptanceItemState
    fun write(id: CanonicalId, value: AcceptanceItemState)
    fun clear(id: CanonicalId)
}

class SharedPreferencesAcceptanceStateStore(
    context: Context,
) : AcceptanceStateStore {
    private val preferences =
        context.getSharedPreferences("railbrake_acceptance_state_v1", Context.MODE_PRIVATE)

    private val legacy = context.getSharedPreferences("technical_acceptance_states", Context.MODE_PRIVATE)

    override fun read(id: CanonicalId): AcceptanceItemState = synchronized(storeLock) {
        migrateOnce(id)
        val state = (preferences.all[stateKey(id)] as? String)
            ?.let { runCatching { AcceptanceCheckState.valueOf(it) }.getOrNull() }
            ?: AcceptanceCheckState.NOT_CHECKED
        val note = (preferences.all[noteKey(id)] as? String).orEmpty()
        AcceptanceItemState(state = state, note = note)
    }

    override fun write(id: CanonicalId, value: AcceptanceItemState) = synchronized(storeLock) {
        preferences.edit().apply {
            putBoolean(migrationKey(id), true)
            putString(stateKey(id), value.state.name)
            if (value.note.isBlank()) remove(noteKey(id))
            else putString(noteKey(id), value.note.trim())
        }.apply()
    }

    override fun clear(id: CanonicalId) = synchronized(storeLock) {
        preferences.edit()
            .putBoolean(migrationKey(id), true)
            .remove(stateKey(id))
            .remove(noteKey(id))
            .apply()
    }

    private fun migrateOnce(id: CanonicalId) {
        val value = LegacyAcceptanceMigration.pending(id.value, preferences.all, legacy.all) ?: return
        preferences.edit()
            .putString(stateKey(id), value.state.name)
            .putString(noteKey(id), value.note)
            .putBoolean(migrationKey(id), true)
            .apply()
    }

    private companion object {
        // All store instances in this process share the same preferences.
        val storeLock = Any()
    }

    private fun migrationKey(id: CanonicalId) = "legacy_imported:${id.value}"
    private fun stateKey(id: CanonicalId) = "state:${id.value}"
    private fun noteKey(id: CanonicalId) = "note:${id.value}"
}

/** Exact identity crosswalk: pinned Test- VL80S acceptance asset, 66 matching
 * IDs, titles and check text in items.pack.json. Required-only Beta IDs excluded. */
internal object LegacyAcceptanceMigration {
    private val verifiedIds = setOf(
        "VL80-ACC-001",
        "VL80-ACC-002",
        "VL80-ACC-003",
        "VL80-ACC-004",
        "VL80-ACC-005",
        "VL80-ACC-006",
        "VL80-ACC-007",
        "VL80-ACC-008",
        "VL80-ACC-009",
        "VL80-ACC-010",
        "VL80-ACC-011",
        "VL80-ACC-012",
        "VL80-ACC-013",
        "VL80-ACC-014",
        "VL80-ACC-015",
        "VL80-ACC-016",
        "VL80-ACC-017",
        "VL80-ACC-018",
        "VL80-ACC-019",
        "VL80-ACC-020",
        "VL80-ACC-021",
        "VL80-ACC-022",
        "VL80-ACC-023",
        "VL80-ACC-024",
        "VL80-ACC-025",
        "VL80-ACC-026",
        "VL80-ACC-027",
        "VL80-ACC-028",
        "VL80-ACC-029",
        "VL80-ACC-030",
        "VL80-ACC-031",
        "VL80-ACC-032",
        "VL80-ACC-033",
        "VL80-ACC-034",
        "VL80-ACC-035",
        "VL80-ACC-036",
        "VL80-ACC-037",
        "VL80-ACC-038",
        "VL80-ACC-039",
        "VL80-ACC-040",
        "VL80-ACC-041",
        "VL80-ACC-042",
        "VL80-ACC-043",
        "VL80-ACC-044",
        "VL80-ACC-045",
        "VL80-ACC-046",
        "VL80-ACC-047",
        "VL80-ACC-048",
        "VL80-ACC-049",
        "VL80-ACC-050",
        "VL80-ACC-051",
        "VL80-ACC-052",
        "VL80-ACC-053",
        "VL80-ACC-054",
        "VL80-ACC-055",
        "VL80-ACC-056",
        "VL80-ACC-057",
        "VL80-ACC-058",
        "VL80-ACC-059",
        "VL80-ACC-060",
        "VL80-ACC-061",
        "VL80-ACC-062",
        "VL80-ACC-063",
        "VL80-ACC-064",
        "VL80-ACC-065",
        "VL80-ACC-066",
    )

    fun pending(id: String, current: Map<String, *>, legacy: Map<String, *>): AcceptanceItemState? {
        if (current.containsKey("legacy_imported:$id") ||
            current.containsKey("state:$id") || current.containsKey("note:$id")) return null
        return decode(id, legacy)
    }

    fun decode(id: String, legacy: Map<String, *>): AcceptanceItemState? {
        if (id !in verifiedIds) return null
        val rawState = legacy[id]
        val rawNote = legacy["note:$id"]
        if (rawState == null && rawNote == null) return null
        if (rawNote != null && rawNote !is String) return null
        val state = when (rawState) {
            null, "NOT_CHECKED" -> AcceptanceCheckState.NOT_CHECKED
            "OK" -> AcceptanceCheckState.CHECKED
            "NOTE", "BLOCKING" -> AcceptanceCheckState.NOTE
            "NOT_APPLICABLE" -> AcceptanceCheckState.NOT_APPLICABLE
            else -> return null
        }
        return AcceptanceItemState(state, (rawNote as? String).orEmpty())
    }
}
