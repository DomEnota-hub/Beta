package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Device coverage for all source-pinned VL80S learning modes, without
 * publishing or endorsing any operational instruction.
 *
 * The shared Compose UI must reset to step one when switching scenarios,
 * and preserve backwards/forwards/reset controls for each model-owned mode.
 */
@RunWith(AndroidJUnit4::class)
class Vl80sLearningFlowInstrumentationTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Test
    fun pneumaticModesResetTheirStepsAndAllowReplay() {
        compose.onNodeWithText("Пошаговая пневматика")
            .assertIsDisplayed().performClick()

        compose.onNodeWithText("Шаг 1 из 4").assertExists()
        compose.onNodeWithText("Далее").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 2 из 4").assertExists()
        compose.onNodeWithText("Назад").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()

        compose.onNodeWithText("Служебное").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 7").assertExists()
        compose.onNodeWithText("Далее").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 2 из 7").assertExists()
        compose.onNodeWithText("С начала").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 7").assertExists()

        compose.onNodeWithText("Отпуск").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()

        compose.onNodeWithText("Вспомогательное").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()
        compose.onNodeWithText("Далее").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 2 из 4").assertExists()
        compose.onNodeWithText("С начала").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()
    }

    @Test
    fun electricalScenariosSwitchWithIndependentInitialSteps() {
        compose.onNodeWithText("Функциональные электрические цепи")
            .assertIsDisplayed().performClick()

        compose.onNodeWithText("Шаг 1 из 5").assertExists()
        compose.onNodeWithText("Далее").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 2 из 5").assertExists()

        compose.onNodeWithText("Подъём ТП").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 6").assertExists()
        compose.onNodeWithText("Далее").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 2 из 6").assertExists()
        compose.onNodeWithText("С начала").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 6").assertExists()

        compose.onNodeWithText("Вспомогательные").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()

        compose.onNodeWithText("Реостатный тормоз").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 5").assertExists()

        compose.onNodeWithText("Защита").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()
        compose.onNodeWithText("Далее").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 2 из 4").assertExists()
        compose.onNodeWithText("Назад").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()

        compose.onNodeWithText("← В Атлас").performScrollTo().performClick()
        compose.onNodeWithText("Пошаговая пневматика").assertExists()
    }
}
