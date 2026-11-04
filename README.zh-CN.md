<div align="center">

<img src="docs/banner.png" alt="码上 · Mashang" width="830"/>

**手机上写代码，六种语言真跑，不用联网。**

[![License: MIT](https://img.shields.io/badge/License-MIT-00E5FF.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-7.0%2B-00E5FF.svg)]()
[![Languages](https://img.shields.io/badge/Languages-6-00FF9C.svg)]()
[![Download](https://img.shields.io/badge/Download-APK-FF2D78.svg)](https://github.com/badhope/mashang/releases/latest)

🌐 [English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja-JP.md)

</div>

---

## 界面

| 首页 | 课程 | 判题 |
|:--:|:--:|:--:|
| ![首页](demo/app/home.png) | ![课程](demo/app/lessons.png) | ![判题](demo/app/judge_pass.png) |

| 练习编辑器 | 终端 | 语言中心 |
|:--:|:--:|:--:|
| ![练习](demo/app/lesson_exercise.png) | ![终端](demo/app/terminal.png) | ![语言中心](demo/app/contenthub.png) |

---

## 六门语言，写错会报错

| 语言 | 运行时 | 课程 |
|---|---|---|
| **Python** | CPython 3.13 | 38 讲 + DSA + 内置函数 |
| **JavaScript** | Rhino 1.7.15 | 6 讲 |
| **TypeScript** | 类型擦除 → Rhino | 6 讲 |
| **C** | 内置解释器 | 6 讲 |
| **Lua** | LuaJ 3.0.1 | 6 讲 |
| **SQL** | SQLite | 6 讲 |

Python 主线随 APK 内置；其余五门从「语言中心」按需下载。首装约 39 MB。

C 和 TypeScript 是教学子集（C 无指针/结构体，TS 无装饰器/命名空间），遇到会明确提示。

---

## 安装

- **直接装**：[GitHub Releases](https://github.com/badhope/mashang/releases/latest) 下载 `mashang-*.apk`
- Android 7.0+，arm64-v8a

从源码构建：

```bash
./gradlew :app:assembleDebug
```

---

## 许可

MIT。第三方组件许可见应用内「关于 → 开源许可」。

📄 [隐私政策](PRIVACY_POLICY.md) · [用户协议](TERMS_OF_SERVICE.md)

---

<sub>源码镜像：[GitHub](https://github.com/badhope/mashang) · [GitCode](https://gitcode.com/badhope/mashang) · [Gitee](https://gitee.com/badhope/mashang)</sub>
