package ru.railbrake.calculator.calculations

import org.junit.Assert.*
import org.junit.Test

class SecuringInputReviewTest {
    private val mass = MassSecuringDraft("4000", "212", "", "12", "15", "4")
    private val appendix = AppendixSecuringDraft(
        axleCount = "200", slopePermille = "8", formula = AppendixFormula.FORMULA_1,
        availableShoes = "15", axlesPerHandBrakeUnit = "4",
    )

    @Test fun massDraftProducesArithmeticOnlyPreview() {
        val result = SecuringInputReview.byMass(mass) as SecuringReview.Mass
        assertEquals(16, result.calculation.requiredShoes)
        assertEquals(1, result.supplement.shoeShortage)
        assertEquals(CalculationApproval.DONOR_PARITY_ONLY, result.approval)
        assertFalse(CalculationPublicationPolicy.canPublishOperationalResult(CalculationMode.BY_MASS))
    }

    @Test fun appendixDraftProducesArithmeticOnlyPreview() {
        val result = SecuringInputReview.byAppendix(appendix) as SecuringReview.Appendix
        assertEquals(13, result.calculation.totalRequiredShoes)
        assertEquals(CalculationApproval.FORMULA_REVIEWED_LOCAL_RULES_REQUIRED, result.approval)
        assertFalse(CalculationPublicationPolicy.canPublishOperationalResult(CalculationMode.APPENDIX_12))
    }

    @Test fun commaDecimalsAcceptedButInvalidNumbersRejected() {
        assertTrue(SecuringInputReview.byMass(mass.copy(massTons = "4000,0")) is SecuringReview.Mass)
        assertTrue(SecuringInputReview.byMass(mass.copy(massTons = "NaN")) is SecuringReview.Invalid)
        assertTrue(SecuringInputReview.byMass(mass.copy(massTons = "Infinity")) is SecuringReview.Invalid)
        assertTrue(SecuringInputReview.byAppendix(appendix.copy(windSpeedMs = "-1")) is SecuringReview.Invalid)
    }

    @Test fun missingFormulaNeverDefaultsSilently() {
        val result = SecuringInputReview.byAppendix(appendix.copy(formula = null))
        assertTrue(result is SecuringReview.Invalid)
    }

    @Test fun leavingWithoutLocoOverThresholdFailsClosed() {
        val result = SecuringInputReview.byAppendix(appendix.copy(leavingWithoutLocomotive = true))
        assertTrue(result is SecuringReview.Invalid)
        assertTrue((result as SecuringReview.Invalid).reason.contains("п. 20"))
    }

    @Test fun contradictoryAxleLoadIsRejected() {
        val result = SecuringInputReview.byMass(mass.copy(axleLoadTons = "5"))
        assertTrue(result is SecuringReview.Invalid)
    }

    @Test fun overflowAndNegativeInputsAreReportedNotCrashes() {
        assertTrue(SecuringInputReview.byMass(mass.copy(availableShoes = "-1")) is SecuringReview.Invalid)
        assertTrue(SecuringInputReview.byAppendix(appendix.copy(axleCount = "2147483647", slopePermille = "100")) is SecuringReview.Invalid)
        assertTrue(SecuringInputReview.byMass(mass.copy(axleCount = "x")) is SecuringReview.Invalid)
    }

    @Test fun largeAxleWindPreviewDoesNotSilentlyUndercount() {
        val result = SecuringInputReview.byAppendix(
            appendix.copy(
                axleCount = "1500000000",
                slopePermille = "0",
                formula = null,
                windSpeedMs = "16",
                windMatchesMovement = true,
                availableShoes = "0",
            )
        ) as SecuringReview.Appendix
        assertEquals(22_500_000, result.calculation.windShoes)
        assertEquals(22_500_002, result.calculation.totalRequiredShoes)
        assertEquals(CalculationApproval.FORMULA_REVIEWED_LOCAL_RULES_REQUIRED, result.approval)
    }

    @Test fun impossibleHandBrakeAxleCountIsAnErrorNotARecommendation() {
        val massInvalid = SecuringInputReview.byMass(
            mass.copy(massTons = "100", axleCount = "2", slopePermille = "12",
                availableShoes = "0", axlesPerHandBrakeUnit = "4")
        )
        assertTrue(massInvalid is SecuringReview.Invalid)
        assertTrue((massInvalid as SecuringReview.Invalid).reason.contains("больше осей"))

        val appendixInvalid = SecuringInputReview.byAppendix(
            appendix.copy(axleCount = "2", slopePermille = "0", formula = null,
                availableShoes = "0", axlesPerHandBrakeUnit = "4")
        )
        assertTrue(appendixInvalid is SecuringReview.Invalid)
        assertTrue((appendixInvalid as SecuringReview.Invalid).reason.contains("больше осей"))
    }

    @Test fun roundedLoadCannotChangeTenTonCategory() {
        val below = mass.copy(massTons = "1999", axleCount = "200", axleLoadTons = "10")
        val above = mass.copy(massTons = "2001", axleCount = "200", axleLoadTons = "9.999")
        for (draft in listOf(below, above)) {
            val result = SecuringInputReview.byMass(draft)
            assertTrue(result is SecuringReview.Invalid)
            assertTrue((result as SecuringReview.Invalid).reason.contains("границы 10"))
        }
        assertTrue(SecuringInputReview.byMass(
            mass.copy(massTons = "2000", axleCount = "200", axleLoadTons = "10")
        ) is SecuringReview.Mass)
    }

    @Test fun profileDoesNotInventFormulaSelection() {
        ProfileMode.entries.forEach { mode ->
            val result = SecuringInputReview.byAppendix(appendix.copy(profile = mode, formula = null))
            assertTrue(result is SecuringReview.Invalid)
        }
    }
}
