package ru.railbrake.calculator.history

import java.nio.ByteBuffer
import java.nio.charset.CodingErrorAction
import java.util.Base64

/** Exact pinned Test- diagnostic_sessions/records seven-field StringSet format.
 * Read-only compatibility: a legacy report is user history, NOT an approved procedure.
 */
data class LegacyDiagnosticSession(
    val timestampMillis: Long,
    val profileId: String,
    val variantId: String,
    val scenarioId: String,
    val scenarioTitle: String,
    val severity: String,
    val report: String,
)

data class LegacyDiagnosticRead(
    val records: List<LegacyDiagnosticSession>,
    val malformedCount: Int,
    val excludedProfileCount: Int = 0,
)

object LegacyDiagnosticSessionCodec {
    private const val MAX_FIELD_BYTES = 64 * 1024
    private val decoder = Base64.getUrlDecoder()

    private fun text(field: String): String {
        require(field.length <= MAX_FIELD_BYTES * 2) { "Legacy diagnostic field too large" }
        val bytes = decoder.decode(field)
        require(bytes.size <= MAX_FIELD_BYTES) { "Legacy diagnostic field too large" }
        return Charsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(bytes)).toString()
    }

    fun parse(raw: String): LegacyDiagnosticSession? = runCatching {
        val fields = raw.split('|')
        require(fields.size == 7) { "Expected seven Base64 fields" }
        val values = fields.map(::text)
        val timestamp = values[0].toLong()
        require(timestamp >= 0L && values[1].isNotBlank() && values[3].isNotBlank()) {
            "Invalid timestamp, profile or scenario"
        }
        LegacyDiagnosticSession(timestamp, values[1], values[2], values[3],
            values[4], values[5], values[6])
    }.getOrNull()

    fun read(source: Set<String>): LegacyDiagnosticRead {
        require(source.size <= 5000) { "Legacy diagnostic archive too large; no data modified" }
        val valid = source.mapNotNull(::parse)
        // Preserve same-timestamp distinct reports, unlike the donor's add() policy.
        return LegacyDiagnosticRead(
            records = valid.distinct().sortedWith(compareByDescending<LegacyDiagnosticSession> { it.timestampMillis }
                .thenBy { it.profileId }.thenBy { it.variantId }.thenBy { it.scenarioId }
                .thenBy { it.scenarioTitle }.thenBy { it.severity }.thenBy { it.report }),
            malformedCount = source.size - valid.size,
        )
    }

    /** Never alias Ermak family "ermak" to 2es5k/3es5k or guess a variant. */
    fun forExactModel(read: LegacyDiagnosticRead, modelId: String): LegacyDiagnosticRead {
        require(modelId.isNotBlank())
        val matching = read.records.filter { it.profileId == modelId }
        return read.copy(records = matching,
            excludedProfileCount = read.excludedProfileCount + read.records.size - matching.size)
    }
}
