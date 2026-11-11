package ru.railbrake.calculator.calculations

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test

class BrakeCalculatorSafetyBoundaryTest {
    @Test fun tinyPositiveResultIsRoundedUpNotDown() {
        val result = BrakeCalculator.calculateMass(
            MassCalculationInput(
                massTons = 1e-10,
                manualAxleLoadTons = 1.0,
                slopePermille = 0.0,
            )
        )
        assertTrue(result.shoesExact > 0.0)
        assertEquals(1, result.requiredShoes)
        assertEquals(1, result.fullManualBrakeAxles)
    }

    @Test fun rejectsNonfiniteOrInvalidMassInputs() {
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(Double.NaN, 10, slopePermille = 0.0)) }
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(Double.POSITIVE_INFINITY, 10, slopePermille = 0.0)) }
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(0.0, 10, slopePermille = 0.0)) }
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(100.0, 0, slopePermille = 0.0)) }
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(100.0, slopePermille = 0.0)) }
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(100.0, manualAxleLoadTons = Double.NaN, slopePermille = 0.0)) }
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(100.0, 10, slopePermille = 3.0)) }
        rejects { BrakeCalculator.calculateMass(MassCalculationInput(100.0, 10, slopePermille = Double.NaN)) }
    }

    @Test fun checkedAxleAndBrakeArithmeticRejectsOverflow() {
        assertEquals(36, BrakeCalculator.wagonAxles(4, 2, 1, 0))
        rejects { BrakeCalculator.wagonAxles(Int.MAX_VALUE, 0, 0, 0) }
        rejects { BrakeCalculator.wagonAxles(-1, 0, 0, 0) }

        val mass = BrakeCalculator.calculateMass(
            MassCalculationInput(1000.0, 100, slopePermille = 0.0)
        ).copy(
            requiredShoes = Int.MAX_VALUE,
            shoesExact = Int.MAX_VALUE.toDouble(),
            shoeCoefficientPer100Tons = 0.2,
            manualAxleCoefficientPer100Tons = 0.2,
        )
        rejects { BrakeCalculator.calculateMassSupplement(mass, 0, 2) }

        rejects {
            BrakeCalculator.calculateAppendix12(
                appendix(slope = 30.0).copy(axleCount = Int.MAX_VALUE)
            )
        }
    }

    @Test fun directMassEngineRejectsContradictoryOrNegativeAxleInputs() {
        // UI validation is not enough: the engine can also be called directly.
        rejects {
            BrakeCalculator.calculateMass(
                MassCalculationInput(100.0, axleCount = -1, manualAxleLoadTons = 10.0, slopePermille = 0.0)
            )
        }
        rejects {
            BrakeCalculator.calculateMass(
                MassCalculationInput(100.0, axleCount = 10, manualAxleLoadTons = 5.0, slopePermille = 0.0)
            )
        }
        val consistent = BrakeCalculator.calculateMass(
            MassCalculationInput(100.0, axleCount = 10, manualAxleLoadTons = 10.0, slopePermille = 0.0)
        )
        assertEquals(10.0, consistent.axleLoadTons, 0.0)
    }

    @Test fun windForLargeAxleCountsNeverUsesOverflowingIntegerProduct() {
        // Previously 1_500_000_000 * 3 overflowed Int before / 200.0,
        // silently undercounting wind shoes rather than rejecting the input.
        val base = appendix(slope = 0.0).copy(
            axleCount = 1_500_000_000,
            windDirectionMatchesPossibleMovement = true,
        )
        val strong = BrakeCalculator.calculateAppendix12(base.copy(windSpeedMs = 16.0))
        assertEquals(22_500_000, strong.windShoes)
        assertEquals(22_500_002, strong.totalRequiredShoes)
        val storm = BrakeCalculator.calculateAppendix12(base.copy(windSpeedMs = 22.0))
        assertEquals(52_500_000, storm.windShoes)
        assertEquals(52_500_002, storm.totalRequiredShoes)
        assertFalse(CalculationPublicationPolicy.canPublishOperationalResult(CalculationMode.APPENDIX_12))
    }

    @Test fun manualBrakeSubstitutionNeverClaimsMoreAxlesThanTheTrainHas() {
        val mass = BrakeCalculator.calculateMass(
            MassCalculationInput(100.0, axleCount = 2, slopePermille = 12.0)
        )
        rejects { BrakeCalculator.calculateMassSupplement(mass, 0, 4) }
        val feasible = BrakeCalculator.calculateMassSupplement(mass, 0, 2)
        assertEquals(2, feasible.actuallyBrakedAxles)

        // The Appendix #12 low-slope special case still needs a real hand-brake unit.
        rejects {
            BrakeCalculator.calculateAppendix12(
                appendix(slope = 0.0).copy(
                    axleCount = 2, availableShoes = 0, axlesPerHandBrakeUnit = 4
                )
            )
        }
        val appendixFeasible = BrakeCalculator.calculateAppendix12(
            appendix(slope = 0.0).copy(
                axleCount = 8, availableShoes = 0, axlesPerHandBrakeUnit = 4
            )
        )
        assertEquals(4, appendixFeasible.actuallyBrakedAxles)
        assertFalse(CalculationPublicationPolicy.canPublishOperationalResult(CalculationMode.BY_MASS))
    }

    @Test fun appendixRejectsMissingFormulaBadWindAndUnsafeLeaving() {
        rejects { BrakeCalculator.calculateAppendix12(appendix(slope = 8.0).copy(formula = null)) }
        rejects { BrakeCalculator.calculateAppendix12(appendix(slope = 8.0).copy(windSpeedMs = Double.NaN)) }
        rejects { BrakeCalculator.calculateAppendix12(appendix(slope = 8.0).copy(windSpeedMs = -1.0)) }
        rejects { BrakeCalculator.calculateAppendix12(appendix(slope = 8.0).copy(availableShoes = -1)) }
        rejects { BrakeCalculator.calculateAppendix12(appendix(slope = 8.0).copy(axlesPerHandBrakeUnit = 0)) }
        rejects {
            BrakeCalculator.calculateAppendix12(
                appendix(slope = 8.0).copy(leavingWithoutLocomotive = true)
            )
        }
        val withConfirmedCondition = BrakeCalculator.calculateAppendix12(
            appendix(slope = 8.0).copy(
                leavingWithoutLocomotive = true,
                point20ConditionConfirmed = true,
            )
        )
        assertTrue(withConfirmedCondition.totalRequiredShoes > 0)
        assertFalse(withConfirmedCondition.specialUnderHalfPermilleRuleUsed)
    }

    @Test fun unapprovedNormsMustNotBecomeOperationalResults() {
        assertEquals(
            CalculationApproval.DONOR_PARITY_ONLY,
            CalculationPublicationPolicy.approval(CalculationMode.BY_MASS)
        )
        assertEquals(
            CalculationApproval.FORMULA_REVIEWED_LOCAL_RULES_REQUIRED,
            CalculationPublicationPolicy.approval(CalculationMode.APPENDIX_12)
        )
        CalculationMode.entries.forEach { mode ->
            assertFalse(CalculationPublicationPolicy.canPublishOperationalResult(mode))
            rejects { CalculationPublicationPolicy.requireOperationalApproval(mode) }
        }
    }

    private fun appendix(slope: Double) = Appendix12Input(
        axleCount = 200,
        profileMode = ProfileMode.NORMAL,
        slopePermille = slope,
        formula = AppendixFormula.FORMULA_1,
        oilyRails = false,
        windSpeedMs = 0.0,
        windDirectionMatchesPossibleMovement = false,
        availableShoes = 0,
        axlesPerHandBrakeUnit = 4,
    )

    private fun rejects(block: () -> Unit) {
        try {
            block()
            fail("Expected validation or safety gate to reject this input")
        } catch (_: IllegalArgumentException) {
            // expected
        } catch (_: IllegalStateException) {
            // expected
        }
    }
}
