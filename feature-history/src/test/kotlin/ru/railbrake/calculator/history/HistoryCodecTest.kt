package ru.railbrake.calculator.history

import org.junit.Assert.*
import org.junit.Test
import java.util.Base64

class HistoryCodecTest {
    private fun record(ts: Long = 1700000000000L, title: String = "Поезд") =
        HistoryRecord(ts, "По массе", title, "12 башмаков", "Проверка: НЕ допуск")

    @Test fun parsesPinnedAndroidUrlSafeBase64FormatWithRussianAndPipe() {
        val b64 = Base64.getUrlEncoder()
        fun enc(s: String) = b64.encodeToString(s.toByteArray(Charsets.UTF_8))
        val raw = "1700000000000|"+enc("По массе")+"|"+enc("Состав | 42")+
            "|"+enc("12 башмаков")+"|"+enc("НЕ допуск")
        assertEquals("Состав | 42", HistoryCodec.parseLegacy(raw)?.title)
        assertEquals("НЕ допуск", HistoryCodec.parseLegacy(raw)?.details)
    }

    @Test fun malformedLegacyIsIgnoredWithoutChangingSource() {
        val original = setOf("bad", HistoryCodec.encodeLegacy(record()))
        assertEquals(1, HistoryCodec.readLegacy(original).size)
        assertEquals(2, original.size)
        assertNull(HistoryCodec.parseLegacy("1|@@@|AA==|AA==|AA=="))
    }

    @Test fun migrationRoundTripPreservesUnicodeAndTimestampCollisions() {
        val a = record(title = "Состав А")
        val b = record(title = "Состав Б")
        val migrated = HistoryCodec.decodeV2(HistoryCodec.encodeV2(listOf(a, b)))
        assertEquals(2, migrated.size)
        assertTrue(migrated.containsAll(listOf(a, b)))
    }

    @Test fun versionedFormatRejectsCorruptionInsteadOfDestroyingHistory() {
        try {
            HistoryCodec.decodeV2("v2|broken")
            fail("Corruption must not be accepted")
        } catch (_: IllegalArgumentException) {}
    }

    @Test fun capsAtThirtyAndDeduplicatesExactCopies() {
        val records = (0L..40L).map { record(ts = it) } + record(ts = 40L)
        val decoded = HistoryCodec.decodeV2(HistoryCodec.encodeV2(records))
        assertEquals(30, decoded.size)
        assertEquals(40L, decoded.first().timestampMillis)
        assertEquals(11L, decoded.last().timestampMillis)
    }

    @Test fun notesRoundTripAndModelIsolation() {
        val notes = listOf(
            WorkNote("a", "vl80s", 2L, "Замечание | №1", "Текст\nвторая строка"),
            WorkNote("b", "chme3", 1L, "Заметка", "Без инструкции"),
        )
        val restored = WorkNotesCodec.decodeV1(WorkNotesCodec.encodeV1(notes))
        assertEquals(notes, restored)
        assertEquals(1, restored.count { it.modelId == "vl80s" })
    }
}
