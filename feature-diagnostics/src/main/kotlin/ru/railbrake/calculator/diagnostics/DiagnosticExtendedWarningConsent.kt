package ru.railbrake.calculator.diagnostics

/**
 * A temporary, session-local consent state for viewing separately approved
 * historical INFORMATION. Neither reaching the bottom nor acknowledgment
 * establishes operating authority, source applicability, or publication.
 *
 * This state is intentionally not persisted and must be recreated whenever the
 * warning closes. No caller may infer read-to-end from a checkbox alone.
 */
data class DiagnosticExtendedWarningConsent(
    val readToEnd: Boolean = false,
    val acknowledged: Boolean = false,
) {
    val canEnableInformation: Boolean
        get() = readToEnd && acknowledged

    fun reachedViewportEnd(
        scrollValue: Int,
        maxScrollValue: Int,
        viewportLaidOut: Boolean,
    ): DiagnosticExtendedWarningConsent =
        if (viewportLaidOut && maxScrollValue > 0 &&
            scrollValue >= maxScrollValue && scrollValue >= 0
        ) copy(readToEnd = true) else this

    fun acknowledge(checked: Boolean): DiagnosticExtendedWarningConsent =
        copy(acknowledged = checked && readToEnd)

    fun asPresentationSettings(): DiagnosticPresentationSettings =
        DiagnosticPresentationSettings(
            extendedEnabled = canEnableInformation,
            warningReadToEnd = readToEnd,
            warningAcknowledged = acknowledged && readToEnd,
        )
}
