package com.pyneon.academy.utils

import android.content.Context
import java.util.Locale

/**
 * 简易国际化支持
 * 当前优先支持中文，后续可扩展英文、日文
 */
object I18n {
    
    fun getString(context: Context, key: String): String {
        val locale = Locale.getDefault()
        return when (locale.language) {
            "zh" -> getZhString(key)
            "ja" -> getJaString(key)
            else -> getEnString(key)
        }
    }
    
    private fun getZhString(key: String): String {
        return when (key) {
            "welcome.title" -> "欢迎使用 CodeLearning"
            "welcome.subtitle" -> "码上 · 编程学院"
            "welcome.offline.title" -> "完全离线学习"
            "welcome.offline.desc" -> "内置语言运行时\n地铁、飞机、偏远地区都能学\n无需网络，随时学习"
            "welcome.gamification.title" -> "游戏化成长"
            "welcome.gamification.desc" -> "XP 经验值系统\n6 大段位晋升\n每日任务 + 成就徽章\n让学习像打游戏一样上瘾"
            "welcome.snapshot.title" -> "独家变量快照"
            "welcome.snapshot.desc" -> "运行后立即看到所有变量\n名字、类型、值一目了然\n理解代码执行过程\n其他 App 没有的独家功能"
            "welcome.plan.title" -> "7天入门计划"
            "welcome.plan.desc" -> "每天2个精心设计的课程\n循序渐进掌握编程\n从基础语法到面向对象\n完成即可独立编程"
            "button.next" -> "下一步"
            "button.skip" -> "跳过"
            "button.start" -> "开始学习"
            else -> key
        }
    }
    
    private fun getEnString(key: String): String {
        return when (key) {
            "welcome.title" -> "Welcome to CodeLearning"
            "welcome.subtitle" -> "Code Now, Any Language"
            "welcome.offline.title" -> "Learn Completely Offline"
            "welcome.offline.desc" -> "Built-in language runtimes\nLearn on subway, plane, anywhere\nNo internet needed"
            "welcome.gamification.title" -> "Gamified Progress"
            "welcome.gamification.desc" -> "XP system with 6 ranks\nDaily missions & achievements\nMake learning addictive"
            "welcome.snapshot.title" -> "Exclusive Variable Snapshot"
            "welcome.snapshot.desc" -> "See all variables after running\nNames, types, values at a glance\nUnderstand code execution"
            "welcome.plan.title" -> "7-Day Beginner Plan"
            "welcome.plan.desc" -> "2 lessons per day\nMaster coding step by step\nFrom basics to OOP"
            "button.next" -> "Next"
            "button.skip" -> "Skip"
            "button.start" -> "Start Learning"
            else -> key
        }
    }
    
    private fun getJaString(key: String): String {
        return when (key) {
            "welcome.title" -> "CodeLearning へようこそ"
            "welcome.subtitle" -> "今すぐコードを書こう"
            "button.next" -> "次へ"
            "button.skip" -> "スキップ"
            "button.start" -> "学習開始"
            else -> getEnString(key) // Fallback to English
        }
    }
}
