package ru.railbrake.calculator.acceptance

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.designsystem.RailContentEntryScreen
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLink
import ru.railbrake.calculator.navigation.FeatureDestination

@Composable
fun AcceptanceItemScreen(
    entry: ContentEntry,
    modelTitle: String,
    notice: String?,
    onLink: (ContentLink) -> Unit,
    onBack: (() -> Unit)? = null,
) {
    val context = LocalContext.current
    val store = remember {
        SharedPreferencesAcceptanceStateStore(context.applicationContext)
    }
    var itemState by remember(entry.id.value) {
        mutableStateOf(store.read(entry.id))
    }

    fun save(next: AcceptanceItemState) {
        store.write(entry.id, next)
        itemState = next
    }

    RailContentEntryScreen(
        entry = entry,
        destination = FeatureDestination.ACCEPTANCE,
        modelTitle = modelTitle,
        notice = notice,
        extraContent = {
            Column(
                modifier = Modifier.fillMaxWidth(),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                Text(
                    text = "Пункт: ${entry.title}",
                    style = MaterialTheme.typography.titleMedium,
                )
                Text(
                    text = "Статус: ${itemState.state.label}",
                    style = MaterialTheme.typography.titleMedium,
                )

                LazyRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                ) {
                    items(AcceptanceCheckState.entries) { option ->
                        FilterChip(
                            selected = itemState.state == option,
                            onClick = {
                                save(itemState.copy(state = option))
                            },
                            label = { Text(option.label) },
                        )
                    }
                }

                if (itemState.state == AcceptanceCheckState.NOTE) {
                    OutlinedTextField(
                        value = itemState.note,
                        onValueChange = { value ->
                            save(itemState.copy(note = value))
                        },
                        modifier = Modifier.fillMaxWidth().testTag("acceptance-note"),
                        minLines = 3,
                        maxLines = 6,
                        label = { Text("Замечание") },
                        placeholder = { Text("Что обнаружено при проверке") },
                    )
                }
            }
        },
        onLink = onLink,
        onBack = onBack,
    )
}
