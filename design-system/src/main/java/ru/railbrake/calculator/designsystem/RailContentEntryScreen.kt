package ru.railbrake.calculator.designsystem

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.key
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLink
import ru.railbrake.calculator.domain.LinkType
import ru.railbrake.calculator.navigation.FeatureDestination

@Composable
fun RailContentEntryScreen(
    entry: ContentEntry,
    destination: FeatureDestination,
    modelTitle: String,
    notice: String?,
    extraContent: @Composable () -> Unit = {},
    onBack: (() -> Unit)? = null,
    onLink: (ContentLink) -> Unit,
) {
    RailFeatureScaffold(
        template = destination.visualTemplate(),
        title = entry.title,
        subtitle = "${modelTitle} · ${destination.displayTitle()}",
    ) {
        if (onBack != null) {
            TextButton(onClick = onBack) { Text("← Назад") }
        }
        key(entry.id.value) {
            // Keep the module header fixed; the long model-owned article,
            // acceptance state and canonical cross-feature links all scroll.
            // Keying the viewport resets its position when following a link.
            Column(
                modifier = Modifier
                    .weight(1f)
                    .verticalScroll(rememberScrollState()),
            ) {
                entry.summary?.takeIf { it.isNotBlank() }?.let {
                    Text(
                        text = it,
                        style = MaterialTheme.typography.bodyLarge,
                    )
                }

                if (entry.details.isNotEmpty()) {
                    Column(
                        modifier = Modifier.padding(top = 12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        entry.details.forEach { detail ->
                            Text(
                                text = "• $detail",
                                style = MaterialTheme.typography.bodyMedium,
                            )
                        }
                    }
                }

                if (entry.blocks.isNotEmpty()) {
                    Column(
                        modifier = Modifier.padding(top = 12.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                    ) {
                        entry.blocks.forEach { block ->
                            Column(
                                verticalArrangement = Arrangement.spacedBy(5.dp),
                            ) {
                                Text(
                                    text = block.title,
                                    style = MaterialTheme.typography.titleMedium,
                                )
                                block.lines.forEach { line ->
                                    Text(
                                        text = "• $line",
                                        style = MaterialTheme.typography.bodyMedium,
                                    )
                                }
                            }
                        }
                    }
                }

                extraContent()

                if (!notice.isNullOrBlank()) {
                    HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp))
                    Text(
                        text = notice,
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }

                if (entry.links.isNotEmpty()) {
                    HorizontalDivider(modifier = Modifier.padding(vertical = 12.dp))
                    Column(
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            text = "Связано",
                            style = MaterialTheme.typography.titleMedium,
                        )
                        entry.links.forEach { link ->
                            Button(
                                modifier = Modifier.fillMaxWidth(),
                                onClick = { onLink(link) },
                            ) {
                                Text(link.displayTitle())
                            }
                        }
                    }
                }
            }
        }
    }
}

fun FeatureDestination.displayTitle(): String = when (this) {
    FeatureDestination.DIAGNOSTICS -> "Диагностика"
    FeatureDestination.ATLAS -> "Атлас"
    FeatureDestination.ACCEPTANCE -> "Приёмка"
    FeatureDestination.TECHNICAL_DATA -> "Технические данные"
    FeatureDestination.REFERENCE -> "База знаний"
    FeatureDestination.FIRST_AID -> "Первая помощь"
    FeatureDestination.SAFETY -> "Охрана труда"
}

private fun ContentLink.displayTitle(): String = when (role) {
    "technical-description" -> "Технические данные"
    "normal-parameter" -> "Опорные параметры"
    "related-diagnostic" -> "Связанная диагностика"
    "primary-equipment",
    "related-equipment",
    "describes-equipment",
    "actuates-pantograph" -> "Связанное оборудование"
    else -> when (type) {
        LinkType.RELATED_SCENARIO -> "Связанная диагностика"
        LinkType.EQUIPMENT -> "Связанное оборудование"
        LinkType.ATLAS_SCHEME -> "Связанная схема"
        LinkType.ACCEPTANCE_ITEM -> "Связанная приёмка"
        LinkType.TECHNICAL_DATA -> "Технические данные"
        LinkType.KNOWLEDGE -> "База знаний"
        LinkType.SOURCE -> "Источник"
        LinkType.FIRST_AID -> "Первая помощь"
        LinkType.SAFETY -> "Охрана труда"
    }
}
