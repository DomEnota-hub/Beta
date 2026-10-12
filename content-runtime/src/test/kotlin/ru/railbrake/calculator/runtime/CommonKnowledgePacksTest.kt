package ru.railbrake.calculator.runtime

import java.nio.file.Files
import java.nio.file.Path
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import ru.railbrake.calculator.domain.CanonicalId
import ru.railbrake.calculator.domain.ContentTarget
import ru.railbrake.calculator.domain.ContentType
import ru.railbrake.calculator.domain.RuntimeContext

class CommonKnowledgePacksTest {
    @Test fun allCommonPacksLoadOnceAndRemainGated() {
        val registry = ContentRegistry()
        val paths = listOf(
            "first-aid/topics.pack.json",
            "knowledge/articles.pack.json",
            "safety/articles.pack.json",
        )
        val packs = paths.map { relative ->
            ContentPackJsonLoader().parse(Files.readString(
                Path.of("..", "content-packs", "common", relative),
            ))
        }
        assertEquals(listOf(20, 45, 22), packs.map { it.entries.size })
        packs.forEach { assertTrue(registry.install(it).isEmpty()) }
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertTrue(registry.install(packs[1]).any {
            it.code == ValidationIssueCode.DUPLICATE_CANONICAL_ID
        })
        for ((id, type) in listOf(
            "common.knowledge.appendix12" to ContentType.KNOWLEDGE,
            "common.safety.safety-electrical" to ContentType.SAFETY,
            "common.first-aid.frostbite" to ContentType.FIRST_AID,
        )) {
            assertEquals(
                ResolveResult.NotPublished,
                registry.resolve(ContentTarget(CanonicalId(id), type), RuntimeContext()),
            )
        }
    }
}
