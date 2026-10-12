package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertExists
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class Vl80sAcceptanceNavigationInstrumentationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun allEightRoutesOpenFromShellInSourceOrder() {
        compose.onNodeWithText("Приёмка").assertIsDisplayed().performClick()
        val routes = listOf(
            "Обязательная приёмка" to 15,
            "Полный осмотр" to 81,
            "Список по зонам" to 81,
            "Полный осмотр — начать снаружи" to 81,
            "Полный осмотр — начать из кабины" to 81,
            "Экипажная часть" to 42,
            "Машинное отделение / ВВК" to 30,
            "Функциональные проверки" to 29,
        )
        routes.forEach { (title, count) ->
            compose.onNodeWithText(title).performScrollTo().performClick()
            compose.onNodeWithText("Найдено: $count из $count").assertExists()
            compose.activity.onBackPressedDispatcher.onBackPressed()
        }
    }
}
