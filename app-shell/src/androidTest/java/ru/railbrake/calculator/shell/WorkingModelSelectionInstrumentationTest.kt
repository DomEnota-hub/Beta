package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertDoesNotExist
import androidx.compose.ui.test.assertExists
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/** Stage 15: a family reference preview is not a VL80S published feature. */
@RunWith(AndroidJUnit4::class)
class WorkingModelSelectionInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun freshLaunchHasNoImplicitVl80sWorkspace() {
        compose.onNodeWithText("Рабочий локомотив").assertIsDisplayed()
        compose.onNodeWithText("Пошаговая пневматика").assertDoesNotExist()
    }

    @Test fun unpublishedFamilyAtlasRequiresExecutionAndNeverBorrowsVl80s() {
        compose.onNodeWithText("2ЭС5К «Ермак»").performClick()
        compose.onNodeWithText("Атлас").performClick()
        compose.onNodeWithText("Исполнение не указано. Доступ к материалам закрыт.").assertExists()
        compose.onNodeWithText("Пошаговая пневматика").assertDoesNotExist()
        compose.onNodeWithText("2ЭС5К, МСУД-Н").performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Справочные описания из Test- · НЕ инструкция к действию")
                .fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Применимость к выбранному исполнению НЕ подтверждена.").assertExists()
        compose.onNodeWithText("Пошаговая пневматика").assertDoesNotExist()
        compose.activity.onBackPressedDispatcher.onBackPressed()
        compose.onNodeWithText("2ЭС5К «Ермак» · Сменить").performClick()
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Атлас").performClick()
        compose.onNodeWithText("Пошаговая пневматика").assertIsDisplayed()
    }
}
