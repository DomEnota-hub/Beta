package ru.railbrake.calculator.shell

import android.content.res.AssetManager
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.assistant.AssistantTextEngine
import ru.railbrake.calculator.assistant.TextAssistantResult
import ru.railbrake.calculator.assistant.TextIntent
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.safety.CommonReferenceCatalog

/** Category is a filter, not an authority to bypass source or profile gates. */
enum class AssistantSearchCategory(
    val title: String, val intent: TextIntent, val types: Set<ContentType>,
) {
    EQUIPMENT("Оборудование", TextIntent.REFERENCE,
        setOf(ContentType.EQUIPMENT, ContentType.TECHNICAL_DATA)),
    FAULTS("Неисправности", TextIntent.DIAGNOSTICS,
        setOf(ContentType.DIAGNOSTIC_SCENARIO)),
    SCHEMES("Схемы", TextIntent.SCHEME, setOf(ContentType.ATLAS_SCHEME)),
    KNOWLEDGE("База знаний", TextIntent.REFERENCE, setOf(ContentType.KNOWLEDGE)),
}

private fun assistantModelTitle(model: ModelId): String = when (model.value) {
    "vl80s" -> "ВЛ80С"
    "2es5k" -> "2ЭС5К"
    "3es5k" -> "3ЭС5К"
    "chme3" -> "ЧМЭ3"
    "chme3t" -> "ЧМЭ3Т"
    "chme3e" -> "ЧМЭ3Э"
    "tem2" -> "ТЭМ2"
    "tem2u" -> "ТЭМ2У"
    else -> "Неизвестная модель"
}

@Composable
fun AssistantSearchScreen(
    engine: AssistantTextEngine?,
    assets: AssetManager,
    workingModelId: ModelId,
    workingModelTitle: String,
    draft: String,
    submitted: String,
    category: AssistantSearchCategory?,
    visibleCount: Int,
    notice: String?,
    onDraftChange: (String) -> Unit,
    onSubmit: () -> Unit,
    onCategoryChange: (AssistantSearchCategory?) -> Unit,
    onShowMore: () -> Unit,
    onClarify: (ModelId) -> Unit,
    onOpen: (TextAssistantResult.Matches, ContentTarget) -> Unit,
    onOpenCommon: (ShellHomeDestination, String) -> Unit,
    onBack: () -> Unit,
) {
    // Donor common cards are a distinct, read-only lane. They are never installed
    // into the published assistant registry or interpreted as action permissions.
    var commonEntries by remember(assets) { mutableStateOf<List<ContentEntry>?>(null) }
    var commonLoadFailed by remember(assets) { mutableStateOf(false) }
    LaunchedEffect(assets) {
        try {
            commonEntries = withContext(Dispatchers.IO) { CommonReferenceCatalog(assets).load() }
            commonLoadFailed = false
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            commonEntries = emptyList()
            commonLoadFailed = true
        }
    }
    val commonHits = remember(commonEntries, submitted, category) {
        AssistantCommonReferencePolicy.search(commonEntries.orEmpty(), submitted, category)
    }
    val result = remember(engine, workingModelId, submitted, category) {
        if (submitted.isBlank() || engine == null) null
        else engine.query(
            text = submitted,
            workingModelId = workingModelId,
            limit = 50,
            intentOverride = category?.intent,
            allowedTypes = category?.types,
        )
    }
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        TextButton(onClick = onBack) { Text("← На главную") }
        Text("Помощник", style = MaterialTheme.typography.headlineMedium)
        Text("Рабочий локомотив: " + workingModelTitle)
        Text("Поиск по опубликованным карточкам и отдельно отмеченным справочным материалам. Это не генеративная нейросеть.")
        OutlinedTextField(
            value = draft, onValueChange = onDraftChange,
            label = { Text("Что нужно найти?") },
            modifier = Modifier.fillMaxWidth(), singleLine = true,
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
            keyboardActions = KeyboardActions(onSearch = { onSubmit() }),
        )
        AssistantVoiceButton(onTranscript = onDraftChange)
        Button(onClick = onSubmit, enabled = draft.isNotBlank(),
            modifier = Modifier.fillMaxWidth()) { Text("Найти") }
        Text("Категории", style = MaterialTheme.typography.titleMedium)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            AssistantCategoryButton("Все", category == null) { onCategoryChange(null) }
            AssistantCategoryButton("Оборудование",
                category == AssistantSearchCategory.EQUIPMENT) {
                onCategoryChange(AssistantSearchCategory.EQUIPMENT)
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            AssistantCategoryButton("Неисправности",
                category == AssistantSearchCategory.FAULTS) {
                onCategoryChange(AssistantSearchCategory.FAULTS)
            }
            AssistantCategoryButton("Схемы",
                category == AssistantSearchCategory.SCHEMES) {
                onCategoryChange(AssistantSearchCategory.SCHEMES)
            }
        }
        AssistantCategoryButton("База знаний",
            category == AssistantSearchCategory.KNOWLEDGE) {
            onCategoryChange(AssistantSearchCategory.KNOWLEDGE)
        }
        Text("Список материалов", style = MaterialTheme.typography.titleMedium)
        if (notice != null) Text(notice, color = MaterialTheme.colorScheme.error)
        if (engine == null) {
            Text("Каталог материалов недоступен. Поиск закрыт до восстановления данных.")
        } else if (submitted.isBlank()) {
            Text("Введите запрос. При необходимости выберите категорию.")
        } else when (result) {
            TextAssistantResult.WorkingModelRequired ->
                Text("Сначала выберите рабочий локомотив.")
            is TextAssistantResult.ClarifyModel -> {
                Text("Уточните серию локомотива, не меняя рабочий выбор.")
                result.choices.sortedBy { it.value }.forEach { model ->
                    OutlinedButton(onClick = { onClarify(model) }) {
                        Text(assistantModelTitle(model))
                    }
                }
            }
            is TextAssistantResult.UnpublishedModel ->
                Text("Материалы " + assistantModelTitle(result.modelId) +
                    " пока не опубликованы.")
            is TextAssistantResult.NoMatches -> Text(result.reason)
            is TextAssistantResult.Matches -> {
                Text("Найдено: " + result.hits.size,
                    style = MaterialTheme.typography.titleMedium)
                if (result.scope.modelId != workingModelId) {
                    Text("Поиск по " + assistantModelTitle(result.scope.modelId) +
                        "; рабочий локомотив не изменён.")
                }
                result.hits.take(visibleCount).forEach { hit ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(14.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Text(hit.entry.title, style = MaterialTheme.typography.titleMedium)
                            hit.entry.summary?.takeIf { it.isNotBlank() }?.let {
                                Text(it, style = MaterialTheme.typography.bodyMedium)
                            }
                            Text(if (hit.sourceVerified) "Источник подтверждён"
                                else "Подтверждение первоисточника отсутствует")
                            OutlinedButton(onClick = {
                                onOpen(result, ContentTarget(hit.entry.id, hit.entry.type))
                            }) { Text("Открыть карточку") }
                        }
                    }
                }
                if (result.hits.size > visibleCount) {
                    TextButton(onClick = onShowMore) { Text("Показать ещё") }
                }
            }
            null -> Unit
        }
        if (submitted.isNotBlank() && commonHits.isNotEmpty()) {
            Text("Справочные материалы из Test- · требуют проверки",
                style = MaterialTheme.typography.titleMedium)
            Text("Справка доступна для чтения, но не является разрешением на действия. " +
                "Редакции и происхождение источников проверяются отдельно.")
            commonHits.take(visibleCount).forEach { hit ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(hit.card.title, style = MaterialTheme.typography.titleMedium)
                        Text(hit.card.summary)
                        Text("Раздел: " + hit.destination.title)
                        Text("Источник требует проверки. Неподтверждённые действия не показываются.")
                        OutlinedButton(onClick = {
                            onOpenCommon(hit.destination, hit.card.id)
                        }) { Text("Читать справочную карточку") }
                    }
                }
            }
            if (commonHits.size > visibleCount) {
                TextButton(onClick = onShowMore) { Text("Показать ещё справочные материалы") }
            }
        }
        if (submitted.isNotBlank() && commonLoadFailed) {
            Text("Справочный каталог недоступен: не удалось проверить его целостность.")
        }
    }
}

@Composable
private fun AssistantCategoryButton(title: String, selected: Boolean, onClick: () -> Unit) {
    if (selected) Button(onClick = onClick) { Text(title) }
    else OutlinedButton(onClick = onClick) { Text(title) }
}
