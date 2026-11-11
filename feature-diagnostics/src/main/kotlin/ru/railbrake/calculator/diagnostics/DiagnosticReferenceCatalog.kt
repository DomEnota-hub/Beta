package ru.railbrake.calculator.diagnostics

import java.util.Locale
import ru.railbrake.calculator.domain.ActionDisposition
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
    // Read-only donor observations and cautionary evidence, NOT approved orders.
    // Never add checks, executable steps or a permission flag to this type.
    val observedSigns: List<String>,
    val donorCautions: List<String>,
    val donorStopSignals: List<String>,
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
                !(
                    entry.publicationStatus == PublicationStatus.CANDIDATE ||
                        (entry.publicationStatus == PublicationStatus.ACTIVE &&
                            entry.actionDisposition == ActionDisposition.INFORMATION_ONLY)
                ) ||
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
                sourceNotice = if (entry.publicationStatus == PublicationStatus.ACTIVE) {
                    "Опубликованная справка для чтения. Допуск к действиям не предоставлен."
                } else if (entry.sourceStatus == SourceStatus.CURRENT) {
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
                // Donor evidence is visible with explicit uncertainty labels in the UI.
                // Unlike checks/immediateActions these lists do not authorize a procedure.
                observedSigns = scenario.observableSigns.toList(),
                donorCautions = scenario.prohibited.toList(),
                donorStopSignals = scenario.stopConditions.toList(),
            )
        }
    }

    fun search(query: String): List<DiagnosticReferencePreview> {
        val needle = query.trim().lowercase(Locale.ROOT)
        if (needle.isEmpty()) return references
        return references.filter { item ->
            sequenceOf(item.title, item.summary, item.category)
                .plus(item.observedSigns.asSequence())
                .plus(item.donorCautions.asSequence())
                .plus(item.donorStopSignals.asSequence())
                .any { needle in it.lowercase(Locale.ROOT) }
        }
    }

    /** Returns text-only data; never a graph, a check or an executable step. */
    fun open(id: String): DiagnosticReferencePreview? =
        references.firstOrNull { it.id == id }
}
