package com.pyneon.academy.nav

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.outlined.MenuBook
import androidx.compose.material.icons.outlined.LocalFireDepartment
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.SpaceDashboard
import androidx.compose.material.icons.outlined.Terminal
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.isImeVisible
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.pyneon.academy.screens.ArenaScreen
import com.pyneon.academy.screens.BootScreen
import com.pyneon.academy.screens.CertificateScreen
import com.pyneon.academy.screens.ChallengeDetailScreen
import com.pyneon.academy.screens.ContentHubScreen
import com.pyneon.academy.screens.DiagnosticsScreen
import com.pyneon.academy.screens.HomeScreen
import com.pyneon.academy.screens.LessonDetailScreen
import com.pyneon.academy.screens.LanguageCenterScreen
import com.pyneon.academy.screens.LessonsScreen
import com.pyneon.academy.screens.MistakeScreen
import com.pyneon.academy.screens.ProfileScreen
import com.pyneon.academy.screens.StreakScreen
import com.pyneon.academy.screens.TerminalScreen
import com.pyneon.academy.screens.TracksScreen
import com.pyneon.academy.screens.AboutScreen
import com.pyneon.academy.screens.BackupScreen
import com.pyneon.academy.screens.HelpScreen
import com.pyneon.academy.screens.HistoryScreen
import com.pyneon.academy.screens.LicensesScreen
import com.pyneon.academy.screens.ReviewScreen
import com.pyneon.academy.screens.SettingsScreen
import com.pyneon.academy.screens.PrivacyConsentDialog
import com.pyneon.academy.screens.PrivacyPolicyScreen
import com.pyneon.academy.screens.finishApp
import com.pyneon.academy.ui.theme.Bg1
import com.pyneon.academy.ui.theme.Bg0
import com.pyneon.academy.ui.theme.NeonCyan
import com.pyneon.academy.ui.components.WelcomeTutorial
import com.pyneon.academy.ui.theme.TextDim
import com.pyneon.academy.utils.AppPrefs

private data class TopDest(val route: String, val label: String, val icon: ImageVector)

private val TOP_DESTS = listOf(
    TopDest("home", "首页", Icons.Outlined.SpaceDashboard),
    TopDest("lessons", "课程", Icons.AutoMirrored.Outlined.MenuBook),
    TopDest("terminal", "终端", Icons.Outlined.Terminal),
    TopDest("arena", "挑战", Icons.Outlined.LocalFireDepartment),
    TopDest("profile", "我的", Icons.Outlined.Person)
)

@Composable
@OptIn(androidx.compose.foundation.layout.ExperimentalLayoutApi::class)
fun AppRoot() {
    val navController = rememberNavController()
    val backStack by navController.currentBackStackEntryAsState()
    val currentRoute = backStack?.destination?.route ?: "boot"
    val showBar = TOP_DESTS.any { it.route == currentRoute }
    
    // Track if welcome tutorial has been shown in this session
    val context = LocalContext.current
    val showWelcome = remember { mutableStateOf(AppPrefs.isFirstLaunch(context)) }
    // 首次启动必须明示同意隐私政策（华为/工信部合规）
    var showConsent by remember { mutableStateOf(!AppPrefs.isPrivacyConsented(context)) }

    Scaffold(
        containerColor = Bg0,
        bottomBar = {
            // 键盘弹出时隐藏底部导航：否则它要么被键盘盖住点不到，要么和输入框
            // 争夺垂直空间把输入区挤没（终端/练习页实测）。输入期间不需要切 Tab。
            if (showBar && !WindowInsets.isImeVisible) {
                NavigationBar(containerColor = Bg1) {
                    TOP_DESTS.forEach { dest ->
                        NavigationBarItem(
                            selected = currentRoute == dest.route,
                            onClick = {
                                navController.navigate(dest.route) {
                                    popUpTo(navController.graph.findStartDestination().id) {
                                        saveState = true
                                    }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            },
                            icon = { Icon(dest.icon, contentDescription = dest.label, tint = if (currentRoute == dest.route) NeonCyan else TextDim) },
                            label = { Text(dest.label, style = MaterialTheme.typography.labelSmall, color = if (currentRoute == dest.route) NeonCyan else TextDim) },
                            colors = NavigationBarItemDefaults.colors(indicatorColor = Color.Transparent)
                        )
                    }
                }
            }
        }
    ) { padding ->
        NavHost(
            navController = navController,
            startDestination = "boot",
            modifier = Modifier
                .padding(padding)
                .background(Bg0),
            enterTransition = {
                androidx.compose.animation.slideInHorizontally(
                    animationSpec = androidx.compose.animation.core.tween(260),
                    initialOffsetX = { it / 4 }
                ) + androidx.compose.animation.fadeIn(androidx.compose.animation.core.tween(260))
            },
            exitTransition = {
                androidx.compose.animation.fadeOut(androidx.compose.animation.core.tween(160))
            },
            popEnterTransition = {
                androidx.compose.animation.fadeIn(androidx.compose.animation.core.tween(200))
            },
            popExitTransition = {
                androidx.compose.animation.slideOutHorizontally(
                    animationSpec = androidx.compose.animation.core.tween(240),
                    targetOffsetX = { it / 4 }
                ) + androidx.compose.animation.fadeOut(androidx.compose.animation.core.tween(240))
            }
        ) {
            composable("boot") {
                // 合规：未同意隐私政策前不初始化运行时、不写任何学习数据。
                // BootScreen 内部据此跳过预热与连击记录（个保法 / 商店审核要求）。
                BootScreen(
                    consented = !showConsent,
                    onDone = {
                        if (showWelcome.value) {
                            navController.navigate("welcome") {
                                popUpTo("boot") { inclusive = true }
                            }
                        } else {
                            navController.navigate("home") {
                                popUpTo("boot") { inclusive = true }
                            }
                        }
                    }
                )
            }
            
            composable("welcome") {
                // Mark as seen immediately when entering welcome screen
                // This prevents showing it again if user presses back button
                LaunchedEffect(Unit) {
                    AppPrefs.markFirstLaunchComplete(context)
                }
                
                WelcomeTutorial(onComplete = {
                    navController.navigate("home") {
                        popUpTo("welcome") { inclusive = true }
                    }
                })
            }
            composable("home") {
                HomeScreen(
                    onOpenLesson = { id -> navController.navigate("lesson/$id") },
                    onOpenTerminal = { navController.navigate("terminal") },
                    onOpenArena = { navController.navigate("arena") },
                    onOpenLessons = { navController.navigate("lessons") },
                    onOpenTracks = { navController.navigate("tracks") }
                )
            }
            composable("tracks") {
                TracksScreen(
                    onBack = { navController.popBackStack() },
                    onOpenLessons = { navController.navigate("lessons") },
                    onOpenContentHub = { navController.navigate("contenthub") }
                )
            }
            composable("lessons") {
                LessonsScreen(openLesson = { id -> navController.navigate("lesson/$id") })
            }
            composable("lesson/{id}") { entry ->
                val id = entry.arguments?.getString("id").orEmpty()
                LessonDetailScreen(
                    lessonId = id,
                    onBack = { navController.popBackStack() },
                    // U4: 学完一课直接进入下一课（替换当前页，避免栈无限增长）
                    onNextLesson = { nextId ->
                        navController.navigate("lesson/$nextId") {
                            popUpTo("lesson/$id") { inclusive = true }
                        }
                    }
                )
            }
            composable("terminal") { TerminalScreen() }
            composable("arena") {
                ArenaScreen(openChallenge = { id -> navController.navigate("challenge/$id") })
            }
            composable("challenge/{id}") { entry ->
                val id = entry.arguments?.getString("id").orEmpty()
                ChallengeDetailScreen(challengeId = id, onBack = { navController.popBackStack() })
            }
            composable("profile") { ProfileScreen(
                onOpenContentHub = { navController.navigate("contenthub") },
                onOpenLanguageCenter = { navController.navigate("langcenter") },
                onOpenCertificate = { navController.navigate("certificate") },
                onOpenStreak = { navController.navigate("streak") },
                onOpenMistakes = { navController.navigate("mistakes") },
                onOpenPrivacy = { navController.navigate("privacy") },
                onOpenHelp = { navController.navigate("help") },
                onOpenAbout = { navController.navigate("about") },
                onOpenBackup = { navController.navigate("backup") },
                onOpenHistory = { navController.navigate("history") },
                onOpenReview = { navController.navigate("review") },
                onOpenSettings = { navController.navigate("settings") }
            ) }
            composable("contenthub") { ContentHubScreen(onBack = { navController.popBackStack() }) }
            composable("langcenter") { LanguageCenterScreen(onBack = { navController.popBackStack() }) }
            // 「备份/恢复」入口此前只在 ProfileScreen 里 navigate("backup")，但导航图
            // 从未注册该路由 → 点击必崩（IllegalArgumentException: route backup not found）。
            composable("backup") { BackupScreen(onBack = { navController.popBackStack() }) }
            composable("certificate") { CertificateScreen(onBack = { navController.popBackStack() }) }
            composable("streak") {
                StreakScreen(
                    onBack = { navController.popBackStack() },
                    onOpenReview = { navController.navigate("review") }
                )
            }
            composable("review") { ReviewScreen(onBack = { navController.popBackStack() }) }
            composable("history") { HistoryScreen(onBack = { navController.popBackStack() }) }
            composable("settings") {
                SettingsScreen(
                    onBack = { navController.popBackStack() },
                    onOpenDiagnostics = { navController.navigate("diagnostics") }
                )
            }
            composable("diagnostics") { DiagnosticsScreen(onBack = { navController.popBackStack() }) }
            composable("mistakes") {
                MistakeScreen(
                    onBack = { navController.popBackStack() },
                    onOpenLesson = { id -> navController.navigate("lesson/$id") }
                )
            }
            composable("mistakes/{lessonId}") { entry ->
                val id = entry.arguments?.getString("lessonId").orEmpty()
                MistakeScreen(
                    onBack = { navController.popBackStack() },
                    onOpenLesson = { lid -> navController.navigate("lesson/$lid") },
                    lessonId = id
                )
            }
            composable("privacy") { PrivacyPolicyScreen(onBack = { navController.popBackStack() }) }
            composable("help") { HelpScreen(onBack = { navController.popBackStack() }) }
            composable("about") {
                AboutScreen(
                    onBack = { navController.popBackStack() },
                    onOpenLicenses = { navController.navigate("licenses") }
                )
            }
            composable("licenses") { LicensesScreen(onBack = { navController.popBackStack() }) }
        }

        if (showConsent) {
            PrivacyConsentDialog(
                onConsent = {
                    AppPrefs.setPrivacyConsented(context, true)
                    showConsent = false
                },
                onDecline = { finishApp(context) }
            )
        }
}
}
