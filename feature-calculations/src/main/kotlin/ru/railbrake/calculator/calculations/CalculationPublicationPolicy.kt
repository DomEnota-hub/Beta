package ru.railbrake.calculator.calculations

/**
 * Pure donor-parity calculations are testable without being approved as
 * operational advice. Never equate a green unit test with a source approval.
 */
enum class CalculationMode { BY_MASS, APPENDIX_12 }

enum class CalculationApproval {
    DONOR_PARITY_ONLY,
    FORMULA_REVIEWED_LOCAL_RULES_REQUIRED,
    APPROVED_FOR_OPERATION,
}

object CalculationPublicationPolicy {
    fun approval(mode: CalculationMode): CalculationApproval = when (mode) {
        CalculationMode.BY_MASS -> CalculationApproval.DONOR_PARITY_ONLY
        CalculationMode.APPENDIX_12 ->
            CalculationApproval.FORMULA_REVIEWED_LOCAL_RULES_REQUIRED
    }

    fun canPublishOperationalResult(mode: CalculationMode): Boolean =
        approval(mode) == CalculationApproval.APPROVED_FOR_OPERATION

    fun requireOperationalApproval(mode: CalculationMode) {
        check(canPublishOperationalResult(mode)) {
            "Нормативная применимость расчёта не подтверждена; эксплуатационный результат закрыт"
        }
    }
}
