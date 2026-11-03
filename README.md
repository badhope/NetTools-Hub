<div align="center">

<img src="docs/banner.png" alt="Mashang · 码上" width="830"/>

**Code now, master any language. Six real runtimes, fully offline.**

A coding learning terminal that fits in your pocket: **six languages actually execute**
(Python / JavaScript / TypeScript / C / Lua / SQL), 79 lessons, assert-based grading,
step-through visualizations, and a choice of cyberpunk or minimal UI.

[![CI](https://img.shields.io/github/actions/workflow/status/badhope/mashang/ci.yml?branch=main&label=CI)](https://github.com/badhope/mashang/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-00E5FF.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-7.0%2B-00E5FF.svg)]()
[![Languages](https://img.shields.io/badge/Languages-6-00FF9C.svg)](#six-languages-all-genuinely-executed)
[![Offline](https://img.shields.io/badge/Offline-100%25-FF2D78.svg)]()
[![Download](https://img.shields.io/badge/%F0%9F%8C%90-Download-FF2D78.svg)](https://badhope.github.io/mashang/)

🌐 [English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja-JP.md)

</div>

---

## Six languages, all genuinely executed

Not syntax highlighting. Not simulated output. Every language has a real runtime —
mistakes raise real errors, correct code passes real tests.

| Language | Runtime | What you learn | Lessons |
|---|---|---|---|
| **Python** | Embedded CPython 3.13 | print through async coroutines, decorators, regex, type hints | 38-lesson mainline + DSA + builtins |
| **JavaScript** | Rhino 1.7.15 | console.log, Math, strings, branching, arrays, objects | 6-lesson starter |
| **TypeScript** | Type erasure + Rhino | annotations, interface, generics, unions, enum | 6-lesson starter |
| **C** | Built-in interpreter (no NDK) | printf, types, loops, arrays, recursion, language limits | 6-lesson starter |
| **Lua** | LuaJ 3.0.1 | local, tables, multiple returns, string library | 6-lesson starter |
| **SQL** | SQLite in-memory | SELECT, JOIN, aggregates, subqueries, NULL | 6-lesson starter |

**Built-in vs on-demand**: the Python mainline ships inside the APK. The other five download
from the Language Center and only then appear in the lesson list — first install stays lean (~39 MB).

**Honest limits**: C and TypeScript are teaching subsets, not gcc / tsc. C omits pointers,
structs and the preprocessor; TypeScript omits decorators and namespaces. Both say so
explicitly rather than returning wrong answers. Java / C++ / Go / Rust need compiler
toolchains and can't ship offline — the Language Center marks them unsupported.

---

## Why Mashang

| | Others | Mashang |
|---|---|---|
| Execution | ☁️ Cloud, dies offline | 📱 **Real runtimes on device** |
| Teaching | Dry docs | Everyday analogies + ASCII diagrams + inline quizzes |
| Feedback | Plain print output | **Variable snapshots** + frame-by-frame visualizations |
| Multi-language | Separate silos | **One grading contract + side-by-side comparison** |
| Motivation | Check-in calendar | XP / six tiers / daily quests / achievement wall |

---

## The learning loop

```
write → run → assert → coach on failure → advance on pass
```

- **Assert-based grading** — you don't pass until the tests pass
- **Offline L0 coach** — diagnoses the error, gives three guided steps plus a minimal fix example; hints only, never writes the answer
- **Mistake book + spaced repetition** — wrong answers auto-collected, SM-2 scheduling (1 day → 6 days → adaptive)
- **Four exercise types** — fill-in-the-blank, code ordering, inline quiz, hands-on grading

---

## Process visualization

How a variable changes, how a loop turns, how a recursion stack grows —
things prose explains poorly become obvious frame by frame.

```
Summing 1+2+3+4+5:
[start]  i=—   sum=0
[round1] i=1   sum=1    ← changed value highlighted
[round2] i=2   sum=3
...
[end]    i=6   sum=15
```

Single-step, autoplay, reset. Plus **side-by-side language comparison**: the same loop or
the same function written in four languages, each column runnable for instant output diffing.

---

## Appearance, not one taste

Cyberpunk is the default personality, not the only option.

- **Light by default** — ships with Paper White for comfortable long-form reading; the six dark palettes are one tap away
- **Two styles** — Cyber (glitch text / scanlines / neon borders / cut corners) and Minimal (static type / hairline borders / rounded cards). Switch in Settings → Appearance.
- **Seven palettes** — Cyber Neon / Deep Space / Aurora Green / Twilight Purple / Sunset Orange / Soft Eye-Care / Paper White, plus custom accent color
- **Four font sizes** — Compact / Normal / Comfortable / Large. Scales lesson prose only; code blocks keep their size so indentation stays aligned
- Palette, style and font size are **independent** — combine freely

---

## When something goes wrong

An offline app has no server logs. **Settings → Developer Diagnostics** surfaces the environment,
all six runtime states, installed content packs and the runtime log, with copy and export buttons.

Logs stay on device, are never uploaded, and never contain your code — only event types and error summaries.

---

## Architecture

```
Kotlin + Jetpack Compose
        │  LanguageRuntime contract (JSON payload)
PyBridge(Chaquopy) ──► CPython 3.13
JsBridge(Rhino)    ──► JavaScript
TsBridge           ──► type erasure, reuses Rhino
CBridge            ──► teaching-subset interpreter (pure Kotlin)
LuaBridge(LuaJ)    ──► Lua (no io/os/require)
SqlBridge(sqlite3) ──► SQL (in-memory, ATTACH denied)
```

**Single source of truth**: `runner.py` is the only grading engine. Android runs it via Chaquopy,
the web client via Pyodide — the same source, byte-for-byte verified in tests. Adding a language
means implementing `LanguageRuntime` and registering it; UI code doesn't change.

**Separate sandboxes**: Python uses a `settrace` watchdog; JS/TS deny all Java classes via
`ClassShutter`; C has no pointers or structs; Lua omits `io`/`os`; SQL stays on `:memory:`.
This is a learning sandbox, not a security container — see [SECURITY.md](SECURITY.md).

---

## Install

- Android 7.0+ (minSdk 24), arm64-v8a
- Download: [GitHub Releases](https://github.com/badhope/mashang/releases/latest) · [Download page](https://badhope.github.io/mashang/)
- Build from source:

```bash
./gradlew :app:assembleDebug        # Debug APK
./gradlew :app:assembleRelease      # needs KEYSTORE_PATH and 3 more env vars
python -m unittest discover -s tests  # full unit suite
python tests/validate_content.py     # validates all 79 lessons
bash scripts/ci/check_all.sh         # one-shot gate (11 checks)
```

---

## Quality gates

| Gate | Command | What it proves |
|---|---|---|
| One-shot | `bash scripts/ci/check_all.sh` | 11 gates in sequence, failures summarised at the end |
| Engine + content | `python -m unittest discover -s tests` | sandbox, timeouts, grading, concurrency, content structure, doc claims |
| Lessons × answers | `python tests/validate_content.py` | Every language's reference answers pass end-to-end |
| Real execution | per-language suites | Python/JS/TS/Lua/SQL/C all verified by actually running code |
| Android | `./gradlew :app:lintDebug :app:testDebugUnitTest` | 0 lint errors + JVM unit tests |
| APK probe | `python tests/ci_apk_probe.py <apk>` | Engine, assets and all six grammars present inside the APK |

---

## Curriculum

**Python mainline — 38 lessons, 5 acts**

<details>
<summary><b>Act I · Foundations</b></summary>

`01 First Contact` · `02 Variables & Types` · `03 String Operations` · `04 Numeric Protocols` · `05 Input Signals` · `06 Condition Matrix` · `07 Loop Engine` · `08 List Warehouse` · `09 Dict Keyvault` · `10 Foundations Graduation`

</details>

<details>
<summary><b>Act II · Upgrades</b></summary>

`11 String Toolkit` · `12 Tuples & Sets` · `13 Function Evolution` · `14 Comprehension Storm` · `15 Exception Shield` · `16 Data Persistence` · `17 Module Summoning` · `18 Classes Awaken`

</details>

<details>
<summary><b>Act III · Advanced Cyberware</b></summary>

`19 Inheritance & Dunders` · `20 Capstone: Cyber Bank` · `21 Generator Engine` · `22 Decorator Armor` · `23 Lambda Trio` · `24 Stdlib in Action` · `25 Time & Random` · `26 Capstone: Log Analyzer`

</details>

<details>
<summary><b>Act IV · Beyond the Edge</b></summary>

`27 Context Managers` · `28 File I/O Protocols` · `29 Custom Exceptions` · `30 Modules & __main__`

</details>

<details>
<summary><b>Act V · Production</b></summary>

`31 Regex` · `32 Type Hints & Dataclasses` · `33 Functional Toolbox` · `34 Concurrency Intro` · `35 Async Coroutines` · `36 CLI Tooling` · `37 Debugging & Testing` · `38 Virtualenv & Engineering`

</details>

**Language packs**: JavaScript / TypeScript / C / Lua / SQL, 6 lessons each · DSA basics & advanced, 5 each · Builtin Tour, 1 · Arena, 8 challenges

---

## Who it's for

| You are | You get |
|---|---|
| A beginner or career switcher | 38 narrative lessons, from print to decorators |
| Someone learning several languages | Six languages under one grading and progression system, comparable side by side |
| A commuter learner | Fully offline — code runs in the subway tunnel |
| A teacher or parent | No ads, no account, zero data upload |
| A developer | A complete Compose + six-runtime reference implementation, MIT licensed |

---

## Roadmap

- [x] v0.5 Multi-language: Lua + SQL runtimes, Language Center
- [x] v0.6 Six languages: TypeScript + C, dual styles, four font sizes, process visualization, language comparison
- [ ] v0.7 Turtle canvas · matplotlib output · tablet layout
- [ ] v1.0 Store rollout

**Deliberately out of scope**: cloud execution (conflicts with offline-first), accounts (invites data collection), paid content (MIT licensed).

---

## Contributing

Fork → branch → PR. For lesson changes, update the reference answers in
`tests/validate_content.py` and make sure everything passes.

## License

**MIT** — free to use, modify and redistribute, including commercially; just keep the notice.
"码上" / "Mashang" names are reserved trademarks.

Third-party: [Chaquopy](https://github.com/chaquo/chaquopy) (MIT) · [Rhino](https://github.com/mozilla/rhino) (MPL-2.0) · [sora-editor](https://github.com/Rosemoe/sora-editor) (LGPL-2.1) · Compose (Apache-2.0) · LuaJ (MIT)

📄 [Privacy](PRIVACY_POLICY.md) · [Terms](TERMS_OF_SERVICE.md) · [Security](SECURITY.md)

---

## Mirrors & distribution

Source is mirrored to [GitHub/badhope](https://github.com/badhope/mashang) · [GitCode](https://gitcode.com/badhope/mashang) · [Gitee](https://gitee.com/badhope/mashang) · [GitHub/x33834](https://github.com/x33834/mashang) · [GitHub/Morningstar202604](https://github.com/Morningstar202604/mashang).

> CI and release gates run only on GitHub Actions; GitCode's code pipeline must be enabled manually and does not trigger on push.
