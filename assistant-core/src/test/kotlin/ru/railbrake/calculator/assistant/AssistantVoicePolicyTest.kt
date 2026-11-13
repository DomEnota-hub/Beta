package ru.railbrake.calculator.assistant

import org.junit.Assert.*
import org.junit.Test

class AssistantVoicePolicyTest {
    @Test fun offlineOnlyAndPermissionGates() {
        assertEquals(AssistantVoicePolicy.Capability.UNAVAILABLE,
            AssistantVoicePolicy.capability(30, true, true))
        assertEquals(AssistantVoicePolicy.Capability.UNAVAILABLE,
            AssistantVoicePolicy.capability(34, false, true))
        assertEquals(AssistantVoicePolicy.Capability.PERMISSION_REQUIRED,
            AssistantVoicePolicy.capability(34, true, false))
        assertEquals(AssistantVoicePolicy.Capability.AVAILABLE,
            AssistantVoicePolicy.capability(34, true, true))
    }

    @Test fun russianOfflinePackMustAlreadyBeInstalled() {
        val p = AssistantVoicePolicy
        assertEquals(AssistantVoicePolicy.RussianPack.INSTALLED,
            p.russianPack(listOf("en-US", "ru-RU"), listOf("de-DE"), emptyList()))
        assertEquals(AssistantVoicePolicy.RussianPack.INSTALLED,
            p.russianPack(listOf("RU_ru"), emptyList(), emptyList()))
        assertEquals(AssistantVoicePolicy.RussianPack.NEEDS_DOWNLOAD,
            p.russianPack(emptyList(), listOf("ru"), emptyList()))
        assertEquals(AssistantVoicePolicy.RussianPack.NEEDS_DOWNLOAD,
            p.russianPack(emptyList(), emptyList(), listOf("ru-RU")))
        assertEquals(AssistantVoicePolicy.RussianPack.UNAVAILABLE,
            p.russianPack(listOf("uk-UA", "en-RU", "russian"), emptyList(), emptyList()))
        assertEquals(AssistantVoicePolicy.RussianPack.UNAVAILABLE,
            p.russianPack(emptyList(), emptyList(), emptyList()))
    }

    @Test fun permissionGrantAfterLeavingScreenMustNotStartMicrophone() {
        val gate = AssistantVoiceSessionGate()
        val permissionRequest = gate.next()!!
        assertTrue(gate.isCurrent(permissionRequest))
        gate.dispose()
        assertFalse(gate.isCurrent(permissionRequest))
        assertNull(gate.next())
    }

    @Test fun cancelledAndSupersededVoiceCallbacksAreIgnored() {
        val gate = AssistantVoiceSessionGate()
        val first = gate.next()!!
        val second = gate.next()!!
        assertFalse(gate.isCurrent(first))
        assertTrue(gate.isCurrent(second))
        gate.invalidate()
        assertFalse(gate.isCurrent(second))
        val third = gate.next()!!
        assertTrue(gate.isCurrent(third))
        gate.dispose()
        assertFalse(gate.isCurrent(third))
    }

    @Test fun cancelledPermissionCannotBeReplacedBeforeOldCallbackArrives() {
        val request = AssistantVoicePermissionRequest()
        assertTrue(request.begin(1L))
        request.cancel()
        assertTrue(request.pending)
        assertFalse(request.begin(2L))
        assertNull(request.complete())
        assertFalse(request.pending)
        assertTrue(request.begin(3L))
        assertEquals(3L, request.complete())
        assertNull(request.complete())
    }

    @Test fun rejectEmptyControlAndOversizedSpeech() {
        assertNull(AssistantVoicePolicy.transcriptOrNull(null))
        assertNull(AssistantVoicePolicy.transcriptOrNull("   "))
        assertNull(AssistantVoicePolicy.transcriptOrNull("a".repeat(241)))
        assertNull(AssistantVoicePolicy.transcriptOrNull("ВЛ80С\u0000"))
    }

    @Test fun keepSpeechAsTextWithoutExecutingIt() {
        assertEquals("ВЛ80С пантограф не поднимается",
            AssistantVoicePolicy.transcriptOrNull(" ВЛ80С  пантограф\nне поднимается "))
        assertEquals("2ЭС5К ГВ", AssistantVoicePolicy.transcriptOrNull("2ЭС5К ГВ"))
        assertEquals(240, AssistantVoicePolicy.transcriptOrNull("я".repeat(240))?.length)
    }
}
