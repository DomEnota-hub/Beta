package ru.railbrake.calculator.runtime

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.ActionDisposition
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentEntry
import ru.railbrake.calculator.domain.ContentLink
import ru.railbrake.calculator.domain.ContentOwner
import ru.railbrake.calculator.domain.ContentPackManifest
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.LinkScope
import ru.railbrake.calculator.domain.LinkType
import ru.railbrake.calculator.domain.ModelId
import ru.railbrake.calculator.domain.PackId
import ru.railbrake.calculator.domain.ProvenanceClass
import ru.railbrake.calculator.domain.PublicationStatus
import ru.railbrake.calculator.domain.RuntimeContext
import ru.railbrake.calculator.domain.SourceStatus

class CommonInternalLinksTest {
    private val source = ContentEntry(
        id = CanonicalId("common.source.first-aid-donor"),
        type = ContentType.SOURCE,
        owner = ContentOwner.Common,
        title = "Source",
        provenance = ProvenanceClass.UNKNOWN,
        sourceStatus = SourceStatus.UNKNOWN,
        actionDisposition = ActionDisposition.INFORMATION_ONLY,
        publicationStatus = PublicationStatus.CANDIDATE,
    )
    private val topic = ContentEntry(
        id = CanonicalId("common.first-aid.hypothermia"),
        type = ContentType.FIRST_AID,
        owner = ContentOwner.Common,
        title = "Topic",
        provenance = ProvenanceClass.UNKNOWN,
        sourceStatus = SourceStatus.UNKNOWN,
        actionDisposition = ActionDisposition.INFORMATION_ONLY,
        publicationStatus = PublicationStatus.CANDIDATE,
        links = listOf(ContentLink(
            type = LinkType.SOURCE,
            targetId = source.id,
            scope = LinkScope.COMMON_INTERNAL,
        )),
    )

    private fun pack(entries: List<ContentEntry>) = ContentPack(
        manifest = ContentPackManifest(
            schemaVersion = 1,
            packId = PackId("common.test"),
            packVersion = "0.1",
            family = null,
            modelIds = emptySet(),
            variantIds = emptySet(),
            locale = "ru-RU",
            entries = entries.map { it.id }.toSet(),
            requiresRuntime = "1.1",
            sourceCatalogVersion = "test",
            checksums = emptyMap(),
        ),
        entries = entries,
    )

    @Test fun commonTopicCanCiteCommonSourceWhileRemainingUnpublished() {
        val registry = ContentRegistry()
        assertTrue(registry.install(pack(listOf(topic, source))).isEmpty())
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertEquals(
            ResolveResult.NotPublished,
            registry.resolve(ContentTarget(topic.id, ContentType.FIRST_AID), RuntimeContext()),
        )
    }

    @Test fun commonInternalScopeCannotPointToModelSource() {
        val modelSource = source.copy(
            id = CanonicalId("vl80s.source.some"),
            owner = ContentOwner.Model(ModelId("vl80s")),
        )
        val registry = ContentRegistry()
        assertTrue(registry.install(pack(listOf(topic.copy(
            links = listOf(ContentLink(
                type = LinkType.SOURCE,
                targetId = modelSource.id,
                scope = LinkScope.COMMON_INTERNAL,
            )),
        )))).isEmpty())
        assertTrue(registry.install(pack(listOf(modelSource))).isEmpty())
        assertTrue(registry.validateGlobalLinks().any {
            it.code == ValidationIssueCode.LINK_SCOPE_VIOLATION
        })
    }
}
