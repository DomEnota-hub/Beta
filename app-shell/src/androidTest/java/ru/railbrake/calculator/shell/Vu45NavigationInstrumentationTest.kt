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
class Vu45NavigationInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun certificateVerificationHasBothIndependentModesAndFullResult() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Расчёты").performClick()
        compose.onNodeWithText("Проверка ВУ-45").performClick()
        compose.onNodeWithText("Проверка ВУ-45").assertIsDisplayed()
        compose.onNodeWithText("В вагонах").performClick()
        compose.onNodeWithText("Количество вагонов").assertIsDisplayed()
        compose.onNodeWithText("В осях").performClick()
        compose.onNodeWithText("Количество осей").assertIsDisplayed()
        compose.onNodeWithText("Проверить").performClick()
        compose.onNodeWithText("Результат проверки").assertIsDisplayed()
        compose.onNodeWithText("Неполные или некорректные данные.", substring = true).assertIsDisplayed()
    }
}
