package ru.railbrake.calculator.shell

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.navigation.WorkingModelDescriptor

/**
 * Model-aware shell only: unpublished runtime and not-yet-integrated features
 * are represented by explicit unavailable routes, never by fabricated content.
 * The drawer is available by swipe on this screen; interactive diagrams remain
 * outside the drawer so their gestures cannot accidentally open it.
 */
@Composable
fun ShellHomeScreen(
    model: WorkingModelDescriptor,
    onChangeModel: () -> Unit,
    onOpen: (ShellHomeDestination) -> Unit,
) {
    val drawer = rememberDrawerState(initialValue = DrawerValue.Closed)
    val scope = androidx.compose.runtime.rememberCoroutineScope()
    val openDestination: (ShellHomeDestination) -> Unit = { destination ->
        scope.launch { drawer.close() }
        onOpen(destination)
    }

    ModalNavigationDrawer(
        drawerState = drawer,
        gesturesEnabled = true,
        drawerContent = {
            ModalDrawerSheet {
                Column(
                    modifier = Modifier.verticalScroll(rememberScrollState()).padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(5.dp),
                ) {
                    Text("Рабочие разделы", style = MaterialTheme.typography.titleMedium)
                    listOf(
                        ShellHomeDestination.ASSISTANT,
                        ShellHomeDestination.CALCULATIONS,
                        ShellHomeDestination.DIAGNOSTICS,
                        ShellHomeDestination.ATLAS,
                        ShellHomeDestination.ACCEPTANCE,
                        ShellHomeDestination.RECORDS,
                    ).forEach { destination ->
                        TextButton(onClick = { openDestination(destination) }) {
                            Text(destination.title)
                        }
                    }
                    HorizontalDivider()
                    Text("Общие материалы", style = MaterialTheme.typography.titleMedium)
                    listOf(
                        ShellHomeDestination.KNOWLEDGE,
                        ShellHomeDestination.TRAFFIC_SAFETY,
                        ShellHomeDestination.OCCUPATIONAL_SAFETY,
                        ShellHomeDestination.FIRST_AID,
                    ).forEach { destination ->
                        TextButton(onClick = { openDestination(destination) }) {
                            Text(destination.title)
                        }
                    }
                    HorizontalDivider()
                    listOf(
                        ShellHomeDestination.APPEARANCE,
                        ShellHomeDestination.SETTINGS,
                        ShellHomeDestination.ABOUT,
                    ).forEach { destination ->
                        TextButton(onClick = { openDestination(destination) }) {
                            Text(destination.title)
                        }
                    }
                }
            }
        },
    ) {
        Column(
            modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(14.dp),
        ) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Ассистент", style = MaterialTheme.typography.headlineMedium)
                TextButton(onClick = { scope.launch { drawer.open() } }) { Text("☰ Меню") }
            }
            Text("Рабочий локомотив", style = MaterialTheme.typography.titleMedium)
            OutlinedButton(onClick = onChangeModel, modifier = Modifier.fillMaxWidth()) {
                Text(model.title + " · Сменить")
            }
            if (!model.runtimePublished) {
                Text(
                    "Для этой модели материалы ещё не опубликованы. " +
                        "Разделы остаются доступными для просмотра структуры, без выдачи неподтверждённых инструкций.",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            listOf(
                ShellHomeDestination.ASSISTANT,
                ShellHomeDestination.CALCULATIONS,
                ShellHomeDestination.DIAGNOSTICS,
                ShellHomeDestination.ATLAS,
                ShellHomeDestination.RECORDS,
            ).forEach { destination ->
                Button(
                    onClick = { openDestination(destination) },
                    modifier = Modifier.fillMaxWidth(),
                ) { Text(destination.title) }
            }
        }
    }
}

@Composable
fun ShellUnavailableScreen(
    title: String,
    explanation: String,
    onBack: () -> Unit,
) {
    Column(
        modifier = Modifier.fillMaxSize().padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        Text(title, style = MaterialTheme.typography.headlineSmall)
        Text(explanation, style = MaterialTheme.typography.bodyMedium)
        TextButton(onClick = onBack) { Text("← На главную") }
    }
}
