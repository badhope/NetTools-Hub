package com.pyneon.academy

import android.app.Application
import android.util.Log
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.pyneon.academy.c.CBridge
import com.pyneon.academy.debug.DebugLog
import com.pyneon.academy.js.JsBridge
import com.pyneon.academy.lang.LanguageRegistry
import com.pyneon.academy.lua.LuaBridge
import com.pyneon.academy.py.PyBridge
import com.pyneon.academy.sql.SqlBridge
import com.pyneon.academy.ts.TsBridge

class PyNeonApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // 注册所有可用语言运行时（新增语言在此处补一行 register 即可）
        LanguageRegistry.register(PyBridge)
        LanguageRegistry.register(JsBridge)
        LanguageRegistry.register(TsBridge)
        LanguageRegistry.register(CBridge)
        LanguageRegistry.register(LuaBridge)
        LanguageRegistry.register(SqlBridge)
        DebugLog.i("App", "启动 v" + com.pyneon.academy.utils.AppConstants.VERSION_NAME +
            " · 已注册运行时 " + LanguageRegistry.ids().joinToString(","))
        try {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(this))
                DebugLog.i("Python", "解释器启动成功")
            }
        } catch (t: Throwable) {
            Log.e("PyNeon", "Python runtime failed to start", t)
            DebugLog.e("Python", "解释器启动失败", t)
        }
    }
}
