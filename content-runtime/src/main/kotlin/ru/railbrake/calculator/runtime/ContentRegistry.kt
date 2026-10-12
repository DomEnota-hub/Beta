package ru.railbrake.calculator.runtime

import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentPackManifest
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.LinkScope
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.expectedTargetType

data class ContentPack(
    val manifest: ContentPackManifest,
    val entries: List<ContentEntry>,
)

enum class ValidationIssueCode {
    MANIFEST_ENTRY_MISMATCH,
    DUPLICATE_CANONICAL_ID,
    DUPLICATE_ALIAS,
    ALIAS_COLLIDES_WITH_CANONICAL_ID,
    MISSING_LINK_TARGET,
    LINK_TYPE_MISMATCH,
    LINK_SCOPE_VIOLATION,
}

data class ValidationIssue(
    val code: ValidationIssueCode,
    val message: String,
)

sealed interface ResolveResult {
    data class Found(val entry: ContentEntry) : ResolveResult
    data object NotFound : ResolveResult
    data object TypeMismatch : ResolveResult
    data object Inapplicable : ResolveResult
    data object LayerDenied : ResolveResult
    data object NotPublished : ResolveResult
}

class ContentRegistry {
    private val entries = linkedMapOf<CanonicalId, ContentEntry>()
    private val aliases = linkedMapOf<CanonicalId, CanonicalId>()

    fun install(pack: ContentPack): List<ValidationIssue> {
        val issues = validatePack(pack).toMutableList()

        for (entry in pack.entries) {
            if (entry.id in entries) {
                issues += ValidationIssue(
                    ValidationIssueCode.DUPLICATE_CANONICAL_ID,
                    "Canonical id already registered: ${entry.id.value}",
                )
            }
            if (entry.id in aliases) {
                issues += ValidationIssue(
                    ValidationIssueCode.ALIAS_COLLIDES_WITH_CANONICAL_ID,
                    "Canonical id collides with alias: ${entry.id.value}",
                )
            }

            for (alias in entry.aliases) {
                if (alias in entries || alias in aliases || pack.entries.any { it.id == alias }) {
                    issues += ValidationIssue(
                        ValidationIssueCode.DUPLICATE_ALIAS,
                        "Alias is not globally unique: ${alias.value}",
                    )
                }
            }
        }

        if (issues.isNotEmpty()) return issues

        for (entry in pack.entries) {
            entries[entry.id] = entry
            entry.aliases.forEach { alias -> aliases[alias] = entry.id }
        }
        return emptyList()
    }

    fun find(id: CanonicalId): ContentEntry? {
        val canonical = when {
            id in entries -> id
            id in aliases -> aliases.getValue(id)
            else -> return null
        }
        return entries.getValue(canonical)
    }

    fun validateGlobalLinks(): List<ValidationIssue> =
        entries.values.flatMap { source ->
            source.links.flatMap { link ->
                val target = find(link.targetId)
                when {
                    target == null -> listOf(
                        ValidationIssue(
                            ValidationIssueCode.MISSING_LINK_TARGET,
                            "${source.id.value} -> missing ${link.targetId.value}",
                        )
                    )
                    target.type != link.type.expectedTargetType() -> listOf(
                        ValidationIssue(
                            ValidationIssueCode.LINK_TYPE_MISMATCH,
                            "${source.id.value} -> ${target.id.value}: expected ${link.type.expectedTargetType()}, got ${target.type}",
                        )
                    )
                    !scopeAllows(source, target, link.scope) -> listOf(
                        ValidationIssue(
                            ValidationIssueCode.LINK_SCOPE_VIOLATION,
                            "${source.id.value} -> ${target.id.value}: scope ${link.scope} is not allowed for owners ${source.owner} -> ${target.owner}",
                        )
                    )
                    else -> emptyList()
                }
            }
        }

    fun scopeAllows(source: ContentEntry, target: ContentEntry, scope: LinkScope): Boolean =
        when (scope) {
            LinkScope.SAME_MODEL ->
                source.owner is ContentOwner.Model &&
                    target.owner == source.owner

            LinkScope.COMMON_TARGET ->
                source.owner is ContentOwner.Model &&
                    target.owner == ContentOwner.Common

            LinkScope.COMMON_INTERNAL ->
                source.owner == ContentOwner.Common &&
                    target.owner == ContentOwner.Common
        }

    fun resolve(target: ContentTarget, context: RuntimeContext): ResolveResult {
        val entry = find(target.id) ?: return ResolveResult.NotFound
        if (entry.type != target.expectedType) return ResolveResult.TypeMismatch
        if (entry.publicationStatus != PublicationStatus.ACTIVE) return ResolveResult.NotPublished
        if (!entry.applicability.matches(context)) return ResolveResult.Inapplicable
        if (entry.layer !in context.allowedLayers) return ResolveResult.LayerDenied
        return ResolveResult.Found(entry)
    }

    private fun validatePack(pack: ContentPack): List<ValidationIssue> {
        val issues = mutableListOf<ValidationIssue>()
        val ids = pack.entries.map { it.id }
        val idSet = ids.toSet()

        if (ids.size != idSet.size) {
            issues += ValidationIssue(
                ValidationIssueCode.DUPLICATE_CANONICAL_ID,
                "Pack contains duplicate canonical ids: ${pack.manifest.packId.value}",
            )
        }

        if (pack.manifest.entries != idSet) {
            issues += ValidationIssue(
                ValidationIssueCode.MANIFEST_ENTRY_MISMATCH,
                "Manifest entry set does not match pack content: ${pack.manifest.packId.value}",
            )
        }

        val aliasesInPack = mutableSetOf<CanonicalId>()
        for (entry in pack.entries) {
            for (alias in entry.aliases) {
                if (alias in idSet || !aliasesInPack.add(alias)) {
                    issues += ValidationIssue(
                        ValidationIssueCode.DUPLICATE_ALIAS,
                        "Alias is ambiguous inside pack: ${alias.value}",
                    )
                }
            }
        }

        return issues
    }
}
