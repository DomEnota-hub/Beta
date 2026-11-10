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
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
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

private data class Vu45RowInput(
    val force: String = "", val axles: String = "", val wagons: String = "",
    val enabled: Boolean = true,
)
private data class Vu45FormInput(
    val mass: String = "", val axles: String = "", val required: String = "",
    val actual: String = "", val manual: String = "",
    val rows: List<Vu45RowInput> = listOf(Vu45RowInput()),
)
private fun String.toVu45Number(): Double? = trim().replace(',', '.').toDoubleOrNull()

private fun Vu45FormInput.toDraft(mode: Vu45EntryMode) = Vu45Draft(
    mode = mode,
    massTons = mass.toVu45Number(),
    declaredAxles = axles.toIntOrNull(),
    requiredForceTons = required.toVu45Number(),
    declaredForceTons = actual.toVu45Number(),
    manualBrakeAxles = if (manual.isBlank()) null else manual.toIntOrNull() ?: -1,
    axleRows = if (mode == Vu45EntryMode.AXLES) rows.map {
        Vu45AxleRow(it.force.toVu45Number() ?: -1.0, it.axles.toIntOrNull() ?: -1, it.enabled)
    } else emptyList(),
    wagonRows = if (mode == Vu45EntryMode.WAGONS) rows.map {
        Vu45WagonRow(
            it.force.toVu45Number() ?: -1.0, it.axles.toIntOrNull() ?: -1,
            it.wagons.toIntOrNull() ?: -1, it.enabled,
        )
    } else emptyList(),
)
private fun Double.asVu45Text() = java.math.BigDecimal.valueOf(this).stripTrailingZeros().toPlainString()

@Composable
private fun Vu45NumberField(label: String, value: String, change: (String) -> Unit) {
    OutlinedTextField(
        value = value, onValueChange = change, label = { Text(label) },
        singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
        modifier = Modifier.fillMaxWidth(),
    )
}

@Composable
fun Vu45VerificationScreen(onBack: () -> Unit) {
    var mode by remember { mutableStateOf(Vu45EntryMode.AXLES) }
    var axleForm by remember { mutableStateOf(Vu45FormInput()) }
    var wagonForm by remember { mutableStateOf(Vu45FormInput()) }
    var result by remember { mutableStateOf<Vu45CheckResult?>(null) }
    var showRowSettings by remember { mutableStateOf(false) }
    val form = if (mode == Vu45EntryMode.AXLES) axleForm else wagonForm
    val updateForm: (Vu45FormInput) -> Unit = { updated ->
        if (mode == Vu45EntryMode.AXLES) axleForm = updated else wagonForm = updated
        result = null
    }
    val updateRow: (Int, (Vu45RowInput) -> Vu45RowInput) -> Unit = { index, change ->
        updateForm(form.copy(rows = form.rows.mapIndexed { i, row ->
            if (i == index) change(row) else row
        }))
    }

    if (showRowSettings) {
        AlertDialog(
            onDismissRequest = { showRowSettings = false },
            title = { Text("Настройки строк") },
            text = {
                Column {
                    form.rows.forEachIndexed { index, row ->
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text("Строка " + (index + 1))
                            Switch(checked = row.enabled, onCheckedChange = { enabled ->
                                updateRow(index) { it.copy(enabled = enabled) }
                            })
                        }
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showRowSettings = false }) { Text("Готово") }
            },
        )
    }
    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        TextButton(onClick = onBack) { Text("← К расчётам") }
        Text("Проверка ВУ-45", style = MaterialTheme.typography.headlineSmall)
        Text(
            "Проверка существующей справки, не её копия. " +
                "Арифметическое совпадение не подтверждает нормативную пригодность или исправность тормозов.",
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            if (mode == Vu45EntryMode.AXLES) {
                Button(onClick = {}) { Text("В осях") }
                OutlinedButton(onClick = { mode = Vu45EntryMode.WAGONS; result = null }) { Text("В вагонах") }
            } else {
                OutlinedButton(onClick = { mode = Vu45EntryMode.AXLES; result = null }) { Text("В осях") }
                Button(onClick = {}) { Text("В вагонах") }
            }
        }
        Text("Черновики режимов независимы; переключение не сбрасывает введённые данные.")
        Vu45NumberField("Масса по справке, т", form.mass) { updateForm(form.copy(mass = it)) }
        Vu45NumberField("Всего осей по справке", form.axles) { updateForm(form.copy(axles = it)) }
        Vu45NumberField("Требуемое нажатие по справке, тс", form.required) {
            updateForm(form.copy(required = it))
        }
        Vu45NumberField("Фактическое нажатие по справке, тс", form.actual) {
            updateForm(form.copy(actual = it))
        }
        Vu45NumberField("Ручные тормозные оси (если указаны)", form.manual) {
            updateForm(form.copy(manual = it))
        }
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Распределение", style = MaterialTheme.typography.titleMedium)
            TextButton(onClick = { showRowSettings = true }) { Text("Настройки строк") }
        }
        form.rows.forEachIndexed { index, row ->
            if (row.enabled) {
                Text("Строка " + (index + 1))
                Vu45NumberField("Нажатие на ось, тс", row.force) { value ->
                    updateRow(index) { it.copy(force = value) }
                }
                Vu45NumberField(
                    if (mode == Vu45EntryMode.AXLES) "Количество осей" else "Осей на вагон",
                    row.axles,
                ) { value -> updateRow(index) { it.copy(axles = value) } }
                if (mode == Vu45EntryMode.WAGONS) {
                    Vu45NumberField("Количество вагонов", row.wagons) { value ->
                        updateRow(index) { it.copy(wagons = value) }
                    }
                }
            }
        }
        OutlinedButton(
            onClick = { updateForm(form.copy(rows = form.rows + Vu45RowInput())) },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("+ Добавить строку") }
        Button(
            onClick = { result = Vu45Verifier.check(form.toDraft(mode)) },
            modifier = Modifier.fillMaxWidth(),
        ) { Text("Проверить") }
        result?.let { checked ->
            Text("Результат проверки", style = MaterialTheme.typography.titleLarge)
            Text(when (checked.status) {
                Vu45Status.INVALID_INPUT -> "Неполные или некорректные данные. Проверка невозможна."
                Vu45Status.DISCREPANCY -> "Обнаружены расхождения. Проверка не пройдена."
                Vu45Status.ARITHMETICALLY_CONSISTENT_NOT_APPROVED ->
                    "Арифметика совпадает. Нормативное соответствие НЕ подтверждено."
            })
            Text("Масса: " + (checked.massTons?.asVu45Text() ?: "нет") + " т")
            Text("Оси по справке: " + (checked.declaredAxles?.toString() ?: "нет"))
            Text("Оси по строкам: " + (checked.calculatedAxles?.toString() ?: "не рассчитаны"))
            Text("Требуемое нажатие: " + (checked.requiredForceTons?.asVu45Text() ?: "нет") + " тс")
            Text("Нажатие по справке: " + (checked.declaredForceTons?.asVu45Text() ?: "нет") + " тс")
            Text("Нажатие по строкам: " + (checked.calculatedForceTons?.asVu45Text() ?: "не рассчитано") + " тс")
            Text("Расхождение с итогом: " + (checked.forceDifferenceTons?.asVu45Text() ?: "нет") + " тс")
            Text("Запас к требуемому: " + (checked.forceReserveTons?.asVu45Text() ?: "нет") + " тс")
            Text("Ручные тормозные оси: " + (checked.manualBrakeAxles?.toString() ?: "не указаны"))
            checked.findings.forEach { finding ->
                Text("• " + when (finding) {
                    Vu45Finding.MISSING_REQUIRED_FIELD -> "Не все обязательные поля заполнены."
                    Vu45Finding.INVALID_NUMBER -> "Некорректное числовое значение."
                    Vu45Finding.EMPTY_DISTRIBUTION -> "Нет включённых строк распределения."
                    Vu45Finding.AXLE_COUNT_MISMATCH -> "Количество осей по строкам не совпадает."
                    Vu45Finding.FORCE_TOTAL_MISMATCH -> "Сумма нажатия по строкам не совпадает."
                    Vu45Finding.INSUFFICIENT_DECLARED_FORCE -> "Указанное нажатие ниже требуемого."
                    Vu45Finding.INSUFFICIENT_CALCULATED_FORCE -> "Рассчитанное нажатие ниже требуемого."
                    Vu45Finding.MANUAL_BRAKE_AXLES_EXCEED_TOTAL -> "Ручных тормозных осей больше, чем всего осей."
                    Vu45Finding.ARITHMETIC_OVERFLOW -> "Переполнение при расчёте осей."
                })
            }
            Text(
                "Нужно отдельно сверить действующие правила с 01.07.2026, допустимое нажатие, " +
                    "плотность сети, хвостовые данные, отметки и местные требования. " +
                    "Автоматический допуск к эксплуатации закрыт.",
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}
