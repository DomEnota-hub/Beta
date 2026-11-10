package ru.railbrake.calculator.shell

import android.content.res.AssetManager
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Button
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.designsystem.RailContentEntryScreen
import ru.railbrake.calculator.navigation.featureDestination
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination

/** Safe family-specific entry point; does not execute diagnostic candidates. */
@Composable
fun FamilyContentScreen(
    modelId: ModelId,
    modelTitle: String,
    destination: ShellHomeDestination,
    assets: AssetManager,
    onBack: () -> Unit,
) {
    val profile = remember(modelId) { FamilyProfiles.forModel(modelId) }
    if (profile == null) {
        ShellUnavailableScreen("Материалы недоступны", "Модель не распознана.", onBack)
        return
    }
    val types = when (destination) {
        ShellHomeDestination.ATLAS -> setOf(ContentType.EQUIPMENT, ContentType.ATLAS_SCHEME,
            ContentType.TECHNICAL_DATA, ContentType.KNOWLEDGE)
        ShellHomeDestination.ACCEPTANCE -> setOf(ContentType.ACCEPTANCE_ITEM)
        else -> emptySet() // Diagnostic flows require a separate graph + safety gate.
    }
    var selectedExecution by rememberSaveable(modelId.value, destination.name) {
        mutableStateOf<String?>(null)
    }
    val repository = remember(assets) { FamilyContentCatalog(assets) }
    val snapshot = remember(profile) {
        runCatching { repository.load(profile) }.getOrNull()
    }
    val execution = selectedExecution?.let(::VariantId)
    val visible = remember(snapshot, execution, destination) {
        if (snapshot == null) emptyList()
        else repository.visible(snapshot, profile, execution, types)
    }
    var openedId by rememberSaveable(modelId.value, destination.name) { mutableStateOf<String?>(null) }
    var notice by remember { mutableStateOf<String?>(null) }
    val opened = visible.firstOrNull { it.id.value == openedId }
    BackHandler { if (openedId != null) openedId = null else onBack() }
    if (opened != null) {
        RailContentEntryScreen(
            entry = opened, destination = opened.type.featureDestination(),
            modelTitle = modelTitle, notice = notice,
            onBack = { openedId = null },
            onLink = { notice = "Связанная карточка не открыта: отдельная проверка источника и исполнения ещё не выполнена." },
        )
        return
    }
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text("$modelTitle · ${destination.title}", style = MaterialTheme.typography.headlineSmall)
        Text("Выберите точное исполнение для этого раздела. Выбор рабочей модели не определяет исполнение автоматически.")
        profile.executions.forEach { option ->
            OutlinedButton(
                onClick = { selectedExecution = option.id.value; openedId = null },
                modifier = Modifier.fillMaxWidth(),
            ) { Text((if (selectedExecution == option.id.value) "✓ " else "") + option.title) }
        }
        when {
            selectedExecution == null ->
                Text("Исполнение не указано. Доступ к материалам закрыт.")
            destination == ShellHomeDestination.DIAGNOSTICS ->
                Text("Диагностические сценарии этого семейства пока не опубликованы: требуется отдельная проверка источников, графа и безопасности.")
            snapshot == null ->
                Text("Не удалось проверить каталог. Доступ закрыт.")
            visible.isEmpty() ->
                Text("Подтверждённых опубликованных карточек для выбранного исполнения пока нет. Исследовательские материалы не показываются.")
            else -> {
                Text("Подтверждённые информационные материалы", style = MaterialTheme.typography.titleMedium)
                visible.forEach { entry ->
                    Button(onClick = { openedId = entry.id.value; notice = null },
                        modifier = Modifier.fillMaxWidth()) { Text(entry.title) }
                    entry.summary?.let { Text(it) }
                }
            }
        }
        if (snapshot != null && snapshot.unreadablePacks > 0) {
            Text("Часть пакетов не прошла проверку формата и не допущена к просмотру.")
        }
        TextButton(onClick = onBack) { Text("← На главную") }
    }
}
