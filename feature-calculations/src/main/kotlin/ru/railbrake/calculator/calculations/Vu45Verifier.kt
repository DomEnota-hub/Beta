package ru.railbrake.calculator.calculations

import java.math.BigDecimal

/**
 * Arithmetic cross-check of the figures copied FROM a VU-45 certificate.
 * This does not generate a certificate or determine the applicable normative
 * braking-force coefficient. All reference values must be supplied from the
 * original document and independently verified against current rules.
 */
enum class Vu45EntryMode { AXLES, WAGONS }

data class Vu45AxleRow(
    val forcePerAxleTons: Double,
    val axleCount: Int,
    val enabled: Boolean = true,
)

data class Vu45WagonRow(
    val forcePerAxleTons: Double,
    val axlesPerWagon: Int,
    val wagonCount: Int,
    val enabled: Boolean = true,
)

data class Vu45Draft(
    val mode: Vu45EntryMode,
    val massTons: Double?,
    val declaredAxles: Int?,
    val requiredForceTons: Double?,
    val declaredForceTons: Double?,
    val manualBrakeAxles: Int?,
    val axleRows: List<Vu45AxleRow> = emptyList(),
    val wagonRows: List<Vu45WagonRow> = emptyList(),
)

enum class Vu45Finding {
    MISSING_REQUIRED_FIELD,
    INVALID_NUMBER,
    EMPTY_DISTRIBUTION,
    AXLE_COUNT_MISMATCH,
    FORCE_TOTAL_MISMATCH,
    INSUFFICIENT_DECLARED_FORCE,
    INSUFFICIENT_CALCULATED_FORCE,
    MANUAL_BRAKE_AXLES_EXCEED_TOTAL,
    ARITHMETIC_OVERFLOW,
}

enum class Vu45Status {
    INVALID_INPUT,
    DISCREPANCY,
    ARITHMETICALLY_CONSISTENT_NOT_APPROVED,
}

data class Vu45CheckResult(
    val status: Vu45Status,
    val findings: Set<Vu45Finding>,
    val calculatedAxles: Int?,
    val calculatedForceTons: Double?,
    val forceDifferenceTons: Double?,
    val forceReserveTons: Double?,
    val declaredAxles: Int?,
    val declaredForceTons: Double?,
    val requiredForceTons: Double?,
    val massTons: Double?,
    val manualBrakeAxles: Int?,
)

/**
 * No implicit conversion between axle and wagon drafts. The UI owns two
 * independent drafts, and only the explicitly selected one is verified.
 */
object Vu45Verifier {
    private val tolerance = BigDecimal("0.01")

    fun check(draft: Vu45Draft): Vu45CheckResult {
        val findings = linkedSetOf<Vu45Finding>()
        if (draft.massTons == null || draft.declaredAxles == null ||
            draft.requiredForceTons == null || draft.declaredForceTons == null
        ) {
            findings += Vu45Finding.MISSING_REQUIRED_FIELD
        }
        fun valid(value: Double?, strictlyPositive: Boolean): Boolean =
            value != null && value.isFinite() &&
                (if (strictlyPositive) value > 0.0 else value >= 0.0)

        if ((draft.massTons != null && !valid(draft.massTons, true)) ||
            (draft.requiredForceTons != null && !valid(draft.requiredForceTons, true)) ||
            (draft.declaredForceTons != null && !valid(draft.declaredForceTons, false)) ||
            (draft.declaredAxles != null && draft.declaredAxles <= 0) ||
            (draft.manualBrakeAxles != null && draft.manualBrakeAxles < 0)
        ) {
            findings += Vu45Finding.INVALID_NUMBER
        }

        var axleTotal = 0
        var forceTotal = BigDecimal.ZERO
        val activeRows = when (draft.mode) {
            Vu45EntryMode.AXLES -> draft.axleRows.count { it.enabled }
            Vu45EntryMode.WAGONS -> draft.wagonRows.count { it.enabled }
        }
        if (activeRows == 0) findings += Vu45Finding.EMPTY_DISTRIBUTION

        try {
            when (draft.mode) {
                Vu45EntryMode.AXLES -> draft.axleRows.filter { it.enabled }.forEach { row ->
                    if (row.axleCount <= 0 || !valid(row.forcePerAxleTons, false)) {
                        findings += Vu45Finding.INVALID_NUMBER
                    } else {
                        axleTotal = Math.addExact(axleTotal, row.axleCount)
                        forceTotal = forceTotal.add(
                            BigDecimal.valueOf(row.forcePerAxleTons)
                                .multiply(BigDecimal.valueOf(row.axleCount.toLong()))
                        )
                    }
                }
                Vu45EntryMode.WAGONS -> draft.wagonRows.filter { it.enabled }.forEach { row ->
                    if (row.wagonCount <= 0 || row.axlesPerWagon <= 0 ||
                        !valid(row.forcePerAxleTons, false)
                    ) {
                        findings += Vu45Finding.INVALID_NUMBER
                    } else {
                        val rowAxles = Math.multiplyExact(row.wagonCount, row.axlesPerWagon)
                        axleTotal = Math.addExact(axleTotal, rowAxles)
                        forceTotal = forceTotal.add(
                            BigDecimal.valueOf(row.forcePerAxleTons)
                                .multiply(BigDecimal.valueOf(rowAxles.toLong()))
                        )
                    }
                }
            }
        } catch (_: ArithmeticException) {
            findings += Vu45Finding.ARITHMETIC_OVERFLOW
        }

        val inputInvalid = findings.any {
            it in setOf(
                Vu45Finding.MISSING_REQUIRED_FIELD, Vu45Finding.INVALID_NUMBER,
                Vu45Finding.EMPTY_DISTRIBUTION, Vu45Finding.ARITHMETIC_OVERFLOW,
            )
        }
        if (!inputInvalid) {
            if (axleTotal != draft.declaredAxles) findings += Vu45Finding.AXLE_COUNT_MISMATCH
            val declared = BigDecimal.valueOf(requireNotNull(draft.declaredForceTons))
            val required = BigDecimal.valueOf(requireNotNull(draft.requiredForceTons))
            if (forceTotal.subtract(declared).abs() > tolerance) {
                findings += Vu45Finding.FORCE_TOTAL_MISMATCH
            }
            if (declared < required) findings += Vu45Finding.INSUFFICIENT_DECLARED_FORCE
            if (forceTotal < required) findings += Vu45Finding.INSUFFICIENT_CALCULATED_FORCE
            if (draft.manualBrakeAxles != null && draft.manualBrakeAxles > axleTotal) {
                findings += Vu45Finding.MANUAL_BRAKE_AXLES_EXCEED_TOTAL
            }
        }
        val status = when {
            inputInvalid -> Vu45Status.INVALID_INPUT
            findings.isNotEmpty() -> Vu45Status.DISCREPANCY
            else -> Vu45Status.ARITHMETICALLY_CONSISTENT_NOT_APPROVED
        }
        return Vu45CheckResult(
            status = status,
            findings = findings,
            calculatedAxles = if (inputInvalid) null else axleTotal,
            calculatedForceTons = if (inputInvalid) null else forceTotal.toDouble(),
            forceDifferenceTons = if (inputInvalid) null else
                forceTotal.subtract(BigDecimal.valueOf(requireNotNull(draft.declaredForceTons))).toDouble(),
            forceReserveTons = if (inputInvalid) null else
                forceTotal.subtract(BigDecimal.valueOf(requireNotNull(draft.requiredForceTons))).toDouble(),
            declaredAxles = draft.declaredAxles,
            declaredForceTons = draft.declaredForceTons,
            requiredForceTons = draft.requiredForceTons,
            massTons = draft.massTons,
            manualBrakeAxles = draft.manualBrakeAxles,
        )
    }
}
