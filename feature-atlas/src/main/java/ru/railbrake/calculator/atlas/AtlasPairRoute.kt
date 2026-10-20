package ru.railbrake.calculator.atlas

import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType

/** Screen coordinates from preserved training layouts, never physical positions. */
data class AtlasPairBounds(val x: Float, val y: Float, val width: Float, val height: Float) {
    init {
        require(x.isFinite() && y.isFinite() && width.isFinite() && height.isFinite())
        require(x >= 0f && y >= 0f && width > 0f && height > 0f)
    }

    val area: Float get() = width * height
    fun contains(px: Float, py: Float): Boolean =
        px >= x && px <= x + width && py >= y && py <= y + height
}

data class AtlasPairNode(
    val key: String,
    val label: String,
    val bounds: AtlasPairBounds,
    val equipmentId: CanonicalId?,
)

data class AtlasPairStep(
    val title: String,
    val explanation: String,
    val activeNodeKeys: Set<String>,
)

data class AtlasPairRoute(
    val sequenceEntryId: String,
    val layoutEntryId: String,
    val modelId: String,
    val variantIds: Set<String>,
    val title: String,
    val functionalDisclaimer: String,
    val nodes: List<AtlasPairNode>,
    val steps: List<AtlasPairStep>,
    val runtimeImport: Boolean = false,
) {
    init {
        require(sequenceEntryId.isNotBlank() && layoutEntryId.isNotBlank() && modelId.isNotBlank())
        require(sequenceEntryId != layoutEntryId)
        require(title.isNotBlank() && functionalDisclaimer.isNotBlank())
        require(!runtimeImport) { "candidate training layout cannot activate runtime" }
        val keys = nodes.map { it.key }
        require(nodes.isNotEmpty())
        require(keys.size == keys.distinct().size && keys.none(String::isBlank))
        require(steps.isNotEmpty() && steps.all { it.title.isNotBlank() })
        require(steps.all { it.activeNodeKeys <= keys.toSet() })
    }

    fun hitTest(x: Float, y: Float): AtlasPairNode? =
        nodes.filter { it.bounds.contains(x, y) }.minByOrNull { it.bounds.area }

    fun equipmentTarget(nodeKey: String, actualVariantId: String?): ContentTarget? {
        if (actualVariantId == null || actualVariantId !in variantIds) return null
        return nodes.singleOrNull { it.key == nodeKey }?.equipmentId
            ?.let { ContentTarget(it, ContentType.EQUIPMENT) }
    }

    fun step(index: Int): AtlasPairStep? = steps.getOrNull(index)
}
