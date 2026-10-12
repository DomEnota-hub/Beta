package ru.railbrake.calculator.runtime

import com.google.gson.Gson
import com.google.gson.JsonObject
import ru.railbrake.calculator.domain.SourceObjectSnapshot
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.Applicability
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentBlock
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLayer
import ru.railbrake.calculator.domain.ContentLink
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentPackManifest
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.LinkScope
import ru.railbrake.calculator.domain.LinkType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.PackId
import ru.railbrake.calculator.domain.ProvenanceClass
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.domain.VariantId

class ContentPackJsonLoader {
    private val gson = Gson()

    fun parse(json: String): ContentPack {
        val document = gson.fromJson(json, JsonContentPack::class.java)
            ?: error("content pack document is empty")

        val entries = document.entries.orEmpty().map { it.toDomain() }
        val manifest = requireNotNull(document.manifest) {
            "content pack manifest is missing"
        }.toDomain()

        return ContentPack(
            manifest = manifest,
            entries = entries,
        )
    }
}

private data class JsonContentPack(
    val manifest: JsonManifest? = null,
    val entries: List<JsonEntry>? = null,
)

private data class JsonManifest(
    val schemaVersion: Int = 0,
    val packId: String? = null,
    val packVersion: String? = null,
    val family: String? = null,
    val modelIds: List<String>? = null,
    val variantIds: List<String>? = null,
    val locale: String? = null,
    val entries: List<String>? = null,
    val requiresRuntime: String? = null,
    val sourceCatalogVersion: String? = null,
    val checksums: Map<String, String>? = null,
) {
    fun toDomain() = ContentPackManifest(
        schemaVersion = schemaVersion,
        packId = PackId(requireText(packId, "manifest.packId")),
        packVersion = requireText(packVersion, "manifest.packVersion"),
        family = family,
        modelIds = modelIds.orEmpty().map(::ModelId).toSet(),
        variantIds = variantIds.orEmpty().map(::VariantId).toSet(),
        locale = requireText(locale, "manifest.locale"),
        entries = entries.orEmpty().map(::CanonicalId).toSet(),
        requiresRuntime = requireText(requiresRuntime, "manifest.requiresRuntime"),
        sourceCatalogVersion = requireText(sourceCatalogVersion, "manifest.sourceCatalogVersion"),
        checksums = checksums.orEmpty(),
    )
}

private data class JsonEntry(
    val id: String? = null,
    val aliases: List<String>? = null,
    val type: String? = null,
    val owner: JsonOwner? = null,
    val applicability: JsonApplicability? = null,
    val layer: String? = null,
    val publicationStatus: String? = null,
    val provenance: String? = null,
    val sourceStatus: String? = null,
    val actionDisposition: String? = null,
    val title: String? = null,
    val summary: String? = null,
    val details: List<String>? = null,
    val blocks: List<JsonBlock>? = null,
    val searchTerms: List<String>? = null,
    val sourceRefs: List<String>? = null,
    val links: List<JsonLink>? = null,
    val sourceObject: JsonSourceObject? = null,
) {
    fun toDomain() = ContentEntry(
        id = CanonicalId(requireText(id, "entry.id")),
        aliases = aliases.orEmpty().map(::CanonicalId).toSet(),
        type = ContentType.valueOf(requireText(type, "entry.type")),
        owner = requireNotNull(owner) { "entry.owner is missing" }.toDomain(),
        applicability = applicability?.toDomain() ?: Applicability(),
        layer = ContentLayer.valueOf(layer ?: "STANDARD"),
        publicationStatus = PublicationStatus.valueOf(publicationStatus ?: "ACTIVE"),
        provenance = ProvenanceClass.valueOf(provenance ?: "UNKNOWN"),
        sourceStatus = SourceStatus.valueOf(sourceStatus ?: "UNKNOWN"),
        actionDisposition = ActionDisposition.valueOf(actionDisposition ?: "INFORMATION_ONLY"),
        title = requireText(title, "entry.title"),
        summary = summary,
        details = details.orEmpty(),
        blocks = blocks.orEmpty().map { it.toDomain() },
        searchTerms = searchTerms.orEmpty().toSet(),
        sourceRefs = sourceRefs.orEmpty().toSet(),
        links = links.orEmpty().map { it.toDomain() },
        sourceObject = sourceObject?.toDomain(),
    )
}

private data class JsonSourceObject(
    val sourcePath: String? = null,
    val sourceBlobSha: String? = null,
    val `object`: JsonObject? = null,
) {
    fun toDomain() = SourceObjectSnapshot(
        sourcePath = requireText(sourcePath, "sourceObject.sourcePath"),
        sourceBlobSha = requireText(sourceBlobSha, "sourceObject.sourceBlobSha"),
        objectJson = requireNotNull(`object`) { "sourceObject.object is missing" }.toString(),
    )
}

private data class JsonBlock(
    val title: String? = null,
    val lines: List<String>? = null,
) {
    fun toDomain() = ContentBlock(
        title = requireText(title, "block.title"),
        lines = lines.orEmpty().filter { it.isNotBlank() },
    )
}

private data class JsonOwner(
    val kind: String? = null,
    val modelId: String? = null,
) {
    fun toDomain(): ContentOwner = when (requireText(kind, "owner.kind")) {
        "COMMON" -> ContentOwner.Common
        "MODEL" -> ContentOwner.Model(ModelId(requireText(modelId, "owner.modelId")))
        else -> error("unknown owner kind: $kind")
    }
}

private data class JsonApplicability(
    val modelIds: List<String>? = null,
    val variantIds: List<String>? = null,
    val sectionIds: List<String>? = null,
    val equipmentIds: List<String>? = null,
) {
    fun toDomain() = Applicability(
        modelIds = modelIds.orEmpty().map(::ModelId).toSet(),
        variantIds = variantIds.orEmpty().map(::VariantId).toSet(),
        sectionIds = sectionIds.orEmpty().toSet(),
        equipmentIds = equipmentIds.orEmpty().map(::CanonicalId).toSet(),
    )
}

private data class JsonLink(
    val type: String? = null,
    val targetId: String? = null,
    val role: String? = null,
    val scope: String? = null,
    val applicability: JsonApplicability? = null,
) {
    fun toDomain() = ContentLink(
        type = LinkType.valueOf(requireText(type, "link.type")),
        targetId = CanonicalId(requireText(targetId, "link.targetId")),
        role = role,
        scope = LinkScope.valueOf(scope ?: "SAME_MODEL"),
        applicability = applicability?.toDomain() ?: Applicability(),
    )
}

private fun requireText(value: String?, field: String): String {
    require(!value.isNullOrBlank()) { "$field must not be blank" }
    return value
}
