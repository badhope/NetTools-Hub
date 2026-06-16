# NetTools Hub · ネットワークツールハブ

> **⚠️ まず [DISCLAIMER.md](./DISCLAIMER.md) をお読みください**
> 本リポジトリは**リンクの目次に過ぎません**。リンク先のソフトウェ
> アをホスティング・配布・推奨・運営することは一切ありません。**掲載
> ＝推奨ではありません**。利用は自己責任で。

活発にメンテナンスされている **210 件のオープンソース・ネットワーク
ツール**を集約した**フィールドマニュアル**：プロキシ、VPN コア、DNS
サーバー、GitHub 高速化、監視エージェント、セキュリティユーティリティ。
**kind（種別）** と **platform（実行環境）** の 2 軸で分類し、**URL
パスでドリルダウン**します（無限スクロールもクライアント状態もありま
せん）。

```
/                                ← ホーム
/explore                         ← 210 件すべて
/explore/k/proxy                 ← kind でドリルダウン（8 種別）
/explore/k/proxy/p/desktop       ← kind + platform でドリルダウン（6 環境）
```

サイトは**事前レンダリングされた単一の静的バンドル**です。**バックエ
ンド、データベース、トラッキング、広告、解析ツールは一切なし**。ホス
ティングは **GitHub Pages**。データは 1 つの JSON ファイル
（[`data/projects.json`](./data/projects.json)）に集約され、メタ
データは GitHub Action により**毎週自動更新**されます。

> 関連：[🇬🇧 `README.md`](./README.md) · [🇨🇳 `README.zh.md`](./README.zh.md) ·
> 🇯🇵 `README.ja.md`（ここ）

---

## これは何？

システムを再インストールするたびに、私は毎回 GitHub で同じ問いを投げ
かけています。_Clash のどのコアがまだ生きているか、sing-box と Xray
の違い、もっと軽い V2Ray 実装はあるか、WireGuard の UI で一番きれい
なのはどれか_。このサイトは私の個人的なチートシートを公開したものです。

これは **VPN サービスではありません**。**プロキシ提供元ではありま
せん**。**掲載ツールのホスティングプラットフォームでもありません**。
**リンクの目次**です。各エントリは実際の GitHub リポジトリを指す
`<a href>` です。[DISCLAIMER.md](./DISCLAIMER.md) を必ずご
確認ください。

---

## 8 種別 × 6 環境

ディレクトリは 2 つの**直交する分類軸**で構成されており、それがそのま
ま URL 階層になります：

| `kind`（URL: `/explore/k/<kind>/`）                        | 件数 | `platform`（URL: `.../p/<platform>/`） | 件数 |
| ---------------------------------------------------------- | ---: | -------------------------------------- | ---: |
| `proxy` プロキシコアとクライアント                         |   78 | `desktop`                              |  102 |
| `vpn` VPN サーバーとクライアント                           |   19 | `mobile`                               |   56 |
| `dns` 再帰・権威・フィルタリング                           |   18 | `cli`                                  |   81 |
| `acceleration` GitHub 高速化、ミラー、トンネル             |   31 | `server`                               |  134 |
| `security` WAF、IDS、IPS、ハニーポット                     |   21 | `browser`                              |   38 |
| `monitoring` 稼働率、指標、可観測性                        |   14 | `router`                               |   23 |
| `ops` デプロイ、オーケストレーション、管理                 |   12 |                                        |      |
| `tools` ユーティリティスクリプト、ポートスキャナ、デバッガ |   17 |                                        |      |

1 つのプロジェクトに複数の `platform` タグを付けることができます
（例：プロキシが `desktop` と `cli` の両方）。URL 階層はこの 2 軸の
直積となるので、すべての `(kind, platform)` ペアが独立した静的ページ
になります。両方の動的ルートに `generateStaticParams` が組み込まれて
おり、ビルド成果物は 1 + 8 + 8 × 6 = **57 個の事前レンダリングされた
ページ** を出力します。

---

## クイックスタート

### ユーザー（ツールを探すだけ）

1. **<https://badhope.github.io/NetTools-Hub/>** を開く
2. **URL でドリルダウン**：
   - `/explore` —— 210 件すべて
   - `/explore/k/proxy` —— プロキシすべて
   - `/explore/k/proxy/p/desktop` —— デスクトップ向けプロキシのみ
3. **左のツリーサイドバー**を使う（kind が第 1 階層、その下の platform
   が第 2 階層）。
4. **行をクリック** して GitHub リポジトリへ。

レスポンシブ対応（デスクトップ / タブレット / モバイル）。右上のラン
ゲージスイッチャで **English / 中文 / 日本語** をいつでも切替可能。
URL に `?lang=zh` または `?lang=ja` が付与されます。

### コントリビュータ

```bash
git clone https://github.com/badhope/NetTools-Hub.git
cd NetTools-Hub
pnpm install --frozen-lockfile   # Node 22+ & pnpm 10+
pnpm dev                          # http://localhost:8080
```

静的サイトをローカルビルド：

```bash
pnpm build        # ./out に静的エクスポート
pnpm start        # http://localhost:8080 で確認
```

データをプッシュ前に検証：

```bash
pnpm run validate # scripts/validate-projects.mjs を実行（CI でも実行）
```

GitHub API からメタデータを更新（`GITHUB_TOKEN` があれば高レート、
無ければ匿名）：

```bash
pnpm run refresh
```

`awesome-*` リストから新規候補を発掘：

```bash
pnpm run scan     # data/candidates.json に書き出し
```

詳細は [`CONTRIBUTING.md`](./CONTRIBUTING.md) を参照。

### メンテナ（Fork & デプロイ）

リポジトリに **GitHub Actions** ワークフローが同梱されています。
Fork 後：

1. **Settings → Pages → Source** を **GitHub Actions** に設定
2. `main` に push —— `.github/workflows/deploy.yml` が自動ビルド &
   デプロイ
3. （任意）リポジトリ名を変更した場合は [`next.config.ts`](./next.config.ts) の `basePath` も更新

あなたの fork は
`https://<username>.github.io/NetTools-Hub/` に公開されます。詳細は
[`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) を参照。

---

## 特徴

- **URL パスナビゲーション** —— `/explore/k/<kind>/p/<platform>/`、
  無限スクロールなし、クライアント状態なし、ディープリンクがそのまま動
  く
- **ツリーサイドバー** —— 第 1 階層が kind、第 2 階層が platform、アク
  ティブなノードをハイライト、モバイルでは折りたたみ
- **事前レンダリング** —— 全ページが静的 HTML。`out/` バンドルは
  `pnpm build` 一発
- **3 言語 UI** —— English / 中文 / 日本語、ランゲージスイッチャまたは
  `?lang=` クエリで切替
- **PWA** —— インストール可、オフライン対応、`manifest` 付き、適切な
  `<html lang>` と OG カード
- **SEO 対応** —— `robots.txt`、`sitemap.xml`、JSON-LD、`hreflang`、
  OpenGraph、Twitter Card
- **メタデータの自動更新** —— 週次の GitHub Action が stars / forks /
  license / last commit を更新し、2 年コミットなしで `status: archived`
  に自動判定
- **データバリデーション** —— 全 PR を独立した CI ジョブで
  `scripts/validate-projects.mjs` がスキャン
- **フィールドマニュアル・デザイン** —— クールなニアブラックの配色、
  ヘアラインルール、IBM Plex Sans + Mono、等幅数字、影なし、角丸なし
- **MIT ライセンス** —— fork / 改変 / 再デプロイ自由

---

## プロジェクト構成

```
NetTools-Hub/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── workflows/
│   │   ├── deploy.yml          # GitHub Pages 自動デプロイ
│   │   ├── refresh-projects.yml # 週次メタデータ更新
│   │   └── ci.yml              # lint + typecheck + validate
│   ├── CODEOWNERS
│   ├── FUNDING.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── data/
│   ├── projects.json           # 210 プロジェクト × (kind + platform) ← データの単一ソース
│   └── candidates.json         # pnpm run scan が生成
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA-MODEL.md
│   ├── DEPLOYMENT.md
│   ├── I18N.md
│   ├── I18N.zh.md
│   └── I18N.ja.md
├── public/
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── manifest.webmanifest
│   ├── og-image.png
│   └── robots.txt
├── scripts/
│   ├── validate-projects.mjs   # スキーマバリデータ（CI で実行）
│   ├── refresh-projects.mjs    # 週次 GitHub API 更新
│   ├── scan-awesome.mjs        # awesome-* 候補マイナー
│   ├── migrate-schema.mjs      # v1 → v2 ワンショット
│   ├── add-batch.mjs           # 手作業追加（レガシー）
│   ├── build-og-image.py       # og-image.png + アイコン再生成
│   ├── smoke.py                # Playwright スモークテスト（手動）
│   ├── snap.py                 # Playwright ページショット（手動）
│   └── pageshot.py             # Playwright デプロイ後チェック（手動）
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx          # ルートレイアウト、フォント、metadata、OG
│   │   ├── page.tsx            # ホーム
│   │   ├── globals.css         # Tailwind v4 + フィールドマニュアルテーマ
│   │   ├── not-found.tsx
│   │   ├── error.tsx
│   │   ├── explore/            # /explore, /explore/k/<kind>/, /explore/k/<kind>/p/<platform>/
│   │   ├── robots.ts
│   │   └── sitemap.ts
│   ├── components/             # top-nav, tree-sidebar, project-table, …
│   ├── lib/                    # i18n, taxonomy, projects, site
│   └── types/
│       └── project.ts          # スキーマ v2 型定義
├── .editorconfig
├── .gitattributes
├── .gitignore
├── .npmrc
├── .nvmrc                      # node 22
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DISCLAIMER.md               # 完全な免責事項（必読）
├── LICENSE                     # MIT
├── README.md                   # 英語（デフォルト）
├── README.zh.md                # 简体中文
├── README.ja.md                # 日本語（ここ）
├── SECURITY.md
├── eslint.config.mjs
├── next.config.ts              # output: "export" + basePath
├── package.json
├── pnpm-lock.yaml
├── postcss.config.mjs
└── tsconfig.json
```

---

## 技術スタック

| レイヤ               | 採用                         | 理由                                                                       |
| -------------------- | ---------------------------- | -------------------------------------------------------------------------- |
| フレームワーク       | **Next.js 16**（App Router） | 静的エクスポート、RSC、ファイルベースルーティング                          |
| UI                   | **React 19**                 | 最新安定版                                                                 |
| スタイリング         | **Tailwind CSS v4**          | `@import "tailwindcss"` + `@theme` トークン                                |
| 言語                 | **TypeScript 5.9**           | strict モード                                                              |
| パッケージマネージャ | **pnpm 10**                  | 高速、ディスク効率                                                         |
| ホスティング         | **GitHub Pages**             | 無料、高速 CDN、ベンダーロックインなし                                     |
| CI/CD                | **GitHub Actions**           | `actions/checkout@v4` + `pnpm/action-setup@v4` + `actions/deploy-pages@v4` |
| i18n                 | 手書き 3 言語対応表          | JS バンドルゼロ、ランタイム切替                                            |
| フォント             | **IBM Plex Sans + Mono**     | クールで工学的；数字は等幅                                                 |

---

## プロジェクトの追加 / 編集

コンテンツは単一の JSON ファイル。スキーマの全容は
[`docs/DATA-MODEL.md`](./docs/DATA-MODEL.md)、TypeScript 型は
[`src/types/project.ts`](./src/types/project.ts) を参照。最小
エントリ：

```json
{
  "id": "sing-box",
  "name": "sing-box",
  "kind": "proxy",
  "platform": ["desktop", "cli", "server"],
  "category": "proxy-core",
  "description": "Universal proxy platform",
  "url": "https://github.com/SagerNet/sing-box",
  "language": "Go",
  "license": "MIT",
  "addedAt": "2024-04-01",
  "verdict": "best-in-class"
}
```

掲載基準：直近 6 ヶ月に活発なコミットがある、OSI 認定のオープンソース
ライセンス、実用的なユースケース。詳細：
[`CONTRIBUTING.md`](./CONTRIBUTING.md)。

> `stars`、`forks`、`lastCommit`、`status` は
> `scripts/refresh-projects.mjs` により**毎週自動再生成**されます。手
> で埋める必要はありません。

---

## 自動化パイプライン

| トリガ                         | スクリプト                      | 出力                                                                                     |
| ------------------------------ | ------------------------------- | ---------------------------------------------------------------------------------------- |
| cron（日曜 03:00 UTC）         | `scripts/refresh-projects.mjs`  | `stars` / `forks` / `license` / `lastCommit` / `status` を更新、差分があれば自動コミット |
| 手動 `workflow_dispatch`       | 同上                            | 同上                                                                                     |
| `data/projects.json` への push | 同上（`paths:` フィルタで）     | 同上                                                                                     |
| `pnpm run scan`（ローカル）    | `scripts/scan-awesome.mjs`      | `data/candidates.json` に書き出し（メンテナが確認）                                      |
| `pnpm run validate`（CI）      | `scripts/validate-projects.mjs` | 終了コード 0/1/2；不合格なら PR を落とす                                                 |

リフレッシュワークフローは `git diff --exit-code` でコミット要否を判定
します。単一プロジェクトの GitHub API 呼び出し失敗はログしてスキップ
するので、1 件の 404 がラン全体をつぶすことはありません。

---

## 国際化（i18n）

| 言語                     | コード | UI  | ドキュメント                     |
| ------------------------ | ------ | --- | -------------------------------- |
| 🇬🇧 English（デフォルト） | `en`   | ✅  | [`README.md`](./README.md)       |
| 🇨🇳 简体中文              | `zh`   | ✅  | [`README.zh.md`](./README.zh.md) |
| 🇯🇵 日本語                | `ja`   | ✅  | [`README.ja.md`](./README.ja.md) |

UI 文字列は [`src/lib/i18n.ts`](./src/lib/i18n.ts) に集約（約 36 キー
の 3 列表）。現在の言語は `?lang=` URL パラメータから読み取られ、
`localStorage` が粘着的な嗜好として保持します。詳細は
[`docs/I18N.md`](./docs/I18N.md)。

---

## コントリビュート

PR を歓迎します。詳細は [`CONTRIBUTING.md`](./CONTRIBUTING.md)：

- ローカル開発環境とスクリプト
- データスキーマとプロジェクトの追加方法
- コードスタイル、lint、**Conventional Commits**（`feat:`、`fix:`、`docs:`、…）
- PR レビュープロセス
- 翻訳の追加・改善方法

参加することで、[行動規範](./CODE_OF_CONDUCT.md) に同意したものと
みなされます。

---

## セキュリティ

脆弱性を発見されましたら、**公開 Issue には記載しないでください**。
[`SECURITY.md`](./SECURITY.md) に従い非公開で開示してください。**3
営業日以内** を目安に返信します。

---

## ライセンス

[MIT ライセンス](./LICENSE) のもとで公開。

---

> NetTools Hub · 210 件のオープンソース・ネットワークツールのフィー
> ルドマニュアル · [English](README.md) · [简体中文](README.zh.md) ·
> 日本語（ここ）
