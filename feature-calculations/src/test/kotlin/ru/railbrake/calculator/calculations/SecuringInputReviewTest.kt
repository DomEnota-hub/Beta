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

    @Test fun profileDoesNotInventFormulaSelection() {
        ProfileMode.entries.forEach { mode ->
            val result = SecuringInputReview.byAppendix(appendix.copy(profile = mode, formula = null))
            assertTrue(result is SecuringReview.Invalid)
        }
    }
}
