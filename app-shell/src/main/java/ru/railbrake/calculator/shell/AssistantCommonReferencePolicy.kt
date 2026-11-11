package ru.railbrake.calculator.shell

import ru.railbrake.calculator.assistant.TextIntent
import ru.railbrake.calculator.assistant.TextQueryParser
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.navigation.ShellHomeDestination
import ru.railbrake.calculator.safety.CommonReferenceCard
import ru.railbrake.calculator.safety.CommonReferencePolicy

/**
 * A separate READ-ONLY assistant search lane for the already visible donor
 * common references. These hits never enter ContentRegistry's published index,
 * never become executable and cannot be opened through AssistantUiNavigationGate.
 */
internal data class AssistantCommonReferenceHit(
    val destination: ShellHomeDestination,
    val card: CommonReferenceCard,
)

internal object AssistantCommonReferencePolicy {
    private val sections = listOf(
        ShellHomeDestination.KNOWLEDGE,
        ShellHomeDestination.TRAFFIC_SAFETY,
        ShellHomeDestination.OCCUPATIONAL_SAFETY,
        ShellHomeDestination.FIRST_AID,
    )

    fun search(
        entries: List<ContentEntry>,
        query: String,
        category: AssistantSearchCategory?,
        limit: Int = 50,
    ): List<AssistantCommonReferenceHit> {
        if (query.isBlank() || (category != null && category != AssistantSearchCategory.KNOWLEDGE)) {
            return emptyList()
        }
        val parsed = TextQueryParser.parse(query)
        // A named locomotive or an ambiguous Ermak is a model-specific request:
        // do not substitute general safety/knowledge for a requested model card.
        if (parsed.explicitModels.isNotEmpty() || parsed.ermakUnspecified ||
            parsed.searchText.isBlank() ||
            parsed.intent in setOf(TextIntent.DIAGNOSTICS, TextIntent.SCHEME, TextIntent.ACCEPTANCE)
        ) return emptyList()

        val allowed = if (category == AssistantSearchCategory.KNOWLEDGE) {
            sections.take(2)
        } else sections
        return allowed.asSequence().flatMap { destination ->
            CommonReferencePolicy.search(
                CommonReferencePolicy.cards(entries, destination), parsed.searchText,
            ).asSequence().map { AssistantCommonReferenceHit(destination, it) }
        }.distinctBy { it.card.id }
            .sortedWith(compareBy({ it.destination.name }, { it.card.title }, { it.card.id }))
            .take(limit.coerceIn(1, 50))
            .toList()
    }
}
