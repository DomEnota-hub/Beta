package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class HistoryNavigationInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun historyAndModelScopedNotesAreReachableFromHome() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Рабочие записи").performClick()
        compose.onNodeWithText("История расчётов").assertIsDisplayed()
        compose.onNodeWithText("Рабочие записи").performClick()
        compose.onNodeWithText("Заголовок").assertIsDisplayed()
        compose.onNodeWithText("Текст записи").assertIsDisplayed()
        compose.onNodeWithText("Рабочий локомотив: ВЛ80С", substring = true).assertIsDisplayed()
    }
}
