package ru.railbrake.calculator.shell

import android.content.res.AssetManager
import org.json.JSONObject
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.navigation.ShellHomeDestination

/**
 * Narrow, summary-only bridge for objects that were readable in pinned Test-.
 * This is NOT a publication or execution permission: no blocks, links, procedures,
 * diagnostics or acceptance checklists are imported into the UI by this bridge.
 */
internal enum class ReferenceScope { DONOR_VARIANT, EXECUTION_UNVERIFIED }

internal data class FamilyReferencePreview(
    val id: String,
    val modelId: String,
    val executionId: String?,
    val scope: ReferenceScope,
    val title: String,
    val summary: String,
    val donorPath: String,
    val donorBlobSha: String,
)

internal object FamilyReferencePreviewPolicy {
    fun canShow(
        entry: FamilyReferencePreview,
        profile: FamilyModelProfile,
        execution: VariantId?,
        destination: ShellHomeDestination,
    ): Boolean {
        if (destination != ShellHomeDestination.ATLAS ||
            execution == null ||
            profile.executions.none { it.id == execution } ||
            entry.modelId != profile.workingModelId.value ||
            entry.id.isBlank() || entry.title.isBlank() || entry.summary.isBlank() ||
            entry.donorPath.isBlank() ||
            !entry.donorBlobSha.matches(Regex("[a-f0-9]{40}"))
        ) return false
        return when (entry.scope) {
            ReferenceScope.DONOR_VARIANT -> entry.executionId == execution.value
            // Donor did not prove the selected execution. Show only as a clearly
            // marked general reference, NEVER as an execution-specific instruction.
            ReferenceScope.EXECUTION_UNVERIFIED -> entry.executionId == null
        }
    }
}

/** Small curated asset; deliberately separate from unpublished family packs. */
internal class FamilyReferencePreviewCatalog(private val assets: AssetManager) {
    fun load(): List<FamilyReferencePreview> {
        val json = assets.open("crew-reference/summaries.json").bufferedReader().use { it.readText() }
        val root = JSONObject(json)
        require(root.getInt("schemaVersion") == 1)
        val entries = root.getJSONArray("entries")
        return (0 until entries.length()).map { index ->
            val item = entries.getJSONObject(index)
            FamilyReferencePreview(
                id = item.getString("id"),
                modelId = item.getString("modelId"),
                executionId = if (item.isNull("executionId")) null else item.getString("executionId"),
                scope = ReferenceScope.valueOf(item.getString("scope")),
                title = item.getString("title"),
                summary = item.getString("summary"),
                donorPath = item.getString("donorPath"),
                donorBlobSha = item.getString("donorBlobSha"),
            )
        }
    }
}
