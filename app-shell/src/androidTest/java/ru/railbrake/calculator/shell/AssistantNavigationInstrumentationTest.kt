package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class AssistantNavigationInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun searchIsReachableAndQueryIsEditable() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("Что нужно найти?").assertIsDisplayed()
        compose.onNodeWithText("Что нужно найти?").performTextInput("главный выключатель")
        compose.onNodeWithText("Найти").performClick()
        compose.onNodeWithText("Помощник").assertIsDisplayed()
    }

    @Test fun commonReferenceSearchOpensMarkedCardWithoutActionPermission() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("Что нужно найти?").performTextInput("слр")
        compose.onNodeWithText("Найти").performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Читать справочную карточку")
                .fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Справочные материалы из Test- · требуют проверки")
            .assertExists()
        compose.onNodeWithText("Читать справочную карточку").performScrollTo().performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Не используйте эту карточку как разрешение на действия.",
                substring = true).fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Исходный справочный текст · требует проверки")
            .assertDoesNotExist()
    }

    @Test fun commonReferenceCardSurvivesActivityRecreation() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("Что нужно найти?").performTextInput("слр")
        compose.onNodeWithText("Найти").performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Читать справочную карточку").fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Читать справочную карточку").performScrollTo().performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Не используйте эту карточку как разрешение на действия.",
                substring = true).fetchSemanticsNodes().isNotEmpty()
        }
        compose.activityRule.scenario.recreate()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Не используйте эту карточку как разрешение на действия.",
                substring = true).fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Исходный справочный текст · требует проверки").assertDoesNotExist()
    }

    @Test fun explicitVl80sSearchFromTem2KeepsWorkingModel() {
        compose.onNodeWithText("ТЭМ2").performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("Что нужно найти?").performTextInput("ВЛ80С главника")
        compose.onNodeWithText("Найти").performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Поиск по ВЛ80С; рабочий локомотив не изменён.")
                .fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("Рабочий локомотив: ТЭМ2").assertExists()
        compose.onNodeWithText("Главный выключатель").assertExists()
        compose.onNodeWithText("← На главную").performScrollTo().performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("ВЛ80С главника").assertExists()
        compose.onNodeWithText("Рабочий локомотив: ТЭМ2").assertExists()
    }

    @Test fun unpublishedModelCannotBorrowVl80s() {
        compose.onNodeWithText("ЧМЭ3").performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("Что нужно найти?").performTextInput("главный выключатель")
        compose.onNodeWithText("Найти").performClick()
        compose.onNodeWithText("Подтверждённые карточки ЧМЭ3 пока не опубликованы.",
            substring = true).assertIsDisplayed()
        compose.onNodeWithText("Справочные описания оборудования из Test-").assertIsDisplayed()
    }
}
