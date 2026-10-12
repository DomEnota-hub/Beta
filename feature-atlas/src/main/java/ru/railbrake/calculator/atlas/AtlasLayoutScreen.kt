package ru.railbrake.calculator.atlas

import android.graphics.BitmapFactory
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.designsystem.RailFeatureScaffold
import ru.railbrake.calculator.designsystem.RailFeatureTemplate
import ru.railbrake.calculator.domain.ContentTarget

@Composable
fun AtlasLayoutScreen(
    layout: AtlasLayoutMap,
    modelTitle: String,
    onEquipmentTarget: (ContentTarget) -> Unit,
    onPneumaticFlow: (() -> Unit)? = null,
    onElectricalFlow: (() -> Unit)? = null,
    onDiagnosticsCatalog: (() -> Unit)? = null,
    onAcceptanceRoutes: (() -> Unit)? = null,
) {
    var selectedId by remember(layout.id) { mutableStateOf<String?>(null) }
    var expanded by remember(selectedId) { mutableStateOf(false) }
    val image = rememberAtlasBackground(layout.background?.assetPath)

    RailFeatureScaffold(
        template = RailFeatureTemplate.ATLAS,
        title = layout.title,
        subtitle = "$modelTitle · Атлас",
    ) {
        Column(
            modifier = Modifier
                .weight(1f)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = layout.summary,
                style = MaterialTheme.typography.bodyMedium,
            )

            if (onPneumaticFlow != null) {
                Button(
                    onClick = onPneumaticFlow,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Пошаговая пневматика") }
            }
            if (onElectricalFlow != null) {
                Button(
                    onClick = onElectricalFlow,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Функциональные электрические цепи") }
            }
            if (onDiagnosticsCatalog != null) {
                Button(
                    onClick = onDiagnosticsCatalog,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Диагностика · только принятые сценарии") }
            }
            if (onAcceptanceRoutes != null) {
                Button(
                    onClick = onAcceptanceRoutes,
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Приёмка") }
            }

            if (image == null) {
                Text(
                    text = "Фоновая схема временно недоступна.",
                    style = MaterialTheme.typography.bodyMedium,
                )
            } else {
                AtlasHotspotImage(
                    image = image,
                    layout = layout,
                    selectedId = selectedId,
                    onSelect = {
                        selectedId = it.id
                        expanded = false
                    },
                )
            }

            val selected = layout.hotspots.firstOrNull { it.id == selectedId }
            if (selected != null) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(
                        modifier = Modifier.padding(14.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            text = selected.title,
                            style = MaterialTheme.typography.titleMedium,
                        )
                        Text(
                            text = selected.subtitle,
                            style = MaterialTheme.typography.bodyMedium,
                        )
                        Text(
                            text = selected.details,
                            style = MaterialTheme.typography.bodyMedium,
                        )

                        selected.equipmentTarget()?.let { target ->
                            Button(
                                onClick = { onEquipmentTarget(target) },
                                modifier = Modifier.fillMaxWidth(),
                            ) {
                                Text("Подробнее")
                            }
                        }

                        if (
                            selected.equipmentTarget() == null &&
                            selected.learnMore.isNotEmpty()
                        ) {
                            TextButton(onClick = { expanded = !expanded }) {
                                Text(if (expanded) "Скрыть" else "Подробнее")
                            }
                        }

                        if (expanded) {
                            selected.learnMore.forEach { line ->
                                Text(
                                    text = "• $line",
                                    style = MaterialTheme.typography.bodyMedium,
                                )
                            }
                        }
                    }
                }
            }

            Text(
                text = "Схема используется как учебный пространственный ориентир и не заменяет монтажную документацию конкретной секции.",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun AtlasHotspotImage(
    image: ImageBitmap,
    layout: AtlasLayoutMap,
    selectedId: String?,
    onSelect: (AtlasLayoutHotspot) -> Unit,
) {
    val ratio = image.width.toFloat() / image.height.toFloat()

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp)),
    ) {
        val widthDp = maxWidth
        val heightDp = (maxWidth.value / ratio).dp

        Box(
            modifier = Modifier.size(widthDp, heightDp),
        ) {
            Image(
                bitmap = image,
                contentDescription = layout.title,
                modifier = Modifier.size(widthDp, heightDp),
                contentScale = ContentScale.FillBounds,
            )

            layout.hotspots.forEach { hotspot ->
                val bounds = hotspot.bounds
                val isSelected = selectedId == hotspot.id
                val x = (widthDp.value * bounds.left).dp
                val y = (heightDp.value * bounds.top).dp
                val hotspotWidth =
                    (widthDp.value * (bounds.right - bounds.left)).dp
                val hotspotHeight =
                    (heightDp.value * (bounds.bottom - bounds.top)).dp

                Box(
                    modifier = Modifier
                        .offset(x = x, y = y)
                        .size(width = hotspotWidth, height = hotspotHeight)
                        .then(
                            if (isSelected) {
                                Modifier.background(
                                    MaterialTheme.colorScheme.primary.copy(alpha = 0.18f),
                                    RoundedCornerShape(6.dp),
                                )
                            } else {
                                Modifier
                            }
                        )
                        .semantics {
                            contentDescription =
                                "${hotspot.title}. ${hotspot.subtitle}"
                        }
                        .clickable { onSelect(hotspot) },
                )
            }
        }
    }
}

@Composable
private fun rememberAtlasBackground(assetPath: String?): ImageBitmap? {
    val context = LocalContext.current
    return remember(assetPath) {
        if (assetPath.isNullOrBlank()) {
            null
        } else {
            runCatching {
                context.assets.open(assetPath).use { stream ->
                    BitmapFactory.decodeStream(stream)?.asImageBitmap()
                }
            }.getOrNull()
        }
    }
}
