package ru.railbrake.calculator.diagnostics

import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.PublicationStatus

/** Presentation and source eligibility are independent of executable action authority. */
enum class DiagnosticCardVersion { SHORT, DETAILED }
enum class DiagnosticKnowledgeVolume { BASIC, EXPANDED }
enum class DiagnosticDisplayDepth { MINIMAL, STANDARD, DETAILED }

data class DiagnosticPresentationSettings(
    val knowledgeVolume: DiagnosticKnowledgeVolume = DiagnosticKnowledgeVolume.BASIC,
    val displayDepth: DiagnosticDisplayDepth = DiagnosticDisplayDepth.MINIMAL,
    val extendedEnabled: Boolean = false,
    val warningAcknowledged: Boolean = false,
)

data class DiagnosticActionInputs(
    val publicationStatus: PublicationStatus,
    val actionDisposition: ActionDisposition,
    val runtimeAvailability: DiagnosticRuntimeAvailability,
    val sourceAuthorityVerified: Boolean = false,
    val exactProfileConfirmed: Boolean = false,
    val installedEquipmentConfirmed: Boolean = false,
)

object DiagnosticActionGate {
    fun permits(input: DiagnosticActionInputs): Boolean =
        input.publicationStatus == PublicationStatus.ACTIVE &&
            input.actionDisposition == ActionDisposition.CONDITIONAL_ACTION &&
            input.runtimeAvailability == DiagnosticRuntimeAvailability.EXECUTABLE_FLOW_AVAILABLE &&
            input.sourceAuthorityVerified && input.exactProfileConfirmed &&
            input.installedEquipmentConfirmed
}

data class DiagnosticEvidenceRoute(
    val sourceId: String,
    val scenarioId: String,
    val exactProfileId: String,
    val startNodeId: String,
    val nodes: List<DiagnosticRouteNode>,
    val executable: Boolean = false,
) {
    init {
        require(sourceId.isNotBlank() && scenarioId.isNotBlank() && exactProfileId.isNotBlank())
        require(!executable) { "extended source evidence cannot grant action authority" }
        validateDiagnosticGraph(startNodeId, nodes)
    }

    fun next(nodeId: String, response: ExecutableDiagnosticResponse): String? =
        nodes.singleOrNull { it.id == nodeId }?.responses?.get(response)
}

data class DiagnosticRouteNode(
    val id: String,
    val responses: Map<ExecutableDiagnosticResponse, String>,
)

private fun validateDiagnosticGraph(startNodeId: String, nodes: List<DiagnosticRouteNode>) {
    val ids = nodes.map { it.id }
    require(ids.size == ids.distinct().size && ids.none(String::isBlank))
    require(startNodeId in ids)
    nodes.forEach { node ->
        require(node.responses.isEmpty() ||
            node.responses.keys == ExecutableDiagnosticResponse.entries.toSet())
        require(node.responses.values.all { it == DIAGNOSTIC_END_OF_FLOW || it in ids })
    }

    // Authoring preflight: every authored node must be reachable, and every node
    // must have a path to an explicit terminal or end-of-flow. Cycles without
    // any exit cannot be published as a diagnostic route.
    val byId = nodes.associateBy { it.id }
    val reached = mutableSetOf(startNodeId)
    val pending = ArrayDeque<String>()
    pending.add(startNodeId)
    while (pending.isNotEmpty()) {
        val node = requireNotNull(byId[pending.removeFirst()])
        node.responses.values.forEach { target ->
            if (target != DIAGNOSTIC_END_OF_FLOW && reached.add(target)) pending.add(target)
        }
    }
    require(reached.size == ids.size) { "unreachable diagnostic nodes" }

    val canFinish = nodes.filter { node ->
        node.responses.isEmpty() || DIAGNOSTIC_END_OF_FLOW in node.responses.values
    }.mapTo(mutableSetOf()) { it.id }
    require(canFinish.isNotEmpty()) { "diagnostic graph has no terminal" }
    var changed = true
    while (changed) {
        changed = false
        nodes.forEach { node ->
            if (node.id !in canFinish && node.responses.values.any { it in canFinish }) {
                canFinish.add(node.id)
                changed = true
            }
        }
    }
    require(canFinish.containsAll(ids)) { "diagnostic nodes have no path to a terminal" }
}

data class DiagnosticCardRoute(
    val version: DiagnosticCardVersion,
    val startNodeId: String,
    val nodes: List<DiagnosticRouteNode>,
    val extendedRoutes: List<DiagnosticEvidenceRoute>,
    // Authoring-only evidence gap. An absent source is NOT a synthetic route,
    // not a published extension and cannot grant execution authority.
    val extendedSourceGapReason: String? = null,
) {
    init {
        validateDiagnosticGraph(startNodeId, nodes)
        require(extendedRoutes.isNotEmpty() || !extendedSourceGapReason.isNullOrBlank()) {
            "each card version needs evidence or an explicit source gap"
        }
        require(extendedRoutes.isEmpty() || extendedSourceGapReason == null) {
            "a bound extension cannot also claim an unbound source gap"
        }
        require(extendedRoutes.map { it.sourceId }.distinct().size == extendedRoutes.size)
    }
}

data class DiagnosticCardSelection(
    val available: Boolean,
    val knowledgeVolume: DiagnosticKnowledgeVolume,
    val displayDepth: DiagnosticDisplayDepth,
    val evidence: List<DiagnosticEvidenceRoute>,
    private val route: DiagnosticCardRoute?,
) {
    fun next(nodeId: String, response: ExecutableDiagnosticResponse): String? =
        route?.nodes?.singleOrNull { it.id == nodeId }?.responses?.get(response)

    fun nextExtended(sourceId: String, nodeId: String, response: ExecutableDiagnosticResponse): String? =
        evidence.singleOrNull { it.sourceId == sourceId }?.next(nodeId, response)
}

data class DiagnosticModeContract(
    val scenarioId: String,
    val exactProfileId: String,
    val routes: List<DiagnosticCardRoute>,
) {
    init {
        require(scenarioId.isNotBlank() && exactProfileId.isNotBlank())
        require(routes.map { it.version }.toSet() == DiagnosticCardVersion.entries.toSet()) {
            "short and detailed routes are both required"
        }
        require(routes.size == DiagnosticCardVersion.entries.size)
        require(routes.all { route -> route.extendedRoutes.all { it.scenarioId == scenarioId } }) {
            "extended branches must belong to this scenario"
        }
        require(routes.map { it.startNodeId to it.nodes }.distinct().size == 2) {
            "short and detailed versions need distinct authored route graphs"
        }
        // Compare only real extensions; one or both versions may have a
        // documented source gap rather than fictitious extended nodes.
        val boundExtensions = routes.filter { it.extendedRoutes.isNotEmpty() }
            .map { route -> route.extendedRoutes.map { it.startNodeId to it.nodes } }
        require(boundExtensions.distinct().size == boundExtensions.size) {
            "short and detailed versions need independently authored extended branches"
        }
        require(routes.all { route ->
            route.extendedRoutes.all { it.exactProfileId == exactProfileId }
        }) { "extended evidence must match the exact scenario profile" }
    }

    fun select(
        version: DiagnosticCardVersion,
        actualProfileId: String?,
        settings: DiagnosticPresentationSettings,
    ): DiagnosticCardSelection {
        val route = routes.single { it.version == version }.takeIf {
            actualProfileId == exactProfileId
        }
        val evidence = if (settings.extendedEnabled && settings.warningAcknowledged) {
            route?.extendedRoutes.orEmpty()
        } else {
            emptyList()
        }
        return DiagnosticCardSelection(
            available = route != null,
            knowledgeVolume = settings.knowledgeVolume,
            displayDepth = settings.displayDepth,
            evidence = evidence,
            route = route,
        )
    }
}
