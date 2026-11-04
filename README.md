<div align="center">

<img src="docs/banner.png" alt="Mashang" width="830"/>

**Write code on your phone. Six languages, really running, no network.**

[![License: MIT](https://img.shields.io/badge/License-MIT-00E5FF.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-7.0%2B-00E5FF.svg)]()
[![Languages](https://img.shields.io/badge/Languages-6-00FF9C.svg)]()
[![Download](https://img.shields.io/badge/Download-APK-FF2D78.svg)](https://github.com/badhope/mashang/releases/latest)

🌐 [English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja-JP.md)

</div>

---

## Screens

| Home | Lessons | Judging |
|:--:|:--:|:--:|
| ![Home](demo/app/home.png) | ![Lessons](demo/app/lessons.png) | ![Judge](demo/app/judge_pass.png) |

| Editor | Terminal | Language Center |
|:--:|:--:|:--:|
| ![Editor](demo/app/lesson_exercise.png) | ![Terminal](demo/app/terminal.png) | ![Language Center](demo/app/contenthub.png) |

---

## Six languages, real errors

| Language | Runtime | Lessons |
|---|---|---|
| **Python** | CPython 3.13 | 38 + DSA + builtins |
| **JavaScript** | Rhino 1.7.15 | 6 |
| **TypeScript** | type erasure → Rhino | 6 |
| **C** | built-in interpreter | 6 |
| **Lua** | LuaJ 3.0.1 | 6 |
| **SQL** | SQLite | 6 |

The Python mainline ships in the APK. The other five download on demand from the Language Center. First install ~39 MB.

C and TypeScript are teaching subsets (C has no pointers/structs; TypeScript has no decorators/namespaces) and say so explicitly.

---

## Install

- **Just install**: grab `mashang-*.apk` from [GitHub Releases](https://github.com/badhope/mashang/releases/latest)
- Android 7.0+, arm64-v8a

Build from source:

```bash
./gradlew :app:assembleDebug
```

---

## License

MIT. Third-party licenses are listed in-app under About → Open Source Licenses.

📄 [Privacy](PRIVACY_POLICY.md) · [Terms](TERMS_OF_SERVICE.md)

---

<sub>Mirrors: [GitHub](https://github.com/badhope/mashang) · [GitCode](https://gitcode.com/badhope/mashang) · [Gitee](https://gitee.com/badhope/mashang)</sub>
