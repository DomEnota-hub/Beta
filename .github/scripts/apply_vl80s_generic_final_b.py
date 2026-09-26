#!/usr/bin/env python3
from pathlib import Path

APP = Path('app/src/main/java/ru/railbrake/calculator/core/DiagnosticDeepening.kt')
PATCH = Path('patch/app/src/main/java/ru/railbrake/calculator/core/DiagnosticDeepening.kt')
APP_REG = Path('app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericRouteRegressionTest.kt')
PATCH_REG = Path('patch/app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericRouteRegressionTest.kt')
APP_TEST = Path('app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericFinalBatchBTest.kt')
PATCH_TEST = Path('patch/app/src/test/java/ru/railbrake/calculator/core/DiagnosticGenericFinalBatchBTest.kt')
APP_AUDIT = Path('app/src/test/java/ru/railbrake/calculator/core/DiagnosticUniversalRouteAuditTest.kt')
PATCH_AUDIT = Path('patch/app/src/test/java/ru/railbrake/calculator/core/DiagnosticUniversalRouteAuditTest.kt')

INSERT = r'''
        "headlight-fault" -> scenario.deepen(
            questions = listOf(
                q("light-common", "Одновременно не работают и прожектор, и буферные фонари при штатной команде?", "Сначала проверять общую команду, питание и цепи управления освещением, а не несколько ламп одновременно.", "При исправной части наружного освещения локализовать конкретный светильник, его цепь и коммутацию.", "light-flicker"),
                q("light-flicker", "Неисправный светильник загорается, мигает или гаснет без срабатывания защиты?", "Вероятны лампа/источник света, соединение, патрон, контакт либо местная коммутация.", "Если свет вообще не появляется, разделить отсутствие команды/питания и действие защиты.", "light-danger"),
                q("light-danger", "При включении срабатывает защита либо появляются нагрев, запах или искрение?", "Не повторять включение ради проверки; цепь считать электрически неисправной до безопасной оценки.", "Зафиксировать, какой именно световой прибор не работает и как это влияет на видимость/обозначение локомотива.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Отсутствует общая команда или питание наружного освещения.", "Неисправен отдельный источник света или его местная цепь.", "Нарушено соединение, контакт или коммутационный аппарат.", "Защита отключает цепь из-за электрического дефекта.", "Неисправен канал управления конкретным световым прибором.", "Проблема общей низковольтной системы ошибочно проявляется как локальный отказ освещения."),
            checks = listOf(
                cab("Состав отказа", "Раздельно проверить штатной командой состояние прожектора и буферных фонарей без многократных повторов.", "Определён общий или локальный отказ освещения.", "При запахе, нагреве или срабатывании защиты повторное включение прекратить."),
                cab("Общее питание", "Сопоставить наружное освещение с состоянием цепей управления и других низковольтных потребителей по штатной индикации.", "Понятно, затронуто общее питание или одна местная цепь.", "Не делать вывод о лампе при одновременном отказе нескольких независимых светильников."),
                authorized("Цепь светового прибора", "Проверить защиту, коммутацию, проводку и сам световой прибор по схеме исполнения.", "Причина отказа подтверждена измерением и осмотром.", "Не ставить защиту большего номинала и не подавать питание на цепь со следами перегрева.")
            ),
            related = listOf("control-fuse-trip", "control-voltage-low", "battery-no-charge", "cab-control-mismatch")
        )

        "wiper-fault" -> scenario.deepen(
            questions = listOf(
                q("wiper-common", "При одной и той же команде не работают оба стеклоочистителя?", "Вероятнее общая команда, питание/привод или общий для системы тракт; не начинать с механизма одной щётки.", "При отказе одной стороны локализовать её привод, тяги, щётку и местную цепь.", "wiper-drive"),
                q("wiper-drive", "Есть признаки работы привода, но щётка не движется, движется рывками или заедает?", "Искать механическое заклинивание, тягу, крепление или перегрузку привода; не помогать механизму рукой при включённой системе.", "Если привод не проявляет работы, проверять команду и питание; неисправность омывателя оценивать отдельно от движения щёток.", "wiper-visibility"),
                q("wiper-visibility", "Из-за осадков или загрязнения обзор уже недостаточен для безопасного ведения поезда?", "Не продолжать движение так, будто очистка стекла исправна; обеспечить безопасный режим/остановку по установленному порядку.", "Если обзор достаточен, всё равно зафиксировать отказ и не допускать ухудшения видимости.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Нет общей команды или питания стеклоочистителей.", "Неисправен привод одного стеклоочистителя.", "Заклинили тяги, ось, щётка или механическая передача.", "Нарушена местная проводка или коммутация.", "Отдельно неисправен омыватель, его подача или форсунка при исправном движении щёток.", "Защита привода действует из-за электрической или механической перегрузки."),
            checks = listOf(
                cab("Одна или обе стороны", "Сопоставить реакцию обоих стеклоочистителей на одну штатную команду.", "Отказ локализован до общей системы или одной стороны.", "Не выполнять серию включений при заклинивании или перегрузке."),
                cab("Привод и обзор", "Отделить отсутствие команды/привода от механического заедания и отдельно оценить работу омывателя и фактический обзор.", "Понятны тип отказа и влияние на видимость.", "При недостаточном обзоре приоритет — безопасное ведение, а не дальнейшая диагностика."),
                authorized("Привод стеклоочистителя", "Проверить питание, привод, тяги, коммутацию и цепь защиты по схеме и документации.", "Причина подтверждена без ручного воздействия на включённый механизм.", "Не удерживать и не перемещать механизм вручную при поданном питании.")
            ),
            related = listOf("control-fuse-trip", "control-voltage-low", "cab-control-mismatch", "headlight-fault")
        )

        "door-lock-fault" -> scenario.deepen(
            questions = listOf(
                q("door-hv", "Неисправность относится к двери/шторе ВВК либо к двери, участвующей в высоковольтной блокировке?", "Это не обычная дверная неисправность: перейти к маршруту блокировки ВВК и не обходить её ради получения разрешения.", "Для обычной двери локализовать механическое закрытие и удержание без переноса правил ВВК.", "door-latch"),
                q("door-latch", "Обычная дверь полностью закрывается, но не удерживается замком или самопроизвольно открывается?", "Вероятны замок, ответная часть, регулировка или крепление; оценить риск открытия в движении и доступа в опасную зону.", "Если дверь физически не доходит до закрытого положения, искать препятствие, перекос, петли или повреждение полотна.", "door-danger"),
                q("door-danger", "Неисправность двери создаёт риск доступа в опасную зону, травмирования или мешает безопасной работе из кабины?", "Не считать дверь эксплуатационно исправной; обеспечить безопасное состояние и доложить по установленному порядку.", "Зафиксировать вид механического дефекта и не применять временную фиксацию, способную нарушить блокировки или эвакуацию.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Неисправен замок или ответная часть обычной двери.", "Перекошены петли, полотно либо крепление двери.", "Закрытию мешает механическое препятствие или повреждение.", "Дверь/штора ВВК не даёт корректного механического или электрического подтверждения.", "Нарушена цепь дверной блокировки или её обратная сигнализация.", "Вибрация или ослабление крепежа вызывает самопроизвольное открывание обычной двери."),
            checks = listOf(
                cab("Тип двери", "Сначала определить, относится ли дефект к обычной двери или к ограждению/блокировке ВВК.", "Выбран правильный безопасный маршрут без смешения дверной механики и высоковольтной блокировки.", "Не обходить блокировку ВВК как способ устранить дверную неисправность."),
                stop("Механическое закрытие", "После безопасной остановки проверить доступное закрытие, замок, петли и отсутствие препятствия без входа в опасную зону.", "Обычная дверь закрывается и удерживается штатным механизмом.", "Не использовать импровизированную фиксацию, мешающую безопасному выходу или блокировкам."),
                authorized("Блокировка и крепление", "Для двери/шторы ВВК проверять блокировочную цепь только по схеме и после выполнения установленного безопасного порядка; для обычной двери проверить крепление/замок.", "Механическое состояние и, где применимо, электрическое подтверждение согласованы.", "Не шунтировать блок-контакты и не удерживать блокировочный аппарат вручную.")
            ),
            related = listOf("vvk-interlock-fault", "cab-control-mismatch", "control-voltage-low", "control-fuse-trip")
        )

        "extinguisher-system-fault" -> scenario.deepen(
            questions = listOf(
                q("ext-fire", "Одновременно есть реальный дым, огонь, резкий запах горения или опасный нагрев?", "Неготовность пожаротушения вторична: немедленно перейти к пожарному маршруту и не тратить время на проверку индикации системы.", "При отсутствии реального пожара диагностировать именно неготовность системы пожаротушения.", "ext-confirm"),
                q("ext-confirm", "Неготовность подтверждается не только одной лампой, но и другим штатным признаком или разрешённым внешним осмотром?", "Вероятен реальный отказ готовности конкретного элемента/системы; не имитировать исправность сбросом или перемычкой.", "Сначала отделить ошибку контроля/индикации от фактической неготовности системы.", "ext-control"),
                q("ext-control", "Ненормальна также штатная индикация питания/управления или пусковой цепи системы?", "Локализовать питание и управление по документации установленной системы; профиль исполнения обязателен.", "Если управление выглядит штатно, проверять цепь контроля/датчики готовности и фактическое состояние только разрешёнными способами.", DiagnosticRepository.END_OF_FLOW)
            ),
            causes = listOf("Фактическая неготовность одного из элементов установленной системы пожаротушения.", "Нарушено питание или управление системы.", "Неисправна пусковая цепь либо её контроль.", "Недостоверна цепь индикации/контроля готовности.", "Повреждение или рассоединение доступного элемента системы.", "Выбран неверный профиль системы пожаротушения и неправильно интерпретирована индикация."),
            checks = listOf(
                cab("Пожар или только неготовность", "Сначала отделить реальные признаки горения от сообщения о неготовности системы.", "При пожаре выбран аварийный маршрут; при отсутствии пожара — маршрут готовности.", "Не задерживать пожарные действия диагностикой неисправной системы."),
                stop("Доступная готовность", "После безопасной остановки оценить только предусмотренные штатные индикаторы и доступные внешние признаки без вскрытия, разрядки или пробного пуска.", "Состояние готовности подтверждено разрешёнными средствами.", "Не проверять систему фактическим выпуском огнетушащего вещества или вмешательством в пусковую цепь."),
                authorized("Система пожаротушения", "После подтверждения установленного исполнения проверить питание, управление, пусковую цепь и контроль готовности по документации именно этой системы.", "Причина неготовности подтверждена по профилю и схеме.", "Не шунтировать контроль, блокировки и пусковые цепи и не объявлять систему готовой по одной погасшей лампе.")
            ),
            related = listOf("fire-loop-fault", "machine-room-smoke", "smoke-fire-flashover", "cab-heating-smell")
        )
'''

REGRESSION = '''package ru.railbrake.calculator.core

import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticGenericRouteRegressionTest {
    @Test
    fun strictGenericRoutesAreAbsent() {
        val genericRoot = "Признак относится только к одной секции, тележке или группе?"
        val strictGeneric = DiagnosticRepository.scenarios.filter { scenario ->
            scenario.questions.firstOrNull()?.text == genericRoot
        }
        val ids = strictGeneric.map { it.id }.sorted()
        println("VL80S_STRICT_GENERIC_IDS=" + ids.joinToString(","))
        println("VL80S_STRICT_GENERIC_ROUTES=" + ids.size)
        assertTrue("strict generic routes remain: ${ids.size}: $ids", ids.isEmpty())
    }
}
'''

BATCH_TEST = '''package ru.railbrake.calculator.core

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticGenericFinalBatchBTest {
    private val ids = setOf("headlight-fault", "wiper-fault", "door-lock-fault", "extinguisher-system-fault")

    @Test
    fun finalBatchUsesSubjectSpecificTrees() {
        ids.forEach { id ->
            val s = DiagnosticRepository.scenario(id)!!
            assertEquals("$id: three-step route", 3, s.questions.size)
            assertEquals("$id: unique questions", 3, s.questions.map { it.text }.distinct().size)
            assertFalse("$id: generic root", s.questions.first().text == "Признак относится только к одной секции, тележке или группе?")
            assertTrue("$id: causes", s.probableCauses.size >= 5)
            assertTrue("$id: authorization boundary", s.checks.any { it.level == DiagnosticActionLevel.AUTHORIZED_ONLY })
        }
    }

    @Test
    fun doorRouteSeparatesVvkFromOrdinaryDoor() {
        val s = DiagnosticRepository.scenario("door-lock-fault")!!
        val text = s.questions.joinToString(" ") { it.text + " " + it.yesMeaning + " " + it.noMeaning }
        assertTrue(text.contains("ВВК", ignoreCase = true))
        assertTrue(text.contains("обычн", ignoreCase = true))
        assertTrue("vvk-interlock-fault" in s.relatedScenarioIds)
    }

    @Test
    fun extinguisherChecksRealFireBeforeReadiness() {
        val s = DiagnosticRepository.scenario("extinguisher-system-fault")!!
        val first = s.questions.first().text
        assertTrue(first.contains("дым", ignoreCase = true) || first.contains("огонь", ignoreCase = true))
        assertTrue("smoke-fire-flashover" in s.relatedScenarioIds)
        val checks = s.checks.joinToString(" ") { it.action + " " + it.ifAbnormal }
        assertTrue(checks.contains("не проверять", ignoreCase = true) || checks.contains("не шунтировать", ignoreCase = true))
    }

    @Test
    fun wiperRouteEscalatesLossOfVisibility() {
        val s = DiagnosticRepository.scenario("wiper-fault")!!
        val text = s.questions.joinToString(" ") { it.text + " " + it.yesMeaning + " " + it.noMeaning }
        assertTrue(text.contains("обзор", ignoreCase = true))
        assertTrue(text.contains("безопас", ignoreCase = true))
    }

    @Test
    fun headlightSeparatesCommonFromLocalLightingFault() {
        val s = DiagnosticRepository.scenario("headlight-fault")!!
        val text = s.questions.joinToString(" ") { it.text + " " + it.yesMeaning + " " + it.noMeaning }
        assertTrue(text.contains("прожектор", ignoreCase = true))
        assertTrue(text.contains("буфер", ignoreCase = true))
        assertTrue(text.contains("защит", ignoreCase = true))
    }
}
'''

UNIVERSAL_AUDIT = '''package ru.railbrake.calculator.core

import org.junit.Assert.assertTrue
import org.junit.Test

class DiagnosticUniversalRouteAuditTest {
    private val legacyGenericQuestions = setOf(
        "Признак относится только к одной секции, тележке или группе?",
        "Признак устойчиво повторяется при одинаковом безопасном наблюдении?",
        "Есть опасный нагрев, дым, дуга, утечка, разрушение или защитное отключение?"
    )

    @Test
    fun legacyUniversalTemplateIsAbsentEverywhere() {
        val hits = DiagnosticRepository.scenarios.flatMap { scenario ->
            scenario.questions.filter { it.text in legacyGenericQuestions }.map { scenario.id + "::" + it.text }
        }
        println("VL80S_LEGACY_GENERIC_HITS=" + hits.joinToString(" | "))
        assertTrue("legacy generic questions remain: $hits", hits.isEmpty())
    }

    @Test
    fun completeQuestionTreesAreNotDuplicatedAcrossScenarios() {
        val duplicates = DiagnosticRepository.scenarios
            .filter { it.questions.isNotEmpty() }
            .groupBy { scenario -> scenario.questions.map { it.text.trim().lowercase() } }
            .filterValues { it.size > 1 }
            .values
            .map { group -> group.map { it.id }.sorted() }
            .sortedBy { it.joinToString(",") }
        println("VL80S_DUPLICATE_QUESTION_TREES=" + duplicates.joinToString(" | "))
        assertTrue("duplicate full question trees remain: $duplicates", duplicates.isEmpty())
    }
}
'''

source = APP.read_text(encoding='utf-8')
marker = '\n        else -> scenario\n'
if marker not in source:
    raise SystemExit('DiagnosticDeepening insertion marker not found')
for sid in ['headlight-fault', 'wiper-fault', 'door-lock-fault', 'extinguisher-system-fault']:
    if f'"{sid}" -> scenario.deepen(' in source:
        raise SystemExit(f'{sid} already deepened')
updated = source.replace(marker, '\n' + INSERT + marker, 1)
APP.write_text(updated, encoding='utf-8')
PATCH.write_text(updated, encoding='utf-8')
APP_REG.write_text(REGRESSION, encoding='utf-8')
PATCH_REG.write_text(REGRESSION, encoding='utf-8')
APP_TEST.write_text(BATCH_TEST, encoding='utf-8')
PATCH_TEST.write_text(BATCH_TEST, encoding='utf-8')
APP_AUDIT.write_text(UNIVERSAL_AUDIT, encoding='utf-8')
PATCH_AUDIT.write_text(UNIVERSAL_AUDIT, encoding='utf-8')
print('VL80S_GENERIC_FINAL_B=headlight-fault,wiper-fault,door-lock-fault,extinguisher-system-fault')
