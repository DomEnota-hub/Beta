package ru.railbrake.calculator.history

import java.util.Base64

/**
 * Codec for the five-field records in the pinned legacy SharedPreferences StringSet.
 *
 * This code reads and encodes individual values only. It never changes the
 * "calculation_history"/"records" preference or opens the storage migration gate.
 */
object LegacyHistoryCodec {
    private val encoder = Base64.getUrlEncoder()
    private val decoder = Base64.getUrlDecoder()

    fun encode(record: HistoryRecord): String = listOf(
        record.timestampMillis.toString(),
        encodeText(record.mode),
        encodeText(record.title),
        encodeText(record.summary),
        encodeText(record.details),
    ).joinToString("|")

    fun decode(raw: String): HistoryRecord? {
        val parts = raw.split('|')
        if (parts.size != 5) return null
        return runCatching {
            HistoryRecord(
                timestampMillis = parts[0].toLong(),
                mode = decodeText(parts[1]),
                title = decodeText(parts[2]),
                summary = decodeText(parts[3]),
                details = decodeText(parts[4]),
            )
        }.getOrNull()
    }

    fun inspect(rawRecords: Set<String>): LegacyHistoryInspection {
        val parsed = rawRecords.map { raw -> raw to decode(raw) }
        val valid = parsed.mapNotNull { (raw, record) ->
            record?.let { raw to it }
        }.sortedWith(
            compareByDescending<Pair<String, HistoryRecord>> { it.second.timestampMillis }
                .thenBy { it.first }
        ).map { it.second }
        return LegacyHistoryInspection(
            rawRecords = rawRecords.toSet(),
            validRecords = valid,
            invalidRawRecords = parsed.filter { it.second == null }.map { it.first }.toSet(),
            timestampCollisions = valid.groupBy { it.timestampMillis }.filterValues { it.size > 1 },
        )
    }

    private fun encodeText(text: String): String =
        encoder.encodeToString(text.toByteArray(Charsets.UTF_8))

    private fun decodeText(encoded: String): String =
        String(decoder.decode(encoded), Charsets.UTF_8)
}

data class LegacyHistoryInspection(
    /** All original serialized values, including records the legacy UI skipped. */
    val rawRecords: Set<String>,
    /** All readable values, newest first. Same-timestamp records are not discarded. */
    val validRecords: List<HistoryRecord>,
    val invalidRawRecords: Set<String>,
    val timestampCollisions: Map<Long, List<HistoryRecord>>,
)
