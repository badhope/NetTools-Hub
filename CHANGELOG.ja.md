# 変更履歴

**NetTools Hub** のすべての注目すべき変更は本ファイルに記録されています。

本ファイルは [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) の形式に準拠し、
本プロジェクトは [セマンティックバージョニング](https://semver.org/lang/ja/spec/v2.0.0.html) に準拠します。

> 🇯🇵 日本語 · 🇬🇧 [English](./CHANGELOG.md) · 🇨🇳 [简体中文](./CHANGELOG.zh.md)

---

## [未リリース]

### 計画中

- 検索履歴と保存済み検索（ブラウザ localStorage 使用）
- あいまい検索の"Did you mean..."提案
- 新規プロジェクト追加の RSS / Atom フィード
- 各言語ごとの CHANGELOG（i18n と同期）

---

## [0.3.0] – 2026-06-02

### 変更（UI ポリッシュ - 第 3 ラウンド）

- **トップナビのスリム化**：重複していた `Categories` ドロップダウンを削除し、最右のハンバーガードロワーのみ残しました。explore ページから `← Home` 枠線ボタンを削除。プライマリ CTA はランディングページでは `Explore`、explore ページでは `Home` に。
- **言語スイッチャーの書き直し**：3 つのインラインボタン（EN/中文/日本語）→ 単一の Globe アイコン + ドロップダウン（外部クリックで閉じる）。モバイルドロワー内でも下部にスイッチャーを配置し、ドロワー内で言語切替可能に。
- **サイドバーのスリム化**：`w-64` (256 px) → `w-[232px]`。底部の単一行 footer テキストを削除。
- **ランディングページ**：「21 の専門カテゴリ」グリッドを **6 テーマグループカード**（プロキシコア · 高速化 · デプロイと運用 · 設定と DNS · ツールとテスト · セキュリティ他）に置き換え。各カード内にサブカテゴリを一覧表示。カードのパディングを p-6 → p-7 に拡大。セクションコピーを「Browse by Group」に更新。
- **ランディング footer**：ロゴ + タイトル + タグライン + 免責事項、間隔を最適化。
- **i18n**：新しい 6 グループモデルに合わせて en/zh/ja 文字列を更新（「21 カテゴリ」→「6 テーマグループ」）。

---

## [0.2.0] – 2026-06-02

### 追加

- **トップナビコンポーネント** (`src/components/top-nav.tsx`)、ランディングと explore で共有。
- **カテゴリグループ** (`src/lib/category-groups.ts`)：6 つの論理クラスタ、合計 21 サブカテゴリ。
- 新しい i18n キー `group.*` および `nav.*`（en / zh / ja）。
- トップナビの**多段ドロップダウン**：デスクトップでホバー、モバイルでハンバーガーシート、外部クリックで閉じる、ARIA ラベル対応。

### 変更

- **プロジェクトリスト** をカテゴリクラスタごとに再構成、セクション間隔を拡大。
- **プロジェクトカード**：p-6 パディング、タグ 2 件 + `+N` オーバーフロー表示、左側のカラーボーダー、冗長な forks を削除、title/description に `line-clamp`、メタ行を区切り線で分離。

---

## [0.1.1] – 2026-06-02

### 修正

- `next.config.ts`：`trailingSlash: true` を有効化し、Next.js が `explore.html` ではなく `explore/index.html` を生成するように。サブパスのルーティングが GitHub Pages で正しく動作するように。
- CSS リソースを `/NetTools-Hub/_next/...` で正しく解決。

---

## [0.1.0] – 2026-06-01

### 追加

- 初回パブリックリリース。
- 21 カテゴリにわたる 120 以上の厳選ネットワークツールを `data/projects.json` に収録。
- ランディングページ（hero、特徴、カテゴリグリッド、CTA、footer）。
- 探索ページ（サイドバー、検索バー、ソートドロップダウン、プロジェクトグリッド）。
- 3 言語 UI：English / 中文 / 日本語。
- 完全レスポンシブ対応（デスクトップ、タブレット、モバイル）。
- `sitemap.xml` および `robots.txt`。
- GitHub Actions による GitHub Pages 自動デプロイ。
- ダークテーマ、GitHub 風デザイントークン。
- MIT ライセンス。

---

[未リリース]: https://github.com/badhope/NetTools-Hub/compare/d835693...HEAD
[0.3.0]: https://github.com/badhope/NetTools-Hub/compare/31dc5d0...d835693
[0.2.0]: https://github.com/badhope/NetTools-Hub/compare/6de3ca2...31dc5d0
[0.1.1]: https://github.com/badhope/NetTools-Hub/compare/f7e258b...6de3ca2
[0.1.0]: https://github.com/badhope/NetTools-Hub/releases/tag/3c58bc5
