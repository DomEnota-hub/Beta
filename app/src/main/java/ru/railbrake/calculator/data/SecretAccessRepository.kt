package ru.railbrake.calculator.data

import android.content.Context

class SecretAccessRepository(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_FILE, Context.MODE_PRIVATE)
    private val stateMarker = mix64(context.packageName.hashCode().toLong() xor MARKER_SEED)

    init {
        migrateLegacyState(context)
    }

    fun isUnlocked(): Boolean = preferences.getLong(KEY_GATE, Long.MIN_VALUE) == stateMarker

    /**
     * Records a completed direct-calculation input and returns true only when it also matches
     * the private local feature signature. The unlock values are not stored as readable literals.
     */
    fun recordDirectCalculation(massTons: Double, axleCount: Int?): Boolean {
        if (!matchesLocalFeatureSignature(massTons, axleCount)) return false
        preferences.edit().putLong(KEY_GATE, stateMarker).apply()
        return true
    }

    fun showExamMaterialsInKnowledge(): Boolean =
        preferences.getBoolean(KEY_SHOW_IN_KNOWLEDGE, false)

    fun setShowExamMaterialsInKnowledge(show: Boolean) {
        preferences.edit().putBoolean(KEY_SHOW_IN_KNOWLEDGE, show).apply()
    }

    fun hide() {
        preferences.edit().remove(KEY_GATE).apply()
    }

    private fun migrateLegacyState(context: Context) {
        val legacy = context.getSharedPreferences(legacyPrefsName(), Context.MODE_PRIVATE)
        val oldGate = legacyUnlockKey()
        val oldShow = legacyShowKey()
        if (!isUnlocked() && legacy.getBoolean(oldGate, false)) {
            preferences.edit().putLong(KEY_GATE, stateMarker).apply()
        }
        if (!preferences.contains(KEY_SHOW_IN_KNOWLEDGE) && legacy.contains(oldShow)) {
            preferences.edit().putBoolean(KEY_SHOW_IN_KNOWLEDGE, legacy.getBoolean(oldShow, false)).apply()
        }
        if (legacy.contains(oldGate) || legacy.contains(oldShow)) {
            legacy.edit().remove(oldGate).remove(oldShow).apply()
        }
    }

    companion object {
        private const val PREFS_FILE = "local_feature_state_v2"
        private const val KEY_GATE = "s1"
        private const val KEY_SHOW_IN_KNOWLEDGE = "s2"
        private const val MARKER_SEED = -4942790177534073029L

        private fun legacyPrefsName(): String = charArrayOf(
            's', 'e', 'c', 'r', 'e', 't', '_', 'a', 'c', 'c', 'e', 's', 's'
        ).concatToString()

        private fun legacyUnlockKey(): String = charArrayOf(
            'e', 'x', 'a', 'm', '_', 'q', 'u', 'e', 's', 't', 'i', 'o', 'n', 's', '_',
            'u', 'n', 'l', 'o', 'c', 'k', 'e', 'd'
        ).concatToString()

        private fun legacyShowKey(): String = charArrayOf(
            'e', 'x', 'a', 'm', '_', 'm', 'a', 't', 'e', 'r', 'i', 'a', 'l', 's', '_',
            'i', 'n', '_', 'k', 'n', 'o', 'w', 'l', 'e', 'd', 'g', 'e'
        ).concatToString()
    }
}

internal fun matchesLocalFeatureSignature(massTons: Double, axleCount: Int?): Boolean {
    if (!massTons.isFinite() || axleCount == null) return false
    val folded = java.lang.Double.doubleToRawLongBits(massTons) xor
        (axleCount.toLong() * -2960836687051489901L) xor
        7640891576956012809L
    return mix64(folded) == -4380884985364558404L
}

private fun mix64(input: Long): Long {
    var value = input - 7046029254386353131L
    value = (value xor (value ushr 30)) * -4658895280553007687L
    value = (value xor (value ushr 27)) * -7723592293110705685L
    return value xor (value ushr 31)
}
