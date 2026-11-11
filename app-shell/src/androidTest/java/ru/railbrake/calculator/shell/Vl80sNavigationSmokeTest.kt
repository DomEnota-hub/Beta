package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Real Android smoke checks for the modular, source-pinned VL80S preview.
 * The diagnostic catalog intentionally has no accepted scenarios yet.
 */
@RunWith(AndroidJUnit4::class)
class Vl80sNavigationSmokeTest {
    @get:Rule
    val compose = createAndroidComposeRule<MainActivity>()

    @Before
    fun selectWorkingVl80s() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("Атлас").performClick()
        compose.waitUntil(20_000) {
            compose.onAllNodesWithText("Пошаговая пневматика").fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun atlasTrainingRoutesNavigateAndReturnWithoutPublishingCandidates() {
        compose.onNodeWithText("Пошаговая пневматика").assertIsDisplayed().performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()

        compose.onNodeWithText("Служебное").performScrollTo().performClick()
        compose.onNodeWithText("Шаг 1 из 7").assertExists()

        compose.onNodeWithText("← В Атлас").performScrollTo().performClick()
        compose.onNodeWithText("Функциональные электрические цепи")
            .assertIsDisplayed().performClick()
        compose.onNodeWithText("Шаг 1 из 5").assertExists()
        compose.onNodeWithText("← В Атлас").performScrollTo().performClick()

        compose.onNodeWithText("Диагностика · только принятые сценарии")
            .assertIsDisplayed().performClick()
        compose.onNodeWithText(
            "Доступных опубликованных сценариев по этому запросу нет.",
            substring = true,
        ).assertExists()
        compose.onNodeWithText("Поиск по названию, признакам и системе")
            .performTextInput("Токоприёмник не поднимается")
        compose.onNodeWithText(
            "Доступных опубликованных сценариев по этому запросу нет.",
            substring = true,
        ).assertExists()

        compose.onNodeWithText("← Назад").performClick()
        compose.onNodeWithText("Пошаговая пневматика").assertExists()
    }

    @Test
    fun pneumaticApparatusDescriptionsOpenAndDismiss() {
        compose.onNodeWithText("Пошаговая пневматика").performClick()
        // The picker is inside a nested horizontal LazyRow. Scrolling its
        // child doesn't scroll the enclosing vertical Atlas page: bring the
        // following step card into view first, then click the actual button.
        compose.onNodeWithText("Шаг 1 из 4").performScrollTo()
        compose.onNodeWithText("Главные резервуары РС1–РС3")
            .assertIsDisplayed().performClick()
        compose.onNodeWithText("Закрыть").assertIsDisplayed()
        compose.onNodeWithText("Как работает").assertExists()
        compose.onNodeWithText("Закрыть").performClick()
        compose.onNodeWithText("Шаг 1 из 4").assertExists()
    }
}
