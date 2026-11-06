package com.pyneon.academy.data

import android.content.Context
import com.pyneon.academy.lang.LanguageIds

enum class TrackStatus { READY, NOT_INSTALLED }

/**
 * 技术栈路线：只列真实存在的内容（内置主线 + 语言中心课程包）。
 *
 * 旧实现维护了 Java / React / 机器学习 等 20 条「开发中 5%」的占位轨道，
 * 进度百分比是编的、点进去只有一张「建设中」页 —— 属于虚假功能，已删除。
 */
data class Track(
    val id: String,
    val title: String,
    val subtitle: String,
    val category: String,
    val status: TrackStatus,
    val accentArgb: Long,
    val lessonCount: Int = 0,
    val doneCount: Int = 0,
    /** 语言中心课程包 id；null 表示 APK 内置 */
    val packId: String? = null,
    val lang: String = LanguageIds.PYTHON,
    /** 该路线由多个课程包组成时列出全部 id（单包路线与 packId 相同） */
    val packIds: List<String> = emptyList()
) {
    val progressPercent: Int
        get() = if (lessonCount <= 0) 0 else (doneCount * 100 / lessonCount).coerceIn(0, 100)

    val progressHint: String
        get() = when {
            status == TrackStatus.NOT_INSTALLED -> "$lessonCount 讲 · 需在语言中心下载"
            else -> "$lessonCount 讲 · 已完成 $doneCount"
        }
}

data class TrackCategory(val name: String, val tracks: List<Track>)

object TrackRepository {

    private const val CYAN = 0xFF00E5FF
    private const val MAGENTA = 0xFFFF2D78
    private const val YELLOW = 0xFFF7FF00
    private const val GREEN = 0xFF00FF9C
    private const val PURPLE = 0xFFB537F2

    private data class Spec(
        val id: String,
        val title: String,
        val subtitle: String,
        val category: String,
        val accent: Long,
        val packId: String?,
        val lang: String,
        val ids: Set<String>,
        val packIds: List<String> = listOfNotNull(packId)
    ) {
        val expectedCount: Int get() = ids.size
    }

    /**
     * 一门语言的 30 讲固定拆成三包：基础 / 核心 / 进阶。
     * 语言中心与路线页共用这套命名，避免两边各写一份字符串。
     */
    private fun tiers(prefix: String): List<String> = listOf("$prefix-basics", "$prefix-core", "$prefix-advanced")

    private val specs = listOf(
        Spec(
            "python", "Python 主线", "38 讲：print 到异步协程，内置判题实战",
            "编程语言", CYAN, null, LanguageIds.PYTHON,
            (1..38).map { "l%02d".format(it) }.toSet(),
            packIds = emptyList()
        ),
        Spec(
            "js", "JavaScript 全阶", "30 讲：console.log 到生成器与项目实战，Rhino 运行时",
            "编程语言", YELLOW, "js-basics", LanguageIds.JAVASCRIPT,
            (1..30).map { "js%02d".format(it) }.toSet(),
            packIds = tiers("js")
        ),
        Spec(
            "ts", "TypeScript 全阶", "30 讲：类型标注到类型建模，转译后跑在 Rhino 上",
            "编程语言", CYAN, "ts-basics", LanguageIds.TYPESCRIPT,
            (1..30).map { "ts%02d".format(it) }.toSet(),
            packIds = tiers("ts")
        ),
        Spec(
            "dsa-basics", "DSA 算法基础", "5 讲：复杂度 / 双指针 / 哈希 / 栈队列 / 递归",
            "算法与数据结构", GREEN, "dsa-basics", LanguageIds.PYTHON,
            (1..5).map { "dsa%02d".format(it) }.toSet()
        ),
        Spec(
            "dsa-mastery", "DSA 算法进阶", "5 讲：排序 / 二分 / 贪心 / 链表 / 最大子段和",
            "算法与数据结构", MAGENTA, "dsa-mastery", LanguageIds.PYTHON,
            (6..10).map { "dsa%02d".format(it) }.toSet()
        ),
        Spec(
            "c", "C 全阶", "30 讲：printf 到指针、结构体与综合项目，设备端解释执行",
            "编程语言", MAGENTA, "c-basics", LanguageIds.C,
            (1..30).map { "c%02d".format(it) }.toSet(),
            packIds = tiers("c")
        ),
        Spec(
            "lua", "Lua 全阶", "30 讲：print 到元表与协程，LuaJ 运行时",
            "编程语言", GREEN, "lua-basics", LanguageIds.LUA,
            (1..30).map { "lua%02d".format(it) }.toSet(),
            packIds = tiers("lua")
        ),
        Spec(
            "sql", "SQL 全阶", "30 讲：SELECT 到窗口函数与事务，SQLite 运行时",
            "编程语言", CYAN, "sql-basics", LanguageIds.SQL,
            (1..30).map { "sql%02d".format(it) }.toSet(),
            packIds = tiers("sql")
        ),
        Spec(
            "bonus-builtin", "彩蛋 · 内置函数巡礼", "1 讲：len / sorted / enumerate / zip / any / all",
            "语言扩展", PURPLE, "bonus-builtin", LanguageIds.PYTHON,
            setOf("bonus-27")
        )
    )

    /** 只统计真实已装载的课程；done 为该用户的通关集合。 */
    fun tracks(context: Context, done: Set<String> = emptySet()): List<Track> {
        val installed = ContentCenter().installedVersions(context)
        val all = LessonRepository.lessons(context)
        return specs.mapNotNull { s ->
            val present = all.filter { it.id in s.ids }
            // 多包路线：装齐任一包即可学习该包内容，但路线整体仍是「未装齐」
            val installedPacks = s.packIds.count { it in installed }
            val available = s.packId == null || installedPacks > 0
            val complete = s.packIds.isEmpty() || installedPacks == s.packIds.size
            // 未下载的内容包也列出（可下载状态），否则路线页在全新安装时只剩一行
            if (present.isEmpty() && available) return@mapNotNull null
            Track(
                id = s.id,
                title = s.title,
                subtitle = s.subtitle,
                category = s.category,
                status = if (available) TrackStatus.READY else TrackStatus.NOT_INSTALLED,
                accentArgb = s.accent,
                lessonCount = if (present.isEmpty()) s.expectedCount else present.size,
                doneCount = present.count { it.id in done },
                packId = s.packId,
                lang = s.lang,
                packIds = s.packIds
            ).let { t ->
                if (!complete && s.packIds.isNotEmpty()) {
                    t.copy(subtitle = t.subtitle + " · 已装 $installedPacks/${s.packIds.size} 包")
                } else t
            }
        }
    }

    fun categories(context: Context, done: Set<String> = emptySet()): List<TrackCategory> =
        tracks(context, done).groupBy { it.category }.map { (name, list) -> TrackCategory(name, list) }

    fun readyTrack(context: Context, done: Set<String> = emptySet()): Track? =
        tracks(context, done).firstOrNull { it.id == "python" }

    fun findById(context: Context, id: String, done: Set<String> = emptySet()): Track? =
        tracks(context, done).firstOrNull { it.id == id }
}
