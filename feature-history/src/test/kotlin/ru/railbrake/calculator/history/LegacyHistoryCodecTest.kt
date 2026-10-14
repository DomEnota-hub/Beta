package ru.railbrake.calculator.history

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class LegacyHistoryCodecTest {
    private val firstRaw =
        "1700000000000|0J_QviDQvNCw0YHRgdC1|NDAwMCDRgg==|OCDQotCR|0KDQsNGB0YfRkdGCIHwg0LfQsNC80LXRgtC60LA="
    private val secondRaw =
        "1700000000000|0JjQlNCfIOKEljEy|0J3QvtCy0YvQuQ==|0KHQstC-0LTQutCw|0JTQtdGC0LDQu9C4"

    @Test
    fun readsExactDonorUrlSafeBase64WithoutLosingUnicodeOrPipes() {
        val record = LegacyHistoryCodec.decode(firstRaw)!!
        assertEquals(1700000000000L, record.timestampMillis)
        assertEquals("По массе", record.mode)
        assertEquals("4000 т", record.title)
        assertEquals("8 ТБ", record.summary)
        assertEquals("Расчёт | заметка", record.details)
        assertEquals(firstRaw, LegacyHistoryCodec.encode(record))
    }

    @Test
    fun inspectionPreservesMalformedRawAndSameTimestampRecords() {
        val raw = setOf(firstRaw, secondRaw, "broken", "2|@@|QQ==|QQ==|QQ==")
        val result = LegacyHistoryCodec.inspect(raw)
        assertEquals(raw, result.rawRecords)
        assertEquals(setOf("broken", "2|@@|QQ==|QQ==|QQ=="), result.invalidRawRecords)
        assertEquals(2, result.validRecords.size)
        assertTrue(result.validRecords.all { it.timestampMillis == 1700000000000L })
        assertEquals(2, result.timestampCollisions[1700000000000L]?.size)
        assertFalse(HistoryStorageMigrationGate.legacyFormatVerified)
    }

    @Test
    fun emptyFieldsAndUnpaddedUrlSafeTextRemainReadable() {
        val record = LegacyHistoryCodec.decode("1||QQ|0J_QviDQvNCw0YHRgdC1|")!!
        assertEquals("", record.mode)
        assertEquals("A", record.title)
        assertEquals("", record.details)
        assertEquals("1||QQ==|0J_QviDQvNCw0YHRgdC1|", LegacyHistoryCodec.encode(record))
    }

    @Test
    fun rejectsWrongFieldCountAndTimestampWithoutThrowing() {
        assertNull(LegacyHistoryCodec.decode("1|QQ=="))
        assertNull(LegacyHistoryCodec.decode("bad|QQ==|QQ==|QQ==|QQ=="))
        assertNull(LegacyHistoryCodec.decode("1|QQ==|QQ==|QQ==|QQ==|extra"))
    }
}
