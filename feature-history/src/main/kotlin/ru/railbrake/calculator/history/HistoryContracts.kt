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
 * The pinned legacy StringSet format is verified by HistoryCodec tests.
 * AndroidHistoryStore reads the legacy source without modifying it and
 * writes versioned records to an independent preference file.
 */
object HistoryStorageMigrationGate {
    const val legacyFormatVerified: Boolean = true
    const val signedUpgradeVerified: Boolean = false
}
