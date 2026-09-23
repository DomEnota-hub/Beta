package ru.railbrake.calculator.data

import android.content.Context

class TechnicalRecentRepository(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_FILE, Context.MODE_PRIVATE)

    fun ids(familyKey: String): List<String> = preferences
        .getString(key(familyKey), "")
        .orEmpty()
        .lineSequence()
        .map(String::trim)
        .filter(String::isNotBlank)
        .toList()

    fun record(familyKey: String, entryId: String) {
        val updated = updateRecentTechnicalIds(ids(familyKey), entryId)
        preferences.edit().putString(key(familyKey), updated.joinToString("\n")).apply()
    }

    private fun key(familyKey: String): String = "recent_${familyKey.lowercase()}"

    private companion object {
        const val PREFS_FILE = "technical_recent_materials"
    }
}

internal fun updateRecentTechnicalIds(
    current: List<String>,
    openedId: String,
    limit: Int = 6
): List<String> {
    if (openedId.isBlank() || limit <= 0) return current.filter(String::isNotBlank).distinct().take(limit.coerceAtLeast(0))
    return (listOf(openedId) + current)
        .filter(String::isNotBlank)
        .distinct()
        .take(limit)
}
