<div align="center">

<img src="docs/banner.png" alt="Mashang · 码上" width="830"/>

**Code now, master any language. Learn offline, anywhere.**

A cyberpunk-styled coding learning terminal that fits in your pocket: embedded real language runtimes (Python, JavaScript, Lua, SQL), 38-lesson gamified curriculum, auto-grading with assert, variable visualization, and six-tier progression system.

[![CI](https://img.shields.io/github/actions/workflow/status/badhope/mashang/ci.yml?branch=main&label=CI)](https://github.com/badhope/mashang/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-00E5FF.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-7.0%2B-00E5FF.svg)]()
[![Python](https://img.shields.io/badge/CPython-3.13--offline-00FF9C.svg)]()
[![Kotlin](https://img.shields.io/badge/Kotlin-2.4-FF2D78.svg)]()
[![Lessons](https://img.shields.io/badge/Curriculum-38_Lessons-F7FF00.svg)](#curriculum-38-lessons--5-acts)
[![Download Page](https://img.shields.io/badge/%F0%9F%8C%90-Download_Page-FF2D78.svg)](https://badhope.github.io/mashang/)

🌐 [English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja-JP.md)

[🎬 Trailer](#-trailer50-seconds) · [⚡ TL;DR](#-tldr30-seconds) · [📊 How it runs](#-how-it-runs-fully-offline) · [📥 Download](#download--install) · [Curriculum](#curriculum-38-lessons--5-acts) · [⭐ Star](../../stargazers)

🌐 **Live Site / 在线官网**：[X33834 Pages](https://x33834.github.io/mashang/) · [Morningstar202604 Pages](https://morningstar202604.github.io/mashang/)

</div>

---

## 🎬 Trailer · 50 Seconds

<p align="center">
  <video src="demo/promo-video.mp4" poster="demo/promo-poster.jpg" controls width="380"></video>
  <br/>
  <a href="demo/promo-video.mp4"><img src="demo/promo-poster.jpg" width="460" alt="▶ Watch the trailer"/></a>
  <br/>
  <sub>▶ Click the poster to watch · <a href="demo/promo-video.mp4">open video directly</a> (MP4, 1080×1920, ~50s, original synth soundtrack)</sub>
</p>

> 🌐 [Online download page](https://badhope.github.io/mashang/) — screenshots, videos and QR download on your phone, no account needed

## ⚡ TL;DR · 30 Seconds

| You Ask | One-Line Answer |
|---|:--|
| **Does it work offline?** | ✅ **Truly offline** — a full CPython 3.13 interpreter is embedded in the APK; code, run and get graded in subway tunnels |
| **Will I actually learn to code?** | ✅ **Assert auto-grading** — you don't advance until test cases pass; cures "understood but can't write" |
| **Ads? Account? Tracking?** | ✅ **Zero ads · zero account · zero data upload**, MIT-licensed — safe to recommend to students |
| **Anything unique?** | 🔬 **Variable Snapshot panel** (whole namespace visualized after each run) · Six Tiers · Daily Quests · Mistake Book |
| **How much content?** | 📚 **38 built-in + 29 extension lessons (67 total)**: Python mainline plus 6 lessons each for JavaScript / Lua / SQL, plus 8 Arena challenges |

> 🎯 **One-line pitch**: not another blank code editor — a pocket learning terminal that bundles a **CPython interpreter + grading engine + game-like progression**, fully offline.

## 📊 How It Runs Fully Offline

Others rely on cloud execution and die without a network. **Mashang** embeds a complete CPython 3.13 interpreter right into the APK — every line of code runs on this phone. Here is the runtime chain:

```mermaid
flowchart TD
    UI["📱 Jetpack Compose UI<br/>Cyber HUD · Five-Tab Nav"] -->|"JSON Bridge PyBridge"| KT["⚙️ Kotlin Business Layer<br/>Progress / Theme / Grading"]
    KT -->|"Chaquopy 17.0.0"| PY["🐍 CPython 3.13 Runtime"]
    PY --> RUN["runner.py · Safe Sandbox<br/>Dead-loop Watchdog · input Takeover"]
    PY --> REPL["repl.py · Stateful Session<br/>↑↓ History · Multi-line"]
    RUN --> OUT["📊 Variable Snapshot + Grade"]
    REPL --> OUT
    OUT -->|"Save Progress"| DS[("💾 DataStore")]
    OUT -->|"Drive UI"| UI
    KT --> DS
    classDef neon fill:#0A0E17,stroke:#00E5FF,color:#E6F6FF;
    classDef green fill:#06281F,stroke:#00FF9C,color:#D6FFF0;
    classDef pink fill:#2A0A18,stroke:#FF2D78,color:#FFD9E7;
    class UI,KT neon;
    class PY,RUN,REPL green;
    class OUT pink;
```

> Network is used **only** when you manually fetch course packs in "Language Center" (sha256-verified, zero personal data). Learning, coding, and grading are 100% offline.

## 🔁 The Learning Loop — Until You Can Code It

Not "watch a video → forget". A closed loop that forces you to write: type → run → grade → coach if failed → tier up only when passed.

```mermaid
flowchart LR
    W["✍️ Write Code"] --> R["▶ Run"]
    R --> G{"assert Grading"}
    G -- "Pass" --> U["⚡ Tier Up +XP"]
    G -- "Fail" --> C["🧭 L0 Rule Coach<br/>Diagnose → 3 Steps → Fix Example"]
    C --> W
    U --> W
```

## 📈 What You Learn · Six Languages, Really Executed

Every language ships a **real runtime + lessons + assert-based judging** — not a syntax cheat sheet:

| Language | Runtime | What you'll learn | Lessons |
|---|---|---|---|
| **Python** | Embedded CPython 3.13 | print through async coroutines, decorators, regex, type hints — plus two capstone projects | 38-lesson mainline + DSA basics/advanced + builtin tour |
| **JavaScript** | Rhino 1.7.15 | console.log, Math, string methods, branching guards, array loops, object stats | 6-lesson starter pack |
| **TypeScript** | Type erasure + Rhino | type annotations, interface, function signatures, union narrowing, generics, enum | 6-lesson starter pack |
| **C** | Built-in interpreter (no NDK) | printf, int/double/char, for/while, arrays, functions & recursion, language limits | 6-lesson starter pack |
| **Lua** | LuaJ 3.0.1 | print, local & types, if/for/while, tables (array + map), multiple returns, string library | 6-lesson starter pack |
| **SQL** | SQLite (in-memory) | SELECT, WHERE/ORDER BY, aggregates, INNER JOIN, INSERT/UPDATE, subqueries & NULL | 6-lesson starter pack |

All four share one judging contract: write → run → assert → coach on failure → advance on pass.

- **Built-in vs on-demand**: the Python mainline ships inside the APK; JS / TS / C / Lua / SQL packs download from the Language Center and only then appear in the lesson list — no first-install bloat.
- **Separate sandboxes**: Python uses a `settrace` watchdog, JS and TS deny all Java classes via `ClassShutter` (TS transpiles then reuses the JS sandbox), C runs on a purpose-built subset interpreter (no pointers/structs/preprocessor), Lua omits `io`/`os`/`require`, SQL stays on `:memory:` with `ATTACH` denied.
- **Not yet supported**: Java / C++ / Go / Rust need compilers or native toolchains and can't ship offline; the Language Center marks them "unsupported" and offers no download.

## 🏆 Six-Tier Progression

Level up like a game — from "Script Kiddie" all the way to "System Architect":

```mermaid
flowchart LR
    T1["🥉 Script Kiddie"] --> T2["🥈 Data Ghost"] --> T3["🥉 Network Ronin"] --> T4["🥇 Cyber Hacker"] --> T5["🏆 Street Legend"] --> T6["👑 System Architect"]
```

Each tier unlocks a new title + neon achievement wall. Complete every course to earn a **Graduation Certificate** (neon cert page, screenshot to share).

## 📱 Screenshots

Captured on a real Android emulator (API 35, 1080×2400) from the shipping build — no mockups, no re-touching.

| Home | Lessons | Lesson Detail |
|:--:|:--:|:--:|
| ![Home](demo/app/home.png) | ![Lessons](demo/app/lessons.png) | ![Lesson Detail](demo/app/lesson_detail.png) |

| Practice & Grading | Steps & Output | Arena |
|:--:|:--:|:--:|
| ![Practice](demo/app/lesson_exercise.png) | ![Steps](demo/app/lesson_steps.png) | ![Arena](demo/app/arena.png) |

| Python REPL (live) | JavaScript REPL (Rhino) | Profile |
|:--:|:--:|:--:|
| ![Terminal](demo/app/terminal.png) | ![JS Terminal](demo/app/terminal_js.png) | ![Profile](demo/app/profile.png) |

| Challenge Detail |
|:--:|
| ![Challenge](demo/app/challenge.png) |

| Judge Passed | Judge Failed | Course Routes |
|:--:|:--:|:--:|
| ![Judge Pass](demo/app/judge_pass.png) | ![Judge Fail](demo/app/judge_fail.png) | ![Tracks](demo/app/tracks.png) |

| Language Center | Settings | JS Lessons |
|:--:|:--:|:--:|
| ![Language Center](demo/app/contenthub.png) | ![Settings](demo/app/settings.png) | ![JS Lessons](demo/app/lessons_js.png) |

> All 16 screenshots are real captures from the v0.4.0 build (1080×2400, API 35 emulator): passing a judge awards +140 XP, the failure panel reports `TestFailed` with the failing case, the routes page lists only content that actually ships, and the content hub downloads packs over HTTPS with SHA-256 verification.


> Everything above is real output from the shipping build: `sorted(nums)` → `[1, 1, 2, 3, 4, 5, 6, 9]`, `sum(nums) / len(nums)` → `3.875`, the JS tab running on Rhino 1.7.15 (`10 21`), the practice editor failing with `NameError` before the answer is filled in, and the Neon Counter challenge with its 150 XP spec.
## 🎥 Web client demo · 28s

<p align="center">
  <video src="demo/web-demo.mp4" poster="demo/web-demo-poster.jpg" controls width="640"></video>
  <br/>
  <a href="demo/web-demo.mp4"><img src="demo/web-demo-poster.jpg" width="620" alt="▶ Watch the web demo"/></a>
  <br/>
  <sub>▶ Recorded from the real web client (1280×800, Chromium): run a lesson block, pass a judge, watch XP persist, then use the REPL.</sub>
</p>

## 🌐 Web client (browser)

A second client runs the **same course JSON and the same `runner.py`** in the browser via Pyodide 0.29.5 (CPython 3.13.2):

| Home | Lesson & Judge | Terminal |
|:--:|:--:|:--:|
| ![Web Home](docs/assets/web-home.jpg) | ![Web Lesson](docs/assets/web-lesson.jpg) | ![Web Terminal](docs/assets/web-terminal.jpg) |

- 🔗 Play online: <https://badhope.github.io/mashang/web/>
- 🧵 Execution runs in a Web Worker (15 s hard timeout, tab never freezes); progress is stored in `localStorage`, hash routes survive refresh
- 🧩 Scope: 38 Python lessons, 6 Python challenges, full REPL; the 2 JavaScript challenges stay App-only



## 🎥 Usage Demo · 100s Hands-on

<p align="center">
  <video src="demo/usage-video.mp4" poster="demo/app/home.png" controls width="380"></video>
  <br/>
  <a href="demo/usage-video.mp4"><img src="demo/app/lesson_exercise.png" width="300" alt="▶ Watch the demo"/></a>
  <br/>
  <sub>▶ Click to watch · <a href="demo/usage-video.mp4">open video directly</a> (MP4, 720×1600, ~100s, real device capture)</sub>
</p>

## 👤 Who Is This For

| You Are | You Get |
|---|---|
| Beginner / Career Changer | 38 Chinese narrative lessons, from `print` to decorators |
| Commuter / Fragmented Learner | Fully offline, code even in subway tunnels |
| Teacher / Parent | No ads, no account, zero data upload — safe for students |
| Developer | Complete Compose + Chaquopy reference implementation, MIT-licensed |

## Why Mashang?

| | Others | Mashang |
|---|---|---|
| Code Execution | ☁️ Cloud-based, dead without net | 📱 **On-device CPython 3.13** |
| Teaching Style | Dry documentation | Cyber narrative + life analogies + pop quizzes |
| Runtime Feedback | Black-box print | **Variable Snapshot Panel** + instant result display |
| Growth Motivation | Check-in calendar | **XP / Six Tiers / Daily Quests / Achievement Wall** |

## ✨ Features

### 🧠 Learning Loop — Until You Can Code It

- ✅ **Assert Grading** — must pass test cases to advance, preventing "understood but can't code"
- ✍️ **Fill-in-the-Blank + 🧩 Code Sorting** — Mimo-style low-barrier exercises: type missing fragments / sort shuffled lines into a correct program
- 🧭 **L0 Rule Coach** — on-error guidance: offline rules give "diagnosis → 3 steps → fix example"; hints never write the code for you
- 📖 **Mistake Book + Spaced Repetition** — wrong answers auto-collected; SM-2 scheduling (1 day → 6 days → ease-based growth)
- 🧭 **Hand-holding Guidance** — each lesson: life analogy → ASCII diagram → TASK follow-along → PRACTICE hands-on → STEPS thinking card

### 🔥 Hardcore Engine — Runs Fully Offline

- 🔌 **Offline CPython 3.13** — Chaquopy-embedded real interpreter; network only for Language Center course packs (sha256 verified, zero personal data)
- 🛡 **Sandbox Security** — dead-loop watchdog force-interrupt, input queue takeover for `input()`, friendly localized exceptions
- 🎹 **Code Editor** — neon Python syntax highlighting, smart indentation (`:` auto-indent), Tab-to-space
- 🖥 **Neural Interface REPL** — stateful session, ↑↓ history, multi-line blocks, one-tap reset
- 🔬 **Variable Snapshot** — every variable's name/type/value in the namespace, shown after each run

### 🏆 Gamification — Learning Feels Like a Game

- 🏆 **Six Tiers** — Script Kiddie → Data Ghost → Network Ronin → Cyber Hacker → Street Legend → System Architect
- ⚡ **Daily Quests / XP / Streak** — a goal every day, feedback on every run
- 📦 **Language Center** — runtimes and course packs: Built-in Function Tour bonus + DSA Basics/Mastery + JavaScript / Lua / SQL Kickoff packs (29 lessons total), download and learn on demand
- 🎓 **Graduation Certificate** — neon certification page unlocked upon completing all courses, screenshot to share

### 🧩 Engineering Quality

- 🎨 **7 Color Themes** — Cyber Neon / Deep Space Gray / Aurora Green / Twilight Purple / Twilight Orange / Soft Eye-Care / Paper White, instant switch without restart
- 🔍 **Four font sizes** — Compact / Normal / Comfortable / Large in Settings; scales lesson prose only, code blocks keep their size so indentation stays aligned
- 🎬 **Step-through visualizations** — loop variables and recursion stacks as frame-by-frame animations: single-step, autoplay, changed values highlighted
- 🔀 **Side-by-side language comparison** — the same task in 2–4 languages, each column runnable for instant output diffing
- 🎛 **Cyber / Minimal Dual Style** — colour and motion are decoupled: if you'd rather not see glitch jitter, scanlines or neon gradient borders, switch to Minimal in Settings → Appearance (static type, hairline borders, rounded cards). Colours stay free to mix.
- 👓 **Readability-First UI** — effects confined to decoration zones (boot/home/terminal…); lesson body and graded results use larger sans-serif text, no gimmicks
- ⚡ **Fully Offline** — lessons and interpreter ship inside the APK, no account required; new versions are installed from Releases (no in-app updater yet)

## 📥 Download & Install

> ⚡ **Fastest path** → 🌐 [Online download page](https://badhope.github.io/mashang/): scan or tap, with trailer, screenshots and install guide.
> ⭐ **Main repo** → [github.com/badhope/mashang](https://github.com/badhope/mashang) (Pages + Releases; live badge at top)
> 🛰 **Pages mirrors** → [x33834.github.io/mashang](https://x33834.github.io/mashang/) · [morningstar202604.github.io/mashang](https://morningstar202604.github.io/mashang/)
> 📦 **Repos (parallel sync, pick any)** → [GitHub/badhope](https://github.com/badhope/mashang) · [GitHub/x33834](https://github.com/x33834/mashang) · [GitCode](https://gitcode.com/badhope/mashang) · [Gitee](https://gitee.com/badhope/mashang)

> Android 7.0+ (minSdk 24), arm64-v8a (this build targets 64-bit ARM devices). Release builds are R8-minified.

- ⭐ Recommended: download the latest `mashang-*.apk` from [GitHub Releases](https://github.com/badhope/mashang/releases/latest)
- Build yourself:

```bash
./gradlew :app:assembleDebug        # Debug build
./gradlew :app:assembleRelease     # signed APK via KEYSTORE_PATH / KEYSTORE_PASSWORD / KEY_ALIAS / KEY_PASSWORD
python tests/test_engine_desktop.py   # Engine unit tests
python tests/validate_content.py      # Full curriculum × answer key validation
```

## ❓ FAQ

**Q: Is it really fully offline? What's the network permission for?**
Learning, coding, and grading are 100% offline. Network is only used when manually checking/downloading new course packs in "Language Center", with zero personal data transmitted.

**Q: How is this different from Pydroid3 or other IDEs?**
Pydroid is a development tool; we're a "curriculum-as-code" learning terminal—each lesson comes with graded challenges and a growth system. Our goal is to teach you, not just give you a blank editor.

**Q: Will there be an iOS version?**
The tech stack (Chaquopy) only supports Android; iOS would require a different approach and is on the long-term roadmap.

**Q: Can I use the curriculum commercially?**
Yes. The project is open-sourced under the **MIT License** — free to use, modify, and distribute, including commercial use, as long as the license notice is retained. See [LICENSE](LICENSE) for the full terms.

## 📚 Curriculum (38 Lessons · 5 Acts)

<details open>
<summary><b>Act I · Foundation Protocol</b> (click to collapse)</summary>

`01 First Handshake` · `02 Variables & Types` · `03 String Operations` · `04 Numeric Protocols` · `05 Input Signals` · `06 Conditional Branching Matrix` · `07 Loop Engines` · `08 List Warehouses` · `09 Dictionary Key Vaults` · `10 Foundation Graduation`

</details>

<details>
<summary><b>Act II · Advanced Gear</b></summary>

`11 String Toolbox` · `12 Tuples & Sets` · `13 Function Evolution (*args/**kwargs)` · `14 Comprehension Storm` · `15 Exception Shields` · `16 Data Persistence (Files/JSON)` · `17 Module Summoning` · `18 Class & Object Awakening`

</details>

<details>
<summary><b>Act III · High-Tier Implants</b></summary>

`19 Inheritance & Magic Methods` · `20 Capstone Project · Cyber Bank` · `21 Generator Engines` · `22 Decorator Suits` · `23 Lambda Trio` · `24 Standard Library Combat (Counter/re)` · `25 Time & Random Universe` · `26 Graduation Project · Log Analyzer`

</details>

<details>
<summary><b>Act IV · Beyond the Boundary</b></summary>

`27 Resource Steward with` · `28 File I/O Protocols` · `29 Custom Exceptions` · `30 Modules & Main Guard (__main__)`

</details>

<details>
<summary><b>Act V · Production Combat</b></summary>

`31 Regex Text Mining` · `32 Type Hints & Dataclasses` · `33 Functional Toolbox` · `34 Concurrency: Threads & Processes` · `35 Async Coroutines async/await` · `36 CLI Toolbox` · `37 Debugging & Testing` · `38 Virtual Env & Engineering`

</details>

<details>
<summary><b>Language Packs · Language Center (downloadable)</b></summary>

Easter Egg · Built-in Function Tour (1 lesson) · DSA Algorithm Basics (5 lessons: complexity intuition / two pointers / hash tables / stacks & queues / recursion memoization) · DSA Algorithm Mastery (5 lessons: hand-written sorting / binary search / greedy change-making / linked-list thinking / maximum subarray) · Language Pack · JavaScript Kickoff (6 lessons, requires the built-in JS runtime — bundled since this version)

</details>

Each lesson includes: **Runnable Example + OUTPUT Preview + Diagram/Table + QUIZ Pop Question + Assert Grading Challenge**
Plus 8 Arena challenges: Neon Counter / Palindrome Detector / Password Strength Firewall / Bracket Firewall / Run-Length Compressor / Inventory Manager (6 Python) + Neon Counter & Bracket Firewall in JavaScript.

## 🧱 Tech Stack

```
Kotlin + Jetpack Compose (Material3 Cyber Custom Theme)
        │  LanguageRuntime contract (JSON payloads)
PyBridge(Chaquopy) ──► CPython 3.13 (runner.py sandbox / repl.py session)
JsBridge(Rhino)    ──► JavaScript (language-pack lessons via Language Center)
LuaBridge(LuaJ)    ──► Lua (sandbox: no io/os/require)
SqlBridge(sqlite3) ──► SQL (in-memory DB, ATTACH denied)
DataStore Progress │ Navigation Single-Activity Five-Tab │ Custom Syntax Highlighter
```

See the [How It Runs](#-how-it-runs-fully-offline) architecture diagram above for the visual runtime chain.

## 🗺 Roadmap

- [x] v0.1 MVP: engine loop + 7 screens + grading
- [x] v0.2 content explosion: 26 lessons + 4 new content blocks (table/diagram/quiz/output preview)
- [x] v0.2.1 Content Hub: online course-pack download (client-cloud), first pack "Built-in Function Tour"
- [x] v0.3 milestone: DSA bonus packs ×2 (10 lessons), L0 offline rule coach, mistake book + spaced repetition, UI readability cleanup
- [ ] v0.3 remaining: turtle canvas · matplotlib output · runtime variable animation
- [x] v0.4.0: `LanguageRuntime` abstraction + JavaScript pack (Rhino) + language filter/switch UI · web client (Pyodide 0.29.5, same engine) · in-app update check · real course-route page
- [ ] v0.5: turtle canvas · matplotlib chart output · tablet layout · QuickJS backend (ES6+)
- [ ] v1.0 full app-store distribution

## 🧪 Testing & quality gates

| Gate | Command | What it proves |
|---|---|---|
| Python engine + content | `python -m unittest discover -s tests` | 149 desktop tests: sandbox, timeouts, judging, content schema, docs claims |
| Curriculum × answers | `python tests/validate_content.py` | 55 Python lessons/packs judged end-to-end, 201 cases |
| JS lessons | `python -m unittest discover -s tests -k test_js_lessons` | Every JS lesson code block + exercise executed with Node |
| Web/App same-source | `python -m unittest discover -s tests -k test_web_sync` | `data.js`/`engine.js` regenerate byte-identically |
| Android lint + unit | `./gradlew :app:lintDebug :app:testDebugUnitTest` | 0 lint errors, JVM unit tests (version compare, file IO) |
| APK probe | `python tests/ci_apk_probe.py <apk>` | runner.py, assets, JS grammar and manifest inside the APK |
| Pages assets | `python tools/sync_pages_assets.py` | catalog / course packs / web client copies are byte-identical |

## 🤝 Contributing

All forms welcome: new lesson content, bug reports, UI polish, multi-language translations.
Fork → New branch → Submit PR; for course content, please update answer keys in `tests/validate_content.py` and ensure all PASS.

## 📄 License & Privacy

This repository is published under the **MIT License** — free to use, modify, and distribute for any purpose (personal, educational, or commercial), provided the license notice is retained.

- ✅ You may view, study, modify, redistribute, and build commercial products upon it.
- ✅ No warranty is provided; use at your own risk.
- ™ "Mashang" / "码上" names and logos remain reserved trademarks.

Third-party components: [Chaquopy](https://github.com/chaquo/chaquopy) (MIT), Jetpack Compose (Apache-2.0), [Rhino](https://github.com/mozilla/rhino) (MPL-2.0), [sora-editor](https://github.com/Rosemoe/sora-editor) (LGPL-2.1).

**CI/CD**: [GitHub Actions](https://github.com/badhope/mashang/actions) — tests, lint, debug/release build, APK probe, signed release (mirrored to 3 GitHub repos) — is the only pipeline that actually runs and enforces gates. `.gitcode/workflows/ci.yml` is a config backup only: GitCode's code-based pipelines must be enabled manually and are not triggered by push (all recorded runs on 2026-10-24 were manual and skipped the Pages-sync/link-check steps).

📄 [Privacy Policy](PRIVACY_POLICY.md) · [Terms of Service](TERMS_OF_SERVICE.md)
