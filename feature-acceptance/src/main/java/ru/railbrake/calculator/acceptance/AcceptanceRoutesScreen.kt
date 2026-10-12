package ru.railbrake.calculator.acceptance

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.designsystem.RailFeatureScaffold
import ru.railbrake.calculator.designsystem.RailFeatureTemplate

/** Shared route chooser; order is the order supplied by the model-owned index. */
@Composable
fun AcceptanceRoutesScreen(
    routes: List<ResolvedAcceptanceRoute>,
    modelTitle: String,
    onOpenRoute: (ResolvedAcceptanceRoute) -> Unit,
) {
    RailFeatureScaffold(
        template = RailFeatureTemplate.ACCEPTANCE,
        title = "Приёмка",
        subtitle = modelTitle,
    ) {
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            items(routes, key = { it.route.id }) { resolved ->
                Card(
                    onClick = { onOpenRoute(resolved) },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(resolved.route.title, style = MaterialTheme.typography.titleMedium)
                        Text(
                            "${resolved.items.size} пункт(ов) · ${resolved.route.modeLabel}",
                            style = MaterialTheme.typography.bodyMedium,
                        )
                    }
                }
            }
        }
    }
}
