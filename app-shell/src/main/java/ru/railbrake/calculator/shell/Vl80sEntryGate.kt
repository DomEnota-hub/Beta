package ru.railbrake.calculator.shell

import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.runtime.ContentRegistry
import ru.railbrake.calculator.runtime.ResolveResult

/**
 * Final authorization for every direct Atlas/Acceptance/linked VL80S entry.
 * A canonical ID alone never grants access to an unpublished or variant-specific card.
 * Diagnostic scenarios are opened only through their separately source-gated runtime.
 */
internal object Vl80sEntryGate {
    private val owner = ContentOwner.Model(ModelId("vl80s"))

    fun open(registry: ContentRegistry, id: CanonicalId, context: RuntimeContext): ContentEntry? {
        if (context.contentModelId != ModelId("vl80s")) return null
        val raw = registry.find(id) ?: return null
        if (raw.owner != owner ||
            raw.type == ContentType.SOURCE ||
            raw.type == ContentType.DIAGNOSTIC_SCENARIO ||
            raw.actionDisposition != ActionDisposition.INFORMATION_ONLY
        ) return null
        val result = registry.resolve(ContentTarget(id, raw.type), context)
        return (result as? ResolveResult.Found)?.entry?.takeIf { it.owner == owner }
    }
}
