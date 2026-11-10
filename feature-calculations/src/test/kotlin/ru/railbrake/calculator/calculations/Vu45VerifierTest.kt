package ru.railbrake.calculator.calculations

import org.junit.Assert.*
import org.junit.Test

class Vu45VerifierTest {
    private fun valid(mode: Vu45EntryMode = Vu45EntryMode.AXLES) = Vu45Draft(
        mode = mode,
        massTons = 4000.0,
        declaredAxles = 200,
        requiredForceTons = 1300.0,
        declaredForceTons = 1400.0,
        manualBrakeAxles = 16,
        axleRows = listOf(Vu45AxleRow(7.0, 200)),
        wagonRows = listOf(Vu45WagonRow(7.0, 4, 50)),
    )

    @Test fun matchingAxleRowsRemainNonOperational() {
        val result = Vu45Verifier.check(valid())
        assertEquals(Vu45Status.ARITHMETICALLY_CONSISTENT_NOT_APPROVED, result.status)
        assertTrue(result.findings.isEmpty())
        assertEquals(200, result.calculatedAxles)
        assertEquals(1400.0, result.calculatedForceTons!!, 0.001)
        assertEquals(100.0, result.forceReserveTons!!, 0.001)
    }

    @Test fun matchingWagonRows() {
        val result = Vu45Verifier.check(valid(Vu45EntryMode.WAGONS))
        assertEquals(Vu45Status.ARITHMETICALLY_CONSISTENT_NOT_APPROVED, result.status)
        assertEquals(200, result.calculatedAxles)
    }

    @Test fun axleMismatchAndForceMismatchAreSeparate() {
        val result = Vu45Verifier.check(valid().copy(declaredAxles = 196, declaredForceTons = 1390.0))
        assertEquals(Vu45Status.DISCREPANCY, result.status)
        assertTrue(Vu45Finding.AXLE_COUNT_MISMATCH in result.findings)
        assertTrue(Vu45Finding.FORCE_TOTAL_MISMATCH in result.findings)
    }

    @Test fun insufficientForceIsNotApproved() {
        val result = Vu45Verifier.check(valid().copy(requiredForceTons = 1500.0))
        assertTrue(Vu45Finding.INSUFFICIENT_CALCULATED_FORCE in result.findings)
        assertTrue(Vu45Finding.INSUFFICIENT_DECLARED_FORCE in result.findings)
    }

    @Test fun missingRequiredFieldFailsClosed() {
        val result = Vu45Verifier.check(valid().copy(requiredForceTons = null))
        assertEquals(Vu45Status.INVALID_INPUT, result.status)
        assertTrue(Vu45Finding.MISSING_REQUIRED_FIELD in result.findings)
        assertNull(result.calculatedForceTons)
    }

    @Test fun disabledRowsAreIgnoredAndNotDeleted() {
        val result = Vu45Verifier.check(
            valid().copy(axleRows = listOf(Vu45AxleRow(7.0, 200), Vu45AxleRow(100.0, 200, false)))
        )
        assertEquals(1400.0, result.calculatedForceTons!!, 0.001)
    }

    @Test fun inactiveModeNeverContributes() {
        val result = Vu45Verifier.check(
            valid().copy(wagonRows = listOf(Vu45WagonRow(99.0, 8, 500)))
        )
        assertEquals(1400.0, result.calculatedForceTons!!, 0.001)
    }

    @Test fun manualBrakeAxlesCannotExceedComposition() {
        val result = Vu45Verifier.check(valid().copy(manualBrakeAxles = 201))
        assertTrue(Vu45Finding.MANUAL_BRAKE_AXLES_EXCEED_TOTAL in result.findings)
    }

    @Test fun overflowAndNonfiniteInputsAreRejected() {
        val overflow = Vu45Verifier.check(
            valid(Vu45EntryMode.WAGONS).copy(
                wagonRows = listOf(Vu45WagonRow(7.0, Int.MAX_VALUE, 2))
            )
        )
        assertEquals(Vu45Status.INVALID_INPUT, overflow.status)
        assertTrue(Vu45Finding.ARITHMETIC_OVERFLOW in overflow.findings)
        val nan = Vu45Verifier.check(valid().copy(declaredForceTons = Double.NaN))
        assertEquals(Vu45Status.INVALID_INPUT, nan.status)
    }

    @Test fun emptyRowsAreNotTreatedAsZeroBrakingForce() {
        val result = Vu45Verifier.check(valid().copy(axleRows = emptyList()))
        assertEquals(Vu45Status.INVALID_INPUT, result.status)
        assertTrue(Vu45Finding.EMPTY_DISTRIBUTION in result.findings)
    }

    @Test fun oneHundredthOfTonForceMismatchIsNotHidden() {
        val result = Vu45Verifier.check(valid().copy(declaredForceTons = 1400.01))
        assertEquals(Vu45Status.DISCREPANCY, result.status)
        assertTrue(Vu45Finding.FORCE_TOTAL_MISMATCH in result.findings)
    }

    @Test fun decimalArithmeticAvoidsFloatingPointMismatch() {
        val result = Vu45Verifier.check(
            valid().copy(
                declaredAxles = 3,
                declaredForceTons = 0.3,
                requiredForceTons = 0.2,
                axleRows = listOf(Vu45AxleRow(0.1, 3)),
                manualBrakeAxles = 0,
            )
        )
        assertEquals(Vu45Status.ARITHMETICALLY_CONSISTENT_NOT_APPROVED, result.status)
    }
}
