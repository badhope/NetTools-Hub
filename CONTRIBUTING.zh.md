# 贡献指南 · Contributing to NetTools Hub

> **语言 / Language:** [🇬🇧 English](CONTRIBUTING.md) · **🇨🇳 简体中文** · [🇯🇵 日本語](CONTRIBUTING.ja.md)

首先感谢你愿意花时间参与贡献！🎉
**NetTools Hub** 是一个由社区共同维护的、对开源网络工具进行收录与导航的平台。每一份贡献 —— 从一个错别字到一条新的项目收录 —— 都会让它变得更好。

本文档将帮助你发起一个高质量的 Pull Request (PR) 或提交一份有用的 Issue。

---

## 📑 目录

- [行为准则](#-行为准则)
- [我能贡献什么？](#-我能贡献什么)
- [报告 Bug](#-报告-bug)
- [推荐新工具 / 新功能](#-推荐新工具--新功能)
- [本地开发环境搭建](#-本地开发环境搭建)
- [项目结构](#-项目结构)
- [新增或修改项目条目](#-新增或修改项目条目)
- [代码风格](#-代码风格)
- [Commit 信息规范](#-commit-信息规范)
- [Pull Request 流程](#-pull-request-流程)
- [本地化 (i18n)](#-本地化-i18n)
- [需要帮助？](#-需要帮助)

---

## 🤝 行为准则

本项目及所有参与者均遵循 [Contributor Covenant v2.1](CODE_OF_CONDUCT.md)。
参与即表示你同意遵守该准则。如有不可接受的行为，请通过 GitHub Issue 反馈。

---

## 🧩 我能贡献什么？

- 在 `data/projects.json` 中**新增工具条目**
- **更新过期数据**（失效链接、过时的 star 数、已弃用的项目等）
- **改进三语 UI 的翻译**（English / 中文 / 日本語）
- **修复 Bug**（布局、搜索、排序、语言切换等）
- **性能 / 可访问性**优化
- **文档**（错别字修正、README 表达更清晰等）

---

## 🐛 报告 Bug

在提 Bug 之前请先：

1. **搜索已有 Issue**，避免重复。
2. 确认复现的是最新 `main` 分支 —— 你的问题可能已被修复。
3. 收集诊断信息：浏览器版本、操作系统、设备、截图、控制台报错。

请到 <https://github.com/badhope/NetTools-Hub/issues/new> 提交 Issue：

- 清晰、描述性的标题
- 复现步骤（编号列出）
- 期望行为 vs 实际行为
- 截图 / 录屏
- 控制台 / 网络日志（请先脱敏任何个人信息）

---

## 💡 推荐新工具 / 新功能

新增项目条目请使用 **"Project submission"** 模板（也可在 Issue 中包含以下字段），以便我们核实项目的活跃度与质量：

- **仓库 URL**（仅限 GitHub）
- **项目名称**及一句话简介
- **主要语言 / 框架**
- **许可证**（必须是 OSI 认可的，例如 MIT / Apache-2.0 / GPL / BSD）
- **Star 数**及**最近一次提交日期**（我们会再核验）
- **所属分类** — 从 `data/projects.json` 中现有的 21 个子分类（归属 6 大主题组）中任选一个；如确需新增，请提供理由。完整列表见 [README → 📑 6 大主题组](../../#-the-6-themed-groups-21-sub-categories)。
- **为什么值得收录** — 用 1-2 句话说明该项目有何亮点

> 收录标准：6 个月内必须有提交记录、项目未被弃用、能解决真实的网络需求，且最好能填补现有收录的空白。

新功能建议请使用 **"Feature request"** 标签，描述用户价值、建议的交互方式以及你考虑过的替代方案。

---

## 🛠 本地开发环境搭建

### 前置条件

- **Node.js** `>= 22.0.0`（见 `.nvmrc`）
- **pnpm** `>= 10.0.0`（见 `.npmrc`）
- 现代浏览器（Chrome / Firefox / Safari / Edge 最新 2 个版本）

### 步骤

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/<你的用户名>/NetTools-Hub.git
cd NetTools-Hub

# 2. 安装依赖
pnpm install --frozen-lockfile

# 3. 启动开发服务器（端口 8080）
pnpm dev

# 4. 打开 http://localhost:8080
```

### 可用脚本

| 命令 | 说明 |
| --- | --- |
| `pnpm dev` | 在 8080 端口启动本地开发服务器 |
| `pnpm build` | 在 `./out` 目录生成静态产物 |
| `pnpm start` | 在 8080 端口服务已构建的 `./out` 目录 |
| `pnpm lint` | 使用 Next.js + TypeScript 规则运行 ESLint |

> **说明**：本项目使用 `output: "export"` 以静态方式部署到 GitHub Pages。开发服务器正常工作，只有生产构建是完全静态的。

---

## 🗂 项目结构

```
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Pages CI/CD
├── data/
│   └── projects.json           # 210 条收录项目，21 个子分类（6 大主题组）
├── src/
│   ├── app/
│   │   ├── explore/            # /explore — 可筛选 / 可排序列表
│   │   ├── error.tsx           # 全局错误边界
│   │   ├── layout.tsx          # 根布局
│   │   ├── not-found.tsx       # 404 页面
│   │   ├── page.tsx            # / — 落地页
│   │   ├── robots.ts           # robots.txt
│   │   └── sitemap.ts          # sitemap.xml
│   ├── components/             # UI 基础组件
│   ├── lib/                    # i18n、数据访问、工具函数
│   └── types/                  # TypeScript 类型
├── public/                     # （可选）静态资源
├── LICENSE                     # MIT
├── README.md                   # 三语文档
├── next.config.ts              # `output: "export"`
├── package.json
├── pnpm-lock.yaml
├── postcss.config.mjs          # Tailwind v4
└── tsconfig.json
```

---

## 📝 新增或修改项目条目

所有数据集中存放在 **`data/projects.json`**。Schema 由 `src/types/project.ts` 强制约束。

### Schema (TypeScript)

```ts
interface Project {
  id: string;              // URL 安全的 slug，例如 "sing-box"
  name: string;            // 显示名称，例如 "sing-box"
  author: string;          // 作者或组织名，例如 "SagerNet"
  description: string;     // 一句话简介（英文）
  url: string;             // 官方主页或仓库 URL
  homepage?: string;       // 可选的项目主页（非 GitHub）
  
  // 指标（由 scripts/refresh-projects.mjs 自动刷新）
  stars: number;           // GitHub star 数
  forks: number;           // GitHub fork 数
  language: string;        // 主要语言，例如 "Go"
  license: string;         // SPDX 标识符，例如 "MIT"
  
  // 分类维度
  kind: ProjectKind;       // "proxy" | "vpn" | "dns" | "acceleration" | "security" | "monitoring" | "ops" | "tools"
  platform: ProjectPlatform[];  // "desktop" | "mobile" | "cli" | "server" | "browser" | "router"
  category: string;        // 编辑分类，例如 "proxy-core"
  tags: string[];          // 自由形式，小写、连字符
  
  // 编辑内容
  notes?: string;          // 可选的维护者备注
  verdict?: ProjectVerdict; // "recommended" | "neutral" | "caution" | "avoid"
  
  // 生命周期
  lastCommit: string;      // ISO 8601 日期，例如 "2026-05-01"
  addedAt: string;         // 首次加入日期
  status: ProjectStatus;   // "active" | "stale" | "archived"
  
  // 视觉
  highlights: string[];    // 项目亮点
  gradient: string[];      // 卡片渐变色
}
```

### 示例条目

```json
{
  "id": "sing-box",
  "name": "sing-box",
  "description": "通用代理平台，支持 Shadowsocks、Trojan、V2Ray、NaïveProxy、Hysteria、TUIC 等。",
  "url": "https://github.com/SagerNet/sing-box",
  "category": "proxy-core",
  "tags": ["proxy", "shadowsocks", "trojan", "v2ray", "hysteria", "tuic"],
  "language": "Go",
  "stars": 25000,
  "lastUpdate": "2026-05-30",
  "license": "MIT"
}
```

### 新增条目 Checklist

- [ ] `id` 全小写、连字符、唯一
- [ ] `url` 返回 HTTP 200，且为规范仓库 URL
- [ ] `category` 已在项目分类枚举中（否则随 PR 一起提议新增）
- [ ] 最近 **6 个月**内有提交
- [ ] 许可证为 OSI 认可的协议
- [ ] 描述简洁（≤ 120 字符）且为英文
- [ ] 标签全小写、连字符、无重复
- [ ] JSON 合法（可执行 `pnpm lint` 校验）

> **排序与分类**由代码动态派生 —— 你不需要手动维护顺序。

---

## 🎨 代码风格

- **语言**：TypeScript（strict 模式）、React 19 函数组件
- **样式**：Tailwind CSS v4 工具类 + `@theme` 设计 token；不写内联样式
- **Lint**：`pnpm lint` 必须通过 —— 它能自动修复大多数常见问题
- **组件**：保持小巧、单一职责，避免布尔参数膨胀（可参考 `vercel-composition-patterns`）
- **可访问性**：每个交互元素都有清晰的焦点状态和必要的 `aria-label`
- **响应式**：移动优先；已在 ≥ 360px（手机）、768px（平板）、1280px（桌面）测试

提交 PR 前请运行：

```bash
pnpm lint
pnpm build
```

---

## 🧾 Commit 信息规范

我们遵循 **Conventional Commits**，以保持提交历史的可读性，并方便后续自动生成 changelog。

```
<type>(<scope>): <简短描述>

[可选 正文]

[可选 脚注]
```

常用 type：

| Type | 用途 |
| --- | --- |
| `feat` | 新增面向用户的功能 |
| `fix` | 修复 Bug |
| `docs` | 仅文档变更（README、CONTRIBUTING 等） |
| `style` | 格式调整、缺失分号等无代码变更 |
| `refactor` | 既不修复 Bug 也不新增功能的代码变更 |
| `perf` | 性能优化 |
| `test` | 新增或修改测试 |
| `chore` | 工具、依赖、CI 等非代码变更 |
| `data` | 更新 `data/projects.json` |

示例：

```
feat(search): 增加 300ms 防抖输入
fix(sidebar): 修复切换页面时丢失 lang 参数的问题
data: 新增 sing-box v1.11 发布条目
docs: 明确 GitHub Pages build_type 的说明
```

---

## 🔁 Pull Request 流程

1. **从 `main` 创建功能分支**：
   ```bash
   git checkout -b feat/<简短描述>
   ```
2. **聚焦提交** —— 一次提交只做一件事，commit 信息遵循 Conventional Commits。
3. **本地运行检查**：
   ```bash
   pnpm lint
   pnpm build
   ```
   两项必须全部通过。
4. **推送并发起 PR**，目标分支为 `main`：<https://github.com/badhope/NetTools-Hub/pulls>
5. **填写 PR 模板** —— 描述本次变更、关联相关 Issue（`Fixes #123`），UI 变更请附截图 / 录屏。
6. **等待 Review** —— 维护者会在数天内回复。请保持开放的心态接受反馈；细小的 nitpick 是正常的。
7. **Squash-merge** 为默认合并策略，最终历史保持线性。

> 不符合模板或 CI 失败的 PR 可能需要先修改再进入 Review。

---

## 🌐 本地化 (i18n)

UI 共三种语言：**English（默认） / 中文 / 日本語**。翻译字符串集中在 `src/lib/i18n.ts`。

新增或修正翻译：

1. 打开 `src/lib/i18n.ts`。
2. 为**三种语言**同时添加新 key（或修正缺失 / 错误的项）。
3. 保持技术术语与项目其他部分一致。
4. **日文**：优先自然表达，而非字面直译（例如慎用 梯子 / 翻墙 等表述，许多读者更接受 プロキシ / VPN）。

如果你只会其中一种语言，**也欢迎提交部分翻译的 PR** —— 其他人会帮你补齐。

---

## 🆘 需要帮助？

- **Issue**：<https://github.com/badhope/NetTools-Hub/issues>
- **Discussion**：<https://github.com/badhope/NetTools-Hub/discussions>
- **README**：参见部署与 FAQ 章节

再次感谢你的贡献 —— 每一份 PR 都让开源网络工具生态更容易被发现。🚀
