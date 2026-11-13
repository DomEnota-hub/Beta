package ru.railbrake.calculator.history

import java.util.Base64
import org.junit.Assert.*
import org.junit.Test

class LegacyDiagnosticSessionCodecTest {
    private fun encoded(vararg fields: String): String {
        val encoder = Base64.getUrlEncoder()
        return fields.joinToString("|") {
            encoder.encodeToString(it.toByteArray(Charsets.UTF_8))
        }
    }

    @Test fun readsPinnedSevenFieldUrlSafeArchiveWithUnicode() {
        val line = encoded("1700000000000", "vl80s", "vl80s", "PAN-1",
            "Токоприёмник | не поднимается", "WARNING", "Проверить\nне лезть на крышу")
        val row = LegacyDiagnosticSessionCodec.parse(line)!!
        assertEquals("Токоприёмник | не поднимается", row.scenarioTitle)
        assertTrue(row.report.contains("не лезть"))
    }

    @Test fun corruptedRecordsAreCountedAndNeverPromoted() {
        val source = setOf("bad", encoded("2", "vl80s", "", "s1", "Тест", "INFO", "Текст"))
        val result = LegacyDiagnosticSessionCodec.read(source)
        assertEquals(1, result.malformedCount)
        assertEquals(1, result.records.size)
        assertEquals(2, source.size)
    }

    @Test fun exactModelFilterNeverAliasesErmakOrOtherLocomotives() {
        val source = setOf(
            encoded("2", "ermak", "msud-n", "a", "Ермак", "INFO", "Архив"),
            encoded("3", "vl80s", "", "b", "ВЛ80С", "INFO", "Архив"),
        )
        val all = LegacyDiagnosticSessionCodec.read(source)
        assertTrue(LegacyDiagnosticSessionCodec.forExactModel(all, "2es5k").records.isEmpty())
        assertEquals(1, LegacyDiagnosticSessionCodec.forExactModel(all, "vl80s").records.size)
        assertEquals(1, LegacyDiagnosticSessionCodec.forExactModel(all, "ermak").records.size)
    }

    @Test fun sameTimestampDistinctReportsAreRetained() {
        val source = setOf(
            encoded("2", "vl80s", "", "a", "Первый", "INFO", "A"),
            encoded("2", "vl80s", "", "b", "Второй", "INFO", "B"),
        )
        assertEquals(2, LegacyDiagnosticSessionCodec.read(source).records.size)
    }

    @Test fun collisionOrderingIsIndependentOfStringSetIteration() {
        val a = encoded("2", "vl80s", "", "a", "Первый", "INFO", "A")
        val b = encoded("2", "vl80s", "", "a", "Первый", "INFO", "B")
        val first = LegacyDiagnosticSessionCodec.read(linkedSetOf(b, a))
        val second = LegacyDiagnosticSessionCodec.read(linkedSetOf(a, b))
        assertEquals(first, second)
        assertEquals(listOf("A", "B"), first.records.map { it.report })
    }

    @Test fun excludedProfilesAreCountedWithoutExposingReports() {
        val all = LegacyDiagnosticSessionCodec.read(setOf(
            "bad",
            encoded("2", "ermak", "msud-n", "a", "Ермак", "INFO", "Other"),
            encoded("3", "vl80s", "", "b", "ВЛ80С", "INFO", "Own")
        ))
        val filtered = LegacyDiagnosticSessionCodec.forExactModel(all, "vl80s")
        assertEquals(1, filtered.excludedProfileCount)
        assertEquals(1, filtered.malformedCount)
        assertEquals(listOf("Own"), filtered.records.map { it.report })
    }

    @Test fun invalidTimestampAndUtf8AreRejected() {
        assertNull(LegacyDiagnosticSessionCodec.parse(encoded("-1", "vl80s", "", "a", "", "", "")))
        val bad = "////|"+encoded("vl80s", "", "a", "Title", "INFO", "Report")
        assertNull(LegacyDiagnosticSessionCodec.parse(bad))
    }
}
