package ru.railbrake.calculator.navigation

import ru.railbrake.calculator.domain.ModelId

/**
 * Stage 3 shell routes. A visible button is not proof that its content is published.
 * Unimplemented features and unpublished locomotive profiles always fail closed.
 */
enum class ShellHomeDestination(val title: String, val requiresModel: Boolean) {
    HOME("Главная", false),
    ASSISTANT("Помощник", true),
    CALCULATIONS("Расчёты", false),
    DIAGNOSTICS("Диагностика", true),
    ATLAS("Атлас", true),
    RECORDS("Рабочие записи", false),
    ACCEPTANCE("Приёмка", true),
    KNOWLEDGE("База знаний", false),
    TRAFFIC_SAFETY("Безопасность движения", false),
    OCCUPATIONAL_SAFETY("Охрана труда", false),
    FIRST_AID("Первая помощь", false),
    APPEARANCE("Оформление", false),
    SETTINGS("Настройки", false),
    ABOUT("О приложении", false),
}

sealed interface ShellHomeRoute {
    data class PublishedModelFeature(
        val modelId: ModelId,
        val destination: ShellHomeDestination,
    ) : ShellHomeRoute

    data class Unavailable(
        val destination: ShellHomeDestination,
        val modelId: ModelId?,
    ) : ShellHomeRoute

    data object ModelSelectionRequired : ShellHomeRoute
}

object ShellHomeNavigationPolicy {
    private val publishedFeatures = setOf(
        ShellHomeDestination.ATLAS,
        ShellHomeDestination.DIAGNOSTICS,
        ShellHomeDestination.ACCEPTANCE,
    )

    fun resolve(modelId: String?, destination: ShellHomeDestination): ShellHomeRoute {
        // The shell can show common destinations without inventing a locomotive.
        if (!destination.requiresModel) {
            return ShellHomeRoute.Unavailable(destination, null)
        }
        val selection = ShellNavigationPolicy.resolve(modelId)
        if (selection !is WorkingModelResolution.Selected) {
            return ShellHomeRoute.ModelSelectionRequired
        }
        val model = selection.model
        if (!model.runtimePublished || destination !in publishedFeatures) {
            return ShellHomeRoute.Unavailable(destination, model.id)
        }
        return ShellHomeRoute.PublishedModelFeature(model.id, destination)
    }
}
