package ru.railbrake.calculator.shell

import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination

/**
 * Stage 13: never start family asset loading until the user explicitly selected
 * a registered execution. Diagnostic graphs have a separate safety/publication gate.
 * This policy only controls *when* to read assets, not whether they are publishable.
 */
internal object FamilyCatalogLoadPolicy {
    fun shouldLoad(
        profile: FamilyModelProfile,
        execution: VariantId?,
        destination: ShellHomeDestination,
    ): Boolean =
        execution != null &&
            profile.executions.any { it.id == execution } &&
            destination in setOf(ShellHomeDestination.ATLAS, ShellHomeDestination.ACCEPTANCE)
}
