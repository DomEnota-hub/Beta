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

class CommonFirstAidPackTest {
    @Test fun sourcePinnedTopicsLoadOnceWithoutPublication() {
        val path = Path.of(
            "..", "content-packs", "common", "first-aid", "topics.pack.json"
        )
        val pack = ContentPackJsonLoader().parse(Files.readString(path))
        val registry = ContentRegistry()
        assertEquals(20, pack.entries.size)
        assertTrue(registry.install(pack).isEmpty())
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertTrue(registry.install(pack).any {
            it.code == ValidationIssueCode.DUPLICATE_CANONICAL_ID
        })
        for (id in listOf("hypothermia", "frostbite")) {
            val entry = registry.find(CanonicalId("common.first-aid.$id"))
            assertEquals(ContentType.FIRST_AID, entry?.type)
            assertEquals(
                ResolveResult.NotPublished,
                registry.resolve(
                    ContentTarget(CanonicalId("common.first-aid.$id"), ContentType.FIRST_AID),
                    RuntimeContext(),
                ),
            )
        }
    }
}
