package ru.railbrake.calculator.assistant

import ru.railbrake.calculator.domain.*
import ru.railbrake.calculator.runtime.ContentRegistry
import ru.railbrake.calculator.runtime.ResolveResult

/** UI navigation re-checks search hits and links; results are not authorizations. */
object AssistantUiNavigationGate {
    fun openHit(
        result: TextAssistantResult.Matches,
        target: ContentTarget,
        registry: ContentRegistry,
        publishedModels: Set<ModelId>,
    ): ContentEntry? {
        if (result.scope.modelId !in publishedModels) return null
        if (result.hits.none { it.entry.id == target.id && it.entry.type == target.expectedType }) {
            return null
        }
        val context = RuntimeContext(
            workingModelId = result.scope.workingModelId,
            viewedModelId = result.scope.modelId,
            activeVariantId = null,
            allowedLayers = setOf(ContentLayer.STANDARD),
        )
        return resolveSafeTarget(target, registry, context, publishedModels)
    }

    fun resolveSafeTarget(
        target: ContentTarget,
        registry: ContentRegistry,
        context: RuntimeContext,
        publishedModels: Set<ModelId>,
    ): ContentEntry? {
        val model = context.contentModelId ?: return null
        if (model !in publishedModels) return null
        val entry = (registry.resolve(target, context) as? ResolveResult.Found)?.entry
            ?: return null
        if (entry.publicationStatus != PublicationStatus.ACTIVE ||
            entry.layer != ContentLayer.STANDARD ||
            entry.actionDisposition != ActionDisposition.INFORMATION_ONLY ||
            entry.type == ContentType.SOURCE ||
            (entry.owner != ContentOwner.Common && entry.owner != ContentOwner.Model(model))) {
            return null
        }
        if (entry.type in setOf(ContentType.DIAGNOSTIC_SCENARIO,
                ContentType.SAFETY, ContentType.FIRST_AID)) {
            if (entry.sourceRefs.isEmpty() || !entry.sourceRefs.all { ref ->
                    val source = registry.find(CanonicalId(ref))
                    source != null && source.type == ContentType.SOURCE &&
                        source.publicationStatus == PublicationStatus.ACTIVE &&
                        source.sourceStatus == SourceStatus.CURRENT &&
                        source.provenance in setOf(
                            ProvenanceClass.CURRENT_OFFICIAL, ProvenanceClass.MANUFACTURER) &&
                        registry.resolve(ContentTarget(source.id, source.type), context)
                            is ResolveResult.Found
                }) return null
        }
        return entry
    }
}
