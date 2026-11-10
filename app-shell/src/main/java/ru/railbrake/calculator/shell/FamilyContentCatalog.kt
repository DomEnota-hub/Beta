package ru.railbrake.calculator.shell

import android.content.res.AssetManager
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.runtime.ContentPackJsonLoader

/**
 * Reads the migrated family packs, but never publishes them merely because they
 * exist in assets. Research and diagnostic candidates are not loaded into UI.
 */
class FamilyContentCatalog(private val assets: AssetManager) {
    private val parser = ContentPackJsonLoader()

    data class Snapshot(val entries: List<ContentEntry>, val unreadablePacks: Int)

    fun load(profile: FamilyModelProfile): Snapshot {
        val all = mutableListOf<ContentEntry>()
        var rejected = 0
        for (path in listPacks(profile.assetRoot)) {
            val pack = runCatching {
                assets.open(path).bufferedReader().use { parser.parse(it.readText()) }
            }.getOrNull()
            if (pack == null || pack.manifest.modelIds != setOf(profile.packOwnerId)) {
                rejected++
                continue
            }
            all += pack.entries
        }
        return Snapshot(all, rejected)
    }

    fun visible(
        snapshot: Snapshot,
        profile: FamilyModelProfile,
        execution: VariantId?,
        allowedTypes: Set<ContentType>,
    ): List<ContentEntry> {
        val sources = snapshot.entries.filter {
            FamilyPublicationGate.trustedSource(it, profile, execution)
        }.map { it.id.value }.toSet()
        return snapshot.entries.filter {
            FamilyPublicationGate.canDisplay(it, profile, execution, sources, allowedTypes)
        }.distinctBy { it.id }.sortedBy { it.title }
    }

    private fun listPacks(path: String): List<String> {
        if (path.split('/').any {
                it in setOf("migration", "authoring", "research", "recommended",
                    "extended", "archived-official", "manufacturer-extended",
                    "historical-training", "field-practice", "supplemental-operational")
            }) return emptyList()
        return assets.list(path).orEmpty().flatMap { name ->
            val child = "$path/$name"
            when {
                name.endsWith(".pack.json") && !name.contains("candidate", true) ->
                    listOf(child)
                '.' in name -> emptyList()
                else -> listPacks(child)
            }
        }
    }
}
