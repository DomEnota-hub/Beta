package ru.railbrake.calculator.shell

import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.navigation.ShellNavigationPolicy
import ru.railbrake.calculator.navigation.WorkingModelResolution

/**
 * Only an explicitly selected, published VL80S can trigger its expensive
 * runtime bootstrap. Reference-only family models and the model picker must
 * remain usable even if the VL80S pack is missing or malformed.
 */
internal object Vl80sBootstrapPolicy {
    fun shouldLoad(selectedModelId: String?): Boolean {
        val resolved = ShellNavigationPolicy.resolve(selectedModelId)
        return resolved is WorkingModelResolution.Selected &&
            resolved.model.id == ModelId("vl80s") &&
            resolved.model.runtimePublished
    }
}
