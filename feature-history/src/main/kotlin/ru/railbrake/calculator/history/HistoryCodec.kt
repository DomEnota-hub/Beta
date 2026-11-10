package ru.railbrake.calculator.history

import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.util.Base64

/**
 * Pinned Test- legacy format: timestamp|mode|title|summary|details.
 * Four strings are Android Base64.URL_SAFE|NO_WRAP UTF-8. The old StringSet is
 * read only; this module never overwrites its unversioned "records" key.
 */
object HistoryCodec {
    private const val MAX_RECORDS = 30
    private const val MAX_FIELD_BYTES = 64 * 1024
    private val encoder = Base64.getUrlEncoder()
    private val decoder = Base64.getUrlDecoder()

    private fun encodeText(value: String): String =
        encoder.encodeToString(value.toByteArray(Charsets.UTF_8))

    private fun decodeText(value: String): String {
        require(value.length <= MAX_FIELD_BYTES * 2) { "History field too large" }
        val bytes = decoder.decode(value)
        require(bytes.size <= MAX_FIELD_BYTES) { "History field too large" }
        return Charsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(bytes)).toString()
    }

    fun encodeLegacy(record: HistoryRecord): String =
        listOf(record.timestampMillis.toString(), encodeText(record.mode),
            encodeText(record.title), encodeText(record.summary),
            encodeText(record.details)).joinToString("|")

    fun parseLegacy(line: String): HistoryRecord? = runCatching {
        val fields = line.split('|')
        require(fields.size == 5) { "Expected five fields" }
        val timestamp = fields[0].toLong()
        require(timestamp >= 0L) { "Negative timestamp" }
        HistoryRecord(timestamp, decodeText(fields[1]), decodeText(fields[2]),
            decodeText(fields[3]), decodeText(fields[4]))
    }.getOrNull()

    /** Match donor behavior: corrupt entries ignored, newest first, at most 30. */
    fun readLegacy(records: Set<String>): List<HistoryRecord> =
        canonical(records.mapNotNull(::parseLegacy))

    /** Unlike legacy, identical timestamps do not discard distinct calculations. */
    fun canonical(records: List<HistoryRecord>): List<HistoryRecord> =
        records.distinct().sortedByDescending { it.timestampMillis }.take(MAX_RECORDS)

    /** Versioned, newline-delimited encoding stored in a DIFFERENT preference file. */
    fun encodeV2(records: List<HistoryRecord>): String =
        canonical(records).joinToString("\n") { "v2|" + encodeLegacy(it) }

    /** A damaged v2 store must FAIL, not silently overwrite user data. */
    fun decodeV2(raw: String): List<HistoryRecord> {
        if (raw.isEmpty()) return emptyList()
        require(raw.length <= MAX_RECORDS * MAX_FIELD_BYTES * 12) { "History too large" }
        return canonical(raw.split('\n').map { line ->
            require(line.startsWith("v2|")) { "Unsupported history schema" }
            parseLegacy(line.removePrefix("v2|"))
                ?: throw IllegalArgumentException("Corrupt v2 history record")
        })
    }
}

/** Notes are independent of calculator history and scoped to an explicit model. */
data class WorkNote(
    val id: String,
    val modelId: String,
    val timestampMillis: Long,
    val title: String,
    val body: String,
)

object WorkNotesCodec {
    private val encoder = Base64.getUrlEncoder()
    private val decoder = Base64.getUrlDecoder()
    private fun encode(value: String) = encoder.encodeToString(value.toByteArray(Charsets.UTF_8))
    private fun decode(value: String): String {
        require(value.length <= 131072)
        return Charsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(decoder.decode(value))).toString()
    }

    fun encodeV1(notes: List<WorkNote>): String {
        require(notes.size <= 200) { "Work notes limit reached; no notes were deleted" }
        require(notes.map { it.id }.distinct().size == notes.size) { "Duplicate note ID" }
        return notes.sortedByDescending { it.timestampMillis }
        .joinToString("\n") {
            listOf("n1", it.timestampMillis.toString(), encode(it.id),
                encode(it.modelId), encode(it.title), encode(it.body)).joinToString("|")
        }
    }

    fun decodeV1(raw: String): List<WorkNote> {
        if (raw.isEmpty()) return emptyList()
        require(raw.length <= 200 * 350000) { "Notes too large" }
        return raw.split('\n').map {
            val p = it.split('|')
            require(p.size == 6 && p[0] == "n1") { "Corrupt notes schema" }
            WorkNote(decode(p[2]), decode(p[3]), p[1].toLong(),
                decode(p[4]), decode(p[5]))
        }.also { notes ->
            require(notes.size <= 200)
            require(notes.all { it.id.isNotBlank() && it.modelId.isNotBlank() })
            require(notes.map { it.id }.distinct().size == notes.size)
        }
    }
}
