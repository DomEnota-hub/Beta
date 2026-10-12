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

class Tem2VariantPacksTest {
    @Test fun catalogsGraphsAndTrainingLayoutsStayVariantScoped() {
        val specs = listOf(
            Triple("technical-data/catalog", "catalog", 13),
            Triple("diagnostics/recommended", "diagnostics", 2),
            Triple("atlas/layouts", "layouts", 1),
            Triple("atlas/sequences", "sequences", 1),
        )
        val paths = specs.flatMap { (section, kind, count) ->
            (1..count).map { n ->
                Path.of("..", "content-packs", "diesel", "tem2-family", section,
                    "%s-%02d.pack.json".format(kind, n))
            }
        }
        val packs = paths.map { ContentPackJsonLoader().parse(Files.readString(it)) }
        assertEquals(17, packs.size)
        assertEquals(320, packs.sumOf { it.entries.size })
        assertEquals(1073, packs.sumOf { pack -> pack.entries.sumOf { it.links.size } })
        val registry = ContentRegistry()
        packs.forEach { assertTrue(registry.install(it).isEmpty()) }
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertTrue(registry.install(packs.first()).any {
            it.code == ValidationIssueCode.DUPLICATE_CANONICAL_ID
        })
        val tem2 = RuntimeContext(workingModelId = ModelId("tem2-family"),
            activeVariantId = VariantId("tem2"))
        val tem2u = tem2.copy(activeVariantId = VariantId("tem2u"))
        val uEquipment = registry.find(CanonicalId("tem2.catalog.tem2-eq-tg.tem2u"))!!
        assertFalse(uEquipment.applicability.matches(tem2))
        assertTrue(uEquipment.applicability.matches(tem2u))
        val shared = registry.find(CanonicalId("tem2.diagnostics.tem2-diag-001"))!!
        assertTrue(shared.applicability.matches(tem2))
        assertTrue(shared.applicability.matches(tem2u))
        assertEquals(ResolveResult.NotPublished, registry.resolve(
            ContentTarget(shared.id, ContentType.DIAGNOSTIC_SCENARIO), tem2,
        ))
        val layout = registry.find(CanonicalId(
            "tem2.layouts.tem2-tem2-sch-traction-flow"))!!
        val raw = JsonParser.parseString(layout.sourceObject!!.objectJson).asJsonObject
        assertTrue(raw.has("contentBounds"))
        assertTrue(raw.getAsJsonArray("nodes").size() > 0)
    }
}
