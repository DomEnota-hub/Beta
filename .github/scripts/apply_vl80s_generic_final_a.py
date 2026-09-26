#!/usr/bin/env python3
from pathlib import Path

APP = Path('app/src/main/java/ru/railbrake/calculator/core/DiagnosticDeepening.kt')
PATCH = Path('patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticDeepening.kt')
APP_REG = Path('app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericRouteRegressionTest.kt')
PATCH_REG = Path('patch/app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericRouteRegressionTest.kt')
APP_TEST = Path('app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericFinalBatchATest.kt')
PATCH_TEST = Path('patch/app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericFinalBatchATest.kt')

INSERT = r'''
        "field-weakening-fault" -> scenario.deepen(
            questions = listOf(
                q("fw-before", "До команды ослабления поля тяга и токи были устойчивыми?", "Неисправность локализуется к переходу на ослабление поля; сравнить команду и подтверждение ступени.", "Сначала разбирать исходный тяговый отказ, а не цепь ослабления поля.", "fw-confirm"),
                q("fw-confirm", "После команды ступень ослабления поля подтверждается хотя бы кратковременно?", "Если затем ступень отпадает, искать потерю удержания, блокировку или действие защиты.", "Если подтверждения нет с самого начала, проверять формирование команды, блокировки и исполнительную цепь по профилю.", "fw-danger"),
                q("fw-danger", "Переход сопровождается асимметрией токов, срабатыванием защиты, запахом или искрением?", "Не повторять переход ради проверки; снять тяговую нагрузку и локализовать секцию/группу по первой защите.", "Зафиксировать, на какой ступени и в какой секции отсутствует подтверждение, без многократных повторов.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Не формируется команда ослабления поля.", "Не выполняется блокировка или условие разрешения конкретного исполнения.", "Не включается либо не удерживается исполнительный контактор ослабления поля.", "Срабатывает защита тяговой группы при переходе.", "Недостоверно подтверждается положение контактора или ступени.", "Исходная неисправность тяговой цепи ошибочно проявляется как отказ ослабления поля."),
            checks = listOf(
                cab("Момент отказа", "Сопоставить устойчивость тяги до команды, саму команду и изменение токов после неё.", "Понятно, связан ли отказ именно с переходом на ослабление поля.", "При броске тока или защите не повторять переход для воспроизведения."),
                cab("Секция и подтверждение", "Сравнить подтверждение ступени и токи секций/групп по штатной индикации.", "Локализована секция/группа и тип отказа: нет включения либо отпадание.", "Не считать отсутствие изменения одного прибора доказательством отказа силового контактора."),
                authorized("Цепь ослабления поля", "Проверить команду, блокировки, исполнительные аппараты и обратную связь по схеме конкретного исполнения.", "Причина подтверждена по электрической схеме и измерению.", "Не шунтировать блокировки и не удерживать силовой аппарат вручную.")
            ),
            related = listOf("traction-one-section-low", "traction-current-surge", "traction-intermittent", "control-voltage-low", "reverser-no-confirm")
        )

        "fan-vibration" -> scenario.deepen(
            questions = listOf(
                q("fan-running", "Вибрация и стук появляются только при вращении конкретного мотор-вентилятора?", "Неисправность связана с приводом, рабочим колесом, подшипниками или его креплением.", "Если шум сохраняется при остановленном вентиляторе, искать другой механический источник.", "fan-air"),
                q("fan-air", "Одновременно изменился воздушный поток, появился скрежет или признак касания?", "Вероятны повреждение рабочего колеса, воздуховода, крепления или посторонний предмет; повторный пуск может усугубить дефект.", "При нормальном потоке всё равно локализовать источник вибрации и состояние подшипников/креплений.", "fan-danger"),
                q("fan-danger", "Есть дым, запах перегрева, резкий рост вибрации или металлические удары?", "Вентилятор повторно не включать до безопасной оценки; связанное охлаждаемое оборудование не нагружать.", "Зафиксировать режим, при котором появляется вибрация, и перейти к осмотру после безопасной остановки.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Дисбаланс или повреждение рабочего колеса.", "Износ либо повреждение подшипников мотор-вентилятора.", "Ослабление крепления двигателя, вентилятора или кожуха.", "Касание рабочего колеса, воздуховода или посторонний предмет.", "Механическая неисправность электродвигателя.", "Другой узел ошибочно принят за источник вибрации вентилятора."),
            checks = listOf(
                cab("Связь с вращением", "Сопоставить появление вибрации с включением конкретного вентилятора и изменением воздушного потока.", "Источник локализован по машине и режиму.", "Не выполнять серию повторных пусков при нарастающем стуке."),
                stop("Доступный осмотр", "После безопасной остановки проверить доступные воздухозаборники, кожухи и крепления без входа в опасную зону.", "Нет видимого разрушения, касания или постороннего предмета.", "При повреждении или следах касания вентилятор не включать."),
                authorized("Механическая часть вентилятора", "Проверить рабочее колесо, подшипники, крепления и двигатель по документации.", "Причина вибрации подтверждена и устранена установленным порядком.", "Не эксплуатировать вентилятор с подтверждённым механическим дефектом.")
            ),
            related = listOf("fan-low-airflow", "motor-fan-failure", "rectifier-overheat", "traction-motor-overheat", "mechanical-noise-heating")
        )

        "aux-contactor-chatter" -> scenario.deepen(
            questions = listOf(
                q("chatter-command", "Команда на вспомогательную машину остаётся устойчивой во время дребезга контактора?", "При устойчивой команде искать питание катушки, блокировки, механическое удержание или действие защиты.", "При пропадающей команде локализовать цепь управления и условие, которое её снимает.", "chatter-common"),
                q("chatter-common", "Одновременно дребезжат другие контакторы или заметно меняется напряжение цепей управления?", "Вероятна общая проблема питания/цепей управления, а не несколько независимых контакторов.", "Вероятнее локальный дефект катушки, контактора, блокировки или защищаемого двигателя.", "chatter-danger"),
                q("chatter-danger", "Есть запах, нагрев, искрение либо повторное действие защиты двигателя?", "Остановить повторные включения этой машины и не удерживать контактор вручную.", "Зафиксировать, при какой команде и нагрузке возникает дребезг, затем проверять локальную цепь.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Пониженное или нестабильное напряжение цепей управления.", "Прерывистая команда либо блокировка в цепи катушки.", "Неисправность катушки, магнитопровода или механизма контактора.", "Защита двигателя циклически снимает питание контактора.", "Ослабленное соединение в цепи управления.", "Неисправность самого двигателя вызывает повторное отпадание аппарата."),
            checks = listOf(
                cab("Общий или локальный признак", "Сопоставить дребезг с другими контакторами, освещением и штатной индикацией напряжения управления.", "Понятно, общий это провал питания или локальная цепь.", "Не выполнять многократные включения для проверки."),
                cab("Команда и защита", "Зафиксировать устойчивость команды и факт срабатывания защиты соответствующей машины.", "Разделены потеря команды, действие защиты и неспособность контактора удержаться.", "При повторной защите не восстанавливать её многократно."),
                authorized("Контактор и цепь катушки", "Проверить напряжение катушки, блокировки, соединения и механическую часть по схеме.", "Причина дребезга подтверждена измерением.", "Не удерживать контактор механически и не шунтировать защиту.")
            ),
            related = listOf("control-voltage-low", "aux-common-loss", "control-fuse-trip", "motor-fan-failure", "compressor-no-start")
        )

        "heater-fault" -> scenario.deepen(
            questions = listOf(
                q("heater-danger", "Есть запах перегрева, дым, треск или локально чрезмерный нагрев отопителя/проводки?", "Считать это отдельным пожарным признаком: отключить затронутое оборудование разрешённым способом и не восстанавливать до оценки.", "Разбирать отсутствие нагрева или штатное защитное отключение без признаков горения.", "heater-trip"),
                q("heater-trip", "Автомат или защита отопления повторно отключается после штатной попытки включения?", "Не выполнять повторные сбросы; вероятны дефект нагревателя, проводки или контактора.", "Если защита не действует, сравнить наличие команды и работу остальных отопителей.", "heater-scope"),
                q("heater-scope", "Не работает только один отопитель, тогда как остальные потребители отопления получают команду?", "Искать локальную цепь конкретного отопителя, его элемент, контактор или соединение.", "При общем отсутствии нагрева проверять общее питание, управление и условия разрешения отопления.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Нет общего питания или команды системы отопления.", "Неисправен отдельный нагревательный элемент.", "Не включается контактор либо нарушена локальная цепь отопителя.", "Защита отключает цепь из-за электрического дефекта.", "Неисправность управления температурой или условия разрешения.", "Перегрев соединения/проводки с риском возгорания."),
            checks = listOf(
                cab("Характер отказа", "Сначала разделить отсутствие нагрева, повторное защитное отключение и запах/дым/треск.", "Выбрана безопасная ветвь диагностики.", "При дыме или треске не продолжать проверку включением."),
                cab("Локальный или общий отказ отопления", "Сопоставить команду и работу остальных отопителей/связанных потребителей.", "Определена общая или локальная цепь отказа.", "Не обходить отключившийся автомат."),
                authorized("Цепь отопителя", "После снятия опасного состояния проверить нагревательный элемент, контактор, проводку и управление по схеме.", "Причина подтверждена измерением и осмотром.", "Не подавать питание на цепь со следами перегрева до устранения причины.")
            ),
            related = listOf("cab-heating-smell", "control-fuse-trip", "relay-panel-overheat", "smoke-fire-flashover", "control-voltage-low")
        )

        "sand-nozzle-blocked" -> scenario.deepen(
            questions = listOf(
                q("sand-scope", "Подача песка отсутствует только у одной форсунки/колёсной пары при исправной подаче остальных?", "Вероятен локальный засор, положение форсунки, местный клапан или подвод воздуха.", "При отсутствии подачи по нескольким точкам проверять общий запас песка, команду и пневматическое питание системы.", "sand-actuation"),
                q("sand-actuation", "При команде слышно/наблюдается срабатывание пневматического привода, но песок к колесу не поступает?", "Команда до исполнительной части доходит; вероятны засор, слёживание песка, форсунка или местный тракт.", "Если исполнительная часть не срабатывает, локализовать команду, клапан и подачу воздуха.", "sand-danger"),
                q("sand-danger", "Отсутствие песка уже сопровождается устойчивым боксованием или ухудшением сцепления?", "Не рассчитывать на неисправную песочницу и не наращивать тягу ради проверки; выбрать безопасный режим движения.", "После безопасной остановки проверить доступные элементы и направление форсунки.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Засорена или неправильно направлена форсунка.", "Песок слежался либо не поступает из бункера.", "Не срабатывает местный пневматический клапан.", "Нет достаточного пневматического питания системы пескоподачи.", "Не формируется электрическая/пневматическая команда.", "Повреждён или разъединён местный тракт подачи песка."),
            checks = listOf(
                cab("Объём отказа", "Сопоставить подачу по колёсным парам только по доступным безопасным признакам.", "Понятно, локален отказ или общий для системы.", "Не проверять форсунки возле движущегося локомотива."),
                stop("Форсунка и запас песка", "После закрепления и безопасной остановки осмотреть доступное положение форсунки и состояние подачи без нахождения в опасной зоне.", "Форсунка направлена штатно, видимого засора/повреждения нет.", "Не выполнять очистку под локомотивом без установленного обеспечения безопасности."),
                authorized("Клапан и тракт пескоподачи", "Проверить клапан, пневматическое питание, команду и тракт по схеме.", "Причина отсутствия подачи подтверждена.", "Не считать пескоподачу исправной только по звуку клапана.")
            ),
            related = listOf("wheel-slip-protection", "traction-current-surge", "feed-line-leak", "traction-one-section-low", "wheel-flat-impact")
        )
'''

REGRESSION = '''package ru.railbrake.calculator.core

import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticGenericRouteRegressionTest {
    @Test
    fun strictGenericRoutesStayBelowReworkCheckpoint() {
        val genericRoot = "Признак относится только к одной секции, тележке или группе?"
        val strictGeneric = DiagnosticRepository.scenarios.filter { scenario ->
            scenario.questions.firstOrNull()?.text == genericRoot
        }
        val ids = strictGeneric.map { it.id }.sorted()
        println("VL80S_STRICT_GENERIC_IDS=" + ids.joinToString(","))
        println("VL80S_STRICT_GENERIC_ROUTES=" + ids.size)
        assertTrue("strict generic routes regressed: ${ids.size}: $ids", ids.size <= 4)
    }
}
'''

BATCH_TEST = '''package ru.railbrake.calculator.core

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticGenericFinalBatchATest {
    private val ids = setOf(
        "field-weakening-fault", "fan-vibration", "aux-contactor-chatter",
        "heater-fault", "sand-nozzle-blocked"
    )

    @Test
    fun batchAUsesSubjectSpecificTrees() {
        ids.forEach { id ->
            val s = DiagnosticRepository.scenario(id)!!
            assertEquals("$id: three-step route", 3, s.questions.size)
            assertEquals("$id: unique questions", 3, s.questions.map { it.text }.distinct().size)
            assertFalse("$id: generic root", s.questions.first().text == "Признак относится только к одной секции, тележке или группе?")
            assertTrue("$id: causes", s.probableCauses.size >= 5)
            assertTrue("$id: links", s.relatedScenarioIds.size >= 4)
            assertTrue("$id: authorization boundary", s.checks.any { it.level == DiagnosticActionLevel.AUTHORIZED_ONLY })
        }
    }

    @Test
    fun fieldWeakeningSeparatesTransitionFromBaseTractionFault() {
        val s = DiagnosticRepository.scenario("field-weakening-fault")!!
        val text = s.questions.joinToString(" ") { it.text + " " + it.yesMeaning + " " + it.noMeaning }
        assertTrue(text.contains("До команды", ignoreCase = true))
        assertTrue(text.contains("подтверж", ignoreCase = true))
        assertTrue(s.relatedScenarioIds.contains("traction-current-surge"))
    }

    @Test
    fun heaterEscalatesFireSignsWithoutRepeatedReset() {
        val s = DiagnosticRepository.scenario("heater-fault")!!
        val text = (s.questions.flatMap { listOf(it.text, it.yesMeaning, it.noMeaning) } + s.checks.flatMap { listOf(it.action, it.ifAbnormal) }).joinToString(" ")
        assertTrue(text.contains("дым", ignoreCase = true))
        assertTrue(text.contains("не выполнять повтор", ignoreCase = true) || text.contains("не обходить", ignoreCase = true))
        assertTrue(s.relatedScenarioIds.contains("smoke-fire-flashover"))
    }

    @Test
    fun sandRouteDoesNotRequireUnsafeMovingInspection() {
        val s = DiagnosticRepository.scenario("sand-nozzle-blocked")!!
        val text = s.checks.joinToString(" ") { it.action + " " + it.ifAbnormal }
        assertTrue(text.contains("безопас", ignoreCase = true))
        assertTrue(text.contains("движущ", ignoreCase = true) || text.contains("закреп", ignoreCase = true))
    }
}
'''

source = APP.read_text(encoding='utf-8')
marker = '\n        else -> scenario\n'
if marker not in source:
    raise SystemExit('DiagnosticDeepening insertion marker not found')
for sid in ['field-weakening-fault', 'fan-vibration', 'aux-contactor-chatter', 'heater-fault', 'sand-nozzle-blocked']:
    if f'"{sid}" -> scenario.deepen(' in source:
        raise SystemExit(f'{sid} already deepened')
updated = source.replace(marker, '\n' + INSERT + marker, 1)
APP.write_text(updated, encoding='utf-8')
PATCH.write_text(updated, encoding='utf-8')
APP_REG.write_text(REGRESSION, encoding='utf-8')
PATCH_REG.write_text(REGRESSION, encoding='utf-8')
APP_TEST.write_text(BATCH_TEST, encoding='utf-8')
PATCH_TEST.write_text(BATCH_TEST, encoding='utf-8')
print('VL80S_GENERIC_FINAL_A=field-weakening-fault,fan-vibration,aux-contactor-chatter,heater-fault,sand-nozzle-blocked')
