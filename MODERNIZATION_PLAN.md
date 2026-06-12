# NetTools Hub 现代化重构计划

**制定日期**: 2026-06-12  
**目标**: 打造世界级的网络工具导航站，在内容、美学、体验、性能、可维护性上达到行业顶尖水平  
**预计周期**: 8-12 周（分 4 个阶段）

---

## 执行摘要

本次重构计划基于对代码库的全面审计（发现 38 个问题），结合现代 Web 开发最佳实践，提出系统性的改进方案。核心目标：

1. **内容质量** — 数据准确性、分类科学性、描述专业性
2. **视觉美学** — 设计系统升级、动效精细化、响应式优化
3. **用户体验** — 交互流畅度、可访问性、国际化完善
4. **技术架构** — 代码质量、测试覆盖、性能优化、安全性
5. **开发体验** — 工具链完善、文档清晰、CI/CD 高效

---

## 第一阶段：基础加固（Week 1-2）

### 1.1 代码质量提升

#### 1.1.1 启用 TypeScript 严格模式

**优先级**: P1 | **工作量**: 2h | **风险**: 低

**问题**: `tsconfig.json` 缺少关键类型安全选项

**改动**:

```json
{
  "compilerOptions": {
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**预期效果**: 捕获潜在的数组越界、undefined 访问等类型错误

---

#### 1.1.2 消除代码重复

**优先级**: P3 | **工作量**: 3h | **风险**: 低

**问题**: `formatStars`、`KIND_ORDER` 在多处重复定义

**改动**:

- 创建 `src/lib/constants.ts`，集中管理所有常量
- 将 `formatStars` 移至 `src/lib/utils.ts`
- 更新所有引用点

**文件清单**:

- `src/lib/constants.ts` (新建)
- `src/lib/utils.ts` (添加 formatStars)
- `src/app/page.tsx` (移除重复定义)
- `src/components/top-nav.tsx` (引用 constants)
- `src/components/tree-sidebar.tsx` (引用 constants)

---

#### 1.1.3 集成 Prettier 代码格式化

**优先级**: P3 | **工作量**: 2h | **风险**: 低

**改动**:

```bash
pnpm add -D prettier eslint-config-prettier
```

创建 `.prettierrc`:

```json
{
  "semi": true,
  "trailingComma": "all",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

更新 `package.json`:

```json
{
  "scripts": {
    "format": "prettier --write .",
    "format:check": "prettier --check ."
  }
}
```

在 CI 中添加格式化检查。

---

### 1.2 测试覆盖扩展

#### 1.2.1 核心工具函数测试

**优先级**: P1 | **工作量**: 4h | **风险**: 低

**测试清单**:

- `src/lib/utils.test.ts` — 补充 `safeJsonLd`、`formatTotalStars` 测试
- `src/lib/i18n.test.ts` (新建) — 测试 `t()`、`formatNumber()`、语言解析
- `src/lib/projects.test.ts` (新建) — 测试索引构建、查询函数
- `src/lib/taxonomy.test.ts` (新建) — 测试分类映射、标签处理

**目标覆盖率**: 核心逻辑 80%+

---

#### 1.2.2 组件测试基础

**优先级**: P2 | **工作量**: 6h | **风险**: 中

**测试清单**:

- `ProjectRow.test.tsx` — 渲染、点击、键盘导航、链接预检
- `TopNav.test.tsx` — 桌面/移动导航、语言切换
- `TreeSidebar.test.tsx` — 展开/折叠、筛选
- `LanguageSwitcher.test.tsx` — 切换、焦点管理

**工具**: React Testing Library + Vitest

---

### 1.3 CI/CD 增强

#### 1.3.1 添加依赖安全审计

**优先级**: P1 | **工作量**: 1h | **风险**: 低

**改动** (`.github/workflows/ci.yml`):

```yaml
- name: Audit dependencies
  run: pnpm audit --audit-level=high
```

---

#### 1.3.2 添加 Bundle 分析

**优先级**: P2 | **工作量**: 2h | **风险**: 低

**改动**:

```bash
pnpm add -D @next/bundle-analyzer
```

创建 `next.config.analyze.ts`，在 CI 中生成 bundle 报告并上传为 artifact。

---

## 第二阶段：架构优化（Week 3-4）

### 2.1 组件重构

#### 2.1.1 拆分 ProjectRow 组件

**优先级**: P2 | **工作量**: 6h | **风险**: 中

**问题**: 205 行，职责过多

**重构方案**:

```
src/components/
├── project-row/
│   ├── index.tsx          # 主组件（布局 + 状态）
│   ├── use-link-prefetch.ts  # 链接预检 hook
│   ├── project-meta.tsx   # 元数据展示
│   └── project-badges.tsx # 平台/状态徽章
```

**收益**: 单一职责、可测试性提升、代码复用

---

#### 2.1.2 提取 MobileNavDrawer 组件

**优先级**: P3 | **工作量**: 3h | **风险**: 低

**问题**: TopNav 260 行，移动导航逻辑复杂

**重构方案**:

```
src/components/
├── top-nav.tsx            # 桌面导航
├── mobile-nav-drawer.tsx  # 移动导航抽屉
└── language-switcher.tsx  # 语言切换（独立）
```

---

#### 2.1.3 创建 EmptyState 通用组件

**优先级**: P3 | **工作量**: 2h | **风险**: 低

**设计**:

```tsx
interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: { label: string; href: string };
}
```

**使用场景**:

- 筛选无结果
- 分类无项目
- 搜索无匹配

---

### 2.2 数据层优化

#### 2.2.1 优化静态生成

**优先级**: P2 | **工作量**: 3h | **风险**: 低

**问题**: 生成 48 个 kind+platform 组合，包括空页面

**改动** (`src/app/explore/k/[kind]/p/[platform]/page.tsx`):

```typescript
export function generateStaticParams() {
  const projects = getAllProjects();
  const validCombinations = new Set(projects.map((p) => `${p.kind}/${p.platform[0]}`));

  return Array.from(validCombinations).map((comb) => {
    const [kind, platform] = comb.split('/');
    return { kind, platform };
  });
}
```

**收益**: 减少构建时间、避免空页面

---

#### 2.2.2 添加数据版本检查

**优先级**: P3 | **工作量**: 1h | **风险**: 低

**改动** (`src/lib/projects.ts`):

```typescript
if (data.schemaVersion !== CURRENT_SCHEMA_VERSION) {
  console.warn(
    `Data schema version mismatch: expected ${CURRENT_SCHEMA_VERSION}, ` +
      `got ${data.schemaVersion}. Some features may not work correctly.`,
  );
}
```

---

#### 2.2.3 增量更新机制

**优先级**: P2 | **工作量**: 8h | **风险**: 中

**问题**: 刷新脚本失败后需从头开始

**方案**:

- 使用临时文件存储已获取的数据
- 记录每个项目的 ETag/Last-Modified
- 失败后从断点恢复

**实现**:

```javascript
// scripts/refresh-projects.mjs
const CACHE_FILE = '.refresh-cache.json';

async function refreshWithCache(projects) {
  const cache = loadCache(CACHE_FILE);

  for (const project of projects) {
    if (cache[project.id]?.etag === latestEtag) {
      continue; // 跳过未变更的项目
    }

    const data = await fetchRepo(project.url);
    cache[project.id] = { etag: data.etag, data };
    saveCache(CACHE_FILE, cache);
  }
}
```

---

### 2.3 性能优化

#### 2.3.1 启用图片优化

**优先级**: P1 | **工作量**: 1h | **风险**: 低

**改动** (`next.config.ts`):

```typescript
const nextConfig = {
  images: {
    unoptimized: false, // 启用优化
    formats: ['image/avif', 'image/webp'],
  },
};
```

---

#### 2.3.2 添加路由预取

**优先级**: P3 | **工作量**: 2h | **风险**: 低

**改动**:

```tsx
<Link href="/explore" prefetch={true}>
  Explore
</Link>
```

为所有导航链接添加 `prefetch`，提升页面切换速度。

---

#### 2.3.3 优化字体加载

**优先级**: P3 | **工作量**: 2h | **风险**: 低

**改动**: 使用 `next/font` 的 `preload` 选项，确保关键字体优先加载。

---

## 第三阶段：体验升级（Week 5-7）

### 3.1 设计系统升级

#### 3.1.1 添加亮色模式支持

**优先级**: P2 | **工作量**: 8h | **风险**: 中

**方案**:

```css
:root {
  /* 暗色模式（默认） */
  --color-bg: #0b0d10;
  --color-fg: #e6edf3;
  /* ... */
}

:root[data-theme='light'] {
  --color-bg: #ffffff;
  --color-fg: #1a1a1a;
  --color-fg-2: #4a4a4a;
  --color-muted: #8a8a8a;
  --color-dim: #d0d0d0;
  --color-accent: #2563eb;
  --color-accent-2: #059669;
  /* ... */
}
```

**实现**:

- 添加主题切换按钮
- 使用 `localStorage` 保存用户偏好
- 尊重 `prefers-color-scheme` 系统设置

---

#### 3.1.2 动效精细化

**优先级**: P2 | **工作量**: 6h | **风险**: 低

**改进清单**:

1. **页面过渡动画** — 使用 Framer Motion 实现页面切换效果
2. **列表加载动画** — 骨架屏 + 淡入效果
3. **微交互** — 按钮悬停、卡片浮起、图标动画
4. **滚动动画** — 元素进入视口时的渐显效果

**工具**: Framer Motion 或 CSS `@keyframes`

---

#### 3.1.3 响应式优化

**优先级**: P2 | **工作量**: 4h | **风险**: 低

**改进清单**:

1. **移动端表格** — 改为卡片布局，避免横向滚动
2. **触摸优化** — 增大点击区域、优化手势
3. **断点统一** — 全部使用 Tailwind 断点，移除 CSS 媒体查询
4. **字体缩放** — 使用 `clamp()` 实现流体排版

---

### 3.2 可访问性增强

#### 3.2.1 完善 ARIA 标签

**优先级**: P2 | **工作量**: 3h | **风险**: 低

**改动清单**:

- `LanguageSwitcher` — 添加 `aria-labelledby` 关联触发器
- `ProjectTable` — 添加 `aria-describedby` 说明表格用途
- `TreeSidebar` — 为树形结构添加 `role="tree"` 和 `role="treeitem"`
- 所有图标按钮 — 添加 `aria-label`

---

#### 3.2.2 简化键盘导航

**优先级**: P2 | **工作量**: 4h | **风险**: 中

**方案**: 使用 Radix UI 或 Headless UI 的无障碍组件替代手动实现

**收益**: 减少代码量、提升可访问性、降低维护成本

---

#### 3.2.3 添加屏幕阅读器优化

**优先级**: P3 | **工作量**: 3h | **风险**: 低

**改进**:

- 为动态内容添加 `aria-live` 区域
- 优化焦点管理（模态框、抽屉）
- 添加跳过导航链接（已实现，验证效果）

---

### 3.3 国际化完善

#### 3.3.1 添加更多语言支持

**优先级**: P3 | **工作量**: 8h | **风险**: 低

**候选语言**:

- 韩语 (ko)
- 西班牙语 (es)
- 法语 (fr)
- 德语 (de)

**实现**: 扩展 `i18n.ts`，添加翻译文件，更新语言切换器。

---

#### 3.3.2 RTL 支持

**优先级**: P3 | **工作量**: 4h | **风险**: 中

**改动**:

- 添加阿拉伯语 (ar) 翻译
- 使用 CSS `dir` 属性切换布局方向
- 测试 RTL 布局下的组件表现

---

### 3.4 搜索功能增强

#### 3.4.1 添加全文搜索

**优先级**: P2 | **工作量**: 6h | **风险**: 中

**方案**: 使用 Fuse.js 实现客户端模糊搜索

**功能**:

- 搜索项目名称、描述、标签
- 支持拼音搜索（中文）
- 搜索结果高亮
- 搜索历史（localStorage）

---

#### 3.4.2 添加筛选器

**优先级**: P2 | **工作量**: 4h | **风险**: 低

**功能**:

- 按语言筛选（Go、Rust、Python 等）
- 按许可证筛选（MIT、Apache、GPL 等）
- 按活跃度筛选（最近更新时间）
- 多选筛选、组合筛选

---

## 第四阶段：高级特性（Week 8-12）

### 4.1 PWA 增强

#### 4.1.1 添加 Service Worker

**优先级**: P3 | **工作量**: 6h | **风险**: 中

**方案**: 使用 `next-pwa` 或 Workbox

**功能**:

- 离线访问所有页面
- 后台数据刷新
- 推送通知（可选）

---

#### 4.1.2 添加安装提示

**优先级**: P3 | **工作量**: 2h | **风险**: 低

**实现**: 检测 PWA 安装能力，显示安装引导。

---

### 4.2 数据分析

#### 4.2.1 添加匿名使用统计

**优先级**: P3 | **工作量**: 4h | **风险**: 低

**方案**: 使用 Plausible 或 Fathom（隐私友好）

**指标**:

- 页面浏览量
- 项目点击率
- 搜索关键词
- 语言偏好

---

#### 4.2.2 添加项目热度排行

**优先级**: P3 | **工作量**: 3h | **风险**: 低

**功能**: 基于点击量、GitHub stars 增长等计算热度，显示"本周热门"。

---

### 4.3 社区功能

#### 4.3.1 添加用户收藏

**优先级**: P3 | **工作量**: 6h | **风险**: 中

**方案**: 使用 localStorage 或后端 API

**功能**:

- 收藏项目
- 创建自定义列表
- 分享列表

---

#### 4.3.2 添加评论/反馈

**优先级**: P3 | **工作量**: 8h | **风险**: 高

**方案**: 使用 Giscus（基于 GitHub Discussions）

**功能**: 用户可对项目发表评论、报告问题。

---

### 4.4 性能极致优化

#### 4.4.1 添加 CDN 支持

**优先级**: P2 | **工作量**: 2h | **风险**: 低

**配置**: 在 `next.config.ts` 中配置 CDN 域名，确保静态资源通过 CDN 分发。

---

#### 4.4.2 优化首屏加载

**优先级**: P2 | **工作量**: 4h | **风险**: 中

**改进**:

- 关键 CSS 内联
- 非关键 JS 延迟加载
- 图片懒加载
- 预连接关键域名

---

#### 4.4.3 添加性能监控

**优先级**: P2 | **工作量**: 3h | **风险**: 低

**方案**: 集成 Sentry Performance 或 Web Vitals

**指标**:

- LCP (Largest Contentful Paint)
- FID (First Input Delay)
- CLS (Cumulative Layout Shift)

---

## 美学升级专项

### 5.1 视觉设计

#### 5.1.1 重新设计 Hero 区域

**工作量**: 4h

**方案**:

- 添加动态背景（粒子效果或渐变动画）
- 使用更大的排版（clamp 流体字体）
- 添加统计数字动画（计数效果）
- 优化 CTA 按钮设计

---

#### 5.1.2 卡片设计升级

**工作量**: 3h

**改进**:

- 添加玻璃拟态效果（glassmorphism）
- 优化阴影层次
- 添加悬停 3D 倾斜效果
- 改进渐变配色

---

#### 5.1.3 图标系统

**工作量**: 4h

**方案**: 使用 Lucide Icons 或 Heroicons，统一图标风格，添加动画效果。

---

### 5.2 动效设计

#### 5.2.1 页面过渡

**工作量**: 4h

**方案**: 使用 Framer Motion 实现：

- 淡入淡出
- 滑动过渡
- 缩放效果

---

#### 5.2.2 微交互

**工作量**: 3h

**改进**:

- 按钮点击波纹效果
- 卡片悬停浮起
- 图标旋转/缩放
- 加载动画（骨架屏 + 脉冲）

---

#### 5.2.3 滚动动画

**工作量**: 3h

**方案**: 使用 Intersection Observer 实现元素进入视口时的渐显、滑入效果。

---

## 技术债务清理

### 6.1 代码清理

#### 6.1.1 移除未使用的代码

**工作量**: 2h

**清单**:

- 未使用的导入
- 注释掉的代码
- 过时的组件
- 重复的工具函数

---

#### 6.1.2 统一代码风格

**工作量**: 2h

**改动**:

- 运行 Prettier 格式化全部代码
- 统一注释风格
- 统一命名规范

---

### 6.2 文档完善

#### 6.2.1 更新 CONTRIBUTING

**工作量**: 2h

**改进**:

- 添加开发环境搭建指南
- 添加代码规范说明
- 添加 PR 流程
- 添加测试要求

---

#### 6.2.2 添加 API 文档

**工作量**: 3h

**内容**:

- 数据模型说明
- 工具函数文档
- 组件 Props 文档
- 脚本使用说明

---

## 风险评估与缓解

### 高风险项

| 项目                | 风险         | 缓解措施                   |
| ------------------- | ------------ | -------------------------- |
| TypeScript 严格模式 | 大量类型错误 | 分步启用，逐步修复         |
| 组件重构            | 破坏现有功能 | 充分测试、渐进式重构       |
| 亮色模式            | 设计不一致   | 先完成暗色模式优化，再扩展 |
| PWA Service Worker  | 缓存问题     | 使用成熟库（Workbox）      |

### 中风险项

| 项目     | 风险     | 缓解措施                    |
| -------- | -------- | --------------------------- |
| 搜索功能 | 性能问题 | 客户端搜索，限制数据量      |
| 动效升级 | 过度动画 | 遵循 prefers-reduced-motion |
| 社区功能 | 内容审核 | 使用 GitHub 托管评论        |

---

## 成功指标

### 定量指标

| 指标                  | 当前值 | 目标值 | 测量方式        |
| --------------------- | ------ | ------ | --------------- |
| Lighthouse 性能分     | 95     | 98+    | Lighthouse CI   |
| Lighthouse 可访问性分 | 98     | 100    | Lighthouse CI   |
| 测试覆盖率            | 15%    | 80%+   | Vitest coverage |
| Bundle 大小           | 1.3MB  | <1MB   | Bundle analyzer |
| 首屏加载时间          | 1.2s   | <0.8s  | Web Vitals      |
| 页面数量（有效）      | 63     | 40+    | 移除空页面      |

### 定性指标

- [ ] 设计系统完整、一致
- [ ] 动效流畅、自然
- [ ] 响应式完美（移动端、平板、桌面）
- [ ] 可访问性符合 WCAG 2.1 AA
- [ ] 代码质量高、易维护
- [ ] 文档清晰、完整
- [ ] 用户体验流畅、愉悦

---

## 实施建议

### 优先级排序

1. **P0（立即）**: TypeScript 严格模式、依赖审计、图片优化
2. **P1（Week 1-2）**: 测试覆盖、代码重复消除、Prettier
3. **P2（Week 3-4）**: 组件重构、静态生成优化、增量更新
4. **P3（Week 5-7）**: 设计系统升级、动效、可访问性
5. **P4（Week 8-12）**: 高级特性、PWA、社区功能

### 团队协作

- **前端开发**: 组件重构、动效、响应式
- **设计**: 设计系统、亮色模式、图标
- **测试**: 单元测试、E2E 测试
- **运维**: CI/CD、性能监控、CDN

### 里程碑

| 时间    | 里程碑       | 交付物                          |
| ------- | ------------ | ------------------------------- |
| Week 2  | 基础加固完成 | 类型安全、测试覆盖 60%、CI 完善 |
| Week 4  | 架构优化完成 | 组件重构、性能优化、数据层改进  |
| Week 7  | 体验升级完成 | 设计系统、动效、可访问性、搜索  |
| Week 12 | 高级特性完成 | PWA、社区功能、性能极致优化     |

---

## 附录

### A. 技术栈建议

| 类别   | 推荐          | 理由                       |
| ------ | ------------- | -------------------------- |
| 动画   | Framer Motion | 声明式、性能优、React 友好 |
| 图标   | Lucide Icons  | 统一风格、可定制、轻量     |
| 测试   | Vitest + RTL  | 快速、现代、生态好         |
| 格式化 | Prettier      | 行业标准、零配置           |
| 监控   | Sentry        | 错误 + 性能、集成好        |
| 分析   | Plausible     | 隐私友好、轻量             |
| PWA    | Workbox       | Google 出品、功能全        |

### B. 参考资源

- [Next.js Best Practices](https://nextjs.org/docs/app/building-your-application/rendering)
- [Web Vitals](https://web.dev/vitals/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Design Systems](https://www.designsystemsrepo.com/)
- [Framer Motion Documentation](https://www.framer.com/motion/)

---

**计划制定**: 2026-06-12  
**预计完成**: 2026-08-31  
**负责人**: 开发团队  
**审批**: 待确认
