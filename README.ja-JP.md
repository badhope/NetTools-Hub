<div align="center">

<img src="docs/banner.png" alt="Mashang" width="830"/>

**スマホでコードを書く。6 言語が本当に動く。ネット不要。**

[![License: MIT](https://img.shields.io/badge/License-MIT-00E5FF.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-7.0%2B-00E5FF.svg)]()
[![Languages](https://img.shields.io/badge/Languages-6-00FF9C.svg)]()
[![Download](https://img.shields.io/badge/Download-APK-FF2D78.svg)](https://github.com/badhope/mashang/releases/latest)

🌐 [English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja-JP.md)

</div>

---

## スクリーンショット

| ホーム | レッスン | 採点 |
|:--:|:--:|:--:|
| ![ホーム](demo/app/home.png) | ![レッスン](demo/app/lessons.png) | ![採点](demo/app/judge_pass.png) |

| エディタ | ターミナル | 言語センター |
|:--:|:--:|:--:|
| ![エディタ](demo/app/lesson_exercise.png) | ![ターミナル](demo/app/terminal.png) | ![言語センター](demo/app/contenthub.png) |

---

## 6 言語、間違えれば本物のエラー

| 言語 | ランタイム | レッスン |
|---|---|---|
| **Python** | CPython 3.13 | 38 + DSA + 組み込み関数 |
| **JavaScript** | Rhino 1.7.15 | 6 |
| **TypeScript** | 型消去 → Rhino | 6 |
| **C** | 内蔵インタプリタ | 6 |
| **Lua** | LuaJ 3.0.1 | 6 |
| **SQL** | SQLite | 6 |

Python メインラインは APK に内蔵。残り 5 言語は「言語センター」からオンデマンドでダウンロード。初回インストール約 39 MB。

C と TypeScript は学習用サブセットです（C はポインタ・構造体なし、TypeScript はデコレータ・名前空間なし）。非対応時は明示します。

---

## インストール

- **すぐ使う**：[GitHub Releases](https://github.com/badhope/mashang/releases/latest) から `mashang-*.apk` を取得
- Android 7.0+、arm64-v8a

ソースからビルド：

```bash
./gradlew :app:assembleDebug
```

---

## ライセンス

MIT。サードパーティのライセンスはアプリ内「About → オープンソースライセンス」に記載。

📄 [プライバシー](PRIVACY_POLICY.md) · [利用規約](TERMS_OF_SERVICE.md)

---

<sub>ミラー：[GitHub](https://github.com/badhope/mashang) · [GitCode](https://gitcode.com/badhope/mashang) · [Gitee](https://gitee.com/badhope/mashang)</sub>
