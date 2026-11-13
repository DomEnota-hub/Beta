package ru.railbrake.calculator.shell

import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.assistant.TextQueryParser
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.navigation.ShellNavigationPolicy
import ru.railbrake.calculator.navigation.WorkingModelResolution

/**
 * A selected VL80S or an unambiguous explicit assistant query can trigger
 * the published VL80S runtime bootstrap. Reference-only family models and the model picker must
 * remain usable even if the VL80S pack is missing or malformed.
 */
internal object Vl80sBootstrapPolicy {
    // Defer parsing the large published VL80S pack until a feature actually needs it.
    // Common references, calculations and the home screen remain independent.
    private val runtimeDestinations = setOf(
        ShellHomeDestination.ASSISTANT,
        ShellHomeDestination.ATLAS,
        ShellHomeDestination.DIAGNOSTICS,
        ShellHomeDestination.ACCEPTANCE,
    )

    fun shouldRequest(
        selectedModelId: String?,
        destination: ShellHomeDestination,
        submittedQuery: String = "",
    ): Boolean {
        if (destination !in runtimeDestinations) return false
        if (shouldLoad(selectedModelId)) return true
        if (destination != ShellHomeDestination.ASSISTANT ||
            ShellNavigationPolicy.resolve(selectedModelId) !is WorkingModelResolution.Selected ||
            !shouldLoad("vl80s")) return false
        val parsed = TextQueryParser.parse(submittedQuery)
        return parsed.explicitModels == setOf(ModelId("vl80s")) &&
            !parsed.vl80SeriesUnspecified && !parsed.ermakUnspecified &&
            parsed.searchText.isNotBlank()
    }

    fun shouldLoad(selectedModelId: String?): Boolean {
        val resolved = ShellNavigationPolicy.resolve(selectedModelId)
        return resolved is WorkingModelResolution.Selected &&
            resolved.model.id == ModelId("vl80s") &&
            resolved.model.runtimePublished
    }
}
