package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithContentDescription
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * End-to-end link through model-owned Atlas content into shared Technical Data.
 * Large model cards must scroll so canonical links cannot disappear below
 * the screen. This checks the real Android UI, not only LinkResolver policies.
 */
@RunWith(AndroidJUnit4::class)
class Vl80sContentNavigationInstrumentationTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun longEquipmentCardCanScrollToItsTechnicalDataLink() {
        compose.onNodeWithContentDescription("Тяговый трансформатор. ОДЦЭ-5000/25Б")
            .performScrollTo().performClick()
        compose.onNodeWithText("Подробнее").performScrollTo().performClick()

        // Regression gate: entry pages must be scrollable independently of
        // their scrollable Atlas parent, including long descriptive blocks.
        compose.onNodeWithText("Технические данные").performScrollTo().performClick()
        compose.onNodeWithText("ВЛ80С · Технические данные").assertIsDisplayed()
    }

    @Test
    fun systemBackFromLinkedTechnicalDataReturnsToEquipmentCard() {
        compose.onNodeWithContentDescription("Тяговый трансформатор. ОДЦЭ-5000/25Б")
            .performScrollTo().performClick()
        compose.onNodeWithText("Подробнее").performScrollTo().performClick()
        compose.onNodeWithText("Технические данные").performScrollTo().performClick()
        compose.onNodeWithText("ВЛ80С · Технические данные").assertIsDisplayed()

        compose.activity.onBackPressedDispatcher.onBackPressed()
        compose.onNodeWithText("Технические данные").performScrollTo().assertIsDisplayed()
    }

    @Test
    fun visibleBackFromLinkedTechnicalDataReturnsToEquipmentCard() {
        compose.onNodeWithContentDescription("Тяговый трансформатор. ОДЦЭ-5000/25Б")
            .performScrollTo().performClick()
        compose.onNodeWithText("Подробнее").performScrollTo().performClick()
        compose.onNodeWithText("Технические данные").performScrollTo().performClick()
        compose.onNodeWithText("ВЛ80С · Технические данные").assertIsDisplayed()

        compose.onNodeWithText("← Назад").assertIsDisplayed().performClick()
        compose.onNodeWithText("Технические данные").performScrollTo().assertIsDisplayed()
    }
}
