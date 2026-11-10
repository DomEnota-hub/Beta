package ru.railbrake.calculator.shell

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.history.HistoryRecord
import ru.railbrake.calculator.history.HistoryStore
import ru.railbrake.calculator.history.WorkNote
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

@Composable
fun HistoryAndNotesScreen(
    historyStore: HistoryStore,
    notesStore: AndroidWorkNotesStore,
    modelId: String,
    modelTitle: String,
    onBack: () -> Unit,
) {
    var tab by rememberSaveable { mutableStateOf("HISTORY") }
    var filter by rememberSaveable { mutableStateOf("Все") }
    var history by remember { mutableStateOf<List<HistoryRecord>>(emptyList()) }
    var notes by remember(modelId) { mutableStateOf<List<WorkNote>>(emptyList()) }
    var error by remember { mutableStateOf<String?>(null) }
    var clearConfirm by remember { mutableStateOf(false) }
    var pendingNoteDelete by remember { mutableStateOf<String?>(null) }
    var noteTitle by rememberSaveable(modelId) { mutableStateOf("") }
    var noteBody by rememberSaveable(modelId) { mutableStateOf("") }

    LaunchedEffect(tab, modelId) {
        runCatching {
            if (tab == "HISTORY") history = historyStore.load()
            else notes = notesStore.load(modelId)
        }.onFailure { error = "Не удалось прочитать локальные данные. Запись заблокирована до восстановления." }
    }
    pendingNoteDelete?.let { noteId ->
        AlertDialog(
            onDismissRequest = { pendingNoteDelete = null },
            title = { Text("Удалить рабочую запись?") },
            text = { Text("Это действие нельзя отменить.") },
            confirmButton = {
                TextButton(onClick = {
                    runCatching {
                        notesStore.delete(modelId, noteId)
                        notes = notesStore.load(modelId)
                    }.onFailure { error = "Не удалось удалить запись." }
                    pendingNoteDelete = null
                }) { Text("Удалить") }
            },
            dismissButton = { TextButton(onClick = { pendingNoteDelete = null }) { Text("Отмена") } },
        )
    }
    if (clearConfirm) {
        AlertDialog(
            onDismissRequest = { clearConfirm = false },
            title = { Text("Очистить историю расчётов?") },
            text = { Text("История в новой версии будет очищена. Исходные записи старой версии сохраняются как резерв для миграции.") },
            confirmButton = {
                TextButton(onClick = {
                    runCatching { historyStore.clear(); history = historyStore.load() }
                        .onFailure { error = "Не удалось очистить историю." }
                    clearConfirm = false
                }) { Text("Очистить") }
            },
            dismissButton = { TextButton(onClick = { clearConfirm = false }) { Text("Отмена") } },
        )
    }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        TextButton(onClick = onBack) { Text("← На главную") }
        Text("История и рабочие записи", style = MaterialTheme.typography.headlineSmall)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (tab == "HISTORY") {
                Button(onClick = {}) { Text("История расчётов") }
                OutlinedButton(onClick = { tab = "NOTES" }) { Text("Рабочие записи") }
            } else {
                OutlinedButton(onClick = { tab = "HISTORY" }) { Text("История расчётов") }
                Button(onClick = {}) { Text("Рабочие записи") }
            }
        }
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        if (tab == "HISTORY") {
            Text("История сохраняется локально. Старые записи Test- читаются без удаления исходного формата.")
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("Все", "По массе", "ИДП №12", "ВУ-45").forEach { value ->
                    TextButton(onClick = { filter = value }) {
                        Text(if (filter == value) "✓ $value" else value)
                    }
                }
            }
            val visible = if (filter == "Все") history else history.filter { it.mode == filter }
            if (visible.isEmpty()) Text("Записей нет.")
            visible.forEach { record ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                        Text(record.mode + " · " + dateText(record.timestampMillis),
                            style = MaterialTheme.typography.labelMedium)
                        Text(record.title, style = MaterialTheme.typography.titleMedium)
                        Text(record.summary)
                        Text(record.details, style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
            OutlinedButton(onClick = { clearConfirm = true }, enabled = history.isNotEmpty()) {
                Text("Очистить историю")
            }
        } else {
            Text("Рабочий локомотив: $modelTitle. Записи привязаны к выбранной модели, " +
                "хранятся только на этом устройстве и не являются проверенными инструкциями.")
            OutlinedTextField(
                value = noteTitle, onValueChange = { if (it.length <= 200) noteTitle = it },
                label = { Text("Заголовок") }, modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = noteBody, onValueChange = { if (it.length <= 10000) noteBody = it },
                label = { Text("Текст записи") }, minLines = 3, modifier = Modifier.fillMaxWidth(),
            )
            Button(
                enabled = noteTitle.isNotBlank() && noteBody.isNotBlank() && error == null,
                onClick = {
                    runCatching {
                        notesStore.add(modelId, noteTitle, noteBody)
                        notes = notesStore.load(modelId)
                        noteTitle = ""; noteBody = ""
                    }.onFailure { error = "Не удалось сохранить запись." }
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Сохранить запись") }
            if (notes.isEmpty()) Text("Для выбранной модели записей пока нет.")
            notes.forEach { note ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(dateText(note.timestampMillis), style = MaterialTheme.typography.labelSmall)
                        Text(note.title, style = MaterialTheme.typography.titleMedium)
                        Text(note.body)
                        TextButton(onClick = { pendingNoteDelete = note.id }) {
                            Text("Удалить запись")
                        }
                    }
                }
            }
        }
    }
}

private fun dateText(millis: Long): String =
    SimpleDateFormat("dd.MM.yyyy HH:mm", Locale("ru", "RU")).format(Date(millis))
