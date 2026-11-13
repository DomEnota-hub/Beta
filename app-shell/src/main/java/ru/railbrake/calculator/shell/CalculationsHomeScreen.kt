package ru.railbrake.calculator.shell

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun CalculationsHomeScreen(
    onBack: () -> Unit,
    onOpenVu45: () -> Unit,
    onOpenSecuring: () -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
    ) {
        TextButton(onClick = onBack) { Text("← На главную") }
        Text("Расчёты", style = MaterialTheme.typography.headlineSmall)
        Button(onClick = onOpenVu45, modifier = Modifier.fillMaxWidth()) {
            Text("Проверка ВУ-45")
        }
        Button(onClick = onOpenSecuring, modifier = Modifier.fillMaxWidth()) {
            Text("Закрепление состава")
        }
        Text("Оба инструмента предоставляют предварительные результаты. " +
            "Эксплуатационная применимость требует подтверждения нормативов и местных условий.")
    }
}
