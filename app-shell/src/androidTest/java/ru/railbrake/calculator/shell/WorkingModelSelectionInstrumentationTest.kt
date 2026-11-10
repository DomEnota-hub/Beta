package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertDoesNotExist
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class WorkingModelSelectionInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun freshLaunchHasNoImplicitVl80sWorkspace() {
        compose.onNodeWithText("Рабочий локомотив").assertIsDisplayed()
        compose.onNodeWithText("Пошаговая пневматика").assertDoesNotExist()
    }

    @Test fun unpublishedModelCannotExposeVl80sContent() {
        compose.onNodeWithText("2ЭС5К «Ермак»").performClick()
        compose.onNodeWithText("Материалы этой модели пока не опубликованы", substring = true)
            .assertIsDisplayed()
        compose.onNodeWithText("Пошаговая пневматика").assertDoesNotExist()
        compose.onNodeWithText("← Сменить локомотив").performClick()
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Пошаговая пневматика").assertIsDisplayed()
    }
}
