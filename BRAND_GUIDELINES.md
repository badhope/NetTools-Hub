# CodeLearning · 码上 — Brand Guidelines

## Project Identity

### Official Name
- **English**: CodeLearning（一个词，C 与 L 大写；2026-11 起主品牌）
- **Chinese**: 码上（保留为中文名，码上 = immediately / on the code）
- **标准写法**: `CodeLearning` 或 `CodeLearning · 码上`
- **旧称**: Mashang 仅保留为仓库名 / 域名 / 包标识（仓库 URL 与 `com.pyneon.academy` 不变），不再用于任何展示文案

> 品牌重塑说明（2026-11-06）：英文主品牌由「码上 / Mashang」升级为 **CodeLearning**，中文名「码上」保留。
> 命名从「单一语言 + 短暂即时感」转向「在代码里持续学习」；产品定位仍是多语言离线编程学习终端，
> 当前内置 CPython 3.13、Rhino（JavaScript）、TypeScript 类型擦除、C 教学子集、LuaJ、SQLite 六个设备端运行时。
>
> 应用桌面名：英文环境显示 `CodeLearning`，中文环境显示 `码上`（`values/strings.xml` 与 `values-zh/strings.xml`）。

### Taglines

#### Primary (English)
> "Code now, learn anywhere. Six languages, 30 lessons each — all offline."

#### Primary (Chinese)
> "码上 · 离线编程学习终端 —— 六门语言，每门 30 讲，真跑，全离线。"

#### Secondary Options
- "Your pocket-sized cyberpunk coding terminal"
- "Learn to code without limits, without internet"
- "From print() to decorators — fully offline"

#### Chinese
> "码上，就是马上。"
> "装进口袋的赛博朋克编程学习终端"

#### Japanese
> "今すぐコードを書いて、どの言語もマスターしよう。"
> "ポケットに入るサイバーパンク風プログラミング学習ターミナル"

## Visual Identity

### Color Palette

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| Neon Cyan | `#00E5FF` | `rgb(0, 229, 255)` | Primary accent, links, highlights |
| Neon Green | `#00FF9C` | `rgb(0, 255, 156)` | Success states, Python branding |
| Neon Magenta | `#FF2D78` | `rgb(255, 45, 120)` | Warnings, errors, secondary accent |
| Neon Yellow | `#F7FF00` | `rgb(247, 255, 0)` | Badges, important callouts |
| Background Dark | `#0A0E17` | `rgb(10, 14, 23)` | 品牌背景：Logo / 图标 / 品牌资产底色 |
| Surface Dark | `#0E1420` | `rgb(14, 20, 32)` | App 页面背景（与 `Color.kt` 的 `bg0` 一致） |
| Background Medium | `#111827` | `rgb(17, 24, 39)` | Secondary background, cards（`bg1`） |
| Text Dim | `#93A3B8` | `rgb(147, 163, 184)` | Secondary text, labels（深色主题；对比度 ≥ 4.5:1） |
| Text Bright | `#F9FAFB` | `rgb(249, 250, 251)` | Primary text |

### Typography

#### UI Fonts
- **Primary**: System default (San Francisco on iOS, Roboto on Android)
- **Code**: Monospace (JetBrains Mono, Fira Code, or system monospace)

#### Documentation Fonts
- **Headings**: Bold, larger sizes with neon color accents
- **Body**: Regular weight, high contrast for readability
- **Code blocks**: Monospace with syntax highlighting

### Logo

#### 概念
标识由「代码括号」升级为「学习进阶」：一对 `< >` 折角括号界定代码语境，括号内是一条三级上升阶梯
（Green `#00FF9C`），把「一讲一讲往上走」的课程体系压缩成一个可缩放的极简几何符号。
括号走 Cyan `#00E5FF`，与阶梯形成「语境（代码）+ 结果（成长）」两层含义，不依赖文字也能读出品牌。

#### 几何规范（108×108 网格）
| 元素 | 路径 | 说明 |
| --- | --- | --- |
| 左括号 | `M41,32 L27,54 L41,76` | Cyan，笔画 8/108 ≈ 7.4% |
| 右括号 | `M67,32 L81,54 L67,76` | Cyan，与左括号镜像 |
| 上升阶梯 | `M40,74 L40,64 L51,64 L51,54 L62,54 L62,44` | Green，三级递进 |
- 描边端点 / 拐角均为 round，保证 24dp 下不出现尖角锯齿
- 最小笔画 8/108 单位（> 6/108 下限），外接框 23..85 × 28..80，四周留白 ≥ 18/108
- 右侧开口（`>` 不闭合）+ 阶梯左低右高，构成「向右上」的动势，缩到 48dp / 24dp 仍可辨识

#### 交付物
| 文件 | 尺寸 | 用途 |
| --- | --- | --- |
| `docs/logo.svg` | 1200×300 | 横版组合标志（图形 + CodeLearning 字标 + 「码上 · 离线编程学习终端」副标） |
| `docs/logo-mark.svg` | 512×512 | 方形纯图形标记，用于 favicon / 社交头像 |
| `app/src/main/res/drawable/ic_launcher_foreground.xml` | 108×108 viewport | 自适应图标前景（图形居中，安全区内） |
| `app/src/main/res/drawable/ic_launcher_legacy.xml` | 48×48 | 旧式图标（深色圆角底 + 同一标记） |

#### 清晰空间与最小尺寸
- Clear space: 图形四周至少留出 1/4 个标记宽度
- Minimum size: 完整组合标志 ≥ 120px 宽；纯图形标记 ≥ 24dp（App 图标场景 48dp 起）

#### Logo Variations
- Full color（Cyan + Green，深色底）
- 单色（`#F9FAFB` 或 `#0A0E17`，用于单色印刷 / 水印）
- Icon only（favicon、应用图标、社交头像）

#### Don'ts
- 不要拉伸、压缩或旋转标志
- 不要改变括号与阶梯的配色关系（括号 Cyan、阶梯 Green）
- 不要在低对比或高频纹理背景上直接放置
- 不要给标志叠加投影、描边或多重渐变
- 不要用 Mashang / 码上替换英文主字标（中文名只作为副标出现）

## Tone of Voice

### Personality Traits
- **Cyberpunk**: Edgy, futuristic, tech-savvy
- **Approachable**: Friendly, encouraging, non-intimidating
- **Professional**: Well-documented, reliable, polished
- **Gamified**: Fun, rewarding, progression-focused

### Writing Style

#### Do
- ✅ Use active voice ("Run your code" not "Code should be run")
- ✅ Be concise and direct
- ✅ Use analogies from gaming/cyberpunk culture
- ✅ Celebrate user progress ("You've unlocked Level 5!")
- ✅ Provide clear error messages with actionable fixes

#### Don't
- ❌ Use jargon without explanation
- ❌ Sound condescending or overly academic
- ❌ Leave users stuck without hints
- ❌ Use excessive exclamation marks!!!
- ❌ Assume prior programming knowledge

### Example Phrases

**Good:**
- "Neural interface initialized — ready for code injection"
- "Variable snapshot captured! See what's in memory"
- "Assert shield activated — your code must pass these tests"
- "Welcome back, cyber apprentice_"

**Avoid:**
- "The program has been executed successfully"
- "An error occurred during runtime"
- "Please input your data"
- "Hello user"

## Content Guidelines

### README Structure
1. Hero section with logo and tagline
2. Quick visual preview (terminal mockup or screenshot)
3. Target audience table
4. Value proposition comparison
5. Feature list with emojis
6. Download/install instructions
7. FAQ addressing common concerns
8. Curriculum overview
9. Tech stack diagram
10. Roadmap showing active development
11. Contributing guidelines
12. License information

### Release Notes Format
```markdown
## v0.X.X - Codename (Optional)

### 🚀 New Features
- Feature description with benefit

### 🛠 Improvements
- Enhancement that makes existing feature better

### 🐛 Bug Fixes
- Issue that was resolved

### 📚 Content Updates
- New lessons or improvements to existing content

### 🔧 Technical Changes
- Behind-the-scenes improvements (for developers)
```

### Social Media Posts

#### Twitter/X (280 chars)
```
CodeLearning v0.6 just dropped!

✓ Embedded CPython 3.13
✓ 6 languages, 30 lessons each (180+)
✓ Fully offline - no internet needed
✓ Cyberpunk neon UI

Download: [link]
#python #android #offline #coding
```

#### LinkedIn (Professional)
```
Excited to share CodeLearning (码上) v0.6 - an open-source Android app that teaches six programming languages completely offline.

Built with Kotlin, Jetpack Compose, and Chaquopy (embedded CPython 3.13), it features:
• Six device-side runtimes: CPython 3.13, Rhino, TypeScript, C, LuaJ, SQLite
• 180+ lessons with assert-based auto-grading
• Unique variable visualization panel
• Gamified progression system

Perfect for commuters, students in low-connectivity areas, or anyone who wants to learn Python without distractions.

Check it out: [GitHub link]

#OpenSource #Python #MobileLearning #EdTech #Android
```

## Community Guidelines

### Contributor Recognition
- 贡献者名单由 GitHub 贡献图与 Release Notes 体现（不单独维护 `CONTRIBUTORS.md`）
- Mention significant PRs in release notes
- Add "Contributors" badge to README when count grows

### Code of Conduct Summary
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers learn
- Respect intellectual property
- Follow project coding standards

### Support Channels
- GitHub Issues：Bug reports and feature requests（模板见 `.github/ISSUE_TEMPLATE/`）
- Email：安全漏洞走私密渠道，见 `SECURITY.md`

## Merchandise & Extensions (Future)

Potential branded items:
- Stickers with neon logo
- T-shirts with terminal art
- Mousepads with Python cheat sheets
- Phone cases with cyberpunk design

## Contact & Licensing

For brand usage questions:
- Open a GitHub Discussion
- Email: [project maintainer email]

License: MIT - Free to use with attribution
Trademark: CodeLearning and 码上 names and logo are project identity markers

---

*Last updated: 2026-11-06*
*Version: 2.0*
