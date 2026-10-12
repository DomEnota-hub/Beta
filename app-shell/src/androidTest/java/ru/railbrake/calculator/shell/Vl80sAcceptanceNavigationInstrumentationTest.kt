package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.assertTextContains
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performScrollTo
import androidx.compose.ui.test.performTextInput
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
            compose.onNodeWithTag("acceptance-found-count")
                .assertTextContains("Найдено: $count из $count")
            compose.activity.onBackPressedDispatcher.onBackPressed()
        }
    }

    @Test fun noteAndCanonicalStateSurviveRouteSwitchAndActivityRecreation() {
        compose.activity.getSharedPreferences(
            "railbrake_acceptance_state_v1", android.content.Context.MODE_PRIVATE,
        ).edit().clear().commit()

        compose.onNodeWithText("Приёмка").performClick()
        compose.onNodeWithText("Обязательная приёмка").performClick()
        compose.onNodeWithText("Документы и передача замечаний")
            .performScrollTo().performClick()
        compose.onNodeWithText("Замечание").performScrollTo().performClick()
        compose.onNodeWithText("Статус: Замечание").assertExists()
        compose.onNodeWithTag("acceptance-note")
            .performTextInput("Требуется уточнить запись")
        compose.activity.onBackPressedDispatcher.onBackPressed()
        compose.onNodeWithText("Замечания: 1", substring = true).assertExists()

        compose.activity.onBackPressedDispatcher.onBackPressed()
        compose.onNodeWithText("Полный осмотр").performScrollTo().performClick()
        compose.onNodeWithText("Замечания: 1", substring = true).assertExists()
        compose.onNodeWithText("Поиск по пунктам")
            .performTextInput("Документы и передача замечаний")
        compose.onNodeWithTag("acceptance-found-count")
            .assertTextContains("Найдено: 1 из 81")

        compose.activity.recreate()
        compose.onNodeWithText("Приёмка").performClick()
        compose.onNodeWithText("Полный осмотр").performScrollTo().performClick()
        compose.onNodeWithText("Замечания: 1", substring = true).assertExists()
        compose.onNodeWithText("Документы и передача замечаний")
            .performScrollTo().performClick()
        compose.onNodeWithText("Требуется уточнить запись").assertExists()
    }
}
