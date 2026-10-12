package ru.railbrake.calculator.runtime

import com.google.gson.JsonParser
import java.nio.file.Files
import java.nio.file.Path
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.RuntimeContext

class ErmakSourcePacksTest {
    @Test fun allStructuredPacksLoadOnceAndPreserveNestedData() {
        val files = listOf(
            Triple("atlas/equipment", "equipment", 6),
            Triple("technical-data/knowledge", "knowledge", 7),
            Triple("diagnostics/recommended", "diagnostics", 7),
            Triple("atlas/schemes", "schemes", 2),
        ).flatMap { (subdir, name, count) ->
            (1..count).map { n ->
                Path.of("..", "content-packs", "electric", "ermak", subdir,
                    "%s-%02d.pack.json".format(name, n))
            }
        }
        val packs = files.map { ContentPackJsonLoader().parse(Files.readString(it)) }
        assertEquals(22, packs.size)
        assertEquals(407, packs.sumOf { it.entries.size })
        val registry = ContentRegistry()
        packs.forEach { assertTrue(registry.install(it).isEmpty()) }
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertTrue(registry.install(packs[0]).any {
            it.code == ValidationIssueCode.DUPLICATE_CANONICAL_ID
        })
        val equipment = registry.find(CanonicalId("ER-EQ-HV-001"))!!
        val raw = JsonParser.parseString(equipment.sourceObject!!.objectJson).asJsonObject
        assertEquals("ER-EQ-HV-001", raw.get("id").asString)
        assertEquals("MPa", raw.getAsJsonArray("parameters")[12].asJsonObject.get("unit").asString)
        assertEquals("each_section", raw.getAsJsonObject("location").get("sectionScope").asString)
        val scenario = registry.find(CanonicalId("ER-DIAG-001"))!!
        val graph = JsonParser.parseString(scenario.sourceObject!!.objectJson)
            .asJsonObject.getAsJsonObject("graph")
        assertTrue(graph.getAsJsonArray("nodes").size() > 0)
        val scheme = registry.find(CanonicalId("ER-SCH-EL-BASE-POWER"))!!
        assertTrue(JsonParser.parseString(scheme.sourceObject!!.objectJson)
            .asJsonObject.has("layers"))
        assertEquals(ResolveResult.NotPublished, registry.resolve(
            ContentTarget(CanonicalId("ER-DIAG-001"), ContentType.DIAGNOSTIC_SCENARIO),
            RuntimeContext(workingModelId = ModelId("ermak")),
        ))
    }
}
