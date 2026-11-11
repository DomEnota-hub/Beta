package ru.railbrake.calculator.shell

import android.content.Context
import ru.railbrake.calculator.history.HistoryCodec
import ru.railbrake.calculator.history.HistoryRecord
import ru.railbrake.calculator.history.HistoryStore
import ru.railbrake.calculator.history.WorkNote
import ru.railbrake.calculator.history.WorkNotesCodec
import java.util.UUID

/**
 * Upgrade in-place: read pinned donor calculation_history/records StringSet,
 * write only to a NEW versioned preference file. Legacy data is never deleted.
 * An empty v2 marker prevents cleared records from reappearing on next launch.
 */
class AndroidHistoryStore(context: Context) : HistoryStore {
    private val legacy = context.getSharedPreferences("calculation_history", Context.MODE_PRIVATE)
    private val modern = context.getSharedPreferences("railbrake_history_v2", Context.MODE_PRIVATE)
    private val key = "records_v2"

    @Synchronized
    override fun load(): List<HistoryRecord> {
        if (modern.contains(key)) {
            return HistoryCodec.decodeV2(modern.getString(key, null)
                ?: throw IllegalStateException("Invalid history storage type"))
        }
        // Copy the legacy StringSet before inspecting it; never mutate the returned set.
        val source = if (legacy.contains("records")) {
            legacy.getStringSet("records", null)?.toSet()
                ?: throw IllegalStateException("Invalid legacy history storage type")
        } else emptySet()
        val migrated = HistoryCodec.readLegacy(source)
        check(modern.edit().putString(key, HistoryCodec.encodeV2(migrated)).commit()) {
            "History migration could not be committed"
        }
        return migrated
    }

    @Synchronized
    override fun add(record: HistoryRecord) {
        require(record.timestampMillis >= 0L)
        val updated = HistoryCodec.canonical(listOf(record) + load())
        check(modern.edit().putString(key, HistoryCodec.encodeV2(updated)).commit()) {
            "History write failed"
        }
    }

    @Synchronized
    override fun clear() {
        check(modern.edit().putString(key, "").commit()) { "History clear failed" }
    }
}

/** Separate, explicit model-scoped personal notes. No cloud upload. */
class AndroidWorkNotesStore(context: Context) {
    private val prefs = context.getSharedPreferences("railbrake_work_notes_v1", Context.MODE_PRIVATE)
    private val key = "notes_v1"

    @Synchronized
    private fun all(): List<WorkNote> =
        WorkNotesCodec.decodeV1(prefs.getString(key, "") 
            ?: throw IllegalStateException("Invalid work notes storage type"))

    @Synchronized
    fun load(modelId: String): List<WorkNote> {
        require(modelId.isNotBlank())
        return all().filter { it.modelId == modelId }
    }

    @Synchronized
    fun add(modelId: String, title: String, body: String): WorkNote {
        require(modelId.isNotBlank() && title.isNotBlank() && body.isNotBlank())
        require(title.length <= 200 && body.length <= 10000)
        val note = WorkNote(UUID.randomUUID().toString(), modelId,
            System.currentTimeMillis(), title.trim(), body.trim())
        val updated = listOf(note) + all()
        check(prefs.edit().putString(key, WorkNotesCodec.encodeV1(updated)).commit()) {
            "Work note write failed"
        }
        return note
    }

    @Synchronized
    fun delete(modelId: String, noteId: String) {
        val updated = all().filterNot { it.modelId == modelId && it.id == noteId }
        check(prefs.edit().putString(key, WorkNotesCodec.encodeV1(updated)).commit()) {
            "Work note delete failed"
        }
    }
}
