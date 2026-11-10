package ru.railbrake.calculator.shell

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Column
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import ru.railbrake.calculator.assistant.AssistantVoicePolicy
import java.util.Locale

/**
 * Push-to-talk only. Uses Android's *on-device* recognizer (API 31+).
 * Never falls back to the generic recognizer, which may use network services.
 * A transcript populates the editable draft; search and navigation require separate user action.
 */
@Composable
internal fun AssistantVoiceButton(onTranscript: (String) -> Unit) {
    val context = LocalContext.current
    val latestTranscript by rememberUpdatedState(onTranscript)
    val handler = remember { Handler(Looper.getMainLooper()) }
    var recognizer by remember { mutableStateOf<SpeechRecognizer?>(null) }
    var timeout by remember { mutableStateOf<Runnable?>(null) }
    var status by remember { mutableStateOf("Голосовой ввод: только локальное распознавание.") }

    fun stop(message: String) {
        timeout?.let { handler.removeCallbacks(it) }
        timeout = null
        val previous = recognizer
        recognizer = null
        previous?.cancel()
        previous?.destroy()
        status = message
    }

    fun start() {
        if (Build.VERSION.SDK_INT < AssistantVoicePolicy.MIN_ON_DEVICE_API ||
            !SpeechRecognizer.isOnDeviceRecognitionAvailable(context)) {
            status = "Офлайн-распознавание недоступно на этом устройстве. Используйте текст."
            return
        }
        if (context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) !=
            PackageManager.PERMISSION_GRANTED) {
            status = "Нет разрешения на микрофон."
            return
        }
        try {
            val current = SpeechRecognizer.createOnDeviceSpeechRecognizer(context)
            recognizer = current
            current.setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: Bundle?) {
                    if (recognizer === current) status = "Говорите..."
                }
                override fun onBeginningOfSpeech() {
                    if (recognizer === current) status = "Слушаю..."
                }
                override fun onRmsChanged(rmsdB: Float) = Unit
                override fun onBufferReceived(buffer: ByteArray?) = Unit
                override fun onEndOfSpeech() {
                    if (recognizer === current) status = "Распознаю..."
                }
                override fun onError(error: Int) {
                    if (recognizer === current) stop(
                        when (error) {
                            SpeechRecognizer.ERROR_NO_MATCH, SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->
                                "Речь не распознана. Повторите запрос или введите текст."
                            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ->
                                "Разрешение на микрофон отсутствует."
                            else -> "Офлайн-распознавание недоступно (код $error)."
                        }
                    )
                }
                override fun onResults(results: Bundle?) {
                    if (recognizer !== current) return
                    val transcript = AssistantVoicePolicy.transcriptOrNull(
                        results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                            ?.firstOrNull()
                    )
                    stop(if (transcript == null) "Речь не распознана." else
                        "Текст распознан. Проверьте его и нажмите «Найти».")
                    if (transcript != null) latestTranscript(transcript)
                }
                override fun onPartialResults(partialResults: Bundle?) = Unit
                override fun onEvent(eventType: Int, params: Bundle?) = Unit
            })
            val watchdog = Runnable {
                if (recognizer === current) stop("Время записи истекло. Попробуйте снова.")
            }
            timeout = watchdog
            handler.postDelayed(watchdog, AssistantVoicePolicy.MAX_DURATION_MS)
            current.startListening(Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale("ru", "RU").toLanguageTag())
                putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            })
            status = "Подготовка микрофона..."
        } catch (_: Exception) {
            stop("Не удалось запустить локальное распознавание. Используйте текст.")
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) start() else status = "Доступ к микрофону отклонён."
    }

    DisposableEffect(Unit) {
        onDispose {
            timeout?.let { handler.removeCallbacks(it) }
            recognizer?.cancel()
            recognizer?.destroy()
        }
    }

    Column {
        OutlinedButton(onClick = {
            if (recognizer != null) {
                stop("Запись отменена.")
            } else if (Build.VERSION.SDK_INT < AssistantVoicePolicy.MIN_ON_DEVICE_API ||
                !SpeechRecognizer.isOnDeviceRecognitionAvailable(context)) {
                status = "На устройстве нет доступного офлайн-распознавателя."
            } else if (context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) ==
                PackageManager.PERMISSION_GRANTED) {
                start()
            } else {
                permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }) {
            Text(if (recognizer == null) "🎙 Голосовой ввод" else "Остановить запись")
        }
        Text(status)
    }
}
