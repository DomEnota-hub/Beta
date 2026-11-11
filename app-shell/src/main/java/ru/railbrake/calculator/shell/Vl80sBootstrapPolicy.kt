package ru.railbrake.calculator.shell

import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.navigation.ShellNavigationPolicy
import ru.railbrake.calculator.navigation.WorkingModelResolution

/**
 * Only an explicitly selected, published VL80S can trigger its expensive
 * runtime bootstrap. Reference-only family models and the model picker must
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

    fun shouldRequest(selectedModelId: String?, destination: ShellHomeDestination): Boolean =
        destination in runtimeDestinations && shouldLoad(selectedModelId)

    fun shouldLoad(selectedModelId: String?): Boolean {
        val resolved = ShellNavigationPolicy.resolve(selectedModelId)
        return resolved is WorkingModelResolution.Selected &&
            resolved.model.id == ModelId("vl80s") &&
            resolved.model.runtimePublished
    }
}
