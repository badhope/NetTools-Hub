<div align="center">

<img src="docs/banner.png" alt="Mashang · 码上" width="830"/>

**コードを書け、すぐに。6 言語の本物のランタイム、完全オフライン。**

ポケットに入るプログラミング学習端末：**6 言語が実際に実行**（Python / JavaScript / TypeScript / C / Lua / SQL）、
79 講のレッスン、assert 自動採点、過程の可視化、サイバーパンク／シンプルの 2 スタイル。

[![CI](https://img.shields.io/github/actions/workflow/status/badhope/mashang/ci.yml?branch=main&label=CI)](https://github.com/badhope/mashang/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-00E5FF.svg)](LICENSE)
[![Android](https://img.shields.io/badge/Android-7.0%2B-00E5FF.svg)]()
[![Languages](https://img.shields.io/badge/Languages-6-00FF9C.svg)](#6-言語すべてが実際に実行される)
[![Offline](https://img.shields.io/badge/Offline-100%25-FF2D78.svg)]()
[![Download](https://img.shields.io/badge/%F0%9F%8C%90-Download-FF2D78.svg)](https://badhope.github.io/mashang/)

🌐 [English](README.md) | [中文](README.zh-CN.md) | [日本語](README.ja-JP.md)

</div>

---

## 6 言語、すべてが実際に実行される

シンタックスハイライトでも、擬似出力でもありません。各言語に本物のランタイムがあり、
間違えれば本物のエラーが出て、正しければ本物のテストに通ります。

| 言語 | ランタイム | 学べること | レッスン |
|---|---|---|---|
| **Python** | 内蔵 CPython 3.13 | print から非同期コルーチン、デコレータ、正規表現、型ヒント | 38 講メインライン + DSA + 組み込み関数 |
| **JavaScript** | Rhino 1.7.15 | console.log、Math、文字列、分岐、配列、オブジェクト | 6 講スターター |
| **TypeScript** | 型消去 + Rhino | 型注釈、interface、ジェネリクス、ユニオン型、enum | 6 講スターター |
| **C** | 内蔵インタプリタ（NDK 不要） | printf、型、ループ、配列、再帰、言語の境界 | 6 講スターター |
| **Lua** | LuaJ 3.0.1 | local、テーブル、多値返却、string ライブラリ | 6 講スターター |
| **SQL** | SQLite インメモリ | SELECT、JOIN、集計、サブクエリ、NULL | 6 講スターター |

**内蔵とオンデマンド**：Python メインラインは APK に内蔵され、すぐ学べます。残り 5 言語は
「言語センター」からダウンロードし、完了後にレッスン一覧へ表示——初回インストールは軽いまま（約 39 MB）。

**正直な限界**：C と TypeScript は学習用サブセットであり、gcc / tsc ではありません。C はポインタ・
構造体・プリプロセッサ非対応、TypeScript はデコレータ・名前空間非対応です。いずれも黙って誤答せず、
明確に「非対応」と表示します。Java / C++ / Go / Rust はコンパイラツールチェーンが必要で
オフライン同梱できないため、言語センターで「未対応」と表示します。

---

## なぜ Mashang か

| | 他製品 | Mashang |
|---|---|---|
| 実行 | ☁️ クラウド、オフラインで停止 | 📱 **端末上の本物のランタイム** |
| 教材 | 無味乾燥な文書 | 日常的な比喩 + ASCII 図解 + 随所のクイズ |
| 実行結果 | print 出力のみ | **変数スナップショット** + フレーム単位の可視化 |
| 多言語 | 個別に分断 | **単一の採点契約 + 並列比較** |
| 動機付け | チェックインカレンダー | XP / 6 段階 / デイリータスク / 実績ウォール |

---

## 学習ループ

```
書く → 実行 → assert 採点 → 失敗時はコーチ → 合格で次へ
```

- **assert 自動採点** —— テストに通るまで先へ進めない
- **オフライン L0 コーチ** —— エラーを診断し「3 ステップの導き + 最小修正例」を提示。ヒントのみで答えは書かない
- **間違いノート + 間隔反復** —— 誤答を自動収集、SM-2 スケジューリング（1 日 → 6 日 → 適応）
- **4 種類の演習** —— 穴埋め、コード整序、ミニクイズ、実践採点

---

## 過程の可視化

変数がどう変わるか、ループがどう回るか、再帰スタックがどう伸びるか——
文章では伝わりにくいものが、フレーム単位で見れば一目で分かります。

```
1+2+3+4+5 を合計：
[開始]   i=—   sum=0
[1 回目] i=1   sum=1    ← 変化した値がハイライト
[2 回目] i=2   sum=3
...
[終了]   i=6   sum=15
```

単步送り・自動再生・リセットに対応。さらに**言語の並列比較**：同じループや同じ関数を
4 言語で並べ、各列をその場で実行して出力を比較できます。

---

## 見た目は選べる

サイバーパンクは既定の個性であり、唯一の選択肢ではありません。

- **2 スタイル** —— サイバー（グリッチ文字／スキャンライン／ネオン枠／切り欠きカード）とシンプル（静的組版／細枠／角丸カード）。設定 → 外観スタイルで切替
- **7 配色** —— サイバーネオン / ディープスペース / オーロラグリーン / トワイライトパープル / トワイライトオレンジ / ソフトアイケア / ペーパーホワイト、および任意のアクセント色
- **4 段階の文字サイズ** —— コンパクト / 標準 / 快適 / 大。講座本文のみ拡大し、コードブロックはサイズ維持でインデント崩れを防ぐ
- 配色・スタイル・文字サイズは**独立**しており、自由に組み合わせ可能

---

## アーキテクチャ

```
Kotlin + Jetpack Compose
        │  LanguageRuntime 契約（JSON ペイロード）
PyBridge(Chaquopy) ──► CPython 3.13
JsBridge(Rhino)    ──► JavaScript
TsBridge           ──► 型消去後に Rhino を再利用
CBridge            ──► 学習用サブセットインタプリタ（純 Kotlin）
LuaBridge(LuaJ)    ──► Lua（io/os/require なし）
SqlBridge(sqlite3) ──► SQL（インメモリ、ATTACH 拒否）
```

**単一の真実源**：`runner.py` が唯一の採点エンジンです。Android は Chaquopy、Web は Pyodide で
同一ソースを実行し、テストでバイト単位の一致を検証しています。言語追加は `LanguageRuntime` を
実装して登録するだけで、UI コードの変更は不要です。

**サンドボックスは言語ごとに独立**：Python は `settrace` ウォッチドッグ、JS/TS は `ClassShutter` で
Java クラスを全拒否、C はポインタ・構造体なし、Lua は `io`/`os` 非搭載、SQL は `:memory:` 固定。
これは学習用サンドボックスであり、セキュリティコンテナではありません——[SECURITY.md](SECURITY.md) 参照。

---

## インストール

- Android 7.0+（minSdk 24）、arm64-v8a
- ダウンロード：[GitHub Releases](https://github.com/badhope/mashang/releases/latest) · [ダウンロードページ](https://badhope.github.io/mashang/)
- ソースからビルド：

```bash
./gradlew :app:assembleDebug        # Debug APK
./gradlew :app:assembleRelease      # KEYSTORE_PATH など 4 つの環境変数が必要
python -m unittest discover -s tests  # 207 件のテスト
python tests/validate_content.py     # 79 講すべてを検証
```

---

## 品質ゲート

| ゲート | コマンド | 証明する内容 |
|---|---|---|
| エンジン + コンテンツ | `python -m unittest discover -s tests` | 207 件：サンドボックス、タイムアウト、採点、並行性、構造、文書の主張 |
| 講義 × 解答 | `python tests/validate_content.py` | 全言語の模範解答がエンドツーエンドで通る |
| 実実行 | 言語別スイート | Python/JS/TS/Lua/SQL/C を実際に実行して検証 |
| Android | `./gradlew :app:lintDebug :app:testDebugUnitTest` | lint エラー 0 + JVM ユニットテスト |
| APK プローブ | `python tests/ci_apk_probe.py <apk>` | APK 内にエンジン・アセット・6 言語の文法が揃っている |

---

## カリキュラム

**Python メインライン — 38 講・5 幕**

<details>
<summary><b>第 1 幕 · 基礎</b></summary>

`01 最初の接触` · `02 変数と型` · `03 文字列操作` · `04 数値演算` · `05 入力シグナル` · `06 条件分岐` · `07 ループエンジン` · `08 リスト倉庫` · `09 辞書キーボールト` · `10 基礎編卒業`

</details>

<details>
<summary><b>第 2 幕 · 装備強化</b></summary>

`11 文字列ツールボックス` · `12 タプルとセット` · `13 関数の進化` · `14 内包表記の嵐` · `15 例外シールド` · `16 データ永続化` · `17 モジュール召喚` · `18 クラスの覚醒`

</details>

<details>
<summary><b>第 3 幕 · 高度な義体</b></summary>

`19 継承と特殊メソッド` · `20 総合課題・サイバーバンク` · `21 ジェネレータ` · `22 デコレータ` · `23 ラムダ三銃士` · `24 標準ライブラリ実践` · `25 時間と乱数` · `26 総合課題・ログ解析`

</details>

<details>
<summary><b>第 4 幕 · 境界の先へ</b></summary>

`27 コンテキストマネージャ` · `28 ファイル入出力` · `29 独自例外` · `30 モジュールと __main__`

</details>

<details>
<summary><b>第 5 幕 · 実務</b></summary>

`31 正規表現` · `32 型ヒントとデータクラス` · `33 関数型ツールボックス` · `34 並行処理入門` · `35 非同期コルーチン` · `36 CLI ツール` · `37 デバッグとテスト` · `38 仮想環境とエンジニアリング`

</details>

**言語パック**：JavaScript / TypeScript / C / Lua / SQL 各 6 講 · DSA 基礎／応用 各 5 講 · 組み込み関数巡り 1 講 · アリーナ 8 チャレンジ

---

## 対象読者

| あなたは | 得られるもの |
|---|---|
| 初心者・転職希望者 | 38 講の物語仕立てレッスン、print からデコレータまで |
| 複数言語を学びたい人 | 6 言語を単一の採点・成長システムで、横並び比較も可能 |
| 通勤時間で学ぶ人 | 完全オフライン——地下鉄のトンネルでもコードが動く |
| 教師・保護者 | 広告なし、アカウント不要、データ送信ゼロ |
| 開発者 | Compose + 6 ランタイムの完全なリファレンス実装、MIT ライセンス |

---

## ロードマップ

- [x] v0.5 多言語拡張：Lua + SQL ランタイム、言語センター
- [x] v0.6 6 言語：TypeScript + C、2 スタイル、4 段階文字サイズ、過程の可視化、言語比較
- [ ] v0.7 タートルキャンバス · matplotlib 出力 · タブレット対応
- [ ] v1.0 各ストアでのリリース

**意図的にやらないこと**：クラウド実行（オフライン方針と矛盾）、アカウント体系（データ収集を招く）、有料コンテンツ（MIT ライセンス）。

---

## コントリビューション

Fork → ブランチ作成 → PR。講義を変更した場合は `tests/validate_content.py` の模範解答も
更新し、すべて PASS することを確認してください。

## ライセンス

**MIT** —— 商用を含め自由に使用・改変・再配布できます。ライセンス表示を保持してください。
「码上」/「Mashang」の名称は商標として留保されます。

サードパーティ：[Chaquopy](https://github.com/chaquo/chaquopy) (MIT) · [Rhino](https://github.com/mozilla/rhino) (MPL-2.0) · [sora-editor](https://github.com/Rosemoe/sora-editor) (LGPL-2.1) · Compose (Apache-2.0) · LuaJ (MIT)

📄 [プライバシー](PRIVACY_POLICY.md) · [利用規約](TERMS_OF_SERVICE.md) · [セキュリティ](SECURITY.md)

---

## ミラーと配布

ソースは [GitHub/badhope](https://github.com/badhope/mashang) · [GitCode](https://gitcode.com/badhope/mashang) · [Gitee](https://gitee.com/badhope/mashang) · [GitHub/x33834](https://github.com/x33834/mashang) · [GitHub/Morningstar202604](https://github.com/Morningstar202604/mashang) に同期しています。

> CI とリリースゲートは GitHub Actions でのみ実行されます。GitCode のコードパイプラインは手動で有効化が必要で、push では自動実行されません。
