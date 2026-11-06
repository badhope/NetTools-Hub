package com.pyneon.academy.debug

import android.app.Application
import android.content.Context
import android.content.Intent
import android.os.Process
import kotlin.system.exitProcess

/**
 * 全局未捕获异常处理。
 *
 * 为什么必须有：离线 App 一旦崩溃，系统直接杀掉进程，用户只看到「应用已停止运行」，
 * 既不知道发生了什么，也无法向开发者提供有效信息。这里在进程死亡前：
 *
 *   1. 把异常类型、消息、堆栈摘要写入诊断日志（可被用户导出）
 *   2. 记录一条 [CrashRecord] 到 SharedPreferences，下次启动时可提示「上次异常退出」
 *   3. 交回系统默认处理器（保留系统的崩溃行为，不做静默吞掉）
 *
 * 设计边界：
 * - **不上传**（与「零数据上传」一致）
 * - **不吞异常**：仍然交由默认处理器终止，避免掩盖真实错误
 * - 堆栈只保留前 40 行，避免日志爆炸
 */
object CrashHandler {

    private const val PREFS = "crash_recovery"
    private const val KEY_LAST_CRASH = "last_crash"

    /** 上次崩溃的摘要，供 UI 展示 */
    data class CrashRecord(
        val timestamp: Long,
        val type: String,
        val message: String,
        val stackHead: String
    )

    private var installed = false

    fun install(app: Application) {
        if (installed) return
        installed = true
        val previous = Thread.getDefaultUncaughtExceptionHandler()
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            try {
                record(app, throwable)
            } catch (_: Throwable) {
                // 记录失败绝不能影响原始崩溃流程
            }
            previous?.uncaughtException(thread, throwable)
                ?: run {
                    Process.killProcess(Process.myPid())
                    exitProcess(10)
                }
        }
    }

    private fun record(app: Application, t: Throwable) {
        val stack = t.stackTraceToString().lines().take(40).joinToString("\n")
        val type = t.javaClass.simpleName
        val msg = (t.message ?: "").take(300)

        DebugLog.e("Crash", "未捕获异常：$type | $msg")

        val payload = listOf(
            System.currentTimeMillis().toString(),
            type,
            msg.replace("\n", " "),
            stack
        ).joinToString("\u0001")

        app.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_LAST_CRASH, payload)
            .apply()
    }

    /** 读取上次崩溃记录（若有）；不影响正常流程 */
    fun lastCrash(context: Context): CrashRecord? {
        val raw = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(KEY_LAST_CRASH, null) ?: return null
        val parts = raw.split("\u0001")
        if (parts.size < 4) return null
        return CrashRecord(
            timestamp = parts[0].toLongOrNull() ?: 0L,
            type = parts[1],
            message = parts[2],
            stackHead = parts[3]
        )
    }

    /**
     * 是否有尚未告知用户的崩溃记录。
     *
     * 「上次未正常退出」弹窗展示一次后即调 [clear]；
     * 用户选择「查看诊断」时保留记录（诊断页仍可读），但弹窗不再出现——
     * 由调用方用会话内状态保证，不在此处持久化「已展示」标记。
     */
    fun hasPendingCrash(context: Context): Boolean = lastCrash(context) != null

    fun clear(context: Context) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().remove(KEY_LAST_CRASH).apply()
    }

    /** 构造「反馈崩溃」的邮件内容（用户主动发送，应用不自动上传） */
    fun crashReportText(context: Context): String {
        val c = lastCrash(context) ?: return "（无崩溃记录）"
        return buildString {
            appendLine("应用版本：${com.pyneon.academy.utils.AppConstants.VERSION_NAME}")
            appendLine("崩溃类型：${c.type}")
            appendLine("错误消息：${c.message}")
            appendLine()
            appendLine("堆栈摘要：")
            appendLine(c.stackHead)
        }
    }

    /** 打开邮件客户端预填崩溃报告 */
    fun shareByEmail(context: Context, email: String) {
        val intent = Intent(Intent.ACTION_SENDTO).apply {
            data = android.net.Uri.parse("mailto:$email")
            putExtra(Intent.EXTRA_SUBJECT, "[崩溃报告] CodeLearning ${com.pyneon.academy.utils.AppConstants.VERSION_NAME}")
            putExtra(Intent.EXTRA_TEXT, crashReportText(context))
        }
        runCatching { context.startActivity(intent) }
    }
}
