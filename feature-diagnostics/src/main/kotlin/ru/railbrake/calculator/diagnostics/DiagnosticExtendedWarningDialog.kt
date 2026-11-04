package ru.railbrake.calculator.diagnostics

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.onGloballyPositioned
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.unit.dp

/**
 * Warning UI for a future independently published, INFORMATION-ONLY source.
 *
 * Deliberately NOT invoked by DiagnosticCatalogScreen: that screen has only
 * PublishedDiagnosticCatalog and no accepted historical evidence adapter yet.
 * Mounting a candidate research JSON here would bypass publication review.
 * The caller must separately enforce publication, exact profile and role gates.
 */
@Composable
fun DiagnosticExtendedWarningDialog(
    open: Boolean,
    onDismiss: () -> Unit,
    onConfirmed: (DiagnosticPresentationSettings) -> Unit,
) {
    if (!open) return

    // Remember, NOT rememberSaveable: consent is invalidated on dismiss/unmount,
    // process recreation or a new warning session.
    var consent by remember { mutableStateOf(DiagnosticExtendedWarningConsent()) }
    var laidOut by remember { mutableStateOf(false) }
    val scroll = rememberScrollState()

    // Text is deliberately longer than the fixed-height viewport. A merely
    // measured zero-distance viewport does not count as scrolling to the end.
    LaunchedEffect(laidOut, scroll.value, scroll.maxValue) {
        consent = consent.reachedViewportEnd(
            scrollValue = scroll.value,
            maxScrollValue = scroll.maxValue,
            viewportLaidOut = laidOut,
        )
    }

    AlertDialog(
        modifier = Modifier.testTag("diagnostic_extended_warning_dialog"),
        onDismissRequest = onDismiss,
        title = { Text("Предупреждение об архивных материалах") },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text(
                    text = DIAGNOSTIC_EXTENDED_WARNING_TEXT,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(176.dp)
                        .verticalScroll(scroll)
                        .onGloballyPositioned { laidOut = true }
                        .testTag("diagnostic_extended_warning_scroll"),
                    style = MaterialTheme.typography.bodyMedium,
                )
                Text(
                    if (consent.readToEnd) {
                        "Предупреждение просмотрено до конца."
                    } else {
                        "Прокрутите предупреждение до конца для подтверждения."
                    },
                    style = MaterialTheme.typography.bodySmall,
                )
                Row {
                    Checkbox(
                        checked = consent.acknowledged,
                        enabled = consent.readToEnd,
                        onCheckedChange = { checked ->
                            consent = consent.acknowledge(checked)
                        },
                        modifier = Modifier.testTag("diagnostic_extended_warning_checkbox"),
                    )
                    Text(
                        "Я понимаю, что архивная информация не разрешает выполнять действия.",
                        modifier = Modifier.padding(top = 10.dp),
                        style = MaterialTheme.typography.bodyMedium,
                    )
                }
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text("Отмена") }
        },
        confirmButton = {
            Button(
                enabled = consent.canEnableInformation && laidOut &&
                    scroll.maxValue > 0,
                onClick = {
                    // Recheck actual scroll position, not just the checkbox.
                    val verified = consent.reachedViewportEnd(
                        scrollValue = scroll.value,
                        maxScrollValue = scroll.maxValue,
                        viewportLaidOut = laidOut,
                    )
                    if (verified.canEnableInformation) {
                        onConfirmed(verified.asPresentationSettings())
                    }
                },
                modifier = Modifier.testTag("diagnostic_extended_warning_confirm"),
            ) {
                Text("Показать доступные сведения")
            }
        },
    )
}

/**
 * Warning text is descriptive only; it contains no historical procedures.
 * Showing it does NOT turn any CANDIDATE into ACTIVE or confer action authority.
 */
internal val DIAGNOSTIC_EXTENDED_WARNING_TEXT = """
Расширенные материалы могут включать архивные руководства, учебные
публикации и записи практического опыта. Они могут относиться к другому
году выпуска, исполнению электрической схемы, заводскому номеру,
модернизированному оборудованию или иной профессиональной роли.

Исторический источник сам по себе не является действующей инструкцией.
Содержащиеся в нём технические гипотезы не означают, что неисправность
установлена на конкретном локомотиве. Разные публикации могут
противоречить друг другу, а применимость их положений может быть неизвестна.

Запрещено воспринимать расширенную справочную информацию как разрешение
на ремонт, вмешательство в высоковольтные цепи, обход защит,
применение перемычек, принудительное управление оборудованием или
повторные операции для проверки гипотезы.

Решения о действиях определяются только применимыми действующими
документами, инструкциями эксплуатационного депо, состоянием и
фактическим исполнением локомотива, а также полномочиями и допуском
соответствующего работника.

Если исполнение неизвестно, сведения о безопасности противоречивы
или источник не подтверждён, диагностика остаётся информационной,
а потенциально опасные действия не предлагаются.

Прочтение этого предупреждения и нажатие кнопки подтверждения
не дают никаких дополнительных прав на технические операции.
""".trimIndent()
