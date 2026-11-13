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
import androidx.compose.material3.TextButton
import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
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
    val context = LocalContext.current
    val legacy = context.getSharedPreferences("technical_acceptance_states", Context.MODE_PRIVATE)
    val preferences = context.getSharedPreferences("railbrake_acceptance_state_v1", Context.MODE_PRIVATE)
    val availableIds = routes.map { it.route.id }.toSet()
    var resumeId by remember(availableIds) {
        mutableStateOf(LegacyAcceptanceSession.currentResumeRouteId(preferences.all, legacy.all, availableIds))
    }
    fun openRoute(route: ResolvedAcceptanceRoute) {
        val id = route.route.id
        if (LegacyAcceptanceSession.isKnownRoute(id) && id in availableIds) {
            preferences.edit()
                .putBoolean(LegacyAcceptanceSession.handledKey, true)
                .putString(LegacyAcceptanceSession.currentRouteKey, id)
                .apply()
            resumeId = id
        }
        onOpenRoute(route)
    }
    fun dismissResume() {
        preferences.edit()
            .putBoolean(LegacyAcceptanceSession.handledKey, true)
            .remove(LegacyAcceptanceSession.currentRouteKey)
            .apply()
        resumeId = null
    }
    val resume = routes.firstOrNull { it.route.id == resumeId }
    RailFeatureScaffold(
        template = RailFeatureTemplate.ACCEPTANCE,
        title = "Приёмка",
        subtitle = modelTitle,
    ) {
        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            if (resume != null) {
                item(key = "legacy-resume") {
                    Card(
                        onClick = { openRoute(resume) },
                        modifier = Modifier.fillMaxWidth().testTag("acceptance-legacy-resume"),
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Продолжить маршрут", style = MaterialTheme.typography.titleMedium)
                            Text(resume.route.title, style = MaterialTheme.typography.bodyMedium)
                            Text("Отметки проверяются по текущему списку Beta.")
                            TextButton(onClick = { dismissResume() }) {
                                Text("Убрать из продолжения")
                            }
                        }
                    }
                }
            }
            items(routes, key = { it.route.id }) { resolved ->
                Card(
                    onClick = { openRoute(resolved) },
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
