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
class SecuringNavigationInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun securingHasIndependentModesAndRejectsMissingInputs() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Расчёты").performClick()
        compose.onNodeWithText("Закрепление состава").performClick()
        compose.onNodeWithText("По массе").assertIsDisplayed()
        compose.onNodeWithText("ИДП №12").performClick()
        compose.onNodeWithText("Формула 1").assertIsDisplayed()
        compose.onNodeWithText("По массе").performClick()
        compose.onNodeWithText("Масса состава, т").assertIsDisplayed()
        compose.onNodeWithText("Рассчитать предварительно").performClick()
        compose.onNodeWithText("Расчёт невозможен:", substring = true).assertIsDisplayed()
        compose.onNodeWithText("ЭКСПЛУАТАЦИОННЫЙ ДОПУСК НЕ ПОДТВЕРЖДЁН.", substring = true).assertIsDisplayed()
    }
}
