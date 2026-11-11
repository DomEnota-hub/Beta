package ru.railbrake.calculator.shell

import android.content.Context
import ru.railbrake.calculator.history.LegacyDiagnosticRead
import ru.railbrake.calculator.history.LegacyDiagnosticSessionCodec

/**
 * The donor diagnostic journal remains untouched. No silent cross-family/variant
 * remapping, no migration writes and no promotion of reports to crew instructions.
 */
class AndroidLegacyDiagnosticSessionStore(context: Context) {
    private val legacy = context.getSharedPreferences("diagnostic_sessions", Context.MODE_PRIVATE)

    @Synchronized
    fun loadForModel(modelId: String): LegacyDiagnosticRead {
        require(modelId.isNotBlank())
        val source = if (legacy.contains("records")) {
            legacy.getStringSet("records", null)?.toSet()
                ?: throw IllegalStateException("Invalid diagnostic journal storage type")
        } else emptySet()
        return LegacyDiagnosticSessionCodec.forExactModel(
            LegacyDiagnosticSessionCodec.read(source), modelId)
    }
}
