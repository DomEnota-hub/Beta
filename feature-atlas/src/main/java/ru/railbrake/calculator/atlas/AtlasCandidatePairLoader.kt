package ru.railbrake.calculator.atlas

import com.google.gson.JsonObject
import com.google.gson.JsonParser
import ru.railbrake.calculator.domain.CanonicalId

/** Reads an explicitly reviewed candidate pair; callers must not register it in a runtime index. */
class AtlasCandidatePairLoader {
    fun parse(sequenceJson: String, layoutJson: String, bindingsJson: String): AtlasPairRoute {
        val sequence = JsonParser.parseString(sequenceJson).asJsonObject
        val layout = JsonParser.parseString(layoutJson).asJsonObject
        val bindings = JsonParser.parseString(bindingsJson).asJsonObject
        require(bindings.string("publicationStatus") == "CANDIDATE")
        require(bindings.string("actionDisposition") == "INFORMATION_ONLY")
        require(bindings.get("runtimeImport").asBoolean == false)
        val matches = bindings.getAsJsonArray("rows").filter {
            it.asJsonObject.get("sequenceEntryId")?.asString == sequence.string("id")
        }
        require(matches.size == 1) { "candidate sequence binding must be unique" }
        val binding = matches.single().asJsonObject
        val sequenceEntry = sequence.getAsJsonObject("sourceObject").getAsJsonObject("object")
        val layoutEntry = layout.getAsJsonObject("sourceObject").getAsJsonObject("object")
        require(sequence.string("id") == binding.string("sequenceEntryId"))
        require(layout.string("id") == binding.string("layoutEntryId"))
        require(sequence.string("publicationStatus") == layout.string("publicationStatus") &&
            sequence.string("publicationStatus") == "CANDIDATE")
        require(sequence.string("actionDisposition") == layout.string("actionDisposition") &&
            sequence.string("actionDisposition") == "INFORMATION_ONLY")
        val model = binding.string("modelId")
        require(sequence.getAsJsonObject("owner").string("modelId") == model)
        require(layout.getAsJsonObject("owner").string("modelId") == model)
        require(sequenceEntry.string("id") == layoutEntry.string("sequenceId") &&
            sequenceEntry.string("id") == binding.string("sourceSequenceId"))
        require(sequenceEntry.string("sourceSchemeRef") == binding.string("sourceSchemeRef"))
        layoutEntry.get("sourceSchemeRef")?.let {
            require(it.asString == binding.string("sourceSchemeRef"))
        }
        val variantIds = binding.getAsJsonArray("variantIds").map { it.asString }.toSet()
        val targets = binding.getAsJsonObject("nodeTargets")
        val nodes = layoutEntry.getAsJsonArray("nodes").map { item ->
            val node = item.asJsonObject
            val key = node.string("nodeKey")
            val position = node.getAsJsonObject("position")
            val target = targets.get(key)
            AtlasPairNode(
                key = key,
                label = node.string("label"),
                bounds = AtlasPairBounds(
                    position.get("x").asFloat, position.get("y").asFloat,
                    position.get("width").asFloat, position.get("height").asFloat,
                ),
                equipmentId = if (target == null || target.isJsonNull) null else CanonicalId(target.asString),
            )
        }
        require(nodes.size == binding.get("nodeCount").asInt)
        require(targets.keySet() == nodes.map { it.key }.toSet())
        val nodeKeys = nodes.map { it.key }.toSet()
        val steps = sequenceEntry.getAsJsonArray("steps").map { item ->
            val step = item.asJsonObject
            val active = mutableSetOf<String>()
            step.getAsJsonArray("activeHotspotIds")?.forEach { active += it.asString }
            step.getAsJsonArray("activeEquipmentIds")?.forEach { id ->
                if (id.asString in nodeKeys) active += id.asString
            }
            step.getAsJsonArray("edges")?.forEach { itemEdge ->
                val edge = itemEdge.asJsonObject
                for (key in listOf("fromAnchor", "toAnchor", "fromEquipmentId", "toEquipmentId")) {
                    edge.get(key)?.asString?.let { if (it in nodeKeys) active += it }
                }
            }
            AtlasPairStep(step.string("title"), step.string("explanation"), active)
        }
        require(steps.size == binding.get("stepCount").asInt)
        return AtlasPairRoute(
            sequenceEntryId = sequence.string("id"), layoutEntryId = layout.string("id"),
            modelId = model, variantIds = variantIds,
            title = sequenceEntry.string("title"),
            functionalDisclaimer = sequenceEntry.string("functionalDisclaimer"),
            nodes = nodes, steps = steps,
        )
    }
}

private fun JsonObject.string(key: String): String =
    requireNotNull(get(key)?.takeUnless { it.isJsonNull }?.asString) { "missing $key" }
        .also { require(it.isNotBlank()) }
