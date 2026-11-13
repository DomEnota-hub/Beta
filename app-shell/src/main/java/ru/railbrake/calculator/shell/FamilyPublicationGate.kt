package ru.railbrake.calculator.shell

import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.ProvenanceClass
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.domain.VariantId

/**
 * Stage 13. Explicit series/execution selection is local to the section.
 * A family name is never an execution and is never sufficient to authorize a card.
 */
data class FamilyExecution(val id: VariantId, val title: String)

data class FamilyModelProfile(
    val workingModelId: ModelId,
    val packOwnerId: ModelId,
    val assetRoot: String,
    val executions: List<FamilyExecution>,
)

object FamilyProfiles {
    fun forModel(modelId: ModelId): FamilyModelProfile? {
        val variants: List<Pair<String, String>>
        val owner: String
        val root: String
        when (modelId.value) {
            "2es5k" -> {
                owner = "ermak"; root = "electric/ermak"
                variants = listOf("2es5k_msud_n" to "2ЭС5К, МСУД-Н",
                    "2es5k_msud_015" to "2ЭС5К, МСУД-015")
            }
            "3es5k" -> {
                owner = "ermak"; root = "electric/ermak"
                variants = listOf("3es5k_msud_n" to "3ЭС5К, МСУД-Н",
                    "3es5k_msud_015" to "3ЭС5К, МСУД-015")
            }
            "chme3" -> {
                owner = "chme3-family"; root = "diesel/chme3-family"
                variants = listOf("chme3" to "ЧМЭ3, исполнение подтверждено")
            }
            "chme3t" -> {
                owner = "chme3-family"; root = "diesel/chme3-family"
                variants = listOf("chme3t_pre6245" to "ЧМЭ3Т, до №6245",
                    "chme3t_from6245" to "ЧМЭ3Т, с №6245")
            }
            "chme3e" -> {
                owner = "chme3-family"; root = "diesel/chme3-family"
                variants = listOf("chme3e" to "ЧМЭ3Э, исполнение подтверждено")
            }
            "tem2" -> {
                owner = "tem2-family"; root = "diesel/tem2-family"
                variants = listOf("tem2" to "ТЭМ2, исполнение подтверждено")
            }
            "tem2u" -> {
                owner = "tem2-family"; root = "diesel/tem2-family"
                variants = listOf("tem2u" to "ТЭМ2У, исполнение подтверждено")
            }
            else -> return null
        }
        return FamilyModelProfile(modelId, ModelId(owner), root,
            variants.map { FamilyExecution(VariantId(it.first), it.second) })
    }
}

/**
 * Source-bound, informational-only publication. A CANDIDATE, UNKNOWN,
 * missing source, broad family-only applicability or ambiguous execution
 * can never become a user-visible card through this path.
 */
object FamilyPublicationGate {
    private val trustedProvenance = setOf(
        ProvenanceClass.CURRENT_OFFICIAL, ProvenanceClass.MANUFACTURER,
    )
    private val informationTypes = setOf(
        ContentType.EQUIPMENT, ContentType.ATLAS_SCHEME,
        ContentType.ACCEPTANCE_ITEM, ContentType.TECHNICAL_DATA,
        ContentType.KNOWLEDGE,
    )

    fun trustedSource(entry: ContentEntry, profile: FamilyModelProfile, execution: VariantId?): Boolean =
        execution != null && profile.executions.any { it.id == execution } &&
        entry.type == ContentType.SOURCE &&
            entry.owner == ContentOwner.Model(profile.packOwnerId) &&
            entry.applicability.modelIds == setOf(profile.packOwnerId) &&
            execution in entry.applicability.variantIds &&
            entry.publicationStatus == PublicationStatus.ACTIVE &&
            entry.sourceStatus == SourceStatus.CURRENT &&
            entry.provenance in trustedProvenance &&
            entry.actionDisposition == ActionDisposition.INFORMATION_ONLY

    fun canDisplay(
        entry: ContentEntry,
        profile: FamilyModelProfile,
        execution: VariantId?,
        trustedSourceIds: Set<String>,
        allowedTypes: Set<ContentType>,
    ): Boolean {
        if (execution == null || profile.executions.none { it.id == execution }) return false
        if (entry.type !in informationTypes || entry.type !in allowedTypes) return false
        if (entry.owner != ContentOwner.Model(profile.packOwnerId)) return false
        if (entry.publicationStatus != PublicationStatus.ACTIVE) return false
        if (entry.sourceStatus != SourceStatus.CURRENT ||
            entry.provenance !in trustedProvenance) return false
        if (entry.layer != ContentLayer.STANDARD ||
            entry.actionDisposition != ActionDisposition.INFORMATION_ONLY) return false
        // Family-only / generic material cannot silently cross variants.
        if (entry.applicability.modelIds != setOf(profile.packOwnerId)) return false
        if (execution !in entry.applicability.variantIds) return false
        if (entry.sourceRefs.isEmpty() ||
            !trustedSourceIds.containsAll(entry.sourceRefs)) return false
        return true
    }
}
