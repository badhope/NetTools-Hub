package com.pyneon.academy

import android.app.Application
import android.util.Log
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.pyneon.academy.c.CBridge
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
        try {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(this))
            }
        } catch (t: Throwable) {
            Log.e("PyNeon", "Python runtime failed to start", t)
        }
    }
}
