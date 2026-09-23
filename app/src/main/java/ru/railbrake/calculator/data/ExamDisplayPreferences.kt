package ru.railbrake.calculator.data

import android.content.Context

class ExamDisplayPreferences(context: Context) {
    private val preferences = context.getSharedPreferences(PREFS_FILE, Context.MODE_PRIVATE)

    fun readingMode(): Boolean = preferences.getBoolean(KEY_READING_MODE, false)

    fun setReadingMode(enabled: Boolean) {
        preferences.edit().putBoolean(KEY_READING_MODE, enabled).apply()
    }

    fun showLinks(): Boolean = preferences.getBoolean(KEY_SHOW_LINKS, true)

    fun setShowLinks(show: Boolean) {
        preferences.edit().putBoolean(KEY_SHOW_LINKS, show).apply()
    }

    private companion object {
        const val PREFS_FILE = "exam_display_preferences"
        const val KEY_READING_MODE = "reading_mode"
        const val KEY_SHOW_LINKS = "show_links"
    }
}
