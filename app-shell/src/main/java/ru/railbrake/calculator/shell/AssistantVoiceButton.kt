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
import android.speech.RecognitionSupport
import android.speech.RecognitionSupportCallback
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
import ru.railbrake.calculator.assistant.AssistantVoiceSessionGate
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
    val gate = remember { AssistantVoiceSessionGate() }
    var permissionToken by remember { mutableStateOf<Long?>(null) }
    var recognizer by remember { mutableStateOf<SpeechRecognizer?>(null) }
    var timeout by remember { mutableStateOf<Runnable?>(null) }
    var status by remember { mutableStateOf("Голосовой ввод: только локальное распознавание.") }

    fun stop(message: String) {
        gate.invalidate()
        permissionToken = null
        timeout?.let { handler.removeCallbacks(it) }
        timeout = null
        val previous = recognizer
        recognizer = null
        previous?.cancel()
        previous?.destroy()
        status = message
    }

    fun offlineRecognizerAvailable(): Boolean =
        Build.VERSION.SDK_INT >= AssistantVoicePolicy.MIN_ON_DEVICE_API &&
            runCatching { SpeechRecognizer.isOnDeviceRecognitionAvailable(context) }
                .getOrDefault(false)

    fun start() {
        val session = gate.next() ?: return
        // Keep an explicit SDK check in this call path so Android lint can prove
        // createOnDeviceSpeechRecognizer (API 31+) is never reached on API 26–30.
        if (Build.VERSION.SDK_INT < AssistantVoicePolicy.MIN_ON_DEVICE_API ||
            !offlineRecognizerAvailable()) {
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
                    if (recognizer === current && gate.isCurrent(session)) status = "Говорите..."
                }
                override fun onBeginningOfSpeech() {
                    if (recognizer === current && gate.isCurrent(session)) status = "Слушаю..."
                }
                override fun onRmsChanged(rmsdB: Float) = Unit
                override fun onBufferReceived(buffer: ByteArray?) = Unit
                override fun onEndOfSpeech() {
                    if (recognizer === current && gate.isCurrent(session)) status = "Распознаю..."
                }
                override fun onError(error: Int) {
                    if (recognizer === current && gate.isCurrent(session)) stop(
                        when (error) {
                            SpeechRecognizer.ERROR_NO_MATCH, SpeechRecognizer.ERROR_SPEECH_TIMEOUT ->
                                "Речь не распознана. Повторите запрос или введите текст."
                            SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ->
                                "Разрешение на микрофон отсутствует."
                            SpeechRecognizer.ERROR_LANGUAGE_UNAVAILABLE,
                            SpeechRecognizer.ERROR_LANGUAGE_NOT_SUPPORTED ->
                                "Русская офлайн-модель недоступна. Используйте текст."
                            else -> "Офлайн-распознавание недоступно (код $error)."
                        }
                    )
                }
                override fun onResults(results: Bundle?) {
                    if (recognizer !== current || !gate.isCurrent(session)) return
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
                if (recognizer === current && gate.isCurrent(session)) stop("Время записи истекло. Попробуйте снова.")
            }
            timeout = watchdog
            handler.postDelayed(watchdog, AssistantVoicePolicy.MAX_DURATION_MS)
            val request = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale("ru", "RU").toLanguageTag())
                putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, true)
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            }
            // API 33+ exposes installed language packs. Never trigger a download
            // or silently switch to a remote recognition service.
            if (Build.VERSION.SDK_INT >= 33) {
                status = "Проверяю русскую офлайн-модель..."
                current.checkRecognitionSupport(request, context.mainExecutor,
                    object : RecognitionSupportCallback {
                        override fun onSupportResult(support: RecognitionSupport) {
                            if (recognizer !== current || !gate.isCurrent(session)) return
                            when (AssistantVoicePolicy.russianPack(
                                support.installedOnDeviceLanguages,
                                support.supportedOnDeviceLanguages,
                                support.pendingOnDeviceLanguages
                            )) {
                                AssistantVoicePolicy.RussianPack.INSTALLED -> {
                                    status = "Подготовка микрофона..."
                                    try {
                                        current.startListening(request)
                                    } catch (_: Exception) {
                                        stop("Не удалось начать локальное распознавание.")
                                    }
                                }
                                AssistantVoicePolicy.RussianPack.NEEDS_DOWNLOAD ->
                                    stop("Русская офлайн-модель не установлена. Используйте текст.")
                                AssistantVoicePolicy.RussianPack.UNAVAILABLE ->
                                    stop("Русское офлайн-распознавание не поддерживается.")
                            }
                        }
                        override fun onError(error: Int) {
                            if (recognizer === current && gate.isCurrent(session))
                                stop("Не удалось проверить офлайн-модель (код $error). Используйте текст.")
                        }
                    })
            } else {
                // API 31–32 has no support-query API. The recognizer itself is
                // strictly on-device; errors fail closed to editable text.
                current.startListening(request)
                status = "Подготовка микрофона..."
            }
        } catch (_: Exception) {
            stop("Не удалось запустить локальное распознавание. Используйте текст.")
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        val token = permissionToken
        permissionToken = null
        // A permission result can arrive after navigation/disposal or cancellation.
        if (token != null && gate.isCurrent(token)) {
            if (granted) start() else status = "Доступ к микрофону отклонён."
        }
    }

    DisposableEffect(Unit) {
        onDispose {
            gate.dispose()
            permissionToken = null
            timeout?.let { handler.removeCallbacks(it) }
            timeout = null
            val previous = recognizer
            recognizer = null
            previous?.cancel()
            previous?.destroy()
        }
    }

    Column {
        OutlinedButton(onClick = {
            if (recognizer != null) {
                stop("Запись отменена.")
            } else if (permissionToken != null) {
                gate.invalidate()
                permissionToken = null
                status = "Запрос разрешения отменён."
            } else if (!offlineRecognizerAvailable()) {
                status = "На устройстве нет доступного офлайн-распознавателя."
            } else if (context.checkSelfPermission(Manifest.permission.RECORD_AUDIO) ==
                PackageManager.PERMISSION_GRANTED) {
                start()
            } else {
                permissionToken = gate.next()
                if (permissionToken != null) {
                    permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
                }
            }
        }) {
            Text(when {
                recognizer != null -> "Остановить запись"
                permissionToken != null -> "Отменить запрос"
                else -> "🎙 Голосовой ввод"
            })
        }
        Text(status)
    }
}
