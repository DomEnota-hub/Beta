package ru.railbrake.calculator.acceptance

import com.google.gson.Gson
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.runtime.ResolveResult
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.runtime.ContentRegistry

data class AcceptanceRoute(
    val id: String,
    val title: String,
    val mode: String,
    val modeLabel: String,
    val status: String,
    val sequence: List<CanonicalId>,
    val sourceRouteId: String?,
    val description: String?,
) {
    init {
        require(id.isNotBlank()) { "acceptance route id must not be blank" }
        require(title.isNotBlank()) { "acceptance route title must not be blank" }
        require(mode.isNotBlank()) { "acceptance route mode must not be blank" }
        require(sequence.isNotEmpty()) { "acceptance route must contain items" }
        require(sequence.size == sequence.distinct().size) {
            "acceptance route sequence must not contain duplicates"
        }
    }
}

data class AcceptanceFeatureIndex(
    val schemaVersion: Int,
    val modelId: String,
    val itemPacks: List<String>,
    val routes: List<AcceptanceRoute>,
) {
    init {
        require(schemaVersion > 0)
        require(modelId.isNotBlank())
        require(itemPacks.isNotEmpty())
        require(itemPacks.size == itemPacks.distinct().size)
        require(routes.isNotEmpty())
        require(routes.map { it.id }.distinct().size == routes.size) {
            "acceptance route ids must be unique"
        }
    }

    fun route(id: String): AcceptanceRoute? =
        routes.firstOrNull { it.id == id }
}

class AcceptanceFeatureIndexJsonLoader {
    private val gson = Gson()

    fun parse(json: String): AcceptanceFeatureIndex {
        val raw = gson.fromJson(json, JsonAcceptanceIndex::class.java)
            ?: error("acceptance index is empty")

        return AcceptanceFeatureIndex(
            schemaVersion = raw.schemaVersion,
            modelId = requireText(raw.modelId, "index.modelId"),
            itemPacks = raw.itemPacks.orEmpty(),
            routes = raw.routes.orEmpty().map { route ->
                AcceptanceRoute(
                    id = requireText(route.id, "route.id"),
                    title = requireText(route.title, "route.title"),
                    mode = requireText(route.mode, "route.mode"),
                    modeLabel = requireText(route.modeLabel, "route.modeLabel"),
                    status = requireText(route.status, "route.status"),
                    sequence = route.sequence.orEmpty().map(::CanonicalId),
                    sourceRouteId = route.sourceRouteId?.takeIf(String::isNotBlank),
                    description = route.description?.takeIf(String::isNotBlank),
                )
            },
        )
    }
}

data class AcceptanceRouteIssue(
    val itemId: CanonicalId,
    val message: String,
)

data class ResolvedAcceptanceRoute(
    val route: AcceptanceRoute,
    val items: List<ContentEntry>,
)

sealed interface AcceptanceRouteResolution {
    data class Ready(val value: ResolvedAcceptanceRoute) : AcceptanceRouteResolution
    data class Invalid(val issues: List<AcceptanceRouteIssue>) : AcceptanceRouteResolution
}

class AcceptanceRouteResolver(
    private val registry: ContentRegistry,
    private val context: RuntimeContext,
) {
    fun resolve(route: AcceptanceRoute): AcceptanceRouteResolution {
        val issues = mutableListOf<AcceptanceRouteIssue>()
        val expectedOwner = context.contentModelId?.let(ContentOwner::Model)
        val items = route.sequence.mapNotNull { id ->
            // Raw find() bypasses publication, variant and layer policy.
            val result = registry.resolve(ContentTarget(id, ContentType.ACCEPTANCE_ITEM), context)
            val entry = (result as? ResolveResult.Found)?.entry
            if (entry == null || expectedOwner == null || entry.owner != expectedOwner) {
                issues += AcceptanceRouteIssue(
                    id,
                    "acceptance item denied by publication, model or variant policy: $result",
                )
                null
            } else {
                entry
            }
        }

        return if (issues.isEmpty()) {
            AcceptanceRouteResolution.Ready(
                ResolvedAcceptanceRoute(route = route, items = items)
            )
        } else {
            AcceptanceRouteResolution.Invalid(issues)
        }
    }
}

fun ContentEntry.matchesAcceptanceQuery(query: String): Boolean {
    val normalized = query.trim().lowercase()
    if (normalized.isEmpty()) return true

    val haystack = buildList {
        add(title)
        summary?.let(::add)
        addAll(details)
        addAll(searchTerms)
        blocks.forEach { block ->
            add(block.title)
            addAll(block.lines)
        }
    }

    return haystack.any { normalized in it.lowercase() }
}

private data class JsonAcceptanceIndex(
    val schemaVersion: Int = 0,
    val modelId: String? = null,
    val itemPacks: List<String>? = null,
    val routes: List<JsonAcceptanceRoute>? = null,
)

private data class JsonAcceptanceRoute(
    val id: String? = null,
    val title: String? = null,
    val mode: String? = null,
    val modeLabel: String? = null,
    val status: String? = null,
    val sequence: List<String>? = null,
    val sourceRouteId: String? = null,
    val description: String? = null,
)

private fun requireText(value: String?, field: String): String {
    require(!value.isNullOrBlank()) { "$field must not be blank" }
    return value
}
