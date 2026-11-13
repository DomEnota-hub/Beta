package ru.railbrake.calculator.shell

import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.compose.ui.test.onAllNodesWithText
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * End-to-end Stage 15 route smoke. CI compiles these tests; actual execution
 * requires the final agreed device QA. All reference sections are model-neutral,
 * but none grants permission to execute candidate procedures.
 */
@RunWith(AndroidJUnit4::class)
class Stage15CommonReferenceNavigationTest {
    @get:Rule val compose = createAndroidComposeRule<MainActivity>()

    @Test fun allFourCommonSectionsOpenForAnUnpublishedWorkingModel() {
        compose.onNodeWithText("ЧМЭ3").performClick()
        listOf(
            "База знаний" to 13,
            "Безопасность движения" to 13,
            "Охрана труда" to 22,
            "Первая помощь" to 18,
        ).forEach { (title, count) ->
            compose.onNodeWithText("☰ Меню").performClick()
            compose.onNodeWithText(title).performClick()
            compose.waitUntil(15_000) {
                compose.onAllNodesWithText("Справочные карточки: $count")
                    .fetchSemanticsNodes().isNotEmpty()
            }
            compose.onNodeWithText("Справочные карточки: $count").assertExists()
            compose.onNodeWithText("Источники и действующие редакции требуют проверки.",
                substring = true).assertExists()
            compose.onNodeWithText("Раздел ещё не подключён", substring = true).assertDoesNotExist()
            compose.activity.onBackPressedDispatcher.onBackPressed()
            compose.onNodeWithText("☰ Меню").assertIsDisplayed()
        }
    }

    @Test fun firstAidReferenceShowsWarningButNotUnverifiedSteps() {
        compose.onNodeWithText("ВЛ80С").performClick()
        compose.onNodeWithText("☰ Меню").performClick()
        compose.onNodeWithText("Первая помощь").performClick()
        compose.waitUntil(15_000) {
            compose.onAllNodesWithText("Справочные карточки: 18")
                .fetchSemanticsNodes().isNotEmpty()
        }
        compose.onNodeWithText("При непосредственной угрозе жизни вызывайте 112 или 103.",
            substring = true).assertExists()
        compose.onNodeWithText("Нет сознания").performClick()
        compose.onNodeWithText("Не используйте эту карточку как разрешение на действия.",
            substring = true).assertExists()
        compose.onNodeWithText("Исходный справочный текст · требует проверки").assertDoesNotExist()
        compose.onNodeWithText("← К списку").performClick()
        compose.onNodeWithText("Справочные карточки: 18").assertExists()
    }
}
