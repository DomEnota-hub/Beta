package ru.railbrake.calculator.assistant

import ru.railbrake.calculator.domain.*
import ru.railbrake.calculator.runtime.ContentRegistry
import ru.railbrake.calculator.runtime.ResolveResult

/** Beta's source-gated, offline text assistant. Search is not a generative model. */
enum class TextIntent { REFERENCE, DIAGNOSTICS, SCHEME, ACCEPTANCE, SAFETY }

data class ParsedTextQuery(
    val normalized: String,
    val searchText: String,
    val explicitModels: Set<ModelId>,
    val ermakUnspecified: Boolean,
    val intent: TextIntent,
)

object TextQueryParser {
    private val modelAliases = linkedMapOf(
        "вл80с" to "vl80s", "вл80" to "vl80s", "vl80s" to "vl80s",
        "2эс5к" to "2es5k", "2es5k" to "2es5k",
        "3эс5к" to "3es5k", "3es5k" to "3es5k",
        "чмэ3" to "chme3", "chme3" to "chme3",
        "чмэ3т" to "chme3t", "chme3t" to "chme3t",
        "чмэ3э" to "chme3e", "chme3e" to "chme3e",
        "тэм2" to "tem2", "tem2" to "tem2",
        "тэм2у" to "tem2u", "tem2u" to "tem2u",
    )
    private val stopWords = setOf("на", "у", "по", "для", "мне", "покажи", "найди",
        "что", "где", "как", "это", "есть", "про", "в", "и", "с", "об", "о", "а")
    fun normalize(text: String): String = text.lowercase().replace('ё', 'е')
        .replace(Regex("[^\\p{L}\\p{N}\\s-]"), " ")
        .replace(Regex("\\s+"), " ").trim()

    private fun containsWord(text: String, word: String) =
        Regex("(?<![\\p{L}\\p{N}])" + Regex.escape(word) + "(?![\\p{L}\\p{N}])")
            .containsMatchIn(text)

    fun parse(text: String): ParsedTextQuery {
        val normalized = normalize(text)
        val models = modelAliases.filterKeys { containsWord(normalized, it) }
            .values.map(::ModelId).toSet()
        val ermak = containsWord(normalized, "ермак") && models.none {
            it == ModelId("2es5k") || it == ModelId("3es5k")
        }
        val intent = when {
            listOf("не включ", "не выключ", "не поднима", "не опуска",
                "не запуска", "не работает", "не тормоз", "не отпуска",
                "нет тяги", "пропала тяга", "не набира", "выбивает",
                "отключился", "глох", "неисправ").any(normalized::contains) -> TextIntent.DIAGNOSTICS
            listOf("схем", "чертеж", "цепи управления").any(normalized::contains) -> TextIntent.SCHEME
            listOf("приемк", "осмотр").any(normalized::contains) -> TextIntent.ACCEPTANCE
            listOf("пожар", "охрана труда", "первая помощь").any(normalized::contains) -> TextIntent.SAFETY
            else -> TextIntent.REFERENCE
        }
        var search = normalized
        modelAliases.keys.sortedByDescending(String::length).forEach {
            search = search.replace(Regex("(?<![\\p{L}\\p{N}])" + Regex.escape(it) +
                "(?![\\p{L}\\p{N}])"), " ")
        }
        search = search.replace(Regex("(?<![\\p{L}\\p{N}])ермак(?![\\p{L}\\p{N}])"), " ")
        search = search.split(Regex("\\s+"))
            .filter { it.isNotBlank() && it !in stopWords }.joinToString(" ")
        return ParsedTextQuery(normalized, search, models, ermak, intent)
    }
}

data class TextAssistantHit(
    val entry: ContentEntry,
    val score: Int,
    /** Attribution is not verification of the underlying source. */
    val sourceIds: Set<String>,
    val sourceVerified: Boolean,
)

sealed interface TextAssistantResult {
    data object WorkingModelRequired : TextAssistantResult
    data class ClarifyModel(val choices: Set<ModelId>) : TextAssistantResult
    data class UnpublishedModel(val modelId: ModelId) : TextAssistantResult
    data class NoMatches(val reason: String) : TextAssistantResult
    data class Matches(
        val scope: AssistantScope,
        val intent: TextIntent,
        val hits: List<TextAssistantHit>,
        val recommended: ContentTarget?,
    ) : TextAssistantResult
}

/**
 * Ports the donor's parser -> index -> engine -> conversation boundaries.
 * Only ACTIVE, applicable, information-only entries are indexed. No fallback
 * to research packs, neighboring models or an assumed execution/variant.
 */
class AssistantTextEngine(
    private val registry: ContentRegistry,
    private val publishedModels: Set<ModelId>,
) {
    fun query(
        text: String,
        workingModelId: ModelId?,
        variantId: VariantId? = null,
        limit: Int = 5,
    ): TextAssistantResult {
        val parsed = TextQueryParser.parse(text)
        if (parsed.normalized.isBlank() || parsed.searchText.isBlank()) {
            return TextAssistantResult.NoMatches("Уточните название узла или тему.")
        }
        if (parsed.explicitModels.size > 1) {
            return TextAssistantResult.ClarifyModel(parsed.explicitModels)
        }
        if (parsed.ermakUnspecified) {
            return TextAssistantResult.ClarifyModel(
                parsed.explicitModels + setOf(ModelId("2es5k"), ModelId("3es5k")))
        }
        val scope = when (val result = AssistantScopeResolver.resolve(
            workingModelId, parsed.explicitModels.singleOrNull())) {
            AssistantScopeResult.MissingWorkingModel -> return TextAssistantResult.WorkingModelRequired
            is AssistantScopeResult.Ready -> result.scope
        }
        if (scope.modelId !in publishedModels) {
            return TextAssistantResult.UnpublishedModel(scope.modelId)
        }
        val context = RuntimeContext(
            workingModelId = scope.modelId,
            viewedModelId = scope.modelId,
            activeVariantId = if (scope.mode == AssistantQueryMode.WORKING_MODEL) variantId else null,
            allowedLayers = setOf(ContentLayer.STANDARD),
        )
        val tokens = parsed.searchText.split(" ").filter { it.length >= 2 }.distinct()
        if (tokens.isEmpty()) return TextAssistantResult.NoMatches("Уточните запрос.")
        val hits = registry.allEntries().asSequence()
            .filter { entry ->
                entry.publicationStatus == PublicationStatus.ACTIVE &&
                    entry.actionDisposition == ActionDisposition.INFORMATION_ONLY &&
                    entry.type != ContentType.SOURCE &&
                    (entry.owner == ContentOwner.Common ||
                        entry.owner == ContentOwner.Model(scope.modelId)) &&
                    registry.resolve(ContentTarget(entry.id, entry.type), context) is ResolveResult.Found
            }
            .filter { entry ->
                when (parsed.intent) {
                    TextIntent.DIAGNOSTICS -> entry.type == ContentType.DIAGNOSTIC_SCENARIO
                    TextIntent.SCHEME -> entry.type == ContentType.ATLAS_SCHEME
                    TextIntent.ACCEPTANCE -> entry.type == ContentType.ACCEPTANCE_ITEM
                    TextIntent.SAFETY -> entry.type in setOf(ContentType.SAFETY, ContentType.FIRST_AID)
                    TextIntent.REFERENCE -> entry.type in setOf(
                        ContentType.EQUIPMENT, ContentType.TECHNICAL_DATA, ContentType.KNOWLEDGE)
                }
            }
            .mapNotNull { entry ->
                val score = score(entry, parsed.searchText, tokens)
                if (score < 12) null else {
                    val verified = entry.sourceRefs.isNotEmpty() && entry.sourceRefs.all { ref ->
                        val source = registry.find(CanonicalId(ref))
                        source != null && source.type == ContentType.SOURCE &&
                            source.publicationStatus == PublicationStatus.ACTIVE &&
                            source.sourceStatus == SourceStatus.CURRENT &&
                            source.provenance in setOf(
                                ProvenanceClass.CURRENT_OFFICIAL, ProvenanceClass.MANUFACTURER) &&
                            (registry.resolve(ContentTarget(source.id, source.type), context) is ResolveResult.Found)
                    }
                    // Safety and diagnostics require verified source provenance.
                    if (entry.type in setOf(ContentType.DIAGNOSTIC_SCENARIO,
                            ContentType.SAFETY, ContentType.FIRST_AID) && !verified) null
                    else TextAssistantHit(entry, score, entry.sourceRefs, verified)
                }
            }
            .sortedWith(compareByDescending<TextAssistantHit> { it.score }.thenBy { it.entry.id.value })
            .take(limit.coerceIn(1, 5)).toList()
        if (hits.isEmpty()) return TextAssistantResult.NoMatches(
            "Применимый опубликованный материал не найден; кандидаты скрыты.")
        val first = hits.first()
        val margin = first.score - (hits.getOrNull(1)?.score ?: 0)
        val recommended = if (first.sourceVerified && first.score >= 90 && margin >= 25 &&
            parsed.intent == TextIntent.REFERENCE) ContentTarget(first.entry.id, first.entry.type)
        else null
        return TextAssistantResult.Matches(scope, parsed.intent, hits, recommended)
    }

    private fun score(entry: ContentEntry, query: String, tokens: List<String>): Int {
        val title = TextQueryParser.normalize(entry.title)
        val terms = (entry.searchTerms + entry.aliases.map { it.value } +
            listOfNotNull(entry.summary)).map(TextQueryParser::normalize)
        val titleTokens = title.split(" ").toSet()
        val allTokens = titleTokens + terms.flatMap { it.split(" ") }.toSet()
        val matched = tokens.count { token -> token in allTokens ||
            (token.length >= 5 && allTokens.any { it.length >= 5 &&
                (it.startsWith(token) || token.startsWith(it)) }) }
        var score = matched * 12
        if (title == query) score += 120
        if (terms.any { it == query }) score += 105
        if (title.contains(query) && query.length >= 4) score += 65
        if (tokens.size > 1 && matched == tokens.size) score += 35
        return score
    }
}

/** In-memory clarification; does not change the user's selected locomotive. */
class AssistantTextConversation(private val engine: AssistantTextEngine) {
    private var pending: String? = null
    fun submit(text: String, workingModel: ModelId?): TextAssistantResult {
        val result = engine.query(text, workingModel)
        pending = if (result is TextAssistantResult.ClarifyModel) text else null
        return result
    }
    fun clarify(model: ModelId, workingModel: ModelId?): TextAssistantResult {
        val original = pending ?: return TextAssistantResult.NoMatches("Нет запроса для уточнения.")
        val options = engine.query(original, workingModel) as? TextAssistantResult.ClarifyModel
            ?: return TextAssistantResult.NoMatches("Уточнение устарело.")
        if (model !in options.choices) return options
        pending = null
        return engine.query(TextQueryParser.parse(original).searchText + " " + model.value, workingModel)
    }
    fun cancel() { pending = null }
}
