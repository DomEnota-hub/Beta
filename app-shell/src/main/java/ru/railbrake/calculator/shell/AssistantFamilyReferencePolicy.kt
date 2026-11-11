package ru.railbrake.calculator.shell

import ru.railbrake.calculator.assistant.TextIntent
import ru.railbrake.calculator.assistant.TextQueryParser
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination

/**
 * Search donor equipment summaries in a separate read-only lane.
 * An explicit model request does not change the working locomotive.
 * A model selection NEVER implies an execution/serial selection.
 */
internal data class AssistantFamilyQuery(
    val profile: FamilyModelProfile,
    val searchText: String,
)

internal object AssistantFamilyReferencePolicy {
    fun resolveQuery(
        text: String,
        workingModel: ModelId,
        category: AssistantSearchCategory?,
    ): AssistantFamilyQuery? {
        if (text.isBlank() || (category != null && category != AssistantSearchCategory.EQUIPMENT)) {
            return null
        }
        val parsed = TextQueryParser.parse(text)
        if (parsed.intent != TextIntent.REFERENCE || parsed.ermakUnspecified ||
            parsed.vl80SeriesUnspecified ||
            parsed.explicitModels.size > 1 || parsed.searchText.isBlank()) return null
        val model = parsed.explicitModels.singleOrNull() ?: workingModel
        val profile = FamilyProfiles.forModel(model) ?: return null
        return AssistantFamilyQuery(profile, parsed.searchText)
    }

    fun search(
        entries: List<FamilyReferencePreview>,
        query: AssistantFamilyQuery?,
        execution: VariantId?,
        limit: Int = 50,
    ): List<FamilyReferencePreview> {
        if (query == null || execution == null) return emptyList()
        return FamilyReferencePreviewPolicy.search(
            entries, query.profile, execution, ShellHomeDestination.ATLAS,
            query.searchText,
        ).take(limit.coerceIn(1, 50))
    }
}
