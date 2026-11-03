package com.pyneon.academy.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.ArrowBack
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.pyneon.academy.ui.components.NeonButton
import com.pyneon.academy.ui.theme.Bg0
import com.pyneon.academy.ui.theme.NeonCyan
import com.pyneon.academy.ui.theme.TextMid
import com.pyneon.academy.utils.AppConstants
import com.pyneon.academy.utils.ShareHelper

@Composable
fun PrivacyPolicyScreen(onBack: () -> Unit) {
    val context = LocalContext.current
    Column(
        Modifier
            .fillMaxSize()
            .background(Bg0)
            .verticalScroll(rememberScrollState())
            .statusBarsPadding()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(
                Icons.AutoMirrored.Outlined.ArrowBack,
                contentDescription = "返回",
                tint = TextMid,
                modifier = Modifier.padding(10.dp).size(28.dp).clickable { onBack() }
            )
            Text(
                "隐私政策",
                style = MaterialTheme.typography.headlineSmall,
                color = NeonCyan,
                modifier = Modifier.padding(start = 12.dp)
            )
        }
        Text(
            "开发者/运营者：${AppConstants.DEV_NAME}\n隐私联系：${AppConstants.CONTACT_EMAIL}",
            style = MaterialTheme.typography.bodySmall,
            color = TextMid
        )

        PolicyBlock("我们收集什么", "我们不收集任何个人信息，不要求注册账号，也不集成任何第三方统计、广告或追踪 SDK。")
        PolicyBlock("本地存储的数据", "你的学习进度、错题、偏好仅保存在你自己的设备本地（Android DataStore/SharedPreferences），不会上传到任何服务器。你可随时在「我的」页「重置全部进度」清除，或直接卸载应用。")
        PolicyBlock("网络权限说明", "应用仅声明了联网（INTERNET）权限，且只用于你在「语言中心」手动点击下载课程拓展包，该过程不附带传输任何个人信息。无网络时全部内置课程仍可完整运行。")
        PolicyBlock("嵌入的语言运行时", "通过 Chaquopy 在设备端嵌入真实 CPython 解释器，并内置 Mozilla Rhino（JavaScript）、LuaJ（Lua）与 SQLite（SQL）；所有代码均在你的手机本地执行，不会发送到外部服务器。")
        PolicyBlock("未成年人", "本应用面向全年龄段，内容为编程学习，不含面向未成年人的定向收集或商业推送。")
        PolicyBlock("你的权利", "你有权了解、更正、删除设备上的本地数据。因我们不持有任何服务器端个人信息，无需额外的数据导出或注销账户流程。")

        NeonButton(
            label = "查看完整隐私政策",
            accent = NeonCyan,
            onClick = { ShareHelper.openUrl(context, AppConstants.PRIVACY_POLICY_URL) },
            modifier = Modifier.fillMaxWidth()
        )
        NeonButton(
            label = "隐私咨询",
            accent = NeonCyan,
            onClick = { ShareHelper.sendEmail(context, AppConstants.CONTACT_EMAIL, "码上 隐私咨询") },
            modifier = Modifier.fillMaxWidth()
        )
        NeonButton(label = "返回", accent = NeonCyan, onClick = onBack, modifier = Modifier.fillMaxWidth())
    }
}

@Composable
private fun PolicyBlock(title: String, body: String) {
    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Text(title, style = MaterialTheme.typography.titleSmall, color = NeonCyan)
        Text(body, style = MaterialTheme.typography.bodySmall, color = TextMid)
    }
}
