package ru.railbrake.calculator.calculations

/**
 * Both calculation paths are arithmetic previews, never an operational
 * securing order. Unknown local rules and unverified coefficients fail closed.
 */
data class MassSecuringDraft(
    val massTons: String = "",
    val axleCount: String = "",
    val axleLoadTons: String = "",
    val slopePermille: String = "",
    val availableShoes: String = "",
    val axlesPerHandBrakeUnit: String = "",
)

data class AppendixSecuringDraft(
    val axleCount: String = "",
    val slopePermille: String = "",
    val formula: AppendixFormula? = null,
    val profile: ProfileMode = ProfileMode.NORMAL,
    val oilyRails: Boolean = false,
    val windSpeedMs: String = "0",
    val windMatchesMovement: Boolean = false,
    val availableShoes: String = "",
    val axlesPerHandBrakeUnit: String = "",
    val leavingWithoutLocomotive: Boolean = false,
)

sealed interface SecuringReview {
    data class Mass(
        val calculation: MassCalculationResult,
        val supplement: MassSupplementResult,
        val approval: CalculationApproval,
    ) : SecuringReview

    data class Appendix(
        val calculation: Appendix12Result,
        val approval: CalculationApproval,
    ) : SecuringReview

    data class Invalid(val reason: String) : SecuringReview
}

object SecuringInputReview {
    private fun String.number(field: String): Double {
        val parsed = trim().replace(',', '.').toDoubleOrNull()
        require(parsed != null && parsed.isFinite()) { "Укажите корректное число: $field" }
        return parsed
    }

    private fun String.whole(field: String): Int =
        trim().toIntOrNull() ?: throw IllegalArgumentException("Укажите целое число: $field")

    fun byMass(draft: MassSecuringDraft): SecuringReview = try {
        val axles = if (draft.axleCount.isBlank()) null else draft.axleCount.whole("Количество осей")
        val axleLoad = if (draft.axleLoadTons.isBlank()) null else draft.axleLoadTons.number("Нагрузка на ось")
        require(axles != null || axleLoad != null) { "Укажите количество осей или нагрузку на ось" }
        // Do not silently ignore one of two conflicting axle-load inputs.
        val mass = draft.massTons.number("Масса состава")
        if (axles != null && axleLoad != null) {
            require(axles > 0 && axleLoad > 0.0 &&
                kotlin.math.abs(mass / axles - axleLoad) < 0.01
            ) { "Масса, оси и нагрузка на ось противоречат друг другу" }
        }
        val calculated = BrakeCalculator.calculateMass(
            MassCalculationInput(
                massTons = mass,
                axleCount = axles,
                manualAxleLoadTons = axleLoad,
                slopePermille = draft.slopePermille.number("Уклон"),
            )
        )
        val supplement = BrakeCalculator.calculateMassSupplement(
            calculated,
            draft.availableShoes.whole("Имеющиеся башмаки"),
            draft.axlesPerHandBrakeUnit.whole("Оси на одну единицу ручного тормоза"),
        )
        SecuringReview.Mass(
            calculated, supplement,
            CalculationPublicationPolicy.approval(CalculationMode.BY_MASS),
        )
    } catch (error: IllegalArgumentException) {
        SecuringReview.Invalid(error.message ?: "Некорректные данные")
    } catch (error: IllegalStateException) {
        SecuringReview.Invalid(error.message ?: "Расчёт недоступен")
    }

    fun byAppendix(draft: AppendixSecuringDraft): SecuringReview = try {
        val calculated = BrakeCalculator.calculateAppendix12(
            Appendix12Input(
                axleCount = draft.axleCount.whole("Количество осей"),
                profileMode = draft.profile,
                slopePermille = draft.slopePermille.number("Уклон"),
                formula = draft.formula,
                oilyRails = draft.oilyRails,
                windSpeedMs = draft.windSpeedMs.number("Скорость ветра"),
                windDirectionMatchesPossibleMovement = draft.windMatchesMovement,
                availableShoes = draft.availableShoes.whole("Имеющиеся башмаки"),
                axlesPerHandBrakeUnit = draft.axlesPerHandBrakeUnit.whole("Оси на единицу ручного тормоза"),
                leavingWithoutLocomotive = draft.leavingWithoutLocomotive,
                // No user self-approval of point 20: requires verified local rules.
                point20ConditionConfirmed = false,
            )
        )
        SecuringReview.Appendix(
            calculated,
            CalculationPublicationPolicy.approval(CalculationMode.APPENDIX_12),
        )
    } catch (error: IllegalArgumentException) {
        SecuringReview.Invalid(error.message ?: "Некорректные данные")
    } catch (error: IllegalStateException) {
        SecuringReview.Invalid(error.message ?: "Расчёт недоступен")
    }
}
