package ru.railbrake.calculator.core

import org.json.JSONArray
import org.json.JSONObject

/** The same forward/reverse canonical links, indexed once instead of per card. */
internal class ErmakRelatedIndex(root: JSONObject) {
    private val related: Map<String, List<String>> = buildMap {
        val links = linkedMapOf<String, LinkedHashSet<String>>()
        val indexes = root.optJSONObject("indexes") ?: JSONObject()
        for (name in listOf("byEquipment", "bySystem", "byDiagnostic", "byScheme")) {
            val bucket = indexes.optJSONObject(name) ?: continue
            val keys = bucket.keys()
            while (keys.hasNext()) {
                val key = keys.next()
                val refs = linkedSetOf<String>()
                collect(bucket.opt(key), refs)
                links.getOrPut(key) { linkedSetOf() }.addAll(refs)
                if (isReference(key)) refs.forEach { ref ->
                    links.getOrPut(ref) { linkedSetOf() }.add(key)
                }
            }
        }
        links.forEach { (id, refs) -> put(id, refs.filterNot { it == id }) }
    }

    fun relatedTo(id: String): List<String> = related[id].orEmpty()

    private fun isReference(value: String): Boolean =
        value.startsWith("ER-EQ-") || value.startsWith("ER-KB-") ||
            value.startsWith("ER-DIAG-") || value.startsWith("ER-SCH-") ||
            value.startsWith("ER-VARIANT-") || value.startsWith("SYS-")

    private fun collect(value: Any?, result: MutableSet<String>) {
        when (value) {
            is String -> if (isReference(value)) result.add(value)
            is JSONArray -> for (i in 0 until value.length()) collect(value.opt(i), result)
            is JSONObject -> {
                val keys = value.keys()
                while (keys.hasNext()) collect(value.opt(keys.next()), result)
            }
        }
    }
}
