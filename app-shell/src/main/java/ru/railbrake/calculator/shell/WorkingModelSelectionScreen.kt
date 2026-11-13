package ru.railbrake.calculator.shell

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.navigation.WorkingModelCatalog
import ru.railbrake.calculator.navigation.WorkingModelDescriptor

@Composable
fun WorkingModelSelectionScreen(onSelect: (WorkingModelDescriptor) -> Unit) {
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("Рабочий локомотив", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Выберите серию или модель. Исполнение уточняется внутри разделов; " +
                "неподтверждённые материалы не открываются автоматически.",
            style = MaterialTheme.typography.bodyMedium,
        )
        WorkingModelCatalog.models.forEach { model ->
            OutlinedButton(
                onClick = { onSelect(model) },
                modifier = Modifier.fillMaxWidth(),
            ) { Text(model.title) }
        }
    }
}

@Composable
fun UnpublishedWorkingModelScreen(
    model: WorkingModelDescriptor,
    onChangeModel: () -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(model.title, style = MaterialTheme.typography.headlineSmall)
        Text(
            "Материалы этой модели пока не опубликованы в рабочем приложении. " +
                "Проверка источников и исполнений продолжается.",
            style = MaterialTheme.typography.bodyMedium,
        )
        TextButton(onClick = onChangeModel) { Text("← Сменить локомотив") }
    }
}
