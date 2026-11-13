package ru.railbrake.calculator.diagnostics

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.designsystem.RailFeatureScaffold
import ru.railbrake.calculator.designsystem.RailFeatureTemplate

/**
 * One shared diagnostics UI for model-owned, separately accepted scenarios.
 * All queries and opens go through PublishedDiagnosticCatalog; the raw donor
 * executable graph must never be passed directly to a user-facing catalog.
 */
@Composable
fun DiagnosticCatalogScreen(
    catalog: PublishedDiagnosticCatalog,
    modelTitle: String,
    onBack: () -> Unit,
    referenceCatalog: DiagnosticReferenceCatalog? = null,
) {
    var query by remember(catalog) { mutableStateOf("") }
    var selectedId by remember(catalog) { mutableStateOf<String?>(null) }
    var selectedReferenceId by remember(referenceCatalog) { mutableStateOf<String?>(null) }
    val selected = selectedId?.let(catalog::open)
    val reference = selectedReferenceId?.let { referenceCatalog?.open(it) }
    BackHandler(enabled = selectedId != null || selectedReferenceId != null) {
        selectedId = null
        selectedReferenceId = null
    }
    var state by remember(selected?.id) {
        mutableStateOf(selected?.let(ExecutableDiagnosticEngine::start))
    }

    RailFeatureScaffold(
        template = RailFeatureTemplate.DIAGNOSTICS,
        title = "Диагностика",
        subtitle = "$modelTitle · только проверенные опубликованные сценарии",
    ) {
        Column(
            modifier = Modifier.weight(1f).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            TextButton(
                onClick = {
                    if (selectedId == null && selectedReferenceId == null) onBack()
                    else {
                        selectedId = null
                        selectedReferenceId = null
                    }
                },
            ) {
                Text(
                    if (selectedId == null && selectedReferenceId == null)
                        "← Назад" else "← К списку сценариев"
                )
            }

            if (selected == null && reference == null) {
                OutlinedTextField(
                    modifier = Modifier.fillMaxWidth(),
                    value = query,
                    onValueChange = { query = it },
                    label = { Text("Поиск по названию, признакам и системе") },
                    singleLine = true,
                )
                val results = catalog.search(query)
                val references = referenceCatalog?.search(query).orEmpty()
                if (results.isEmpty() && references.isEmpty()) {
                    Text(
                        "Материалов по этому запросу нет. Неподтверждённые " +
                            "действия и диагностические опросы не публикуются.",
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
                results.forEach { scenario ->
                    OutlinedButton(
                        modifier = Modifier.fillMaxWidth(),
                        onClick = { selectedId = scenario.id },
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(scenario.title, style = MaterialTheme.typography.titleSmall)
                            Text(scenario.category, style = MaterialTheme.typography.bodySmall)
                            Text(scenario.summary, style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }
                if (references.isNotEmpty()) {
                    Text(
                        "Справочные описания · требуют проверки",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Text(
                        "Сведения из Test- доступны для чтения. Это не разрешение " +
                            "на действия локомотивной бригады.",
                        style = MaterialTheme.typography.bodySmall,
                    )
                }
                references.forEach { item ->
                    OutlinedButton(
                        modifier = Modifier.fillMaxWidth(),
                        onClick = { selectedReferenceId = item.id },
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                            Text(item.title, style = MaterialTheme.typography.titleSmall)
                            Text(item.category, style = MaterialTheme.typography.bodySmall)
                            Text(item.summary, style = MaterialTheme.typography.bodyMedium)
                        }
                    }
                }
            } else if (reference != null) {
                Text(reference.title, style = MaterialTheme.typography.titleMedium)
                Text(reference.summary)
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(6.dp),
                    ) {
                        Text(
                            "Справка, не инструкция к действию",
                            style = MaterialTheme.typography.titleSmall,
                        )
                        Text(reference.sourceNotice)
                        reference.variantNotice?.let { Text(it) }
                        Text(
                            "Ни один пункт этой справки не подтверждает право локомотивной " +
                                "бригады выполнять работы. Проверки и ремонтные операции " +
                                "из донорского сценария здесь не публикуются.",
                        )
                    }
                }
                if (reference.observedSigns.isNotEmpty()) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            Text(
                                "Наблюдаемые признаки · справочно",
                                style = MaterialTheme.typography.titleSmall,
                            )
                            reference.observedSigns.forEach { Text("• $it") }
                        }
                    }
                }
                if (reference.donorCautions.isNotEmpty()) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            Text(
                                "Предостережения из Test- · требуют проверки",
                                style = MaterialTheme.typography.titleSmall,
                                color = MaterialTheme.colorScheme.error,
                            )
                            Text(
                                "В донорской карточке перечислены действия, которых следует " +
                                    "избегать. Актуальная редакция и применимость к исполнению " +
                                    "не подтверждены; это не самостоятельный нормативный запрет.",
                            )
                            reference.donorCautions.forEach { Text("• $it") }
                        }
                    }
                }
                if (reference.donorStopSignals.isNotEmpty()) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(6.dp),
                        ) {
                            Text(
                                "Признаки прекращения проверки · донорская справка",
                                style = MaterialTheme.typography.titleSmall,
                                color = MaterialTheme.colorScheme.error,
                            )
                            Text(
                                "Перечень требует сверки с действующими инструкциями. " +
                                    "При опасных признаках не продолжайте неподтверждённый опрос.",
                            )
                            reference.donorStopSignals.forEach { Text("• $it") }
                        }
                    }
                }
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Text(
                            "Порядок проверок, разрешённые действия и ограничения по роли " +
                                "здесь не подтверждены. Пошаговый опрос недоступен. " +
                                "Руководствуйтесь действующими инструкциями и допусками.",
                        )
                    }
                }
            } else if (selected != null) {
                Text(selected.title, style = MaterialTheme.typography.titleMedium)
                Text(selected.summary)
                Text(
                    "Пошаговый опрос помогает систематизировать признаки неисправности. " +
                        "Он не является допуском к работам и не заменяет действующие инструкции.",
                    style = MaterialTheme.typography.bodySmall,
                )
                selected.dangerSigns.takeIf { it.isNotEmpty() }?.let { signs ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp),
                        ) {
                            Text("Признаки опасности", style = MaterialTheme.typography.titleSmall)
                            signs.forEach { Text("• $it") }
                        }
                    }
                }
                selected.prohibited.takeIf { it.isNotEmpty() }?.let { prohibitions ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp),
                        ) {
                            Text(
                                "Противопоказания и недопустимые действия",
                                style = MaterialTheme.typography.titleSmall,
                            )
                            prohibitions.forEach { Text("• $it") }
                        }
                    }
                }
                selected.stopConditions.takeIf { it.isNotEmpty() }?.let { stops ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp),
                        ) {
                            Text("Условия прекращения проверки", style = MaterialTheme.typography.titleSmall)
                            stops.forEach { Text("• $it") }
                        }
                    }
                }

                selected.reportFields.takeIf { it.isNotEmpty() }?.let { fields ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(12.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp),
                        ) {
                            Text("Что сообщить", style = MaterialTheme.typography.titleSmall)
                            fields.forEach { Text("• $it") }
                        }
                    }
                }
                Text(
                    "Источник/основание: " + selected.sourceNote,
                    style = MaterialTheme.typography.bodySmall,
                )

                if (state != null) {
                    val result = ExecutableDiagnosticEngine.result(selected, requireNotNull(state))
                    result.nextQuestion?.let { question ->
                        Card(modifier = Modifier.fillMaxWidth()) {
                            Column(
                                modifier = Modifier.padding(16.dp),
                                verticalArrangement = Arrangement.spacedBy(12.dp),
                            ) {
                                Text(
                                    "Вопрос ${result.state.answers.size + 1}",
                                    style = MaterialTheme.typography.labelLarge,
                                )
                                Text(
                                    question.text,
                                    style = MaterialTheme.typography.titleMedium,
                                )
                                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                    ExecutableDiagnosticResponse.entries.forEach { response ->
                                        Button(
                                            onClick = {
                                                state = ExecutableDiagnosticEngine.answer(
                                                    selected,
                                                    requireNotNull(state),
                                                    response,
                                                ).state
                                            },
                                        ) { Text(response.displayLabel()) }
                                    }
                                }
                            }
                        }
                    }
                    if (result.nextQuestion == null) {
                        Text("Опрос завершён", style = MaterialTheme.typography.titleMedium)
                        if (result.leadingCauses.isEmpty()) {
                            Text("По полученным ответам гипотезы не выделены.")
                        } else {
                            Text("Возможные причины (не окончательный диагноз):")
                            result.leadingCauses.forEach { cause ->
                                Text("• ${cause.title}")
                                Text(cause.explanation, style = MaterialTheme.typography.bodySmall)
                            }
                        }
                    }
                    if (result.state.answers.isNotEmpty()) {
                        Text("История ответов", style = MaterialTheme.typography.titleSmall)
                        result.state.answers.forEach { answer ->
                            Text(answer.questionText)
                            Text(
                                "${answer.response.displayLabel()}: ${answer.conclusion}",
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                    }
                    if (result.state.answers.isNotEmpty()) {
                        OutlinedButton(
                            onClick = {
                                state = ExecutableDiagnosticEngine.previous(
                                    selected,
                                    requireNotNull(state),
                                )
                            },
                            modifier = Modifier.fillMaxWidth(),
                        ) { Text("← Исправить предыдущий ответ") }
                    }
                    OutlinedButton(
                        onClick = { state = ExecutableDiagnosticEngine.start(selected) },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("Начать опрос заново") }
                }
            }
        }
    }
}

private fun ExecutableDiagnosticResponse.displayLabel(): String = when (this) {
    ExecutableDiagnosticResponse.YES -> "Да"
    ExecutableDiagnosticResponse.NO -> "Нет"
    ExecutableDiagnosticResponse.UNKNOWN -> "Не знаю"
}
