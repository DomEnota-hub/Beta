package ru.railbrake.calculator.atlas

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.designsystem.RailFeatureScaffold
import ru.railbrake.calculator.designsystem.RailFeatureTemplate
import ru.railbrake.calculator.domain.ContentTarget

/** Shared candidate preview. It is deliberately absent from the published navigation index. */
@Composable
fun AtlasCandidatePairScreen(
    route: AtlasPairRoute,
    modelTitle: String,
    actualVariantId: String?,
    onBack: () -> Unit,
    onEquipmentTarget: (ContentTarget) -> Unit,
) {
    var stepIndex by remember(route.sequenceEntryId) { mutableIntStateOf(0) }
    var selectedNodeKey by remember(route.sequenceEntryId) { mutableStateOf<String?>(null) }
    val step = route.steps[stepIndex]
    val selected = route.nodes.firstOrNull { it.key == selectedNodeKey }

    RailFeatureScaffold(
        template = RailFeatureTemplate.ATLAS,
        title = route.title,
        subtitle = "$modelTitle · учебная функциональная схема",
    ) {
        Column(
            modifier = Modifier.weight(1f).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            TextButton(onClick = onBack) { Text("← В Атлас") }
            Text(route.functionalDisclaimer, style = MaterialTheme.typography.bodySmall)
            Text("Шаг ${stepIndex + 1} из ${route.steps.size}: ${step.title}",
                style = MaterialTheme.typography.titleMedium)
            Text(step.explanation)
            AtlasCandidateNodes(route, step.activeNodeKeys) { selectedNodeKey = it.key }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { stepIndex-- }, enabled = stepIndex > 0) { Text("Назад") }
                Button(onClick = { stepIndex++ }, enabled = stepIndex + 1 < route.steps.size) {
                    Text("Далее")
                }
            }
            selected?.let { node ->
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(node.label, style = MaterialTheme.typography.titleMedium)
                        route.equipmentTarget(node.key, actualVariantId)?.let { target ->
                            Button(onClick = { onEquipmentTarget(target) }) { Text("Карточка оборудования") }
                        }
                    }
                }
            }
            Text(
                "Координаты показывают учебную раскладку на экране, не физическое расположение " +
                    "оборудования и не монтажную трассу. Материал кандидата не разрешает действий.",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun AtlasCandidateNodes(
    route: AtlasPairRoute,
    active: Set<String>,
    onSelect: (AtlasPairNode) -> Unit,
) {
    val minX = route.nodes.minOf { it.bounds.x }
    val minY = route.nodes.minOf { it.bounds.y }
    val width = route.nodes.maxOf { it.bounds.x + it.bounds.width } - minX
    val height = route.nodes.maxOf { it.bounds.y + it.bounds.height } - minY
    BoxWithConstraints(modifier = Modifier.fillMaxWidth().height(300.dp)) {
        val displayWidth = maxWidth.value
        val displayHeight = 300f
        route.nodes.forEach { node ->
            val bounds = node.bounds
            val x = ((bounds.x - minX) / width * displayWidth).dp
            val y = ((bounds.y - minY) / height * displayHeight).dp
            val w = (bounds.width / width * displayWidth).dp
            val h = (bounds.height / height * displayHeight).dp
            Box(
                modifier = Modifier.offset(x, y).size(w, h)
                    .clip(RoundedCornerShape(5.dp))
                    .background(if (node.key in active) MaterialTheme.colorScheme.primaryContainer
                                else MaterialTheme.colorScheme.surfaceVariant)
                    .clickable { onSelect(node) }
                    .semantics { contentDescription = node.label },
            ) {
                Text(node.label, modifier = Modifier.padding(4.dp),
                    style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}
