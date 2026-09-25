package ru.railbrake.calculator.core

enum class DiagnosticLocomotiveFamily(val policyId: String) {
    VL80S("VL80S"),
    ERMAK_2ES5K("2ES5K"),
    ERMAK_3ES5K("3ES5K")
}

enum class ErmakSectionProfile(val policyId: String) {
    HEAD("ermak_section_head"),
    BOOSTER("ermak_section_booster")
}

enum class ErmakControlSystemProfile(val policyId: String) {
    MSUD_N("ermak_msud_n"),
    MSUD_015("ermak_msud_015")
}

enum class ErmakTractionRegulationProfile(val policyId: String) {
    GROUP("ermak_regulation_group"),
    AXLE("ermak_regulation_axle")
}

enum class ErmakBrakeProfile(val policyId: String) {
    CRANE_395("ermak_brake_395"),
    CRANE_130_UKTOL("ermak_brake_130_uktol"),
    CRANE_130_2("ermak_brake_130_2")
}

enum class ErmakMotorAxleBearingProfile(val policyId: String) {
    SLIDING("ermak_mop_sliding"),
    ROLLING("ermak_mop_rolling")
}

/**
 * Explicit profile evidence for diagnostic policy. Null means "not confirmed".
 * The context never derives one trait from another and never treats a UI default as confirmation.
 */
data class DiagnosticProfileContext(
    val family: DiagnosticLocomotiveFamily? = null,
    val ermakSection: ErmakSectionProfile? = null,
    val ermakControlSystem: ErmakControlSystemProfile? = null,
    val ermakTractionRegulation: ErmakTractionRegulationProfile? = null,
    val ermakBrakeProfile: ErmakBrakeProfile? = null,
    val safetySystemProfileId: String? = null,
    val ermakMotorAxleBearing: ErmakMotorAxleBearingProfile? = null,
    val fireSuppressionProfileId: String? = null,
    val legacyProfileIds: Set<String> = emptySet(),
    val confirmed: Boolean = false
) {
    fun confirmedPolicyIds(): Set<String> {
        if (!confirmed) return emptySet()
        return buildSet {
            legacyProfileIds.mapNotNull(::cleanId).forEach(::add)
            ermakSection?.policyId?.let(::add)
            ermakControlSystem?.policyId?.let(::add)
            ermakTractionRegulation?.policyId?.let(::add)
            ermakBrakeProfile?.policyId?.let(::add)
            ermakMotorAxleBearing?.policyId?.let(::add)
            safetySystemProfileId?.let(::cleanId)?.let { add("ermak_safety:$it") }
            fireSuppressionProfileId?.let(::cleanId)?.let { add("ermak_fire:$it") }
        }
    }

    /**
     * Resolves only a profile id that is explicitly confirmed and compatible with the
     * scenario's declared profile ids. No match means profileConfirmed=false.
     */
    fun toPolicyContext(
        applicability: DiagnosticApplicability,
        safetyGateConfirmed: Boolean = false
    ): DiagnosticPolicyContext {
        val familyId = family?.policyId
        val confirmedIds = confirmedPolicyIds()
        val requested = applicability.profiles.map(::policyKey).toSet()
        val selected = when {
            !confirmed || familyId == null || confirmedIds.isEmpty() -> null
            requested.isEmpty() || "all_confirmed_profiles" in requested -> confirmedIds.firstOrNull()
            else -> confirmedIds.firstOrNull { policyKey(it) in requested }
        }
        return DiagnosticPolicyContext(
            selectedFamily = familyId,
            selectedProfileId = selected,
            profileConfirmed = selected != null,
            safetyGateConfirmed = safetyGateConfirmed
        )
    }

    companion object {
        fun safetyTrait(profileId: String): String =
            "ermak_safety:${requireNotNull(cleanId(profileId)) { "Safety profile id must not be blank" }}"

        fun fireSuppressionTrait(profileId: String): String =
            "ermak_fire:${requireNotNull(cleanId(profileId)) { "Fire suppression profile id must not be blank" }}"

        private fun cleanId(value: String): String? = value.trim().takeIf(String::isNotBlank)
        private fun policyKey(value: String): String = value.trim().lowercase()
    }
}
