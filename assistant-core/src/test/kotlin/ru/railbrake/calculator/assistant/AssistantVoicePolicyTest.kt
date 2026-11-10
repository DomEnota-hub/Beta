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
