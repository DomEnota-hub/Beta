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
import ru.railbrake.calculator.designsystem.RailContentEntryScreen
import ru.railbrake.calculator.navigation.featureDestination
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/** Loading is keyed by execution, so an old model's snapshot is never shown for a new selection. */
private sealed interface FamilyCatalogLoadState {
    data object Idle : FamilyCatalogLoadState
    data object Loading : FamilyCatalogLoadState
    data class Ready(val snapshot: FamilyContentCatalog.Snapshot) : FamilyCatalogLoadState
    data object Failed : FamilyCatalogLoadState
}

/** Separate summary-only donor evidence; never an action or a published diagnostic. */
private sealed interface ReferencePreviewLoadState {
    data object Idle : ReferencePreviewLoadState
    data object Loading : ReferencePreviewLoadState
    data class Ready(val entries: List<FamilyReferencePreview>) : ReferencePreviewLoadState
    data object Failed : ReferencePreviewLoadState
}

/** Safe family-specific entry point; does not execute diagnostic candidates. */
@Composable
fun FamilyContentScreen(
    modelId: ModelId,
    modelTitle: String,
    destination: ShellHomeDestination,
    assets: AssetManager,
    initialExecutionId: String? = null,
    initialReferenceId: String? = null,
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
    var selectedExecution by rememberSaveable(modelId.value, destination.name, initialExecutionId) {
        mutableStateOf(initialExecutionId)
    }
    val repository = remember(assets) { FamilyContentCatalog(assets) }
    val execution = selectedExecution?.let(::VariantId)
    // Do not parse potentially large family catalogs on the Compose/UI thread.
    // Do not load anything before an explicit execution selection or for diagnostics,
    // which still require a separately reviewed graph and safety gate.
    var loadState by remember(profile, execution, destination, repository) {
        mutableStateOf<FamilyCatalogLoadState>(FamilyCatalogLoadState.Idle)
    }
    LaunchedEffect(profile, execution, destination, repository) {
        if (!FamilyCatalogLoadPolicy.shouldLoad(profile, execution, destination)) {
            return@LaunchedEffect
        }
        loadState = FamilyCatalogLoadState.Loading
        try {
            val loaded = withContext(Dispatchers.IO) { repository.load(profile) }
            loadState = FamilyCatalogLoadState.Ready(loaded)
        } catch (cancelled: CancellationException) {
            throw cancelled // A superseded model/execution must never publish stale results.
        } catch (_: Exception) {
            loadState = FamilyCatalogLoadState.Failed
        }
    }
    // Load a tiny allowlisted, non-actionable summary set independently of the
    // unpublished family packs. Unknown execution or diagnostics never read it.
    var referenceState by remember(profile, execution, destination, assets) {
        mutableStateOf<ReferencePreviewLoadState>(ReferencePreviewLoadState.Idle)
    }
    LaunchedEffect(profile, execution, destination, assets) {
        if (!FamilyCatalogLoadPolicy.shouldLoad(profile, execution, destination) ||
            destination != ShellHomeDestination.ATLAS) return@LaunchedEffect
        referenceState = ReferencePreviewLoadState.Loading
        try {
            val summaries = withContext(Dispatchers.IO) {
                FamilyReferencePreviewCatalog(assets).load()
            }
            referenceState = ReferencePreviewLoadState.Ready(summaries)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            referenceState = ReferencePreviewLoadState.Failed
        }
    }
    var referenceQuery by rememberSaveable(modelId.value, destination.name) {
        mutableStateOf("")
    }
    val referencePreviews = remember(referenceState, profile, execution, destination, referenceQuery) {
        FamilyReferencePreviewPolicy.search(
            (referenceState as? ReferencePreviewLoadState.Ready)?.entries.orEmpty(),
            profile, execution, destination, referenceQuery,
        )
    }
    val snapshot = (loadState as? FamilyCatalogLoadState.Ready)?.snapshot
    val visible = remember(snapshot, execution, destination) {
        if (snapshot == null) emptyList()
        else repository.visible(snapshot, profile, execution, types)
    }
    var openedId by rememberSaveable(modelId.value, destination.name) { mutableStateOf<String?>(null) }
    var openedReferenceId by rememberSaveable(modelId.value, destination.name, initialReferenceId) {
        mutableStateOf(initialReferenceId)
    }
    var notice by remember { mutableStateOf<String?>(null) }
    val opened = visible.firstOrNull { it.id.value == openedId }
    // Deep links must be checked against the full scoped catalog, not against
    // a stale user-entered list filter. Model, execution and provenance gates remain.
    val openedReference = remember(referenceState, profile, execution, destination, openedReferenceId) {
        FamilyReferencePreviewPolicy.search(
            (referenceState as? ReferencePreviewLoadState.Ready)?.entries.orEmpty(),
            profile, execution, destination, "",
        ).firstOrNull { it.id == openedReferenceId }
    }
    BackHandler {
        when {
            openedReferenceId != null -> {
                if (initialReferenceId != null) onBack() else openedReferenceId = null
            }
            openedId != null -> openedId = null
            else -> onBack()
        }
    }
    if (opened != null) {
        RailContentEntryScreen(
            entry = opened, destination = opened.type.featureDestination(),
            modelTitle = modelTitle, notice = notice,
            onBack = { openedId = null },
            onLink = { notice = "Связанная карточка не открыта: отдельная проверка источника и исполнения ещё не выполнена." },
        )
        return
    }
    if (openedReference != null) {
        Column(
            modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("Справочный материал · не инструкция к действию",
                style = MaterialTheme.typography.titleMedium)
            Text(openedReference.title, style = MaterialTheme.typography.headlineSmall)
            Text(openedReference.summary)
            Text(if (openedReference.scope == ReferenceScope.EXECUTION_UNVERIFIED)
                "Применимость к выбранному исполнению НЕ подтверждена."
            else "Исполнение указано в донорском каталоге; нормативный допуск НЕ подтверждён.")
            Text("Происхождение: технический каталог Test-. " +
                "Актуальность источника и право выполнять действия не подтверждены.")
            Text("Это описание оборудования, а не диагностический алгоритм или карта приёмки.")
            TextButton(onClick = {
                if (initialReferenceId != null) onBack() else openedReferenceId = null
            }) { Text(if (initialReferenceId != null) "← К поиску" else "← К списку") }
        }
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
                onClick = { selectedExecution = option.id.value; openedId = null; openedReferenceId = null },
                modifier = Modifier.fillMaxWidth(),
            ) { Text((if (selectedExecution == option.id.value) "✓ " else "") + option.title) }
        }
        when {
            selectedExecution == null ->
                Text("Исполнение не указано. Доступ к материалам закрыт.")
            profile.executions.none { it.id.value == selectedExecution } ->
                Text("Неизвестное исполнение. Доступ к материалам закрыт.")
            destination == ShellHomeDestination.DIAGNOSTICS ->
                Text("Диагностические сценарии этого семейства пока не опубликованы: требуется отдельная проверка источников, графа и безопасности.")
            loadState is FamilyCatalogLoadState.Idle ||
                loadState is FamilyCatalogLoadState.Loading ->
                Text("Загрузка каталога выбранного исполнения…")
            loadState is FamilyCatalogLoadState.Failed ->
                Text("Не удалось проверить каталог. Доступ закрыт.")
            snapshot == null ->
                Text("Каталог выбранного исполнения недоступен.")
            visible.isEmpty() ->
                Text("Подтверждённых опубликованных карточек для выбранного исполнения пока нет. Ниже могут быть отдельные справочные описания из Test-; они не являются порядком действий.")
            else -> {
                Text("Подтверждённые информационные материалы", style = MaterialTheme.typography.titleMedium)
                visible.forEach { entry ->
                    Button(onClick = { openedId = entry.id.value; notice = null },
                        modifier = Modifier.fillMaxWidth()) { Text(entry.title) }
                    entry.summary?.let { Text(it) }
                }
            }
        }
        if (destination == ShellHomeDestination.ATLAS &&
            execution != null && profile.executions.any { it.id == execution }) {
            if (referenceState is ReferencePreviewLoadState.Ready) {
                Text("Справочные описания из Test- · НЕ инструкция к действию",
                    style = MaterialTheme.typography.titleMedium)
                Text("Это сведения об устройстве, не разрешение на выполнение работ. " +
                    "Нормативная актуальность требует отдельной сверки.")
                OutlinedTextField(
                    value = referenceQuery,
                    onValueChange = { referenceQuery = it },
                    label = { Text("Поиск по справочным описаниям") },
                    singleLine = true,
                    modifier = Modifier.fillMaxWidth(),
                )
                Text("Найдено описаний: ${referencePreviews.size}")
                if (referencePreviews.isEmpty()) Text("Нет совпадений для выбранного исполнения.")
                referencePreviews.forEach { preview ->
                    OutlinedButton(
                        onClick = { openedReferenceId = preview.id },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text(preview.title) }
                    Text(if (preview.scope == ReferenceScope.EXECUTION_UNVERIFIED)
                        "Применимость к выбранному исполнению НЕ подтверждена."
                    else "Исполнение указано в донорском каталоге; нормативный допуск НЕ подтверждён.")
                }
            } else if (referenceState is ReferencePreviewLoadState.Failed) {
                Text("Не удалось открыть отдельные справочные описания из Test-.")
            }
        }
        if (snapshot != null && snapshot.unreadablePacks > 0) {
            Text("Часть пакетов не прошла проверку формата и не допущена к просмотру.")
        }
        TextButton(onClick = onBack) { Text("← На главную") }
    }
}
