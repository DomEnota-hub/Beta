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

class MigratedDataArrayTest {
    @Test fun allCommonAndNewModelPacksLoadTogetherExactlyOnce() {
        val roots = listOf(
            "common",
            "electric/ermak",
            "diesel/chme3-family",
            "diesel/tem2-family",
        )
        val base = Path.of("..", "content-packs")
        val paths = roots.flatMap { name ->
            Files.walk(base.resolve(name)).use { walk ->
                walk.filter { it.fileName.toString().endsWith(".pack.json") }
                    .sorted().toList()
            }
        }
        assertEquals(90, paths.size)
        val packs = paths.map { ContentPackJsonLoader().parse(Files.readString(it)) }
        assertEquals(1789, packs.sumOf { it.entries.size })
        assertEquals(11382, packs.sumOf { pack -> pack.entries.sumOf { it.links.size } })
        val registry = ContentRegistry()
        packs.forEach { assertTrue(registry.install(it).isEmpty()) }
        assertTrue(registry.validateGlobalLinks().isEmpty())
        assertTrue(registry.install(packs.last()).any {
            it.code == ValidationIssueCode.DUPLICATE_CANONICAL_ID
        })
        assertEquals(ResolveResult.NotPublished, registry.resolve(
            ContentTarget(CanonicalId("ER-DIAG-001"), ContentType.DIAGNOSTIC_SCENARIO),
            RuntimeContext(),
        ))
    }
}
