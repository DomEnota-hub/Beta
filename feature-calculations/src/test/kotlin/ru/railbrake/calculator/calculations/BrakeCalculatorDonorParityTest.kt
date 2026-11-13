package ru.railbrake.calculator.calculations

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Pinned donor Test-@3176d6e regression vectors, not an approval to use
 * donor coefficients as current operational norms.
 */
class BrakeCalculatorDonorParityTest {
    @Test fun ordinaryMassAndTenTonBoundary() {
        val ordinary = BrakeCalculator.calculateMass(
            MassCalculationInput(4000.0, axleCount = 212, slopePermille = 12.0)
        )
        assertEquals(16, ordinary.requiredShoes)
        assertEquals(40, ordinary.fullManualBrakeAxles)
        val boundary = BrakeCalculator.calculateMass(
            MassCalculationInput(1200.0, axleCount = 120, slopePermille = 10.0)
        )
        assertTrue(boundary.isExactlyTenTons)
        assertTrue(boundary.heavyCategory)
        assertEquals(4, boundary.requiredShoes)
        val training = BrakeCalculator.calculateMass(
            MassCalculationInput(
                1200.0, axleCount = 120, slopePermille = 10.0,
                tenTonsChoice = TenTonsChoice.LESS_THAN_10
            )
        )
        assertEquals(10, training.requiredShoes)
        assertTrue(training.tenTonsTrainingOverrideUsed)
    }

    @Test fun shortageUsesUnroundedShoeEquivalent() {
        val mass = BrakeCalculator.calculateMass(
            MassCalculationInput(3800.0, axleCount = 200, slopePermille = 12.0)
        )
        assertEquals(15.2, mass.shoesExact, 1e-9)
        assertEquals(16, mass.requiredShoes)
        val supplement = BrakeCalculator.calculateMassSupplement(mass, 15, 4)
        assertEquals(1, supplement.shoeShortage)
        assertEquals(0.2, supplement.remainingShoeEquivalent, 1e-9)
        assertEquals(1, supplement.additionalManualAxles)
        assertEquals(1, supplement.requiredHandBrakeUnits)
        assertEquals(4, supplement.actuallyBrakedAxles)
    }

    @Test fun appendixFormulaOneOilWindAndShortage() {
        val result = BrakeCalculator.calculateAppendix12(
            appendix(slope = 8.0, oily = true, wind = 16.0, available = 15)
        )
        assertEquals(13.0, result.baseExactBeforeOil, 1e-9)
        assertEquals(19.5, result.baseExactAfterOil, 1e-9)
        assertEquals(20, result.baseShoes)
        assertEquals(3, result.windShoes)
        assertEquals(23, result.totalRequiredShoes)
        assertEquals(8, result.shoeShortage)
        assertEquals(40, result.substituteBrakeAxles)
        assertEquals(10, result.requiredHandBrakeUnits)
    }

    @Test fun lowSlopeSpecialAndWindExtraAreDistinct() {
        val noWind = BrakeCalculator.calculateAppendix12(
            appendix(slope = 0.0, wind = 0.0, available = 0)
        )
        assertEquals(2, noWind.totalRequiredShoes)
        assertTrue(noWind.specialUnderHalfPermilleRuleUsed)
        assertEquals(1, noWind.requiredHandBrakeUnits)
        assertEquals(0, noWind.substituteBrakeAxles)

        val wind = BrakeCalculator.calculateAppendix12(
            appendix(slope = 0.0, wind = 16.0, available = 0)
        )
        assertEquals(3, wind.windShoes)
        assertEquals(3, wind.extraShoesAfterSpecialRule)
        assertEquals(15, wind.substituteBrakeAxles)
        assertEquals(5, wind.requiredHandBrakeUnits)

        val boundary = BrakeCalculator.calculateAppendix12(
            appendix(slope = 0.5, wind = 0.0, available = 0)
        )
        assertFalse(boundary.specialUnderHalfPermilleRuleUsed)
        assertEquals(10, boundary.substituteBrakeAxles)
        assertEquals(3, boundary.requiredHandBrakeUnits)
    }

    @Test fun strictWindBoundariesAndFormulaTwo() {
        for ((speed, expected) in listOf(
            15.0 to 0, 15.0001 to 3, 21.0 to 3, 21.0001 to 7
        )) {
            val result = BrakeCalculator.calculateAppendix12(
                appendix(slope = 8.0, wind = speed, available = 0)
            )
            assertEquals("Wind at $speed", expected, result.windCoefficientPer200Axles)
        }
        val formulaTwo = BrakeCalculator.calculateAppendix12(
            appendix(slope = 8.0, wind = 0.0, available = 0).copy(
                formula = AppendixFormula.FORMULA_2
            )
        )
        assertEquals(33.0, formulaTwo.baseExactBeforeOil, 1e-9)
        assertEquals(33, formulaTwo.totalRequiredShoes)
    }

    @Test fun profileModeDoesNotInventDifferentFormula() {
        val reference = BrakeCalculator.calculateAppendix12(
            appendix(slope = 8.0, wind = 0.0, available = 0)
        ).totalRequiredShoes
        ProfileMode.entries.forEach { profile ->
            assertEquals(
                reference,
                BrakeCalculator.calculateAppendix12(
                    appendix(slope = 8.0, wind = 0.0, available = 0)
                        .copy(profileMode = profile)
                ).totalRequiredShoes
            )
        }
    }

    private fun appendix(
        slope: Double,
        wind: Double,
        available: Int,
        oily: Boolean = false,
    ) = Appendix12Input(
        axleCount = 200,
        profileMode = ProfileMode.NORMAL,
        slopePermille = slope,
        formula = if (slope > 0.5) AppendixFormula.FORMULA_1 else null,
        oilyRails = oily,
        windSpeedMs = wind,
        windDirectionMatchesPossibleMovement = true,
        availableShoes = available,
        axlesPerHandBrakeUnit = 4,
    )
}
