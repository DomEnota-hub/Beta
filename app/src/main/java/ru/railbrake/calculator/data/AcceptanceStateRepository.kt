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

fun acceptanceSummary(states: List<AcceptanceCheckState>) = AcceptanceSummary(
    total = states.size,
    checked = states.count { it == AcceptanceCheckState.OK },
    notes = states.count { it == AcceptanceCheckState.NOTE },
    notApplicable = states.count { it == AcceptanceCheckState.NOT_APPLICABLE },
    notChecked = states.count { it == AcceptanceCheckState.NOT_CHECKED }
)

class AcceptanceStateRepository(context: Context) {
    private val preferences = context.getSharedPreferences("technical_acceptance_states", Context.MODE_PRIVATE)

    private fun noteKey(itemId: String) = "note:$itemId"

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
}
