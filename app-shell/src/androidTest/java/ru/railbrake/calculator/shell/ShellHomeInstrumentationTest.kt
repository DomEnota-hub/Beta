package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Stage 15: check current, not historical, shell routes. Requires device execution at final QA. */
@RunWith(AndroidJUnit4::class)
class ShellHomeInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun homeAndDrawerOpenRealCommonReferenceInsteadOfOldPlaceholder() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Помощник").assertIsDisplayed()
        compose.onNodeWithText("Расчёты").assertIsDisplayed()
        compose.onNodeWithText("Диагностика").assertIsDisplayed()
        compose.onNodeWithText("Атлас").assertIsDisplayed()
        compose.onNodeWithText("Рабочие записи").assertIsDisplayed()
        compose.onNodeWithText("☰ Меню").performClick()
        compose.onNodeWithText("Рабочие разделы").assertIsDisplayed()
        compose.onNodeWithText("Общие материалы").assertIsDisplayed()
        compose.onNodeWithText("Охрана труда").performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Справочные карточки: 22").fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Справочные карточки: 22").assertIsDisplayed()
        compose.onNodeWithText("Раздел ещё не подключён", substring = true).assertDoesNotExist()
        compose.activity.onBackPressedDispatcher.onBackPressed()
        compose.onNodeWithText("Атлас").assertIsDisplayed()
    }

    @Test fun assistantSearchAndVu45VerifierAreBothReachable() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("Что нужно найти?").assertIsDisplayed()
        compose.onNodeWithText("← На главную").performClick()
        compose.onNodeWithText("Расчёты").performClick()
        compose.onNodeWithText("Проверка ВУ-45").performClick()
        compose.onNodeWithText("Проверить").assertIsDisplayed()
    }

    @Test fun directDiagnosticsAndAcceptanceRoutesAreScopedToVl80s() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Диагностика").performClick()
        compose.onNodeWithText("Доступных опубликованных сценариев", substring = true)
            .assertIsDisplayed()
        compose.onNodeWithText("← Назад").performClick()
        compose.onNodeWithText("Атлас").assertIsDisplayed()
        compose.onNodeWithText("☰ Меню").performClick()
        compose.onNodeWithText("Приёмка").performClick()
        compose.onNodeWithText("Обязательная приёмка").assertIsDisplayed()
    }
}
