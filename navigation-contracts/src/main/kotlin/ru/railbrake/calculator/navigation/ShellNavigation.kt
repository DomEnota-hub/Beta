package ru.railbrake.calculator.navigation

import ru.railbrake.calculator.domain.CommonSection
import ru.railbrake.calculator.domain.LocomotiveFamily
import ru.railbrake.calculator.domain.ModelId

/**
 * Navigation contracts are deliberately independent of Compose and feature modules.
 * Selecting a series never guesses a locomotive execution/variant.
 */
data class WorkingModelDescriptor(
    val id: ModelId,
    val title: String,
    val family: LocomotiveFamily,
    val runtimePublished: Boolean,
)

object WorkingModelCatalog {
    val models: List<WorkingModelDescriptor> = listOf(
        WorkingModelDescriptor(ModelId("vl80s"), "ВЛ80С", LocomotiveFamily.ELECTRIC, true),
        WorkingModelDescriptor(ModelId("2es5k"), "2ЭС5К «Ермак»", LocomotiveFamily.ELECTRIC, false),
        WorkingModelDescriptor(ModelId("3es5k"), "3ЭС5К «Ермак»", LocomotiveFamily.ELECTRIC, false),
        WorkingModelDescriptor(ModelId("chme3"), "ЧМЭ3", LocomotiveFamily.DIESEL, false),
        WorkingModelDescriptor(ModelId("chme3t"), "ЧМЭ3Т", LocomotiveFamily.DIESEL, false),
        WorkingModelDescriptor(ModelId("chme3e"), "ЧМЭ3Э", LocomotiveFamily.DIESEL, false),
        WorkingModelDescriptor(ModelId("tem2"), "ТЭМ2", LocomotiveFamily.DIESEL, false),
        WorkingModelDescriptor(ModelId("tem2u"), "ТЭМ2У", LocomotiveFamily.DIESEL, false),
    )

    fun find(id: ModelId): WorkingModelDescriptor? = models.firstOrNull { it.id == id }
}

sealed interface WorkingModelResolution {
    data object NotSelected : WorkingModelResolution
    data class Selected(val model: WorkingModelDescriptor) : WorkingModelResolution
    data class Unknown(val requestedId: String) : WorkingModelResolution
}

sealed interface ShellDestination {
    data object ChooseWorkingModel : ShellDestination
    data class ModelWorkspace(val modelId: ModelId) : ShellDestination
    data class ModelUnavailable(val modelId: ModelId) : ShellDestination
    data class CommonContent(val section: CommonSection) : ShellDestination
}

data class ShellNavigationState(
    val workingModelId: ModelId? = null,
    val destination: ShellDestination = ShellDestination.ChooseWorkingModel,
)

object ShellNavigationPolicy {
    /** Null means no selection. Unknown IDs are never coerced to VL80S. */
    fun resolve(id: String?): WorkingModelResolution {
        if (id == null) return WorkingModelResolution.NotSelected
        val model = WorkingModelCatalog.models.firstOrNull { it.id.value == id }
            ?: return WorkingModelResolution.Unknown(id)
        return WorkingModelResolution.Selected(model)
    }

    /** Unknown model IDs cannot enter the shell; unpublished packs get no runtime route. */
    fun select(state: ShellNavigationState, requestedId: ModelId): ShellNavigationState? {
        val model = WorkingModelCatalog.find(requestedId) ?: return null
        val route = if (model.runtimePublished) {
            ShellDestination.ModelWorkspace(model.id)
        } else {
            ShellDestination.ModelUnavailable(model.id)
        }
        return state.copy(workingModelId = model.id, destination = route)
    }

    fun enterWorkspace(state: ShellNavigationState): ShellNavigationState? {
        val id = state.workingModelId ?: return null
        val model = WorkingModelCatalog.find(id) ?: return null
        if (!model.runtimePublished) return null
        return state.copy(destination = ShellDestination.ModelWorkspace(id))
    }

    /** Common information is not silently scoped to an arbitrary locomotive. */
    fun openCommon(state: ShellNavigationState, section: CommonSection): ShellNavigationState =
        state.copy(destination = ShellDestination.CommonContent(section))

    fun returnToModelSelection(): ShellNavigationState = ShellNavigationState()
}
