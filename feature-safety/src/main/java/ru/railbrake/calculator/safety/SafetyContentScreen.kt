package ru.railbrake.calculator.safety

import androidx.compose.runtime.Composable
import ru.railbrake.calculator.designsystem.RailContentEntryScreen
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLink
import ru.railbrake.calculator.navigation.FeatureDestination

@Composable
fun SafetyContentScreen(
    entry: ContentEntry,
    modelTitle: String?,
    notice: String?,
    onLink: (ContentLink) -> Unit,
    onBack: (() -> Unit)? = null,
) {
    RailContentEntryScreen(
        entry = entry,
        destination = FeatureDestination.SAFETY,
        modelTitle = modelTitle ?: "Общий раздел",
        notice = notice,
        onLink = onLink,
        onBack = onBack,
    )
}
