package com.pyneon.academy.data

import android.app.Activity
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import androidx.annotation.RequiresApi
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.OutputStream

object BackupUtil {
    private const val BACKUP_VERSION = 2

    data class BackupData(
        val version: Int = BACKUP_VERSION,
        val timestamp: Long = System.currentTimeMillis(),
        val xpTotal: Int,
        val completedLessons: Set<String>,
        val solvedKeys: Set<String>,
        val streakDays: Int,
        val longestStreak: Int,
        val totalActiveDays: Int,
        val lastActiveEpochDay: Long,
        val dailyDate: Long,
        val dailyCount: Int,
        val firstRunDone: Boolean,
        val nightOwl: Boolean,
        val terminalHead: Boolean,
        val badges: Set<String>,
        val reviewCards: List<ReviewCard>,
        val mistakes: List<MistakeRecord>
    )

    // Export backup to Downloads/CodeLearning
    suspend fun exportBackup(context: Context): Result<Uri> = withContext(Dispatchers.IO) {
        try {
            val progress = ProgressStore.snapshot(context)
            val reviewCards = loadReviewCardsFromFile(context)
            val mistakes = loadMistakesFromFile(context)

            val backup = BackupData(
                xpTotal = progress.xpTotal,
                completedLessons = progress.completedLessons,
                solvedKeys = progress.solvedKeys,
                streakDays = progress.streakDays,
                longestStreak = progress.longestStreak,
                totalActiveDays = progress.totalActiveDays,
                lastActiveEpochDay = progress.lastActiveEpochDay,
                dailyDate = progress.dailyDate,
                dailyCount = progress.dailyCount,
                firstRunDone = progress.firstRunDone,
                nightOwl = progress.nightOwl,
                terminalHead = progress.terminalHead,
                badges = progress.badges,
                reviewCards = reviewCards,
                mistakes = mistakes
            )

            val jsonString = backupToJson(backup).toString(2)
            val uri = saveToStorage(context, jsonString, "codelearning_backup_${System.currentTimeMillis()}.json")
            Result.success(uri)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // Import backup from file picker
    suspend fun importBackup(context: Context, uri: Uri): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            val inputStream = context.contentResolver.openInputStream(uri)
                ?: return@withContext Result.failure(IllegalArgumentException("无法打开文件"))

            val jsonString = inputStream.bufferedReader().use { it.readText() }
            val backup = backupFromJson(JSONObject(jsonString))

            if (backup.version > BACKUP_VERSION) {
                return@withContext Result.failure(IllegalArgumentException("备份版本过新，请更新应用"))
            }

            // Restore DataStore progress
            ProgressStore.restoreFromBackup(
                context,
                xpTotal = backup.xpTotal,
                completedLessons = backup.completedLessons,
                solvedKeys = backup.solvedKeys,
                streakDays = backup.streakDays,
                lastActiveEpochDay = backup.lastActiveEpochDay,
                dailyDate = backup.dailyDate,
                dailyCount = backup.dailyCount,
                firstRunDone = backup.firstRunDone,
                nightOwl = backup.nightOwl,
                terminalHead = backup.terminalHead,
                badges = backup.badges
            )
            // restoreFromBackup 不带 longest/total（旧备份字段），单独补写
            ProgressStore.updateStreakStats(context, backup.streakDays, backup.longestStreak, backup.totalActiveDays)

            // Save review cards and mistakes to their JSON files
            saveReviewCardsToFile(context, backup.reviewCards)
            saveMistakesToFile(context, backup.mistakes)

            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    // ---- JSON serialization helpers using org.json ----
    private fun setToJson(set: Set<String>): JSONArray = JSONArray().apply {
        for (item in set) put(item)
    }

    private fun setFromJson(arr: JSONArray): Set<String> = buildSet {
        for (i in 0 until arr.length()) add(arr.getString(i))
    }

    private fun progressToJson(b: BackupData) = JSONObject().apply {
        put("xpTotal", b.xpTotal)
        put("completedLessons", setToJson(b.completedLessons))
        put("solvedKeys", setToJson(b.solvedKeys))
        put("streakDays", b.streakDays)
        put("longestStreak", b.longestStreak)
        put("totalActiveDays", b.totalActiveDays)
        put("lastActiveEpochDay", b.lastActiveEpochDay)
        put("dailyDate", b.dailyDate)
        put("dailyCount", b.dailyCount)
        put("firstRunDone", b.firstRunDone)
        put("nightOwl", b.nightOwl)
        put("terminalHead", b.terminalHead)
        put("badges", setToJson(b.badges))
    }

    private fun progressFromJson(o: JSONObject) = object {
        val xpTotal = o.optInt("xpTotal")
        val completedLessons = setFromJson(o.getJSONArray("completedLessons"))
        val solvedKeys = setFromJson(o.getJSONArray("solvedKeys"))
        val streakDays = o.optInt("streakDays")
        val longestStreak = o.optInt("longestStreak")
        val totalActiveDays = o.optInt("totalActiveDays")
        val lastActiveEpochDay = o.optLong("lastActiveEpochDay", -1L)
        val dailyDate = o.optLong("dailyDate", -1L)
        val dailyCount = o.optInt("dailyCount")
        val firstRunDone = o.optBoolean("firstRunDone")
        val nightOwl = o.optBoolean("nightOwl")
        val terminalHead = o.optBoolean("terminalHead")
        val badges = setFromJson(o.getJSONArray("badges"))
    }

    private fun reviewCardToJson(c: ReviewCard) = JSONObject().apply {
        put("id", c.id)
        put("lessonId", c.lessonId)
        put("blockType", c.blockType)
        put("blockIndex", c.blockIndex)
        put("question", c.question)
        put("answer", c.answer)
        put("difficulty", c.difficulty)
        put("interval", c.interval)
        put("repetitions", c.repetitions)
        put("nextReviewDate", c.nextReviewDate)
        put("lastReviewDate", c.lastReviewDate)
        put("lapses", c.lapses)
    }

    private fun reviewCardFromJson(o: JSONObject) = ReviewCard(
        id = o.optString("id"),
        lessonId = o.optString("lessonId"),
        blockType = o.optString("blockType"),
        blockIndex = o.optInt("blockIndex"),
        question = o.optString("question"),
        answer = o.optString("answer"),
        difficulty = o.optDouble("difficulty", 2.5).toFloat(),
        interval = o.optInt("interval"),
        repetitions = o.optInt("repetitions"),
        nextReviewDate = o.optLong("nextReviewDate"),
        lastReviewDate = o.optLong("lastReviewDate"),
        lapses = o.optInt("lapses")
    )

    private fun mistakeToJson(m: MistakeRecord) = JSONObject().apply {
        put("id", m.id)
        put("lessonId", m.lessonId)
        put("blockType", m.blockType)
        put("blockIndex", m.blockIndex)
        put("userCode", m.userCode)
        put("expectedOutput", m.expectedOutput)
        put("actualOutput", m.actualOutput)
        put("errorMessage", m.errorMessage)
        put("timestamp", m.timestamp)
        put("conceptTags", setToJson(m.conceptTags.toSet()))
    }

    private fun mistakeFromJson(o: JSONObject) = MistakeRecord(
        id = o.optInt("id", 0),
        lessonId = o.optString("lessonId"),
        blockType = o.optString("blockType"),
        blockIndex = o.optInt("blockIndex"),
        userCode = o.optString("userCode"),
        expectedOutput = o.optString("expectedOutput"),
        actualOutput = o.optString("actualOutput"),
        errorMessage = o.optString("errorMessage"),
        timestamp = o.optLong("timestamp"),
        conceptTags = setFromJson(o.getJSONArray("conceptTags")).toList()
    )

    private fun backupToJson(b: BackupData) = JSONObject().apply {
        put("version", b.version)
        put("timestamp", b.timestamp)
        put("progress", progressToJson(b))
        val cards = JSONArray()
        for (c in b.reviewCards) cards.put(reviewCardToJson(c))
        put("reviewCards", cards)
        val ms = JSONArray()
        for (m in b.mistakes) ms.put(mistakeToJson(m))
        put("mistakes", ms)
    }

    private fun backupFromJson(o: JSONObject): BackupData {
        val p = progressFromJson(o.getJSONObject("progress"))
        return BackupData(
            version = o.optInt("version", 1),
            timestamp = o.optLong("timestamp"),
            xpTotal = p.xpTotal,
            completedLessons = p.completedLessons,
            solvedKeys = p.solvedKeys,
            streakDays = p.streakDays,
            longestStreak = p.longestStreak,
            totalActiveDays = p.totalActiveDays,
            lastActiveEpochDay = p.lastActiveEpochDay,
            dailyDate = p.dailyDate,
            dailyCount = p.dailyCount,
            firstRunDone = p.firstRunDone,
            nightOwl = p.nightOwl,
            terminalHead = p.terminalHead,
            badges = p.badges,
            reviewCards = (0 until o.getJSONArray("reviewCards").length())
                .map { reviewCardFromJson(o.getJSONArray("reviewCards").getJSONObject(it)) },
            mistakes = (0 until o.getJSONArray("mistakes").length())
                .map { mistakeFromJson(o.getJSONArray("mistakes").getJSONObject(it)) }
        )
    }

    // File I/O helpers for review cards and mistakes
    private fun reviewCardsFile(context: Context) = java.io.File(context.filesDir, UserDataFiles.REVIEW_CARDS)
    private fun mistakesFile(context: Context) = java.io.File(context.filesDir, UserDataFiles.MISTAKES)

    private fun loadReviewCardsFromFile(context: Context): List<ReviewCard> {
        val file = reviewCardsFile(context)
        if (!file.exists()) return emptyList()
        return try {
            val json = JSONArray(file.readText())
            (0 until json.length()).map { reviewCardFromJson(json.getJSONObject(it)) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun loadMistakesFromFile(context: Context): List<MistakeRecord> {
        val file = mistakesFile(context)
        if (!file.exists()) return emptyList()
        return try {
            val json = JSONArray(file.readText())
            (0 until json.length()).map { mistakeFromJson(json.getJSONObject(it)) }
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun saveReviewCardsToFile(context: Context, cards: List<ReviewCard>) {
        val file = reviewCardsFile(context)
        val json = JSONArray()
        for (c in cards) json.put(reviewCardToJson(c))
        file.writeText(json.toString())
    }

    private fun saveMistakesToFile(context: Context, mistakes: List<MistakeRecord>) {
        val file = mistakesFile(context)
        val json = JSONArray()
        for (m in mistakes) json.put(mistakeToJson(m))
        file.writeText(json.toString())
    }

    private fun saveToStorage(context: Context, jsonString: String, fileName: String): Uri =
        saveToMediaStoreQ(context, jsonString, fileName)

    @RequiresApi(Build.VERSION_CODES.Q)
    private fun saveToMediaStoreQ(context: Context, jsonString: String, fileName: String): Uri {
        val resolver = context.contentResolver
        val values = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, fileName)
            put(MediaStore.Downloads.MIME_TYPE, "application/json")
            put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/CodeLearning")
            put(MediaStore.Downloads.IS_PENDING, 1)
        }

        val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
            ?: throw IllegalStateException("创建文件失败")

        resolver.openOutputStream(uri).use { outputStream ->
            outputStream?.write(jsonString.toByteArray())
        }

        values.clear()
        values.put(MediaStore.Downloads.IS_PENDING, 0)
        resolver.update(uri, values, null, null)
        // MediaStore 写入完成后系统自动索引，无需手动发扫描广播
        return uri
    }

    // Launch file picker for import
    fun launchImportPicker(activity: Activity, requestCode: Int) {
        val intent = Intent(Intent.ACTION_OPEN_DOCUMENT).apply {
            addCategory(Intent.CATEGORY_OPENABLE)
            type = "application/json"
            putExtra(Intent.EXTRA_MIME_TYPES, arrayOf("application/json"))
        }
        activity.startActivityForResult(intent, requestCode)
    }
}
