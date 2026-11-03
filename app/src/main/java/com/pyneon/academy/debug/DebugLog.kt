package com.pyneon.academy.debug

import android.content.Context
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.CopyOnWriteArrayList

/**
 * 应用内诊断日志。
 *
 * 为什么需要
 * ----------
 * 离线 App 没有服务端日志，用户遇到问题时只能描述「打不开/报错了」，
 * 开发者无法定位。这里把关键事件（运行时启动、执行失败、内容下载、
 * 主题切换、异常兜底）写进一个内存环形缓冲 + 文件，用户可在
 * 「设置 → 开发者诊断」里查看、复制、导出。
 *
 * 设计约束
 * --------
 * 1. **不上传**。日志只留在设备上，符合「零数据上传」的产品底线。
 * 2. **不记录用户代码**。只记事件类型、耗时、错误类型与消息摘要——
 *    代码内容属于用户隐私，且可能很长。
 * 3. **有界**。内存最多 [MAX_ENTRIES] 条，文件最多 [MAX_FILE_BYTES]，
 *    避免长期运行撑爆存储。
 */
object DebugLog {

    enum class Level { DEBUG, INFO, WARN, ERROR }

    data class Entry(
        val timeMs: Long,
        val level: Level,
        val tag: String,
        val message: String
    ) {
        fun format(): String {
            val t = SimpleDateFormat("HH:mm:ss.SSS", Locale.US).format(Date(timeMs))
            return "$t ${level.name.first()} $tag: $message"
        }
    }

    private const val MAX_ENTRIES = 500
    private const val MAX_FILE_BYTES = 256 * 1024
    private const val FILE_NAME = "debug.log"

    private val buffer = CopyOnWriteArrayList<Entry>()

    /** 全局开关：关闭后不再记录（用户可关，减少开销） */
    @Volatile
    var enabled: Boolean = true

    fun d(tag: String, message: String) = log(Level.DEBUG, tag, message)
    fun i(tag: String, message: String) = log(Level.INFO, tag, message)
    fun w(tag: String, message: String) = log(Level.WARN, tag, message)
    fun e(tag: String, message: String) = log(Level.ERROR, tag, message)

    /** 记录异常：只取类型与消息，不取堆栈正文（避免日志爆炸） */
    fun e(tag: String, message: String, t: Throwable?) {
        val detail = t?.let { "${it.javaClass.simpleName}: ${it.message}" } ?: "unknown"
        log(Level.ERROR, tag, "$message | $detail")
    }

    fun log(level: Level, tag: String, message: String) {
        if (!enabled) return
        val entry = Entry(System.currentTimeMillis(), level, tag, message.take(500))
        buffer.add(entry)
        while (buffer.size > MAX_ENTRIES) buffer.removeAt(0)
        if (level == Level.ERROR) android.util.Log.e(tag, message)
    }

    /** 当前所有日志（新的在后） */
    fun entries(): List<Entry> = buffer.toList()

    fun clear() = buffer.clear()

    /** 导出为纯文本，供「复制」或「分享」使用 */
    fun export(): String = buildString {
        appendLine("# Mashang debug log")
        appendLine("# entries: ${buffer.size}")
        appendLine()
        buffer.forEach { appendLine(it.format()) }
    }

    /** 把日志落盘（App 私有目录），返回文件路径 */
    fun dumpToFile(context: Context): String {
        val file = java.io.File(context.filesDir, FILE_NAME)
        val text = export()
        file.writeText(if (text.length > MAX_FILE_BYTES) text.takeLast(MAX_FILE_BYTES) else text)
        return file.absolutePath
    }

    /** 统计：按级别计数，用于诊断页概览 */
    fun counts(): Map<Level, Int> = buffer.groupingBy { it.level }.eachCount()

    /** 清除文件与内存 */
    fun purge(context: Context) {
        buffer.clear()
        runCatching { java.io.File(context.filesDir, FILE_NAME).delete() }
    }
}
