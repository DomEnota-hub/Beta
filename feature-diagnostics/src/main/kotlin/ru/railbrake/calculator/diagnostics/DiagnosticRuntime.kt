package ru.railbrake.calculator.diagnostics

import com.google.gson.Gson
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ExtendedDiagnosticClass
import ru.railbrake.calculator.domain.PublicationStatus

enum class DiagnosticRuntimeAvailability {
    CATALOG_ONLY,
    RELATION_GRAPH_ONLY,
    EXECUTABLE_FLOW_AVAILABLE,
}

data class DiagnosticFeatureIndex(
    val schemaVersion: Int,
    val modelId: String,
    val recommendedPacks: List<String>,
    val extendedCorpora: Map<ExtendedDiagnosticClass, List<String>>,
    val relationGraph: String?,
    val executableFlow: String?,
    val observationIndex: String?,
    val runtimePayloadStatus: String,
    val interactiveRuntimeSource: String?,
    val publicationPolicy: String,
    val goldenReferenceCandidate: String?,
) {
    init {
        require(schemaVersion > 0)
        require(modelId.isNotBlank())
        require(recommendedPacks.isNotEmpty())
        require(recommendedPacks.size == recommendedPacks.distinct().size)
        require(
            extendedCorpora.values.flatten().size ==
                extendedCorpora.values.flatten().distinct().size
        )
        require(runtimePayloadStatus.isNotBlank())
        require(publicationPolicy.isNotBlank())
        val assetPaths = recommendedPacks +
            extendedCorpora.values.flatten() +
            listOfNotNull(relationGraph, executableFlow, observationIndex)
        require(
            assetPaths.all { path ->
                path.isNotBlank() && !path.startsWith("/") &&
                    !path.contains("..") && !path.contains('\\')
            }
        ) { "diagnostics index has an invalid asset path" }
        if (runtimePayloadStatus == "EXECUTABLE_FLOW_AVAILABLE") {
            require(!executableFlow.isNullOrBlank()) {
                "executableFlow is required when executable runtime is available"
            }
        }
    }

    val runtimeAvailability: DiagnosticRuntimeAvailability
        get() = when (runtimePayloadStatus) {
            "RELATION_GRAPH_ONLY_NOT_EXECUTABLE" ->
                DiagnosticRuntimeAvailability.RELATION_GRAPH_ONLY
            "EXECUTABLE_FLOW_AVAILABLE" ->
                DiagnosticRuntimeAvailability.EXECUTABLE_FLOW_AVAILABLE
            else ->
                DiagnosticRuntimeAvailability.CATALOG_ONLY
        }
}

class DiagnosticFeatureIndexJsonLoader {
    private val gson = Gson()

    fun parse(json: String): DiagnosticFeatureIndex {
        val raw = gson.fromJson(json, JsonIndex::class.java)
            ?: error("diagnostic index is empty")

        val extended = raw.extendedCorpora.orEmpty().mapKeys { (key, _) ->
            ExtendedDiagnosticClass.valueOf(key)
        }.mapValues { (_, value) ->
            value.orEmpty()
        }

        return DiagnosticFeatureIndex(
            schemaVersion = raw.schemaVersion,
            modelId = requireText(raw.modelId, "index.modelId"),
            recommendedPacks = raw.recommendedPacks.orEmpty(),
            extendedCorpora = extended,
            relationGraph = raw.relationGraph?.takeIf(String::isNotBlank),
            executableFlow = raw.executableFlow?.takeIf(String::isNotBlank),
            observationIndex = raw.observationIndex?.takeIf(String::isNotBlank),
            runtimePayloadStatus = requireText(
                raw.runtimePayloadStatus,
                "index.runtimePayloadStatus",
            ),
            interactiveRuntimeSource =
                raw.interactiveRuntimeSource?.takeIf(String::isNotBlank),
            publicationPolicy = requireText(
                raw.publicationPolicy,
                "index.publicationPolicy",
            ),
            goldenReferenceCandidate =
                raw.goldenReferenceCandidate?.takeIf(String::isNotBlank),
        )
    }
}

data class DiagnosticDescriptor(
    val id: String,
    val layer: ContentLayer,
    val publicationStatus: PublicationStatus,
    val corpus: String,
    val extendedClass: ExtendedDiagnosticClass?,
) {
    init {
        require(id.isNotBlank())
        require(
            (layer == ContentLayer.STANDARD && extendedClass == null) ||
                (layer == ContentLayer.EXTENDED && extendedClass != null)
        ) {
            "extended diagnostics require an explicit extended class"
        }
    }
}

data class DiagnosticVisibilitySettings(
    val extendedEnabled: Boolean = false,
    val warningAcknowledged: Boolean = false,
    val enabledExtendedClasses: Set<ExtendedDiagnosticClass> = emptySet(),
)

enum class DiagnosticAccessReason {
    AVAILABLE,
    CANDIDATE_NOT_PUBLISHED,
    EXTENDED_DISABLED,
    EXTENDED_WARNING_NOT_ACKNOWLEDGED,
    EXTENDED_CLASS_DISABLED,
    EXECUTABLE_RUNTIME_UNAVAILABLE,
    ACTION_AUTHORITY_UNVERIFIED,
}

data class DiagnosticAccessDecision(
    val visibleInCatalog: Boolean,
    val executable: Boolean,
    val reason: DiagnosticAccessReason,
)

object DiagnosticAccessPolicy {
    fun evaluate(
        descriptor: DiagnosticDescriptor,
        runtimeAvailability: DiagnosticRuntimeAvailability,
        settings: DiagnosticVisibilitySettings = DiagnosticVisibilitySettings(),
        actionInputs: DiagnosticActionInputs? = null,
    ): DiagnosticAccessDecision {
        if (descriptor.layer == ContentLayer.EXTENDED) {
            if (!settings.extendedEnabled) {
                return DiagnosticAccessDecision(
                    visibleInCatalog = false,
                    executable = false,
                    reason = DiagnosticAccessReason.EXTENDED_DISABLED,
                )
            }

            if (!settings.warningAcknowledged) {
                return DiagnosticAccessDecision(
                    visibleInCatalog = false,
                    executable = false,
                    reason = DiagnosticAccessReason.EXTENDED_WARNING_NOT_ACKNOWLEDGED,
                )
            }

            val extendedClass = requireNotNull(descriptor.extendedClass)
            if (extendedClass !in settings.enabledExtendedClasses) {
                return DiagnosticAccessDecision(
                    visibleInCatalog = false,
                    executable = false,
                    reason = DiagnosticAccessReason.EXTENDED_CLASS_DISABLED,
                )
            }
        }

        if (descriptor.publicationStatus != PublicationStatus.ACTIVE) {
            return DiagnosticAccessDecision(
                visibleInCatalog = true,
                executable = false,
                reason = DiagnosticAccessReason.CANDIDATE_NOT_PUBLISHED,
            )
        }

        if (runtimeAvailability != DiagnosticRuntimeAvailability.EXECUTABLE_FLOW_AVAILABLE) {
            return DiagnosticAccessDecision(
                visibleInCatalog = true,
                executable = false,
                reason = DiagnosticAccessReason.EXECUTABLE_RUNTIME_UNAVAILABLE,
            )
        }

        if (descriptor.layer == ContentLayer.EXTENDED || actionInputs == null ||
            actionInputs.publicationStatus != descriptor.publicationStatus ||
            actionInputs.runtimeAvailability != runtimeAvailability ||
            !DiagnosticActionGate.permits(actionInputs)
        ) {
            return DiagnosticAccessDecision(
                visibleInCatalog = true,
                executable = false,
                reason = DiagnosticAccessReason.ACTION_AUTHORITY_UNVERIFIED,
            )
        }

        return DiagnosticAccessDecision(
            visibleInCatalog = true,
            executable = true,
            reason = DiagnosticAccessReason.AVAILABLE,
        )
    }
}

class DiagnosticPackDescriptorJsonLoader {
    private val gson = Gson()

    fun parse(json: String): List<DiagnosticDescriptor> {
        val raw = gson.fromJson(json, JsonPack::class.java)
            ?: error("diagnostic pack is empty")

        return raw.entries.orEmpty().map { entry ->
            val meta = requireNotNull(entry.diagnosticMeta) {
                "diagnosticMeta is required for ${entry.id}"
            }
            DiagnosticDescriptor(
                id = requireText(entry.id, "entry.id"),
                layer = ContentLayer.valueOf(entry.layer ?: "STANDARD"),
                publicationStatus = PublicationStatus.valueOf(
                    entry.publicationStatus ?: "ACTIVE"
                ),
                corpus = requireText(meta.corpus, "diagnosticMeta.corpus"),
                extendedClass = meta.extendedClass
                    ?.takeIf(String::isNotBlank)
                    ?.let(ExtendedDiagnosticClass::valueOf),
            )
        }
    }
}

private data class JsonIndex(
    val schemaVersion: Int = 0,
    val modelId: String? = null,
    val recommendedPacks: List<String>? = null,
    val extendedCorpora: Map<String, List<String>?>? = null,
    val relationGraph: String? = null,
    val executableFlow: String? = null,
    val observationIndex: String? = null,
    val runtimePayloadStatus: String? = null,
    val interactiveRuntimeSource: String? = null,
    val publicationPolicy: String? = null,
    val goldenReferenceCandidate: String? = null,
)

private data class JsonPack(
    val entries: List<JsonEntry>? = null,
)

private data class JsonEntry(
    val id: String? = null,
    val layer: String? = null,
    val publicationStatus: String? = null,
    val diagnosticMeta: JsonDiagnosticMeta? = null,
)

private data class JsonDiagnosticMeta(
    val corpus: String? = null,
    val extendedClass: String? = null,
)

private fun requireText(value: String?, field: String): String {
    require(!value.isNullOrBlank()) { "$field must not be blank" }
    return value
}
