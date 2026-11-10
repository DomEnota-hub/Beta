package ru.railbrake.calculator.shell

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import ru.railbrake.calculator.calculations.*
import ru.railbrake.calculator.history.HistoryRecord

/** Two independent user forms; neither claims to prescribe operational securing. */
@Composable
fun SecuringScreen(onBack: () -> Unit, onSave: (HistoryRecord) -> Boolean) {
    var mode by remember { mutableStateOf(CalculationMode.BY_MASS) }
    var mass by remember { mutableStateOf(MassSecuringDraft()) }
    var appendix by remember { mutableStateOf(AppendixSecuringDraft()) }
    var result by remember { mutableStateOf<SecuringReview?>(null) }
    var saveStatus by remember { mutableStateOf<String?>(null) }
    val updateMass: (MassSecuringDraft) -> Unit = { mass = it; result = null; saveStatus = null }
    val updateAppendix: (AppendixSecuringDraft) -> Unit = { appendix = it; result = null; saveStatus = null }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        TextButton(onClick = onBack) { Text("← К расчётам") }
        Text("Закрепление состава", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Предварительная арифметика, НЕ норма закрепления и НЕ разрешение " +
                "оставлять состав. Условия ТРА, фактический профиль и применимость источника " +
                "проверяются отдельно. Неподтверждённые нормативы не публикуются."
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (mode == CalculationMode.BY_MASS) {
                Button(onClick = {}) { Text("По массе") }
                OutlinedButton(onClick = { mode = CalculationMode.APPENDIX_12; result = null }) {
                    Text("ИДП №12")
                }
            } else {
                OutlinedButton(onClick = { mode = CalculationMode.BY_MASS; result = null }) {
                    Text("По массе")
                }
                Button(onClick = {}) { Text("ИДП №12") }
            }
        }
        Text("Данные двух режимов сохраняются отдельно при переключении.")
        when (mode) {
            CalculationMode.BY_MASS -> MassSecuringForm(mass, updateMass)
            CalculationMode.APPENDIX_12 -> AppendixSecuringForm(appendix, updateAppendix)
        }
        Button(
            onClick = {
                result = when (mode) {
                    CalculationMode.BY_MASS -> SecuringInputReview.byMass(mass)
                    CalculationMode.APPENDIX_12 -> SecuringInputReview.byAppendix(appendix)
                }
            },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Рассчитать предварительно") }
        result?.let { reviewed ->
            SecuringResult(reviewed)
            if (reviewed !is SecuringReview.Invalid) {
                Button(
                    onClick = {
                        saveStatus = if (onSave(reviewed.asHistoryRecord()))
                            "Предварительный расчёт сохранён в истории."
                        else "Не удалось сохранить историю. Проверьте доступность хранилища."
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("Сохранить предварительный расчёт") }
                saveStatus?.let { Text(it) }
            }
        }
    }
}

@Composable
private fun SecuringNumber(label: String, value: String, onChange: (String) -> Unit) {
    OutlinedTextField(
        value = value, onValueChange = onChange,
        label = { Text(label) }, singleLine = true,
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        modifier = Modifier.fillMaxWidth(),
    )
}

@Composable
private fun SecuringToggle(label: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, modifier = Modifier.weight(1f))
        Checkbox(checked = checked, onCheckedChange = onChange)
    }
}

@Composable
private fun MassSecuringForm(d: MassSecuringDraft, change: (MassSecuringDraft) -> Unit) {
    Text("По массе: донорская таблица не подтверждена действующим первоисточником.")
    SecuringNumber("Масса состава, т", d.massTons) { change(d.copy(massTons = it)) }
    SecuringNumber("Количество осей (или нагрузка на ось)", d.axleCount) {
        change(d.copy(axleCount = it))
    }
    SecuringNumber("Нагрузка на ось, тс (или количество осей)", d.axleLoadTons) {
        change(d.copy(axleLoadTons = it))
    }
    SecuringNumber("Уклон, ‰ (0, 2, 4, 6, 8, 10, 12)", d.slopePermille) {
        change(d.copy(slopePermille = it))
    }
    SecuringNumber("Имеется тормозных башмаков", d.availableShoes) {
        change(d.copy(availableShoes = it))
    }
    SecuringNumber("Тормозных осей на одну единицу ручного тормоза", d.axlesPerHandBrakeUnit) {
        change(d.copy(axlesPerHandBrakeUnit = it))
    }
    Text("Если указаны и оси, и нагрузка на ось, они должны согласовываться с массой.")
}

@Composable
private fun AppendixSecuringForm(d: AppendixSecuringDraft, change: (AppendixSecuringDraft) -> Unit) {
    Text("Приложение №12 к ИДП: выбор формулы и местные условия нельзя угадывать.")
    SecuringNumber("Количество осей", d.axleCount) { change(d.copy(axleCount = it)) }
    SecuringNumber("Уклон, ‰", d.slopePermille) { change(d.copy(slopePermille = it)) }
    Text("Формула (при уклоне более 0,5‰ требуется явный выбор)")
    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        listOf(AppendixFormula.FORMULA_1, AppendixFormula.FORMULA_2).forEach { formula ->
            if (d.formula == formula) {
                Button(onClick = {}) { Text(if (formula == AppendixFormula.FORMULA_1) "Формула 1" else "Формула 2") }
            } else {
                OutlinedButton(onClick = { change(d.copy(formula = formula)) }) {
                    Text(if (formula == AppendixFormula.FORMULA_1) "Формула 1" else "Формула 2")
                }
            }
        }
    }
    Text("Профиль пути (не определяет формулу автоматически)")
    listOf(
        ProfileMode.NORMAL to "Обычный путь",
        ProfileMode.BROKEN_FULL_TRACK to "Ломаный профиль",
        ProfileMode.SEPARATE_SEGMENT to "Отдельный участок",
    ).forEach { (profile, label) ->
        if (d.profile == profile) {
            Text("✓ $label")
        } else {
            TextButton(onClick = { change(d.copy(profile = profile)) }) { Text(label) }
        }
    }
    SecuringToggle("Замасленные рельсы", d.oilyRails) {
        change(d.copy(oilyRails = it))
    }
    SecuringNumber("Скорость ветра, м/с", d.windSpeedMs) {
        change(d.copy(windSpeedMs = it))
    }
    SecuringToggle("Ветер направлен в сторону возможного движения", d.windMatchesMovement) {
        change(d.copy(windMatchesMovement = it))
    }
    SecuringNumber("Имеется тормозных башмаков", d.availableShoes) {
        change(d.copy(availableShoes = it))
    }
    SecuringNumber("Тормозных осей на единицу ручного тормоза", d.axlesPerHandBrakeUnit) {
        change(d.copy(axlesPerHandBrakeUnit = it))
    }
    SecuringToggle("Оставление состава без локомотива", d.leavingWithoutLocomotive) {
        change(d.copy(leavingWithoutLocomotive = it))
    }
    if (d.leavingWithoutLocomotive) {
        Text("При уклоне более 2,5‰ расчёт блокируется до отдельного подтверждения условий пункта 20.")
    }
}

@Composable
private fun SecuringResult(result: SecuringReview) {
    Text("Предварительный результат", style = MaterialTheme.typography.titleLarge)
    when (result) {
        is SecuringReview.Invalid -> Text("Расчёт невозможен: " + result.reason)
        is SecuringReview.Mass -> {
            Text("Расчётных башмаков: " + result.calculation.requiredShoes)
            Text("Имеется башмаков: " + result.supplement.availableShoes)
            Text("Недостаток башмаков: " + result.supplement.shoeShortage)
            Text("Дополнительных ручных тормозных осей: " + result.supplement.additionalManualAxles)
            Text("Единиц ручного тормоза: " + result.supplement.requiredHandBrakeUnits)
            Text("Фактически заторможенных осей: " + result.supplement.actuallyBrakedAxles)
            Text("Резерв ручных тормозных осей: " + result.supplement.reserveManualAxles)
            Text("Статус: " + result.approval.name)
        }
        is SecuringReview.Appendix -> {
            val r = result.calculation
            Text("Базовое количество башмаков: " + r.baseShoes)
            Text("Противоположная сторона: " + r.oppositeSideShoes)
            Text("Дополнительно по ветру: " + r.windShoes)
            Text("Всего расчётных башмаков: " + r.totalRequiredShoes)
            Text("Имеется башмаков: " + r.availableShoes)
            Text("Недостаток башмаков: " + r.shoeShortage)
            Text("Замещающих тормозных осей: " + r.substituteBrakeAxles)
            Text("Единиц ручного тормоза: " + r.requiredHandBrakeUnits)
            Text("Фактически заторможенных осей: " + r.actuallyBrakedAxles)
            Text("Резерв тормозных осей: " + r.reserveBrakeAxles)
            Text("Специальное правило до 0,5‰: " + if (r.specialUnderHalfPermilleRuleUsed) "да" else "нет")
            Text("Статус: " + result.approval.name)
        }
    }
    Text(
        "ЭКСПЛУАТАЦИОННЫЙ ДОПУСК НЕ ПОДТВЕРЖДЁН. " +
            "Результат не заменяет ТРА, действующие нормативы и проверку условий на месте.",
        color = MaterialTheme.colorScheme.error,
    )
}

/** History is an audit trail, never a certificate of normative compliance. */
private fun SecuringReview.asHistoryRecord(): HistoryRecord {
    val mode = if (this is SecuringReview.Mass) "По массе" else "ИДП №12"
    val summary = when (this) {
        is SecuringReview.Mass ->
            "Башмаков: ${calculation.requiredShoes}; недостаток: ${supplement.shoeShortage}"
        is SecuringReview.Appendix ->
            "Башмаков: ${calculation.totalRequiredShoes}; недостаток: ${calculation.shoeShortage}"
        is SecuringReview.Invalid -> error("Invalid result cannot be saved")
    }
    val details = when (this) {
        is SecuringReview.Mass ->
            "Имеется: ${supplement.availableShoes}; ручных тормозных осей: " +
                "${supplement.additionalManualAxles}; единиц ручного тормоза: " +
                "${supplement.requiredHandBrakeUnits}; резерв: ${supplement.reserveManualAxles}"
        is SecuringReview.Appendix ->
            "База: ${calculation.baseShoes}; противоположная сторона: " +
                "${calculation.oppositeSideShoes}; ветер: ${calculation.windShoes}; " +
                "замещающих осей: ${calculation.substituteBrakeAxles}; " +
                "единиц ручного тормоза: ${calculation.requiredHandBrakeUnits}"
        is SecuringReview.Invalid -> error("Invalid result cannot be saved")
    }
    return HistoryRecord(
        System.currentTimeMillis(), mode, "Закрепление состава",
        summary + " · ПРЕДВАРИТЕЛЬНО",
        details + ". ЭКСПЛУАТАЦИОННЫЙ ДОПУСК НЕ ПОДТВЕРЖДЁН.",
    )
}
