package ru.railbrake.calculator.diagnostics

import java.util.Locale
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.runtime.ContentRegistry

/**
 * A deliberately non-executable view of donor diagnostic titles and summaries.
 * A CANDIDATE is readable knowledge, never an approved diagnostic action.
 *
 * Do NOT expose ExecutableDiagnosticScenario, checks, actions, graph edges or
 * depot repair instructions through this interface. The actual execution path
 * remains exclusively in PublishedDiagnosticCatalog and its source/profile gate.
 */
data class DiagnosticReferencePreview(
    val id: String,
    val title: String,
    val summary: String,
    val category: String,
    val sourceNotice: String,
    val variantNotice: String?,
)

class DiagnosticReferenceCatalog(
    runtime: ExecutableDiagnosticRuntime,
    registry: ContentRegistry,
    context: RuntimeContext,
) {
    private val references: List<DiagnosticReferencePreview> = if (
        context.contentModelId != ModelId(runtime.modelId)
    ) {
        emptyList()
    } else {
        val expectedOwner = ContentOwner.Model(ModelId(runtime.modelId))
        runtime.scenarios.mapNotNull { scenario ->
            val entry = registry.find(CanonicalId(scenario.id)) ?: return@mapNotNull null
            if (
                entry.id.value != scenario.id ||
                entry.type != ContentType.DIAGNOSTIC_SCENARIO ||
                entry.owner != expectedOwner ||
                entry.publicationStatus != PublicationStatus.CANDIDATE ||
                entry.layer != ContentLayer.STANDARD ||
                scenario.profileId != runtime.modelId ||
                !entry.applicability.matches(context)
            ) {
                return@mapNotNull null
            }
            DiagnosticReferencePreview(
                id = scenario.id,
                title = entry.title,
                summary = entry.summary.orEmpty(),
                category = scenario.category,
                sourceNotice = if (entry.sourceStatus == SourceStatus.CURRENT) {
                    "Статус записи: кандидат. Актуальность конкретного порядка действий не подтверждена."
                } else {
                    "Источник и редакция требуют проверки; сведения из донорской базы Test-."
                },
                variantNotice = if (
                    scenario.applicableVariantIds.isNotEmpty() &&
                    context.activeVariantId?.value !in scenario.applicableVariantIds
                ) {
                    "Применимость к выбранному исполнению не подтверждена."
                } else {
                    null
                },
            )
        }
    }

    fun search(query: String): List<DiagnosticReferencePreview> {
        val needle = query.trim().lowercase(Locale.ROOT)
        if (needle.isEmpty()) return references
        return references.filter { item ->
            sequenceOf(item.title, item.summary, item.category)
                .any { needle in it.lowercase(Locale.ROOT) }
        }
    }

    /** Returns text-only data; never a graph, a check or an executable step. */
    fun open(id: String): DiagnosticReferencePreview? =
        references.firstOrNull { it.id == id }
}
