#!/usr/bin/env python3
from pathlib import Path

FILES = [
    Path("app/src/main/java/ru/railbrake/calculator/core/DiagnosticRepository.kt"),
    Path("patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticRepository.kt"),
]

GV_START = '        "gv-no-close" -> scenario.copy('
TR_START = '        "traction-no-assemble" -> scenario.copy('
BRAKE_START = '        "brake-pipe-leak" -> scenario.copy('

REPLACEMENT = '''        "gv-no-close" -> scenario.copy(
            informationConfidence = InformationConfidence.MANUFACTURER_OR_MANUAL,
            applicableVariantIds = setOf(
                LocomotiveProfiles.VL80S_GENERAL,
                LocomotiveProfiles.VL80S_937_1260,
                LocomotiveProfiles.VL80S_LATER
            ),
            diagnosticCauses = listOf(
                DiagnosticCause("gv-drive", "Пневмопривод или давление ГВ", "Команда есть, но привод не выполняет включение/удержание."),
                DiagnosticCause("gv-control", "Цепь управления или разрешающая блокировка", "До привода не доходит команда либо отсутствует условие включения."),
                DiagnosticCause("gv-protection", "Действие защиты", "ГВ отключается вследствие аварийного или контрольного сигнала связанной цепи."),
                DiagnosticCause("gv-power", "Силовая цепь после ГВ", "Отключение связано с режимом тяги, ЭКГ, ВУ, ТЭД или трансформатором."),
                DiagnosticCause("gv-device", "Сам ГВ", "Неисправность механизма, катушки или контактов выключателя подтверждается только проверкой.")
            ),
            questions = scenario.questions.map { question ->
                when (question.key) {
                    "gvc-danger" -> question.copy(
                        yesCandidateCauseIds = listOf("gv-power", "gv-protection", "gv-device"),
                        noCandidateCauseIds = listOf("gv-control", "gv-drive", "gv-device"),
                        unknownCandidateCauseIds = listOf("gv-protection", "gv-power")
                    )
                    "gvc-scope" -> question.copy(
                        yesCandidateCauseIds = listOf("gv-control"),
                        noCandidateCauseIds = listOf("gv-drive", "gv-device", "gv-protection"),
                        unknownCandidateCauseIds = listOf("gv-control", "gv-drive")
                    )
                    "gvc-voltage" -> question.copy(
                        yesCandidateCauseIds = listOf("gv-control"),
                        noCandidateCauseIds = listOf("gv-drive", "gv-device", "gv-protection"),
                        unknownCandidateCauseIds = listOf("gv-control")
                    )
                    "gvc-attempt" -> question.copy(
                        yesCandidateCauseIds = listOf("gv-drive", "gv-device", "gv-protection"),
                        noCandidateCauseIds = listOf("gv-control", "gv-drive"),
                        unknownCandidateCauseIds = listOf("gv-control", "gv-drive", "gv-device")
                    )
                    "gvc-load" -> question.copy(
                        yesCandidateCauseIds = listOf("gv-power", "gv-protection"),
                        noCandidateCauseIds = listOf("gv-control", "gv-drive", "gv-device"),
                        unknownCandidateCauseIds = listOf("gv-protection", "gv-control")
                    )
                    else -> question
                }
            }
        )
        "traction-no-assemble" -> scenario.copy(
            diagnosticCauses = listOf(
                DiagnosticCause("traction-section", "Локальная секция или группа", "Отказ ограничен одной секцией/группой: искать границу по её индикации и току."),
                DiagnosticCause("traction-control", "Общее разрешение или цепь управления", "Не выполняются общие условия набора позиции или команда не приходит к аппаратам."),
                DiagnosticCause("traction-ekg", "ЭКГ и подтверждение позиции", "Команда есть, но позиция не набирается либо не подтверждается."),
                DiagnosticCause("traction-power", "Силовая цепь тяговой группы", "Признаки возникают после ЭКГ: ВУ, БСА, ТЭД или защита требуют проверки допущенным персоналом."),
                DiagnosticCause("traction-protection", "Защитное отключение", "Тяга разбирается по сигналу защиты; повторные наборы без причины не допускаются.")
            ),
            questions = scenario.questions.map { question ->
                when (question.key) {
                    "tna-scope" -> question.copy(
                        yesCandidateCauseIds = listOf("traction-control"),
                        noCandidateCauseIds = listOf("traction-section"),
                        unknownCandidateCauseIds = listOf("traction-section", "traction-control")
                    )
                    "tna-va2" -> question.copy(
                        yesCandidateCauseIds = listOf("traction-ekg", "traction-control"),
                        noCandidateCauseIds = listOf("traction-control"),
                        unknownCandidateCauseIds = listOf("traction-control")
                    )
                    "tna-apparatus" -> question.copy(
                        yesCandidateCauseIds = listOf("traction-power"),
                        noCandidateCauseIds = listOf("traction-ekg", "traction-control"),
                        unknownCandidateCauseIds = listOf("traction-ekg", "traction-control")
                    )
                    "tna-aux" -> question.copy(
                        yesCandidateCauseIds = listOf("traction-power"),
                        noCandidateCauseIds = listOf("traction-control", "traction-section"),
                        unknownCandidateCauseIds = listOf("traction-control", "traction-section")
                    )
                    "tna-protection" -> question.copy(
                        yesCandidateCauseIds = listOf("traction-protection", "traction-power"),
                        noCandidateCauseIds = listOf("traction-power", "traction-control"),
                        unknownCandidateCauseIds = listOf("traction-protection")
                    )
                    else -> question
                }
            }
        )
'''

for path in FILES:
    text = path.read_text(encoding="utf-8")
    gv = text.index(GV_START)
    tr = text.index(TR_START, gv)
    brake = text.index(BRAKE_START, tr)
    if text.count(GV_START) != 1 or text.count(TR_START) != 1 or text.count(BRAKE_START) != 1:
        raise SystemExit(f"Unexpected diagnostic block count in {path}")
    new_text = text[:gv] + REPLACEMENT + text[brake:]
    path.write_text(new_text, encoding="utf-8")

if FILES[0].read_text(encoding="utf-8") != FILES[1].read_text(encoding="utf-8"):
    raise SystemExit("app/patch DiagnosticRepository.kt differ after rewrite")

print("POST_WORK_DIAGNOSTIC_BASELINE_FIX=APPLIED")
