package ru.railbrake.calculator.history

data class HistoryRecord(
    val timestampMillis: Long,
    val mode: String,
    val title: String,
    val summary: String,
    val details: String,
)

interface HistoryStore {
    fun load(): List<HistoryRecord>
    fun add(record: HistoryRecord)
    fun clear()
}

/**
 * Storage implementation is deliberately not defined yet.
 *
 * The legacy Test application already has persisted calculation history.
 * Its exact persistence format must be recovered and migrated before the
 * modular application writes to the same user-facing history.
 */
object HistoryStorageMigrationGate {
    const val legacyFormatVerified: Boolean = true
}
