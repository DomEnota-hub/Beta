package ru.railbrake.calculator.assistant

/** Voice is only an optional text-input source. It never authorizes a diagnostic action. */
object AssistantVoicePolicy {
    const val MIN_ON_DEVICE_API = 31
    const val MAX_DURATION_MS = 20_000L
    const val MAX_TRANSCRIPT_CHARS = 240

    enum class Capability { AVAILABLE, PERMISSION_REQUIRED, UNAVAILABLE }

    fun capability(api: Int, onDeviceService: Boolean, permissionGranted: Boolean): Capability =
        when {
            api < MIN_ON_DEVICE_API || !onDeviceService -> Capability.UNAVAILABLE
            !permissionGranted -> Capability.PERMISSION_REQUIRED
            else -> Capability.AVAILABLE
        }

    fun transcriptOrNull(raw: String?): String? {
        val text = raw?.trim()?.replace(Regex("\\s+"), " ") ?: return null
        return text.takeIf {
            it.isNotBlank() && it.length <= MAX_TRANSCRIPT_CHARS &&
                it.none { character -> character.code < 32 || character.code == 127 }
        }
    }
}
