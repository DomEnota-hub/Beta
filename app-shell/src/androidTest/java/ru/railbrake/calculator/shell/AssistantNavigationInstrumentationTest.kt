package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
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

    @Test fun unpublishedModelCannotBorrowVl80s() {
        compose.onNodeWithText("ЧМЭ3").performClick()
        compose.onNodeWithText("Помощник").performClick()
        compose.onNodeWithText("Что нужно найти?").performTextInput("главный выключатель")
        compose.onNodeWithText("Найти").performClick()
        compose.onNodeWithText("Материалы ЧМЭ3 пока не опубликованы.").assertIsDisplayed()
    }
}
