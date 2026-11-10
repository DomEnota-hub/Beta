package ru.railbrake.calculator.safety

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
import androidx.compose.material3.OutlinedButton
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
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.navigation.ShellHomeDestination

private sealed interface CommonReferenceLoadState {
    data object Loading : CommonReferenceLoadState
    data class Ready(val entries: List<ContentEntry>) : CommonReferenceLoadState
    data object Failed : CommonReferenceLoadState
}

/**
 * Common sections work with any selected working locomotive and do not infer
 * the locomotive's execution. Candidate text is shown as a marked reference,
 * never as an executable workflow or an approved first-aid algorithm.
 */
@Composable
fun CommonReferenceScreen(
    destination: ShellHomeDestination,
    assets: AssetManager,
    onBack: () -> Unit,
) {
    var loadState by remember(assets) {
        mutableStateOf<CommonReferenceLoadState>(CommonReferenceLoadState.Loading)
    }
    LaunchedEffect(assets) {
        loadState = CommonReferenceLoadState.Loading
        try {
            val entries = withContext(Dispatchers.IO) { CommonReferenceCatalog(assets).load() }
            loadState = CommonReferenceLoadState.Ready(entries)
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (_: Exception) {
            loadState = CommonReferenceLoadState.Failed
        }
    }
    val cards = remember(loadState, destination) {
        val entries = (loadState as? CommonReferenceLoadState.Ready)?.entries.orEmpty()
        CommonReferencePolicy.cards(entries, destination)
    }
    var openedId by rememberSaveable(destination.name) { mutableStateOf<String?>(null) }
    val opened = cards.firstOrNull { it.id == openedId }
    BackHandler { if (opened != null) openedId = null else onBack() }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(destination.title, style = MaterialTheme.typography.headlineSmall)
        Text(
            "Справочные сведения из Test-. Источники и действующие редакции требуют проверки. " +
                "Это не подтверждение допуска к выполнению работ или действий.",
            style = MaterialTheme.typography.bodyMedium,
        )
        if (destination == ShellHomeDestination.FIRST_AID) {
            Text(
                "При непосредственной угрозе жизни вызывайте 112 или 103. " +
                    "Алгоритмы первой помощи из непроверенного донорского пакета здесь не опубликованы.",
                style = MaterialTheme.typography.bodyMedium,
            )
        }
        when {
            loadState is CommonReferenceLoadState.Loading ->
                Text("Загрузка справочных материалов…")
            loadState is CommonReferenceLoadState.Failed ->
                Text("Не удалось проверить целостность общих пакетов. Справочный каталог не открыт.")
            cards.isEmpty() ->
                Text("В этом разделе пока нет проверенных для справочного просмотра материалов.")
            opened != null -> {
                TextButton(onClick = { openedId = null }) { Text("← К списку") }
                Text(opened.title, style = MaterialTheme.typography.titleLarge)
                Text(opened.summary)
                if (opened.details.isNotEmpty()) {
                    Text("Исходный справочный текст · требует проверки",
                        style = MaterialTheme.typography.titleMedium)
                    opened.details.forEach { Text(it) }
                }
                Text("Источник: статус актуальности не подтверждён.",
                    style = MaterialTheme.typography.bodyMedium)
                opened.sources.forEach { source -> Text(source) }
                Text(
                    "Не используйте эту карточку как разрешение на действия. " +
                        "Порядок работы и противопоказания определяются применимыми действующими документами.",
                )
            }
            else -> {
                Text("Справочные карточки: ${cards.size}", style = MaterialTheme.typography.titleMedium)
                cards.forEach { card ->
                    OutlinedButton(
                        onClick = { openedId = card.id },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text(card.title) }
                    Text(card.summary, style = MaterialTheme.typography.bodySmall)
                }
            }
        }
        TextButton(onClick = onBack) { Text("← На главную") }
    }
}
