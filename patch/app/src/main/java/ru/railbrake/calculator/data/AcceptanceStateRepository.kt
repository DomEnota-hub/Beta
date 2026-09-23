package ru.railbrake.calculator.data

import android.content.Context

enum class AcceptanceCheckState(val label: String) {
    NOT_CHECKED("Не проверено"),
    OK("Проверено"),
    NOTE("Замечание"),
    NOT_APPLICABLE("Не применяется")
}

data class AcceptanceSummary(
    val total: Int,
    val checked: Int,
    val notes: Int,
    val notApplicable: Int,
    val notChecked: Int
) {
    val complete: Boolean get() = total > 0 && notChecked == 0
    val result: String get() = when {
        !complete -> "Проверка не завершена"
        notes > 0 -> "Проверка завершена: есть замечания"
        else -> "Проверка завершена: замечаний нет"
    }
}

data class AcceptanceSession(
    val routeId: String,
    val routeTitle: String,
    val startedAtMillis: Long,
    val updatedAtMillis: Long,
    val completedAtMillis: Long?
)

fun acceptanceSummary(states: List<AcceptanceCheckState>) = AcceptanceSummary(
    total = states.size,
    checked = states.count { it == AcceptanceCheckState.OK },
    notes = states.count { it == AcceptanceCheckState.NOTE },
    notApplicable = states.count { it == AcceptanceCheckState.NOT_APPLICABLE },
    notChecked = states.count { it == AcceptanceCheckState.NOT_CHECKED }
)

fun acceptanceReportText(
    familyTitle: String,
    routeTitle: String,
    startedAt: String,
    updatedAt: String,
    summary: AcceptanceSummary,
    notes: List<Pair<String, String>>
): String = buildString {
    appendLine("Приёмка: $familyTitle")
    appendLine("Режим: $routeTitle")
    appendLine("Начато: $startedAt")
    appendLine("Обновлено: $updatedAt")
    appendLine("Результат: ${summary.result}")
    appendLine("Проверено: ${summary.checked}")
    appendLine("Замечания: ${summary.notes}")
    appendLine("Не применяется: ${summary.notApplicable}")
    appendLine("Не проверено: ${summary.notChecked}")
    if (notes.isNotEmpty()) {
        appendLine()
        appendLine("Замечания:")
        notes.forEach { (title, note) ->
            appendLine("- $title: ${note.ifBlank { "без описания" }}")
        }
    }
}.trimEnd()

class AcceptanceStateRepository(context: Context) {
    private val preferences = context.getSharedPreferences("technical_acceptance_states", Context.MODE_PRIVATE)

    companion object {
        private val sessionDisabledByFamily = mutableMapOf<String, MutableSet<String>>()
    }

    private fun noteKey(itemId: String) = "note:$itemId"
    private fun disabledKey(familyKey: String) = "disabled:$familyKey"
    private fun saveParametersKey(familyKey: String) = "save_parameters:$familyKey"
    private fun sessionKey(familyKey: String, field: String) = "session:$familyKey:$field"

    fun state(itemId: String): AcceptanceCheckState =
        preferences.getString(itemId, AcceptanceCheckState.NOT_CHECKED.name)
  ?.replace("BLOCKING", AcceptanceCheckState.NOTE.name)
  ?.let { runCatching { AcceptanceCheckState.valueOf(it) }.getOrNull() }
  ?: AcceptanceCheckState.NOT_CHECKED

    fun setState(itemId: String, state: AcceptanceCheckState) {
        preferences.edit().putString(itemId, state.name).apply()
    }

    fun note(itemId: String): String =
        preferences.getString(noteKey(itemId), "").orEmpty()

    fun setNote(itemId: String, note: String) {
        val normalized = note.trim()
        preferences.edit().apply {
  if (normalized.isBlank()) remove(noteKey(itemId))
  else putString(noteKey(itemId), normalized)
        }.apply()
    }

    fun session(familyKey: String): AcceptanceSession? {
        val startedAt = preferences.getLong(sessionKey(familyKey, "started_at"), 0L)
        if (startedAt <= 0L) return null
        val completedAt = preferences.getLong(sessionKey(familyKey, "completed_at"), 0L)
            .takeIf { it > 0L }
        return AcceptanceSession(
            routeId = preferences.getString(sessionKey(familyKey, "route_id"), "").orEmpty(),
            routeTitle = preferences.getString(sessionKey(familyKey, "route_title"), "Приёмка").orEmpty(),
            startedAtMillis = startedAt,
            updatedAtMillis = preferences.getLong(sessionKey(familyKey, "updated_at"), startedAt),
            completedAtMillis = completedAt
        )
    }

    /**
     * Один сеанс объединяет обязательную и расширенную части: при смене маршрута
     * отметки общих физических пунктов не сбрасываются.
     */
    fun startOrContinueSession(
        familyKey: String,
        routeId: String,
        routeTitle: String,
        nowMillis: Long = System.currentTimeMillis()
    ): AcceptanceSession {
        val current = session(familyKey)
        val startedAt = current?.startedAtMillis ?: nowMillis
        preferences.edit()
            .putString(sessionKey(familyKey, "route_id"), routeId)
            .putString(sessionKey(familyKey, "route_title"), routeTitle)
            .putLong(sessionKey(familyKey, "started_at"), startedAt)
            .putLong(sessionKey(familyKey, "updated_at"), nowMillis)
            .remove(sessionKey(familyKey, "completed_at"))
            .apply()
        return session(familyKey)!!
    }

    fun updateSession(
        familyKey: String,
        complete: Boolean,
        nowMillis: Long = System.currentTimeMillis()
    ) {
        if (session(familyKey) == null) return
        preferences.edit().apply {
            putLong(sessionKey(familyKey, "updated_at"), nowMillis)
            if (complete) putLong(sessionKey(familyKey, "completed_at"), nowMillis)
            else remove(sessionKey(familyKey, "completed_at"))
        }.apply()
    }

    fun resetSession(familyKey: String, itemIds: Collection<String>) {
        preferences.edit().apply {
            itemIds.forEach { itemId ->
                remove(itemId)
                remove(noteKey(itemId))
            }
            remove(sessionKey(familyKey, "route_id"))
            remove(sessionKey(familyKey, "route_title"))
            remove(sessionKey(familyKey, "started_at"))
            remove(sessionKey(familyKey, "updated_at"))
            remove(sessionKey(familyKey, "completed_at"))
        }.apply()
    }

    fun saveParameters(familyKey: String): Boolean =
        preferences.getBoolean(saveParametersKey(familyKey), true)

    fun setSaveParameters(familyKey: String, enabled: Boolean) {
        preferences.edit().putBoolean(saveParametersKey(familyKey), enabled).apply()
        if (enabled) persistDisabled(familyKey, disabledIds(familyKey))
    }

    fun disabledIds(familyKey: String): Set<String> = synchronized(sessionDisabledByFamily) {
        sessionDisabledByFamily.getOrPut(familyKey) {
  preferences.getStringSet(disabledKey(familyKey), emptySet()).orEmpty().toMutableSet()
        }.toSet()
    }

    fun setDisabled(familyKey: String, itemId: String, disabled: Boolean) {
        val snapshot = synchronized(sessionDisabledByFamily) {
  val current = sessionDisabledByFamily.getOrPut(familyKey) {
      preferences.getStringSet(disabledKey(familyKey), emptySet()).orEmpty().toMutableSet()
  }
  if (disabled) current += itemId else current -= itemId
  current.toSet()
        }
        if (saveParameters(familyKey)) persistDisabled(familyKey, snapshot)
    }

    fun restoreAllDisabled(familyKey: String) {
        synchronized(sessionDisabledByFamily) {
  sessionDisabledByFamily.getOrPut(familyKey) {
      preferences.getStringSet(disabledKey(familyKey), emptySet()).orEmpty().toMutableSet()
  }.clear()
        }
        if (saveParameters(familyKey)) persistDisabled(familyKey, emptySet())
    }

    private fun persistDisabled(familyKey: String, disabled: Set<String>) {
        preferences.edit().putStringSet(disabledKey(familyKey), disabled.toSet()).apply()
    }
}
