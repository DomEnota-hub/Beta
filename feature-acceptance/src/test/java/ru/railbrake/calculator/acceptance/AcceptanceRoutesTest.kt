package ru.railbrake.calculator.acceptance

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.Applicability
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentBlock
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentPackManifest
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.VariantId
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.PackId
import ru.railbrake.calculator.domain.ProvenanceClass
import ru.railbrake.calculator.domain.SourceStatus
import ru.railbrake.calculator.runtime.ContentPack
import ru.railbrake.calculator.runtime.ContentRegistry

class AcceptanceRoutesTest {
    private val model = ModelId("vl80s")

    private fun item(
        id: String,
        title: String,
        searchTerms: Set<String> = emptySet(),
        blocks: List<ContentBlock> = emptyList(),
    ) = ContentEntry(
        id = CanonicalId(id),
        type = ContentType.ACCEPTANCE_ITEM,
        owner = ContentOwner.Model(model),
        applicability = Applicability(modelIds = setOf(model)),
        provenance = ProvenanceClass.UNKNOWN,
        sourceStatus = SourceStatus.UNKNOWN,
        actionDisposition = ActionDisposition.INFORMATION_ONLY,
        title = title,
        summary = "Проверить состояние",
        searchTerms = searchTerms,
        blocks = blocks,
    )

    @Test
    fun parsesAndResolvesRouteInDeclaredOrder() {
        val index = AcceptanceFeatureIndexJsonLoader().parse(
            """
            {
              "schemaVersion": 1,
              "modelId": "vl80s",
              "itemPacks": ["required.pack.json", "items.pack.json"],
              "routes": [
                {
                  "id": "route",
                  "title": "Полный осмотр",
                  "mode": "step_by_step",
                  "modeLabel": "пошагово",
                  "status": "ROUTE",
                  "sequence": ["A", "B"],
                  "sourceRouteId": "legacy",
                  "description": "Описание"
                }
              ]
            }
            """.trimIndent()
        )

        val a = item("A", "Первый")
        val b = item("B", "Второй")
        val registry = ContentRegistry()
        assertTrue(
            registry.install(
                ContentPack(
                    manifest = ContentPackManifest(
                        schemaVersion = 1,
                        packId = PackId("acceptance.test"),
                        packVersion = "1",
                        family = "ELECTRIC",
                        modelIds = setOf(model),
                        variantIds = emptySet(),
                        locale = "ru-RU",
                        entries = setOf(a.id, b.id),
                        requiresRuntime = "1",
                        sourceCatalogVersion = "test",
                        checksums = emptyMap(),
                    ),
                    entries = listOf(a, b),
                )
            ).isEmpty()
        )

        val resolved = AcceptanceRouteResolver(registry, RuntimeContext(workingModelId = model)).resolve(index.routes.single())
        assertTrue(resolved is AcceptanceRouteResolution.Ready)
        val ready = (resolved as AcceptanceRouteResolution.Ready).value
        assertEquals(listOf("A", "B"), ready.items.map { it.id.value })
    }

    @Test
    fun searchUsesTermsAndStructuredBlocks() {
        val entry = item(
            id = "A",
            title = "Крышевое оборудование",
            searchTerms = setOf("токоприёмник"),
            blocks = listOf(
                ContentBlock(
                    title = "Опасные признаки",
                    lines = listOf("Повреждение изолятора"),
                )
            ),
        )

        assertTrue(entry.matchesAcceptanceQuery("токопри"))
        assertTrue(entry.matchesAcceptanceQuery("изолятор"))
    }

    @Test
    fun missingRouteTargetFailsClosed() {
        val route = AcceptanceRoute(
            id = "route",
            title = "Маршрут",
            mode = "checklist",
            modeLabel = "контрольный список",
            status = "ROUTE",
            sequence = listOf(CanonicalId("missing")),
            sourceRouteId = null,
            description = null,
        )

        val result = AcceptanceRouteResolver(ContentRegistry(), RuntimeContext(workingModelId = model)).resolve(route)
        assertTrue(result is AcceptanceRouteResolution.Invalid)
        assertEquals(
            "missing",
            (result as AcceptanceRouteResolution.Invalid).issues.single().itemId.value,
        )
    }

    @Test
    fun routeDeniesUnpublishedWrongModelAndVariantSpecificItems() {
        val route = AcceptanceRoute(
            id = "secure-route", title = "Приёмка", mode = "checklist",
            modeLabel = "контрольный список", status = "ROUTE",
            sequence = listOf(CanonicalId("A"), CanonicalId("B"), CanonicalId("C")),
            sourceRouteId = null, description = null,
        )
        val candidate = item("A", "Кандидат").copy(
            publicationStatus = PublicationStatus.CANDIDATE,
        )
        val wrongModel = item("B", "Чужая модель").copy(
            owner = ContentOwner.Model(ModelId("chme3")),
            applicability = Applicability(modelIds = setOf(ModelId("chme3"))),
        )
        val wrongVariant = item("C", "Иное исполнение").copy(
            applicability = Applicability(
                modelIds = setOf(model), variantIds = setOf(VariantId("vl80s_pre697")),
            ),
        )
        val entries = listOf(candidate, wrongModel, wrongVariant)
        val registry = ContentRegistry()
        assertTrue(registry.install(ContentPack(
            manifest = ContentPackManifest(
                schemaVersion = 1, packId = PackId("acceptance.secure"),
                packVersion = "1", family = "ELECTRIC",
                modelIds = setOf(model, ModelId("chme3")), variantIds = emptySet(),
                locale = "ru-RU", entries = entries.map { it.id }.toSet(),
                requiresRuntime = "1", sourceCatalogVersion = "test", checksums = emptyMap(),
            ),
            entries = entries,
        )).isEmpty())
        val result = AcceptanceRouteResolver(
            registry,
            RuntimeContext(workingModelId = model, activeVariantId = VariantId("vl80s_unknown")),
        ).resolve(route)
        assertTrue(result is AcceptanceRouteResolution.Invalid)
        assertEquals(
            listOf("A", "B", "C"),
            (result as AcceptanceRouteResolution.Invalid).issues.map { it.itemId.value },
        )
    }

    @Test
    fun routeWithoutExplicitModelFailsClosed() {
        val route = AcceptanceRoute(
            id = "route", title = "Приёмка", mode = "checklist",
            modeLabel = "контрольный список", status = "ROUTE",
            sequence = listOf(CanonicalId("missing")),
            sourceRouteId = null, description = null,
        )
        assertTrue(
            AcceptanceRouteResolver(ContentRegistry(), RuntimeContext()).resolve(route)
                is AcceptanceRouteResolution.Invalid,
        )
    }
}
