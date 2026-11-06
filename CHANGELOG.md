# 变更记录 · Changelog

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。完整发布说明见 [GitHub Releases](https://github.com/badhope/mashang/releases)。

## [0.7.0] - 2026-11-07

### Added
- **六门语言统一 38 讲**：JavaScript / TypeScript / C / Lua / SQL 各拆 4 包
  （基础 10 + 核心 10 + 进阶 10 + 专业 8），Python 主线 38 讲内置不变。
  全库 23 个课程包、239 讲、2402 个内容块、351 个可运行代码块、803 条判题用例。
- **C 解释器扩展到完整教学子集**：switch（含 fallthrough）、do-while、位运算与复合赋值、
  单级指针（& / * / p[i] / p++ / NULL）、结构体（typedef / 嵌套 / 数组 / ->）、
  sizeof 教学模型、二维数组、常用字符串与数学库函数。150 条单测覆盖。
- **语言中心按需加载重做**：按语言分组显示讲数与体积，支持单包下载与整门一键装齐；
  catalog 新增 `lessons` / `bytes` / `tier` 元数据。
- **品牌升级 CodeLearning · 码上**：新 Logo（`< >` 括号 + 上升阶梯）、自适应图标、
  banner / OG / 特色图 / 宣传海报重建，首页、证书、终端、官网、三语 README 全量同步。

### Fixed
- **同意隐私政策后运行时永不初始化**（发布阻断）：Boot 在未同意时已跑完并导航离开，
  点同意只改状态不重跑初始化，Python/SQL 从此不 start，判题全部报错。
  现在同意后清空回退栈并以 `consentEpoch` 重建 BootScreen。
- **SQL 执行无超时**（发布阻断）：漏写终止条件的 `WITH RECURSIVE` 会永久占住线程。
  改用 `set_progress_handler` 指令级看门狗，超时中断并报 `Timeout`。
- **课程列表筛选后序号错乱 / 解锁指错课**：改用 lesson.id 定位章节位置，不再依赖列表下标。
- **批量下载部分失败被成功提示覆盖**：失败时提示「已装 X/Y 包 + 失败原因」并允许重试。
- **每日任务跨天仍显示已完成**：`dailyMissionDone` 增加日期校验。
- **连击断档后历史徽章被清空**：徽章改为只增不减，按历史最长连击补发，首日补发 `first_day`。
- **路线进度因装新包而倒退**：多包路线分母固定为整门 38 讲。
- **彩蛋包与 Python 第三幕章节重名**导致「下一课」串课、进度条变 x/9：彩蛋包独立章节名。
- **未注册语言静默回落到 Python**：改为返回 `UnsupportedRuntime`，不再用 Python 顶替。
- **挑战页判题异常直接闪退**：补 try/catch，异常转 `RuntimeCrash` 结果。
- **输出只在结束后截断，挡不住 OOM**：Python / JS / Lua 改为写入侧硬上限，超限立即中断。
- 修正 Python 主线 l34（线程完成顺序不确定）、l38（版本约束解析输出错误）两处代码块。
- C / Lua 专业篇综合项目标题与进阶篇重名，改为可区分的标题。

### Changed
- 版本 0.6.0 → **0.7.0**（versionCode 18 → 19）
- 课程口径统一为「六门语言 · 每门 38 讲 · 共 230+ 讲」

## [Unreleased]

### Added
- **C 运行时**（`c/CInterpreter.kt` + `c/CBridge.kt`，纯 Kotlin 教学子集解释器，无 NDK）：支持 int/double/char、一维数组、函数与递归、printf/puts/putchar、assert/assertOutput；不支持指针/结构体/预处理/switch，遇到即明确报错而非静默错答
- **C 启程课程包**（`content_packs/c-basics.json`，6 讲 / 15 判题用例）
- **TypeScript 运行时**（`ts/TypeScriptTranspiler.kt` + `ts/TsBridge.kt`）：类型擦除后复用 Rhino 沙箱，零新增依赖、零 APK 体积增长；支持类型标注/interface/泛型/enum/联合类型，不支持装饰器/命名空间
- **TypeScript 启程课程包**（6 讲 / 17 判题用例）
- **两种新内容块**：`compare`（多语言并排对照，每栏可独立运行）与 `visualize`（过程逐帧可视化，支持单步/自动播放/变化项高亮）
- **视觉风格开关**（`ui/theme/VisualStyle.kt`）：赛博朋克 / 简洁双风格，与配色正交；简洁模式关闭故障字抖动、扫描线、霓虹渐变描边与按压回弹
- **四档字号**（`FontScale`）：紧凑/标准/舒适/大字，只放大课程正文，代码块保持原字号
- 设置页新增「外观风格」与「字号」区块

### Changed
- 版本 0.5.0 → **0.6.0**（versionCode 17 → 18）
- 语言中心 / 课程路线 / README 三语 / 官网同步六门语言口径

### Fixed
- **判题假通过漏洞**（C）：用户代码与测试都定义 `main` 时，测试的 `main` 静默覆盖用户实现，导致空实现也能通过。现改为测试入口重命名为 `__test_main`，并先跑用户 `main` 再跑测试，输出共享同一缓冲区
- **Python 引擎并发串台**：`runner.py` 改写进程级 `sys.stdout` 却无互斥，两路并发执行会互相劫持输出（实测 A 只剩 3/50 行）。新增 `EXEC_LOCK`（RLock），`repl.py` 复用同一把锁，`PyBridge` 加 `synchronized` 门闩
- Windows 下 `test_web_sync` 子进程输出按 GBK 解码导致 UnicodeDecodeError

### Changed（历史遗留项，已在 0.5.0 发布）
- 路线页 / `TrackRepository` / `LessonRepository` 的「内容中心」术语统一为「语言中心」
- `ARCHITECTURE.md` 新增工具清单

## [0.5.0] - 2026-10-24

### Added
- **Lua 运行时**（LuaJ 3.0.1，Lua 5.2 语义，纯 JVM 354 KB）：`app/src/main/java/com/pyneon/academy/lua/LuaBridge.kt`
  - 沙箱只装 Base/Table/String/Math/Coroutine，`io`/`os`/`luajava`/`debug`/`loadfile`/`dofile` 全部不可用
  - 指令钩子看门狗，死循环 0.5 s 内中断；REPL 支持续行
  - TextMate 语法 `syntaxes/lua.tmLanguage.json`；编辑/只读代码块均高亮
- **SQL 运行时**（内嵌 CPython sqlite3，内存库）：`app/src/main/java/com/pyneon/academy/sql/SqlBridge.kt` + `app/src/main/python/sql_runner.py`
  - `ATTACH`/`DETACH` 被 authorizer 拒绝，每次运行都是全新的 `:memory:` 库
  - 判题用例可断言 `columns` / `rows` / `last`；TextMate 语法 `syntaxes/sql.tmLanguage.json`
- **课程包**：`content_packs/lua-basics.json`（6 讲）、`content_packs/sql-basics.json`（6 讲），各含 6 个判题项
- **语言中心**（`screens/LanguageCenterScreen.kt`）：分栏展示内置运行时 / 暂不支持语言 / 课程包下载状态；未内置运行时的语言不出现下载入口
- **按需下载**：课程包未下载前不出现在课程列表；内容包携带 `kind` / `lang` 字段，缺运行时的包显示「缺运行时，暂不可下载」
- 新增 JVM 测试 `LuaSandboxTest`（8 条）、`LuaCoursePacksTest`（2 条），Python 测试 `test_sql_lessons`（7 条）

### Changed
- 版本 0.4.1 → **0.5.0**（versionCode 16 → 17）
- `LanguageIds.PLANNED` 移除 `sql`（已实现），保留 Java / C++ / Go / Rust
- 首页 / 路线页 / 终端语言切换自动包含 Lua 与 SQL
- 文档口径：测试 161 条、判题项 75 个 / 用例 262 条、源程序 64 文件 11,528 行；三语 README / FAQ / CONTRIBUTING / ARCHITECTURE 同步多语言与「语言中心」术语
- README 三语 + FAQ + ARCHITECTURE：GitCode 流水线改为「需手动开通、push 不自动触发」的事实描述

### Fixed
- 课程包下载 UI 与「语言中心」重复维护的问题：`ContentHubScreen` 收敛为 12 行转发入口（原 177 行旧 UI 已删除）；帮助中心/隐私政策/README 的「内容中心」文案同步更名

## [0.4.1] - 2026-10-24

### Fixed
- 文档口径校准：FAQ 测试条数 128 → 149；软著说明书测试合计 119 → 149、用例 200 → 230（Python 55 项/201 用例 + JavaScript 8 项/29 用例）、源程序规模 10,783 → 10,787 行
- 软著说明书「局限性」由「仅内置 Python / JavaScript 未实现」改为「内置 Python 与 JavaScript，其余语言无实现」，与实际能力一致
- 应用内「运行时未内置」提示不再声称可在「语言包」中下载（项目无运行时下载机制）
- 三语 README 首屏运行时描述改为「CPython 3.13 + JavaScript/Rhino」，删除「语言包扩展更多」等未实现承诺
- 关于页、隐私政策、品牌指南、华为商店文案同步为双运行时事实；华为文案构建命令改为环境变量签名方式
- 新增 `tests/test_docs_claims.py`（9 条）：文档数字、能力声明、网页版本串与仓库事实强绑定

### Changed
- 版本 0.4.0 → **0.4.1**（versionCode 15 → 16）；网页端 `APP_VERSION` 与页脚同步

## [0.4.0] - 2026-10-24

### Added
- **网页版（第二端）**：`web/` 纯前端 + Pyodide 0.29.5（CPython 3.13.2），与 App 共用同一套课程 JSON 与同一份 `runner.py`
  - 执行放入 **Web Worker**，15 秒超时强制终止，页面不再被用户死循环冻结
  - 进度 / XP 存 `localStorage`，hash 路由（`#/lesson/l01`、`#/challenge/c01`）刷新与分享可恢复
  - 补齐 `fill` 填空块、章节分组、语言筛选、明暗主题、移动端折叠导航、键盘与读屏可用性
  - 全部用户/课程文本改用 `textContent` 渲染，修复 REPL 输出导致的 DOM XSS
  - 引擎加载失败提供「重试 / 仅浏览课程」两条路径，不再整页卡死
- **应用内检查更新**：设置页读取 GitHub Releases 公开版本号，仅提示 + 打开发布页，不自动下载、不申请安装权限（`utils/UpdateChecker.kt` + JVM 单测）
- **真实课程路线页**：`TrackRepository` 改为按实际装载内容生成（Python 主线 38 讲 / JS 6 讲 / DSA 10 讲 / 彩蛋 1 讲），未下载的包显示「可下载」并跳内容中心；删除 20 条虚构「开发中 x%」占位轨道与「建设中」页
- **内容中心三级源**：GitHub Pages → GitHub raw → GitCode API；新增 `tools/sync_pages_assets.py` 把 catalog、课程包、网页端镜像进 `docs/` 并逐字节校验
- **文档体系**：新增 `ARCHITECTURE.md`（架构、契约、测试布局、已知边界）、`FAQ.md`、`ROADMAP.md`；重写 `SECURITY.md`（威胁模型 / 支持版本 / 响应时限）、`CONTRIBUTING.md`（环境、验证命令、内容规范）、`CODE_OF_CONDUCT.md`（执行流程与联系人）；Issue 模板补环境字段与 `config.yml`
- **展示资产**：全部截图按 v0.4.0 实机重拍（1080×2400，16 张；含判题通过/失败、路线、内容中心、设置、JS 课程）；重制 `docs/banner.png`、`demo/promo-poster.jpg`、OG 分享图；宣传片压到 3.0 MB、官网演示片压到 1.3 MB；`tools/make_brand_assets.py` 可重复生成

### Changed
- 版本 0.3.8 → **0.4.0**（versionCode 14 → 15）
- 课程幕次修正：27-30 归「第四幕 · 边界之外」、31-38 归「第五幕 · 生产实战」（原 31-38 与 27-30 同为第 4 幕，导致五幕结构实际只有四幕）
- 判题契约升级：`check_exercise` 向用例注入 `__stdout__` / `__stderr__`，l01 起要求真正 `print` 出内容（原实现只赋值不输出也能过关）
- 毕业 / 首页 / 课程详情进度统一按 `LessonRepository.mainline()`（`l01..l38`）统计，下载的 DSA 包不再把「x/38」变成「x/49」
- 应用内外链改指 GitHub 主仓；隐私政策 / 用户协议指向 Pages 稳定地址
- 官网 `docs/index.html`：移动端折叠导航、Hero SVG 等比、OG/Twitter/JSON-LD、统计口径改为 63 判题项 / 230 用例、修正「限时挑战」「赛博黑客」「1/3/7 天复习」「8 模块全离线」等不实表述，新增网页版区块与入口

### Fixed
- 判题失败时控制台重复叠加「TestFailed」与「代码运行出错」两块红色面板；`TestFailed` 现在只显示一次并给出可执行建议
- 证书页生成海报后无任何反馈（原 `TODO`），现在成功/失败均有 Toast
- 帮助中心「更新怎么获取」文案与新检查更新链路对齐
- 网页端 REPL 输入 `1+1` / `'a'.upper()` 无回显（改为表达式 eval + repr 回显，语句仍按 exec 执行）
- 网页端点击「下载 App」会抢走导航 active 态（选择器限定 `[data-tab]`）

### Tests
- unittest 140 条全绿；`validate_content.py` 55 个 Python 判题项 / 201 条用例 0 失败
- 新增 `test_ui_static.py::test_tracks_only_lists_real_content`（禁止占位轨道回归）、`UpdateCheckerTest`（3 条语义化版本比较）
- 品牌资产指纹更新为 v0.4.0 重建产物；`test_web_sync` 读文件改为 `with open`（消除 ResourceWarning）
- 新增 `TestTooling` 4 条：链接检查真实通过、坏链接判定逻辑、Pages 同步幂等、品牌资产存在
- Playwright 真实浏览器验收：引擎在线、课程 38 讲 / 5 幕、填空判题、XSS 注入无效、REPL 状态与回显、移动端 390px 无横向溢出、深链刷新恢复
- 模拟器验收：首页 / 课程 / 详情 / 判题通过 +140XP / 判题失败面板 / Python+JS 终端 / 角斗场 / 路线页 / 内容中心下载 / 设置检查更新

## [0.3.8] - 2026-10-23

### Added
- JavaScript 运行时（Rhino 1.7.15，解释模式）与 6 讲语言包；`LanguageRuntime` 抽象 + 语言切换 UI
- L0 离线规则教练、错题本 + SM-2 复习、7 套主题 + 自定义主色
- 内容中心课程包：彩蛋 1 讲、DSA 基础/进阶各 5 讲、JavaScript 启程 6 讲（共 17 讲）

### Fixed
- 界面巡检 12 项（GlitchText 重影、连击台滚动、IME 自动大写、Rhino 错误双前缀等）
- 「备份/恢复」路由未注册导致点击闪退；毕业口径被扩展包污染；catalog sha256 的 CRLF 陷阱

> 更早版本（0.3.7 及以前）见 git 历史与 GitHub Releases。
