package ru.railbrake.calculator.acceptance

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
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
import ru.railbrake.calculator.designsystem.RailFeatureScaffold
import ru.railbrake.calculator.designsystem.RailFeatureTemplate
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentEntry

@Composable
fun AcceptanceRouteScreen(
    route: ResolvedAcceptanceRoute,
    modelTitle: String,
    onOpenItem: (CanonicalId) -> Unit,
) {
    val context = LocalContext.current
    val store = remember {
        SharedPreferencesAcceptanceStateStore(context.applicationContext)
    }
    var query by remember(route.route.id) { mutableStateOf("") }

    val states = route.items.associate { entry ->
        entry.id to store.read(entry.id)
    }
    val summary = acceptanceSummary(states.values)
    val visibleItems = remember(route.items, query) {
        route.items.filter { it.matchesAcceptanceQuery(query) }
    }

    RailFeatureScaffold(
        template = RailFeatureTemplate.ACCEPTANCE,
        title = route.route.title,
        subtitle = "${modelTitle} · ${route.route.modeLabel}",
    ) {
        route.route.description?.let {
            Text(
                text = it,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        Text(
            text = buildString {
                append("Проверено: ${summary.checked}")
                append(" · Замечания: ${summary.notes}")
                append(" · Не применяется: ${summary.notApplicable}")
                append(" · Не проверено: ${summary.notChecked}")
            },
            style = MaterialTheme.typography.bodyMedium,
        )

        Text(
            text = when {
                !summary.complete ->
                    "Маршрут не завершён: осталось ${summary.notChecked} пункт(ов)."
                summary.notes > 0 ->
                    "Маршрут завершён с замечаниями."
                else ->
                    "Маршрут завершён."
            },
            style = MaterialTheme.typography.titleSmall,
        )

        OutlinedTextField(
            value = query,
            onValueChange = { query = it },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            label = { Text("Поиск по пунктам") },
            placeholder = { Text("Оборудование, признак или действие") },
        )

        Text(
            text = "Найдено: ${visibleItems.size} из ${route.items.size}",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.testTag("acceptance-found-count"),
        )

        LazyColumn(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            items(
                items = visibleItems,
                key = { it.id.value },
            ) { entry ->
                val itemState = states.getValue(entry.id)
                AcceptanceRouteCard(
                    entry = entry,
                    state = itemState,
                    onOpen = { onOpenItem(entry.id) },
                )
            }
        }
    }
}

@Composable
private fun AcceptanceRouteCard(
    entry: ContentEntry,
    state: AcceptanceItemState,
    onOpen: () -> Unit,
) {
    Card(
        onClick = onOpen,
        modifier = Modifier.fillMaxWidth(),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            Text(
                text = entry.title,
                style = MaterialTheme.typography.titleMedium,
            )
            entry.summary?.let {
                Text(
                    text = it,
                    style = MaterialTheme.typography.bodySmall,
                )
            }
            Text(
                text = state.state.label,
                style = MaterialTheme.typography.labelMedium,
            )
        }
    }
}
