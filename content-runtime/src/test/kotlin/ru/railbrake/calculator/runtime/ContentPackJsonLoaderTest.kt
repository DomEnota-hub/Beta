package ru.railbrake.calculator.runtime

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.assertThrows
import com.google.gson.JsonParser
import org.junit.Test
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.VariantId

class ContentPackJsonLoaderTest {
    @Test
    fun parsesActiveAndCandidateEntriesAndFailsClosedAtResolution() {
        val json = """
            {
              "manifest": {
                "schemaVersion": 1,
                "packId": "vl80s.test",
                "packVersion": "0.1.0",
                "family": "ELECTRIC",
                "modelIds": ["vl80s"],
                "variantIds": ["vl80s-general"],
                "locale": "ru-RU",
                "entries": ["VL-EQ-HV-002", "vl80s.diag.pantograph-no-rise"],
                "requiresRuntime": "1.1.0",
                "sourceCatalogVersion": "test",
                "checksums": {}
              },
              "entries": [
                {
                  "id": "VL-EQ-HV-002",
                  "type": "EQUIPMENT",
                  "owner": {"kind": "MODEL", "modelId": "vl80s"},
                  "applicability": {
                    "modelIds": ["vl80s"],
                    "variantIds": ["vl80s-general"]
                  },
                  "title": "Токоприёмник",
                  "links": [
                    {
                      "type": "RELATED_SCENARIO",
                      "targetId": "vl80s.diag.pantograph-no-rise"
                    }
                  ]
                },
                {
                  "id": "vl80s.diag.pantograph-no-rise",
                  "aliases": ["pantograph-no-rise"],
                  "type": "DIAGNOSTIC_SCENARIO",
                  "owner": {"kind": "MODEL", "modelId": "vl80s"},
                  "applicability": {
                    "modelIds": ["vl80s"],
                    "variantIds": ["vl80s-general"]
                  },
                  "publicationStatus": "CANDIDATE",
                  "actionDisposition": "CONDITIONAL_ACTION",
                  "title": "Токоприёмник не поднимается"
                }
              ]
            }
        """.trimIndent()

        val pack = ContentPackJsonLoader().parse(json)
        val registry = ContentRegistry()

        assertTrue(registry.install(pack).isEmpty())
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertEquals("Токоприёмник", registry.find(CanonicalId("VL-EQ-HV-002"))?.title)

        val context = RuntimeContext(
            workingModelId = ModelId("vl80s"),
            viewedModelId = ModelId("vl80s"),
            activeVariantId = VariantId("vl80s-general"),
        )
        assertTrue(
            registry.resolve(
                ContentTarget(CanonicalId("VL-EQ-HV-002"), ContentType.EQUIPMENT),
                context,
            ) is ResolveResult.Found
        )
        assertEquals(
            ResolveResult.NotPublished,
            registry.resolve(
                ContentTarget(
                    CanonicalId("pantograph-no-rise"),
                    ContentType.DIAGNOSTIC_SCENARIO,
                ),
                context,
            )
        )
    }
    @Test
    fun preservesNestedDonorObjectAndRejectsIncompleteSnapshot() {
        val source = """{"sourcePath":"app/src/main/assets/technical/ermak_equipment.json.gz",
            "sourceBlobSha":"47a8d2424d69943fba9747746aa6ad8c8f4e2e98",
            "object":{"id":"ER-EQ-HV-001","parameters":[{"value":0.24,"unit":"MPa"}],
            "applicability":{"models":["2ES5K"],"profiles":["base_early"],"exclusions":[]}}}"""
        val prefix = """{"manifest":{"schemaVersion":1,"packId":"ermak.test",
            "packVersion":"0.1.0","modelIds":["ermak"],"variantIds":[],
            "locale":"ru-RU","entries":["ER-EQ-HV-001"],"requiresRuntime":"1.1.0",
            "sourceCatalogVersion":"test"},"entries":[{"id":"ER-EQ-HV-001",
            "type":"EQUIPMENT","owner":{"kind":"MODEL","modelId":"ermak"},
            "publicationStatus":"CANDIDATE","title":"test","sourceObject":"""
        val json = prefix + source + "}]}"
        val entry = ContentPackJsonLoader().parse(json).entries.single()
        assertEquals(
            JsonParser.parseString(source).asJsonObject.getAsJsonObject("object"),
            JsonParser.parseString(entry.sourceObject!!.objectJson),
        )
        assertEquals("app/src/main/assets/technical/ermak_equipment.json.gz",
            entry.sourceObject!!.sourcePath)
        assertThrows(IllegalArgumentException::class.java) {
            ContentPackJsonLoader().parse(
                prefix + """{"sourcePath":"x","sourceBlobSha":"y"}}]}"""
            )
        }
    }
}
