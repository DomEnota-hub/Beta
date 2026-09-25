package ru.railbrake.calculator.core

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticProfileContextTest {
    private val profileAction = DiagnosticActionMetadata(
        riskClass = "normal",
        userFacingPolicy = DiagnosticUserFacingPolicy.SOURCE_AND_PROFILE_REQUIRED,
        rawUserFacingPolicy = "SOURCE_AND_PROFILE_REQUIRED",
        sourceBound = true
    )

    @Test
    fun unknownProfileStaysBlocked() {
        val applicability = DiagnosticApplicability(
            families = setOf("2ES5K", "3ES5K"),
            profiles = setOf("base_early"),
            variantSelectionRequired = true
        )
        val context = DiagnosticProfileContext(
            family = DiagnosticLocomotiveFamily.ERMAK_2ES5K,
            confirmed = false
        )

        assertFalse(
            DiagnosticPolicyEngine.evaluate(
                applicability,
                profileAction,
                context.toPolicyContext(applicability)
            ).allowed
        )
    }

    @Test
    fun compatibleProfilePassesAndIncompatibleProfileDoesNot() {
        val applicability = DiagnosticApplicability(
            families = setOf("2ES5K", "3ES5K"),
            profiles = setOf("base_early"),
            variantSelectionRequired = true
        )
        val compatible = DiagnosticProfileContext(
            family = DiagnosticLocomotiveFamily.ERMAK_2ES5K,
            legacyProfileIds = setOf("base_early"),
            confirmed = true
        )
        val incompatible = compatible.copy(legacyProfileIds = setOf("other_profile"))

        assertTrue(
            DiagnosticPolicyEngine.evaluate(
                applicability,
                profileAction,
                compatible.toPolicyContext(applicability)
            ).allowed
        )
        assertFalse(
            DiagnosticPolicyEngine.evaluate(
                applicability,
                profileAction,
                incompatible.toPolicyContext(applicability)
            ).allowed
        )
    }

    @Test
    fun brakeProfilesDoNotCrossMatch() {
        val needs130 = DiagnosticApplicability(
            families = setOf("2ES5K", "3ES5K"),
            profiles = setOf(ErmakBrakeProfile.CRANE_130_UKTOL.policyId),
            variantSelectionRequired = true
        )
        val profile395 = DiagnosticProfileContext(
            family = DiagnosticLocomotiveFamily.ERMAK_2ES5K,
            ermakBrakeProfile = ErmakBrakeProfile.CRANE_395,
            confirmed = true
        )
        val profile130 = profile395.copy(ermakBrakeProfile = ErmakBrakeProfile.CRANE_130_UKTOL)

        assertFalse(
            DiagnosticPolicyEngine.evaluate(
                needs130,
                profileAction,
                profile395.toPolicyContext(needs130)
            ).allowed
        )
        assertTrue(
            DiagnosticPolicyEngine.evaluate(
                needs130,
                profileAction,
                profile130.toPolicyContext(needs130)
            ).allowed
        )

        val needs395 = needs130.copy(profiles = setOf(ErmakBrakeProfile.CRANE_395.policyId))
        assertFalse(
            DiagnosticPolicyEngine.evaluate(
                needs395,
                profileAction,
                profile130.toPolicyContext(needs395)
            ).allowed
        )
    }

    @Test
    fun safetyProfilesDoNotCrossMatch() {
        val safetyAId = DiagnosticProfileContext.safetyTrait("safety-a")
        val applicability = DiagnosticApplicability(
            families = setOf("2ES5K", "3ES5K"),
            profiles = setOf(safetyAId),
            variantSelectionRequired = true
        )
        val safetyA = DiagnosticProfileContext(
            family = DiagnosticLocomotiveFamily.ERMAK_3ES5K,
            safetySystemProfileId = "safety-a",
            confirmed = true
        )
        val safetyB = safetyA.copy(safetySystemProfileId = "safety-b")

        assertTrue(
            DiagnosticPolicyEngine.evaluate(
                applicability,
                profileAction,
                safetyA.toPolicyContext(applicability)
            ).allowed
        )
        assertFalse(
            DiagnosticPolicyEngine.evaluate(
                applicability,
                profileAction,
                safetyB.toPolicyContext(applicability)
            ).allowed
        )
    }

    @Test
    fun familyMismatchStillFailsClosed() {
        val applicability = DiagnosticApplicability(
            families = setOf("2ES5K", "3ES5K"),
            profiles = setOf("base_early"),
            variantSelectionRequired = true
        )
        val context = DiagnosticProfileContext(
            family = DiagnosticLocomotiveFamily.VL80S,
            legacyProfileIds = setOf("base_early"),
            confirmed = true
        )

        assertFalse(
            DiagnosticPolicyEngine.evaluate(
                applicability,
                profileAction,
                context.toPolicyContext(applicability)
            ).allowed
        )
    }
}
