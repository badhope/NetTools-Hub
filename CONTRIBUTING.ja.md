# 貢献ガイド · Contributing to NetTools Hub

> **言語 / Language:** [🇬🇧 English](CONTRIBUTING.md) · [🇨🇳 简体中文](CONTRIBUTING.zh.md) · **🇯🇵 日本語**

はじめに、貢献するために時間を割いていただきありがとうございます！🎉
**NetTools Hub** は、活発にメンテナンスされているオープンソースのネットワークツールをコミュニティで集約・ナビゲートするプラットフォームです。誤字の修正から新しいプロジェクトの追加まで、すべての貢献がこのプロジェクトをより良いものにします。

このドキュメントでは、高品質な Pull Request (PR) や Issue を提出するために必要な情報をすべて説明します。

---

## 📑 目次

- [行動規範](#-行動規範)
- [何に貢献できる？](#-何に貢献できる)
- [バグ報告](#-バグ報告)
- [新しいツール / 機能の提案](#-新しいツール--機能の提案)
- [ローカル開発環境のセットアップ](#-ローカル開発環境のセットアップ)
- [プロジェクト構成](#-プロジェクト構成)
- [プロジェクトエントリの追加・更新](#-プロジェクトエントリの追加更新)
- [コードスタイル](#-コードスタイル)
- [コミットメッセージ規約](#-コミットメッセージ規約)
- [Pull Request の流れ](#-pull-request-の流れ)
- [ローカライゼーション (i18n)](#-ローカライゼーション-i18n)
- [サポートが必要なときは？](#-サポートが必要なときは)

---

## 🤝 行動規範

本プロジェクトおよびすべての参加者は [Contributor Covenant v2.1](CODE_OF_CONDUCT.md) に従います。
参加することは、この規範を順守することに同意したとみなされます。許容できない行為があった場合は GitHub Issue でご報告ください。

---

## 🧩 何に貢献できる？

- `data/projects.json` への**新規ツールエントリの追加**
- **古いデータの更新**（リンク切れ、スター数の陳腐化、廃止されたプロジェクトなど）
- **三言語 UI の翻訳改善**（English / 中文 / 日本語）
- **バグ修正**（レイアウト、検索、ソート、言語切替など）
- **パフォーマンス / アクセシビリティの改善**
- **ドキュメント**（誤字修正、README の説明改善など）

---

## 🐛 バグ報告

バグを報告する前に以下を確認してください：

1. **既存の Issue を検索** し、重複を避ける。
2. 最新の `main` ブランチで再現するか確認する —— すでに修正されている可能性があります。
3. 診断情報を収集する：ブラウザのバージョン、OS、デバイス、スクリーンショット、コンソールエラー。

以下の情報を添えて <https://github.com/badhope/NetTools-Hub/issues/new> から Issue を作成してください：

- 明確で説明的なタイトル
- 再現手順（番号付き）
- 期待される動作 vs. 実際の動作
- スクリーンショット / 画面録画
- コンソール / ネットワークログ（個人情報は必ずマスキングしてください）

---

## 💡 新しいツール / 機能の提案

新規プロジェクトエントリには **「Project submission」** テンプレートを使用してください（または以下のフィールドを含めてください）。プロジェクトの活動状況と品質を確認するためです：

- **リポジトリ URL**（GitHub のみ）
- **プロジェクト名** と 1 行の説明
- **主な言語 / フレームワーク**
- **ライセンス**（OSI 承認済みであること：例 MIT / Apache-2.0 / GPL / BSD）
- **スター数** と **直近のコミット日**（改めて確認します）
- **カテゴリ** — `data/projects.json` 内の 21 のサブカテゴリ（6 つのテーマグループ配下）から選択してください。新規提案には根拠が必要です。全リストは [README → 📑 6 テーマグループ](../../#-the-6-themed-groups-21-sub-categories) を参照。
- **なぜリストに値するか** — そのプロジェクトが何を特徴とするかを 1〜2 文で

> 収録基準：過去 6 か月以内にコミットがある、放棄されていない、現実的なネットワーク上の課題を解決する、そして既存の収録にないギャップを埋めることが望ましい。

機能リクエストには **「Feature request」** ラベルを使い、ユーザー価値、提案する UX、検討した代替案を記述してください。

---

## 🛠 ローカル開発環境のセットアップ

### 前提条件

- **Node.js** `>= 22.0.0`（`.nvmrc` 参照）
- **pnpm** `>= 10.0.0`（`.npmrc` 参照）
- モダンなブラウザ（Chrome / Firefox / Safari / Edge の最新 2 バージョン）

### 手順

```bash
# 1. リポジトリをフォークしてクローン
git clone https://github.com/<あなたのユーザー名>/NetTools-Hub.git
cd NetTools-Hub

# 2. 依存関係をインストール
pnpm install --frozen-lockfile

# 3. 開発サーバーを起動（ポート 8080）
pnpm dev

# 4. http://localhost:8080 を開く
```

### 利用可能なスクリプト

| コマンド | 説明 |
| --- | --- |
| `pnpm dev` | ポート 8080 でローカル開発サーバーを起動 |
| `pnpm build` | `./out` ディレクトリに静的エクスポートを生成 |
| `pnpm start` | ビルド済みの `./out` をポート 8080 で配信 |
| `pnpm lint` | Next.js + TypeScript ルールで ESLint を実行 |

> **注意**：このプロジェクトは GitHub Pages へ静的デプロイするため `output: "export"` を使用しています。開発サーバーは通常通り動作し、本番ビルドのみ完全静的です。

---

## 🗂 プロジェクト構成

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Pages CI/CD
├── data/
│   └── projects.json           # 210 のプロジェクト、21 サブカテゴリ（6 テーマグループ）
├── src/
│   ├── app/
│   │   ├── explore/            # /explore — 絞り込み / 並び替え可能なリスト
│   │   ├── error.tsx           # グローバルエラーバウンダリ
│   │   ├── layout.tsx          # ルートレイアウト
│   │   ├── not-found.tsx       # 404 ページ
│   │   ├── page.tsx            # / — ランディングページ
│   │   ├── robots.ts           # robots.txt
│   │   └── sitemap.ts          # sitemap.xml
│   ├── components/             # UI プリミティブ
│   ├── lib/                    # i18n、データアクセス、ユーティリティ
│   └── types/                  # TypeScript 型
├── public/                     # （任意）静的アセット
├── LICENSE                     # MIT
├── README.md                   # 三言語ドキュメント
├── next.config.ts              # `output: "export"`
├── package.json
├── pnpm-lock.yaml
├── postcss.config.mjs          # Tailwind v4
└── tsconfig.json
```

---

## 📝 プロジェクトエントリの追加・更新

すべてのデータは **`data/projects.json`** に集約されています。スキーマは `src/types/project.ts` によって強制されます。

### スキーマ (TypeScript)

```ts
interface Project {
  id: string;              // URL セーフなスラッグ（例 "sing-box"）
  name: string;            // 表示名（例 "sing-box"）
  author: string;          // 著者または組織名（例 "SagerNet"）
  description: string;     // 1 行の説明（英語）
  url: string;             // 公式ホームページまたはリポジトリ URL
  homepage?: string;       // オプションのプロジェクトホームページ（GitHub 以外）
  
  // メトリクス（scripts/refresh-projects.mjs によって自動更新）
  stars: number;           // GitHub スター数
  forks: number;           // GitHub フォーク数
  language: string;        // 主要言語（例 "Go"）
  license: string;         // SPDX 識別子（例 "MIT"）
  
  // 分類軸
  kind: ProjectKind;       // "proxy" | "vpn" | "dns" | "acceleration" | "security" | "monitoring" | "ops" | "tools"
  platform: ProjectPlatform[];  // "desktop" | "mobile" | "cli" | "server" | "browser" | "router"
  category: string;        // 編集分類（例 "proxy-core"）
  tags: string[];          // 自由形式、小文字、ハイフン区切り
  
  // 編集内容
  notes?: string;          // オプションのメンテナーメモ
  verdict?: ProjectVerdict; // "recommended" | "neutral" | "caution" | "avoid"
  
  // ライフサイクル
  lastCommit: string;      // ISO 8601 日付（例 "2026-05-01"）
  addedAt: string;         // 初回追加日
  status: ProjectStatus;   // "active" | "stale" | "archived"
  
  // ビジュアル
  highlights: string[];    // プロジェクトのハイライト
  gradient: string[];      // カードのグラデーション色
}
```

### エントリの例

```json
{
  "id": "sing-box",
  "name": "sing-box",
  "description": "Shadowsocks、Trojan、V2Ray、NaïveProxy、Hysteria、TUIC などに対応する汎用プロキシプラットフォーム。",
  "url": "https://github.com/SagerNet/sing-box",
  "category": "proxy-core",
  "tags": ["proxy", "shadowsocks", "trojan", "v2ray", "hysteria", "tuic"],
  "language": "Go",
  "stars": 25000,
  "lastUpdate": "2026-05-30",
  "license": "MIT"
}
```

### 新規エントリのチェックリスト

- [ ] `id` は小文字・ハイフン区切り・一意
- [ ] `url` が HTTP 200 を返し、公式リポジトリ URL である
- [ ] `category` がプロジェクトカテゴリの enum に存在する（新規の場合は PR と同時提案）
- [ ] 過去 **6 か月** 以内にコミットがある
- [ ] ライセンスが OSI 承認済み
- [ ] 説明は簡潔（≤ 120 文字）で英語
- [ ] タグは小文字・ハイフン区切り・重複なし
- [ ] JSON が妥当（`pnpm lint` で検証可能）

> **並び順とカテゴリ**はコードにより動的に決定されるため、手動で順序を維持する必要はありません。

---

## 🎨 コードスタイル

- **言語**：TypeScript（strict モード）、React 19 関数コンポーネント
- **スタイリング**：Tailwind CSS v4 のユーティリティクラスと `@theme` トークン。インラインスタイルは不可
- **Lint**：`pnpm lint` を通すこと —— 一般的な問題は自動修正されます
- **コンポーネント**：小さく・単一責任・真偽値 prop の濫用を避ける（`vercel-composition-patterns` を参照）
- **アクセシビリティ**：すべてのインタラクティブ要素に明確なフォーカス状態と、必要に応じて `aria-label`
- **レスポンシブ**：モバイルファースト。≥ 360px（スマホ）、768px（タブレット）、1280px（デスクトップ）でテスト済み

PR を作成する前に以下を実行してください：

```bash
pnpm lint
pnpm build
```

---

## 🧾 コミットメッセージ規約

**Conventional Commits** に従い、可読性の高い履歴を保ち、将来 changelog を自動化できるようにします。

```
<type>(<scope>): <短い説明>

[任意の本文]

[任意の脚注]
```

よく使う type：

| Type | 用途 |
| --- | --- |
| `feat` | ユーザー向け新機能 |
| `fix` | バグ修正 |
| `docs` | ドキュメントのみの変更（README、CONTRIBUTING など） |
| `style` | フォーマット、セミコロン漏れなどコード変更を含まない調整 |
| `refactor` | バグ修正や機能追加を伴わないコード変更 |
| `perf` | パフォーマンス改善 |
| `test` | テストの追加・修正 |
| `chore` | ツール、依存、CI などの非コード変更 |
| `data` | `data/projects.json` の更新 |

例：

```
feat(search): 300ms デバウンス入力を追加
fix(sidebar): ナビゲーション時に lang パラメータが消える問題を修正
data: sing-box v1.11 リリースエントリを追加
docs: GitHub Pages build_type の説明を明確化
```

---

## 🔁 Pull Request の流れ

1. **`main` から機能ブランチを作成**：
   ```bash
   git checkout -b feat/<短い説明>
   ```
2. **焦点を絞ったコミット** —— 1 コミット 1 ロジック変更、Conventional Commit に従う。
3. **ローカルでチェックを実行**：
   ```bash
   pnpm lint
   pnpm build
   ```
   どちらもクリーンに通る必要があります。
4. **プッシュして PR を作成**（`main` 向け）：<https://github.com/badhope/NetTools-Hub/pulls>
5. **PR テンプレートを埋める** —— 変更内容を記述し、関連 Issue をリンク（`Fixes #123`）。UI 変更にはスクリーンショット / 画面録画を添付。
6. **レビューを待つ** —— メンテナーが数日中に返信します。フィードバックにはオープンな姿勢で応じてください。些細な nitpick は普通のことです。
7. **Squash-merge** がデフォルトのマージ戦略で、最終履歴は線形になります。

> テンプレートに従わない、または CI が失敗している PR は、レビュー前に修正をお願いする場合があります。

---

## 🌐 ローカライゼーション (i18n)

UI は三言語対応です：**English（デフォルト） / 中文 / 日本語**。翻訳文字列は `src/lib/i18n.ts` に集約されています。

翻訳の追加・修正手順：

1. `src/lib/i18n.ts` を開きます。
2. **三言語すべてに**新しいキーを追加（または欠落・誤りを修正）します。
3. 専門用語はプロジェクト内で一貫させてください。
4. **日本語**では直訳よりも自然な表現を優先してください（例：「梯子」「翻墙」のような表現は避け、プロキシ / VPN といった表記が無難です）。

一言語しか話せなくても、**部分的な PR も歓迎します** —— 他の人が残りを補完します。

---

## 🆘 サポートが必要なときは？

- **Issue**：<https://github.com/badhope/NetTools-Hub/issues>
- **Discussion**：<https://github.com/badhope/NetTools-Hub/discussions>
- **README**：デプロイと FAQ セクションを参照

改めて、貢献に感謝します —— すべての PR が、オープンソースのネットワークツールエコシステムの発見可能性を少しずつ高めます。🚀
