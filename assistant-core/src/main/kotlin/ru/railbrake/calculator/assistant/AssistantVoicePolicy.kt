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

    /** API 33+ preflight: only an already installed Russian on-device pack may record.
     * A downloadable or pending pack is NOT silently downloaded or treated as installed.
     */
    enum class RussianPack { INSTALLED, NEEDS_DOWNLOAD, UNAVAILABLE }

    fun russianPack(
        installed: Collection<String>,
        downloadable: Collection<String>,
        pending: Collection<String>
    ): RussianPack {
        fun containsRussian(tags: Collection<String>): Boolean = tags.any { tag ->
            tag.trim().replace('_', '-').lowercase(java.util.Locale.ROOT)
                .substringBefore('-') == "ru"
        }
        return when {
            containsRussian(installed) -> RussianPack.INSTALLED
            containsRussian(downloadable) || containsRussian(pending) -> RussianPack.NEEDS_DOWNLOAD
            else -> RussianPack.UNAVAILABLE
        }
    }

    fun transcriptOrNull(raw: String?): String? {
        val text = raw?.trim()?.replace(Regex("\\s+"), " ") ?: return null
        return text.takeIf {
            it.isNotBlank() && it.length <= MAX_TRANSCRIPT_CHARS &&
                it.none { character -> character.code < 32 || character.code == 127 }
        }
    }
}


/**
 * Invalidates delayed Android permission, recognition-support and recognition callbacks.
 * Each new request owns a generation; cancelling or leaving the screen makes old callbacks inert.
 * Pure Kotlin so the lifecycle race can be regression-tested without a microphone or device.
 */
class AssistantVoiceSessionGate {
    private var attached = true
    private var generation = 0L

    fun next(): Long? = if (attached) ++generation else null

    fun isCurrent(token: Long): Boolean = attached && token == generation

    fun invalidate() {
        generation++
    }

    fun dispose() {
        attached = false
        invalidate()
    }
}
