package ru.railbrake.calculator.ui

import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.Switch
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.foundation.shape.RoundedCornerShape
import ru.railbrake.calculator.core.ExamQuestion
import ru.railbrake.calculator.core.ExamQuestionRepository
import ru.railbrake.calculator.core.DiagnosticRepository
import ru.railbrake.calculator.core.Vl80sObservationCatalog
import ru.railbrake.calculator.data.SecretAccessRepository
import ru.railbrake.calculator.data.ExamDisplayPreferences

private fun examBlockDisplayTitle(sourceTitle: String): String = when (sourceTitle) {
    "Тест 1" -> "Блок 1"
    "Тест 2 - блок 1" -> "Блок 2"
    "Тест 2 - блок 2" -> "Блок 3"
    "Тест 2 - блок 3" -> "Блок 4"
    else -> sourceTitle
}

internal fun examActiveFilterLabel(query: String, block: String?, category: String?): String? = buildList {
    query.trim().takeIf(String::isNotBlank)?.let { value ->
        add("поиск: «${value.take(24)}${if (value.length > 24) "…" else ""}»")
    }
    block?.let { add(it) }
    category?.let(::add)
}.joinToString(" • ").takeIf(String::isNotBlank)

@Composable
fun ExamQuestionScreen(
    onHide: () -> Unit,
    onOpenScenario: (String) -> Unit,
    onOpenEquipment: (String) -> Unit,
    onOpenKnowledgeTopic: (String) -> Unit
) {
    val context = LocalContext.current
    val repository = remember { ExamQuestionRepository(context) }
    val secretAccessRepository = remember { SecretAccessRepository(context) }
    val displayPreferences = remember { ExamDisplayPreferences(context.applicationContext) }
    var showInKnowledge by remember { mutableStateOf(secretAccessRepository.showExamMaterialsInKnowledge()) }
    var readingMode by rememberSaveable { mutableStateOf(displayPreferences.readingMode()) }
    var showLinks by rememberSaveable { mutableStateOf(displayPreferences.showLinks()) }
    var query by rememberSaveable { mutableStateOf("") }
    var block by rememberSaveable { mutableStateOf<String?>(null) }
    var category by rememberSaveable { mutableStateOf<String?>(null) }
    val results = remember(query, block, category) { repository.search(query, block, category) }
    val listState = rememberLazyListState()
    val activeFilter = examActiveFilterLabel(query, block?.let(::examBlockDisplayTitle), category)

    fun setReadingMode(enabled: Boolean) {
        readingMode = enabled
        displayPreferences.setReadingMode(enabled)
    }

    fun setShowLinks(show: Boolean) {
        showLinks = show
        displayPreferences.setShowLinks(show)
    }

    BackHandler(enabled = readingMode) { setReadingMode(false) }

    Column(
        modifier = Modifier.fillMaxSize().padding(
            horizontal = if (readingMode) 10.dp else 16.dp,
            vertical = if (readingMode) 8.dp else 14.dp
        ),
        verticalArrangement = Arrangement.spacedBy(if (readingMode) 8.dp else 12.dp)
    ) {
        if (readingMode) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                shape = RoundedCornerShape(14.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text("Найдено: ${results.size}", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                        Text(
                            activeFilter ?: "Все вопросы",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            maxLines = 1
                        )
                    }
                    Text("Ссылки", style = MaterialTheme.typography.labelMedium)
                    Switch(checked = showLinks, onCheckedChange = ::setShowLinks)
                    TextButton(onClick = { setReadingMode(false) }) { Text("Панель") }
                }
            }
        } else {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Column(Modifier.weight(1f)) {
                    RailSectionHeader("База вопросов", "329 проверочных вопросов • быстрый поиск по формулировке и ответу")
                }
                TextButton(onClick = onHide) { Text("Скрыть") }
            }
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                shape = RoundedCornerShape(16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Text("Показывать материалы в Базе знаний", fontWeight = FontWeight.Bold)
                        Text(
                            if (showInKnowledge) "Материалы из базы 329 вопросов видны в Базе знаний."
                            else "Материалы из базы 329 вопросов скрыты из Базы знаний.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    Switch(
                        checked = showInKnowledge,
                        onCheckedChange = { enabled ->
                            showInKnowledge = enabled
                            secretAccessRepository.setShowExamMaterialsInKnowledge(enabled)
                        }
                    )
                }
            }
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                OutlinedButton(onClick = { setReadingMode(true) }, modifier = Modifier.weight(1f)) {
                    Text("Режим чтения")
                }
                Text("Показывать ссылки", style = MaterialTheme.typography.labelMedium)
                Switch(checked = showLinks, onCheckedChange = ::setShowLinks)
            }
            OutlinedTextField(
                value = query,
                onValueChange = { query = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Поиск по вопросу или ответу") },
                singleLine = true,
                shape = RoundedCornerShape(16.dp)
            )
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                item { FilterChip(selected = block == null, onClick = { block = null }, label = { Text("Все блоки") }) }
                items(repository.blocks) { value ->
                    FilterChip(selected = block == value, onClick = { block = value }, label = { Text(examBlockDisplayTitle(value)) })
                }
            }
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                item { FilterChip(selected = category == null, onClick = { category = null }, label = { Text("Все темы") }) }
                items(repository.categories) { value ->
                    FilterChip(selected = category == value, onClick = { category = value }, label = { Text(value) })
                }
            }
            Text("Найдено: ${results.size}", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
        }
        LazyColumn(
            state = listState,
            modifier = Modifier.weight(1f),
            contentPadding = PaddingValues(bottom = 12.dp),
            verticalArrangement = Arrangement.spacedBy(if (readingMode) 7.dp else 10.dp)
        ) {
            items(results, key = ExamQuestion::id) { item ->
                ExamQuestionCard(
                    item = item,
                    compact = readingMode,
                    showLinks = showLinks,
                    onOpenScenario = onOpenScenario,
                    onOpenEquipment = onOpenEquipment,
                    onOpenKnowledgeTopic = onOpenKnowledgeTopic
                )
            }
        }
    }
}

@Composable
private fun ExamQuestionCard(
    item: ExamQuestion,
    compact: Boolean,
    showLinks: Boolean,
    onOpenScenario: (String) -> Unit,
    onOpenEquipment: (String) -> Unit,
    onOpenKnowledgeTopic: (String) -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(if (compact) 14.dp else 16.dp),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)
    ) {
        Column(
            Modifier.padding(if (compact) 12.dp else 16.dp),
            verticalArrangement = Arrangement.spacedBy(if (compact) 6.dp else 8.dp)
        ) {
            Text("${examBlockDisplayTitle(item.blockTitle)} • №${item.sourceNumber} • ${item.category}", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.primary)
            Text(item.question, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            if (!compact) {
                Text("Правильный ответ", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            }
            androidx.compose.material3.Surface(
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.42f)
            ) {
                val answerParts = item.correctAnswer
                    .split('•')
                    .map(String::trim)
                    .filter(String::isNotBlank)
                val isBulletedAnswer = '•' in item.correctAnswer
                Column(
                    modifier = Modifier.fillMaxWidth().padding(if (compact) 10.dp else 12.dp),
                    verticalArrangement = Arrangement.spacedBy(if (isBulletedAnswer) 6.dp else 0.dp)
                ) {
                    answerParts.forEach { answer ->
                        Text(
                            text = if (isBulletedAnswer) "- $answer" else answer,
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
            if (item.requiresImage) {
                Text("Вопрос требует исходного изображения", style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.error)
            }
            val linkedScenarios = if (showLinks) item.diagnosticScenarioIds.mapNotNull(DiagnosticRepository::scenario) else emptyList()
            val linkedEquipment = if (showLinks) item.equipmentIds.mapNotNull(Vl80sObservationCatalog::equipment) else emptyList()
            if (showLinks && (linkedScenarios.isNotEmpty() || linkedEquipment.isNotEmpty() || item.knowledgeTopics.isNotEmpty())) {
                Text("Связано с приложением", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
                linkedScenarios.forEach { scenario ->
                    OutlinedButton(
                        onClick = { onOpenScenario(scenario.id) },
                        modifier = Modifier.fillMaxWidth(),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = if (compact) 4.dp else 8.dp)
                    ) {
                        Text("Диагностика: ${scenario.title}")
                    }
                }
                linkedEquipment.forEach { equipment ->
                    OutlinedButton(
                        onClick = { onOpenEquipment(equipment.id) },
                        modifier = Modifier.fillMaxWidth(),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = if (compact) 4.dp else 8.dp)
                    ) {
                        Text("Оборудование: ${equipment.title}")
                    }
                }
                item.knowledgeTopics.take(3).forEach { topic ->
                    OutlinedButton(
                        onClick = { onOpenKnowledgeTopic(topic) },
                        modifier = Modifier.fillMaxWidth(),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = if (compact) 4.dp else 8.dp)
                    ) {
                        Text("База знаний: $topic")
                    }
                }
            }
        }
    }
}
