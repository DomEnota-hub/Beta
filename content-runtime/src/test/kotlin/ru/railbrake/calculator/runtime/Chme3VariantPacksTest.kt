package ru.railbrake.calculator.runtime

import com.google.gson.JsonParser
import java.nio.file.Files
import java.nio.file.Path
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.VariantId

class Chme3VariantPacksTest {
    @Test fun mergedExactObjectsRemainVariantScopedAndUnpublished() {
        val paths = listOf("technical-data/catalog" to 34,
            "diagnostics/recommended" to 4).flatMap { (section, count) ->
            val name = if (section.startsWith("technical")) "catalog" else "diagnostics"
            (1..count).map { n ->
                Path.of("..", "content-packs", "diesel", "chme3-family", section,
                    "%s-%02d.pack.json".format(name, n))
            }
        }
        val packs = paths.map { ContentPackJsonLoader().parse(Files.readString(it)) }
        assertEquals(38, packs.size)
        assertEquals(738, packs.sumOf { it.entries.size })
        assertEquals(5421, packs.sumOf { it.entries.sumOf { entry -> entry.links.size } })
        val registry = ContentRegistry()
        packs.forEach { assertTrue(registry.install(it).isEmpty()) }
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertTrue(registry.install(packs.first()).any {
            it.code == ValidationIssueCode.DUPLICATE_CANONICAL_ID
        })
        val eVariant = registry.find(CanonicalId("chme3.catalog.chme3-sys-control.chme3e"))!!
        val baseContext = RuntimeContext(workingModelId = ModelId("chme3-family"),
            activeVariantId = VariantId("chme3"))
        val eContext = baseContext.copy(activeVariantId = VariantId("chme3e"))
        assertFalse(eVariant.applicability.matches(baseContext))
        assertTrue(eVariant.applicability.matches(eContext))
        assertEquals("CHME3-SYS-CONTROL", JsonParser.parseString(
            eVariant.sourceObject!!.objectJson).asJsonObject.get("id").asString)
        val scenario = registry.find(CanonicalId("chme3.diagnostics.chme3-diag-321"))!!
        assertEquals(setOf(VariantId("chme3"), VariantId("chme3t"), VariantId("chme3e")),
            scenario.applicability.variantIds)
        assertTrue(JsonParser.parseString(scenario.sourceObject!!.objectJson)
            .asJsonObject.getAsJsonObject("graph").getAsJsonArray("nodes").size() > 0)
        assertEquals(ResolveResult.NotPublished, registry.resolve(
            ContentTarget(scenario.id, ContentType.DIAGNOSTIC_SCENARIO), eContext,
        ))
    }
}
