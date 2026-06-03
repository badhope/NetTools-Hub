# Security & Code-Quality Audit — NetTools-Hub

**Date:** 2026-06-02
**Scope:** `badhope/NetTools-Hub` @ `a0d8b0c` (main)
**Auditor:** MiniMax-M3 + `security-best-practices` skill
**Stack:** Next.js 16.2.6 (static export) · React 19.2.4 · TypeScript 5.9.3 · Tailwind v4 · GitHub Pages

---

## Executive summary

NetTools-Hub is a **purely static**, **all-self-hosted** site with no server-side
runtime, no auth, no PII, and no user-generated content. The classic frontend
threat surface (XSS, CSRF, token storage, DOM clobbering) is therefore **very
small** and the code is well-written for that surface.

**The good news first:**

- ✅ Zero dangerous sinks: no `dangerouslySetInnerHTML`, no `innerHTML`, no `eval`,
  no `Function()`, no `document.write`, no `setTimeout("…")` string forms.
- ✅ Zero secrets in the bundle: no `process.env.*` / `NEXT_PUBLIC_*` / hard-coded
  API keys / tokens anywhere in `src/`.
- ✅ `localStorage` is used in exactly **3 places**, all for the **non-sensitive**
  `nethub.lang` UI preference, wrapped in `try/catch` for storage-disabled browsers.
- ✅ `target="_blank"` always paired with `rel="noopener noreferrer"` (only 1
  occurrence, in `src/components/project-card.tsx:35`).
- ✅ `window.location` is **only read** (URL parsing for `?lang=` / `?category=`
  / `?q=`); there is **no** `window.location = …` assignment anywhere.
- ✅ No `postMessage` senders or `onmessage` listeners.
- ✅ All 124 project URLs use `http:` / `https:` schemes (verified by automated
  scan — zero `javascript:` / `data:` / `vbscript:` URLs in `data/projects.json`).
- ✅ No HTML markup in any `data/projects.json` field (name / description / tags /
  highlights / author / language / license are all plain text).
- ✅ No duplicate project IDs.
- ✅ `console.*` calls limited to two `console.error(error)` in the React error
  boundaries (`src/app/error.tsx:13`, `src/app/explore/error.tsx:13`) — no
  leaked secrets / tokens / PII.
- ✅ No untracked files, no `TODO` / `FIXME` / `XXX` comments.
- ✅ `output: "export"` = no Node runtime attack surface.
- ✅ `pnpm install --frozen-lockfile` in CI = reproducible builds.
- ✅ `engines.node >= 22` + `engines.pnpm >= 10` + `.nvmrc` + `.npmrc`
  (`package-manager=pnpm@10`) all aligned.
- ✅ Dependabot covers **both** `npm` and `github-actions` ecosystems.
- ✅ Release Drafter is the right tool for this cadence.
- ✅ Issue templates route "how do I…" to Discussions; security reports go to
  GitHub Security Advisories (no public-Issue leakage path).
- ✅ CODEOWNERS, SECURITY.md, CONTRIBUTING (en + zh + ja), PR template,
  RELEASES, CITATION.cff all in place and consistent.

**Bottom line:** the actual security risk is **Low**. Most findings below are
**defense-in-depth improvements** and **code-quality polish**, not live
vulnerabilities.

Findings are grouped by severity. Each finding has a stable ID for cross-referencing.

---

## 🔴 Critical (0)

**None.** The repo has no critical-severity issues.

---

## 🟠 High (3)

### H-1 · No Content-Security-Policy
**Rule:** `JS-CSP-001` / `REACT-CSP-001` (Medium–High, depending on threat model)
**Where:** Repo-wide — there is **no** `Content-Security-Policy` HTTP header
(GitHub Pages does not allow custom headers on the free tier) **and** no
`<meta http-equiv="Content-Security-Policy">` tag in `src/app/layout.tsx` /
`src/app/page.tsx` / any layout.
**Impact:** No defense-in-depth against any future XSS regression. Today the
attack surface is zero (no `dangerouslySetInnerHTML`, no `innerHTML`, no user
input rendered), so a CSP would be a belt-and-braces measure. As soon as someone
adds a Markdown renderer or a "user-submitted project" form, an XSS would have
no second line of defense.
**Fix (minimal):** Add a `<meta http-equiv="Content-Security-Policy" ...>` to
`src/app/layout.tsx`. Suggested starter policy (Tailwind v4 + Next.js 16
generated chunks, no inline event handlers, no eval):

```
default-src 'self';
script-src  'self';
style-src   'self' 'unsafe-inline';   /* Tailwind v4 emits dynamic utility classes */
img-src     'self' data: https:;
font-src    'self' data:;
connect-src 'self';
base-uri    'self';
form-action 'self';
frame-ancestors 'none';
```

Note: `frame-ancestors` and `report-uri` are **ignored** in meta-delivered CSP
(W3C CSP2). For clickjacking protection that survives deployment, the policy
should be moved to a real HTTP header at the edge (out of scope for GitHub
Pages free tier — but the meta tag still helps, and `frame-ancestors 'none'`
will at least be enforced by browsers that respect it in the absence of
headers).

### H-2 · GitHub Actions pinned to major-version tags, not SHAs
**Rule:** `REACT-SUPPLY-001` (Low) — escalated to High because one of the
workflows is on the **most dangerous trigger** (see H-3).
**Where:**
- `.github/workflows/deploy.yml` (lines 23, 26, 31, 41, 52, 58, 70):
  `actions/checkout@v4`, `actions/setup-node@v4`, `pnpm/action-setup@v4`,
  `actions/cache@v4`, `actions/configure-pages@v5`,
  `actions/upload-pages-artifact@v3`, `actions/deploy-pages@v4`.
- `.github/workflows/release-drafter.yml` (line 24):
  `release-drafter/release-drafter@v6`.
**Impact:** A compromised upstream tag (e.g., the maintainer's account or the
GitHub Actions build pipeline is breached) would automatically inject malicious
code on the next push, with no review. Dependabot will keep the tags current,
but it will **not** prevent a tag-flip attack. Pinning to a full commit SHA +
`# vX.Y.Z` comment is the GitHub-recommended hardening.
**Fix:** Replace each `@vN` with a full SHA, e.g.:

```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1
- uses: actions/setup-node@0a44ba7841725637a19e28fa30b79a866c81b0a6  # v4.0.3
- uses: pnpm/action-setup@fe02b34f77f8bc703788d5817da081398fad5dd2  # v4.0.0
- uses: actions/cache@13aacd865c20de90d75de3b17ebe84f7a17e5d4d  # v4.0.3
- uses: actions/configure-pages@9836c0c4445e3a83a686821e6e7af9ec5443de97  # v5.0.0
- uses: actions/upload-pages-artifact@56afc6e85222a9cc9e4736387ce9d1f1c3a55cd5  # v3.0.0
- uses: actions/deploy-pages@d6b9f4f8c1aa6f7c4b5e5e3a0c6e0b7e8e5a1d2f  # v4.0.0
- uses: release-drafter/release-drafter@0d22cb16c4eb9c4f1c4d8a4d4d8c4e3b8f0a4d2e  # v6.0.0
```

(SHAs above are illustrative; use the real SHAs from the actions' `@vN` tag at
the time of pinning.) Dependabot can then bump the SHAs via a `version-update`
PR, which the existing dependabot.yml (lines 37–55) already covers.

### H-3 · `pull_request_target` with `contents: write` permission
**Rule:** Known footgun for public repos (no direct rule ID, but widely
documented in the GitHub Security Lab).
**Where:** `.github/workflows/release-drafter.yml` lines 11–17.
**Evidence:**

```yaml
on:
  push:
    branches: ["main"]
  pull_request_target:
    types: [opened, reopened, synchronize, edited]
  workflow_dispatch:

permissions:
  contents: write       # ← write access to the repo
  pull-requests: read
```

**Why it is risky in general:** `pull_request_target` runs with **write** access
to the repo and the secrets of the base repo, while having access to the **head
ref** of the PR. A common attack pattern is for a malicious PR from a fork to
trick the workflow into checking out the fork's code, then exfiltrating
`secrets.GITHUB_TOKEN` or pushing to `main`. The classic mitigations are:
(a) don't `actions/checkout` PR head code in `pull_request_target`, (b) limit
to trusted actors, (c) add a `branches-ignore` filter.

**Why it is *currently* safe in this repo:** the only step in
`release-drafter.yml` calls `release-drafter/release-drafter@v6` and never
checks out the PR's source. The action only reads PR metadata via the
GitHub API. So there is **no live vulnerability** today.

**Why it is still worth fixing:**

1. The current safety depends on a single line in a single action — easy to
   change accidentally. Hardening the trigger now is cheap.
2. The action is on `@v6`, not pinned to a SHA (see H-2). A compromised
   upstream version **could** start checking out PR code.
3. There is **no `branches-ignore`** filter, so even fork PRs trigger the
   workflow (with the secrets of the base repo). That's wasted CI minutes on
   spam PRs.

**Fix:**

```yaml
on:
  push:
    branches: ["main"]
  pull_request_target:
    types: [opened, reopened, synchronize, edited]
    # Only run on PRs targeting the default branch; ignore the maintainer's
    # own PRs (they're reviewed manually anyway).
    branches-ignore:
      - "dependabot/**"
      - "renovate/**"
  workflow_dispatch:
```

Combined with H-2 (pin the action to a SHA), this brings the trigger risk to
near-zero.

---

## 🟡 Medium (8)

### M-1 · Duplicate `Lang` type across `lib/i18n.ts` and `types/project.ts`
**Where:** `src/lib/i18n.ts:1` and `src/types/project.ts:35` both define
`type Lang = "en" | "zh" | "ja"`.
**Impact:** Drift risk. If a fourth language is added (e.g. Spanish), one of
the two definitions will be updated and the other won't, leading to
non-exhaustive `switch` statements and `Record<Lang, ...>` shapes that silently
drop the new key.
**Fix:** Delete the duplicate in `src/types/project.ts` and re-export from
`@/lib/i18n` (or move the canonical definition to `src/types/` and import
in `lib/i18n.ts` — either is fine; pick one home).

### M-2 · Dead export `LANG_COOKIE` in `src/lib/i18n.ts`
**Where:** `src/lib/i18n.ts:262` — `export const LANG_COOKIE = "nettools_lang";`
is exported but never imported anywhere in the repo (verified by `grep`).
**Impact:** Dead code that hints at a "use a cookie for language preference"
design that was abandoned in favor of `localStorage`. No security impact, but
readers waste time wondering where the cookie is set.
**Fix:** Delete the export. If a cookie path is ever revisited, the constant
can be reintroduced.

### M-3 · Version mismatch: `package.json` vs `data/projects.json`
**Where:** `package.json:3` is `0.3.0`, but `data/projects.json` `version`
field is `1.0.0` (and `lastUpdated` is `2026-06-01`).
**Impact:** Two unrelated "version" concepts in two files. Maintainers
updating one will forget the other.
**Fix:** Decide whether `data/projects.json` should carry a "data schema
version" (independent of the app version) or a "data snapshot timestamp". If
the former, rename the field to `schemaVersion` and document in
`docs/DATA-MODEL.md`; if the latter, sync to `package.json`.

### M-4 · `orcid: ""` in `CITATION.cff`
**Where:** `CITATION.cff:38`.
**Impact:** ORCID identifiers must be a URL like `https://orcid.org/0000-0000-0000-0000` or omitted entirely. An empty string may be silently accepted by GitHub's citation renderer, but downstream tooling (citation managers, ORCID API consumers) will reject it.
**Fix:** Delete the `orcid: ""` line.

### M-5 · Misleading comment in `pnpm-workspace.yaml`
**Where:** `pnpm-workspace.yaml:1-4` says `sharp` is needed for "Next.js
image optimisation", but `next.config.ts:11` has `images: { unoptimized: true }`.
**Impact:** Misleading documentation; future maintainers will be confused about
why `sharp` is allowed to run install scripts.
**Fix:** Either remove `sharp` from `ignoredBuiltDependencies` (it's not
actually needed for the static export), or rewrite the comment to explain the
historical reason.

### M-6 · `import rawData from "@/../data/projects.json";`
**Where:** `src/lib/projects.ts:2`.
**Impact:** The `@/../` traversal is unusual and visually confusing. It works
because of `tsconfig.json`'s `paths: { "@/*": ["./src/*"] }` plus Node's path
resolution, but the intent isn't obvious.
**Fix:** Either (a) keep the data file inside `src/data/projects.json` so it
imports as `@/data/projects.json`, or (b) use a relative path
`../../data/projects.json`. Option (a) is more consistent with the existing
`@/` alias and reduces path-traversal confusion.

### M-7 · `FUNDING.yml` is 100% commented out
**Where:** `.github/FUNDING.yml` is 40 lines of commented-out platform stubs.
**Impact:** Dead file; no "Sponsor" button will appear on the repo, but a
maintainer reading the file will wonder if funding is meant to be enabled.
**Fix:** Delete the file until a funding platform is actually in use. (If
deleting feels too permanent, replace with a one-line `# Funding disabled for
now — see .github/SUPPORT.md.` and leave it.)

### M-8 · Lint reports 4 errors + 1 warning, build is green
**Where:** `pnpm lint` output (verified after fresh `pnpm install`):
- `src/components/explore-content.tsx:34:31` — `react-hooks/set-state-in-effect`
  (error)
- `src/components/landing-content.tsx:22:38` — `react-hooks/set-state-in-effect`
  (error)
- `src/components/landing-content.tsx:23:6` — `react-hooks/exhaustive-deps`
  (warning; missing dep `lang`)
- `src/components/search-bar.tsx:17:5` — `react-hooks/set-state-in-effect`
  (error)
- `src/components/search-bar.tsx:18:2` — `react-hooks/exhaustive-deps` not
  flagged here because `setInputValue(value)` is the only body; the rule
  treats the inner state mirror as the only "intended" pattern.
- `src/components/sidebar.tsx:24:9` — `react-hooks/set-state-in-effect`
  (error)

**Impact:** All four errors are a new React 19 rule
(`react-hooks/set-state-in-effect`) that flags the anti-pattern of
synchronously calling `setState` inside a `useEffect` body — it causes
cascading renders. The build is unaffected (Turbopack is more lenient than
`next build` with ESLint), and `pnpm lint` exits non-zero.

None of the four are actual bugs — they are a code-smell that React 19
introduces a stricter rule for. Specifically:

- `landing-content.tsx:20-23` reads `?lang=` once on mount; the closure
  captures the initial `lang` ("en") and the inner `if (fromUrl !== lang)` is
  correct. Functional, but the React 19 rule wants a ref instead.
- `search-bar.tsx:16-18` mirrors a `value` prop into `inputValue` state
  (debounced search). Standard but a known anti-pattern — `useDeferredValue`
  is the React 19 idiom.
- `sidebar.tsx:20-27` auto-expands a group when `activeCategory` changes.
  This is the "sync derived state to URL" pattern that React 19 now
  discourages in favor of lifting state up.
- `explore-content.tsx:30-41` reads URL params once on mount. Same as the
  landing page; same fix path.

**Fix (one PR, four small diffs):**

1. `landing-content.tsx` — use a `useRef` for the initial check, or remove
   the effect and read the URL on first render via a `useState(() => …)`
   initializer.
2. `search-bar.tsx` — replace the `[value] → [inputValue]` mirror with
   `const [inputValue, setInputValue] = useDeferredValue(value)` (or simply
   lift the debounce into the parent and remove the local state).
3. `sidebar.tsx` — derive the collapsed map at render time
   (`const collapsed = activeCategory ? { ...defaultCollapsed,
   [activeGroupId]: false } : defaultCollapsed`) and drop the effect
   entirely.
4. `explore-content.tsx` — initialize state from `window.location.search`
   via `useState(() => parseFromUrl())` lazy initializers instead of an
   effect; or use Next.js `useSearchParams()` from `next/navigation` (which
   is the framework-recommended path for App Router).

These changes are all **non-functional** — they silence the new rule without
altering behavior. A separate commit per file is the cleanest approach.

---

## 🟢 Low (5)

### L-1 · `tsconfig.json` lacks `noUncheckedIndexedAccess`
**Where:** `tsconfig.json:6-23` — `strict: true` is on, but
`noUncheckedIndexedAccess: true` is not.
**Impact:** `array[i]` is typed as `T`, not `T | undefined`. The codebase
relies on `params.get(...)`, `Object.values(...)`, and `categories[slug]`
lookups that can return `undefined` — currently mitigated by the
`(x as any)` pattern in `landing-content.tsx:48` and by the
`categories[slug]?.icon` defensive access in `explore-content.tsx:122`. With
`noUncheckedIndexedAccess: true` the compiler would catch a missing
`?.` chain.
**Fix:** Add `"noUncheckedIndexedAccess": true` to `compilerOptions` and fix
any newly-flagged access. Likely 5–10 small touchups.

### L-2 · No `pnpm audit` step in CI
**Where:** `.github/workflows/deploy.yml:48-49` only runs
`pnpm install --frozen-lockfile`; no `pnpm audit --prod` follow-up.
**Impact:** Vulnerable dependencies are only surfaced by Dependabot's weekly
PR. A fresh advisory that lands mid-week won't block a deploy.
**Fix:** Add a step that runs `pnpm audit --prod --audit-level=high` and
fails the build on a Critical/High advisory. Dependabot continues to drive
the weekly remediation; this just adds a safety net.

### L-3 · `pino`-style logging is absent, but the two `console.error` sites
        have no structured context
**Where:** `src/app/error.tsx:13` and `src/app/explore/error.tsx:13`.
**Impact:** Only useful in DevTools. There's no remote error reporting, so
production users who hit a runtime error are invisible to the maintainer.
**Fix (optional):** For a static site, the realistic options are (a)
GitHub Issue templates that pre-fill the URL + browser, (b) a small
client-side reporter that POSTs to a serverless function, or (c) a free
tier of Sentry / GlitchTip. Not a security issue, just visibility.

### L-4 · Issue template dropdown defaults not enforced
**Where:** All five issue templates (`bug_report.yml`, `feature_request.yml`,
`project_submission.yml`, `translation.yml`, `question.yml`) have a
`language` dropdown with **no `default` attribute**.
**Impact:** Submitters often skip dropdowns; without a default the value is
empty, and the template's `validations: required: true` is the only
enforcement.
**Fix:** Add `default: 0` (or `default: "English"`) to each `language`
dropdown's `attributes`.

### L-5 · `LANG_COOKIE` constant name is misleading after removal
**Where:** Same as M-2 — once the constant is deleted, the file no longer
references "cookie" anywhere, which is correct. Just flagging that
`LANG_COOKIE = "nettools_lang"` does **not** match the actual storage key
`"nethub.lang"` used in `set-html-lang.tsx:34`,
`landing-content.tsx:33`, and `explore-content.tsx:57`. If the export is
ever restored, this is a footgun.

---

## ✅ Things that were checked and are **clean**

| Area | Result |
| --- | --- |
| `dangerouslySetInnerHTML` / `__html:` | ✅ none |
| `innerHTML` / `outerHTML` / `insertAdjacentHTML` | ✅ none |
| `eval(` / `new Function(` / `setTimeout("...")` | ✅ none |
| `document.write` / `document.writeln` | ✅ none |
| `process.env.*` / `NEXT_PUBLIC_*` in `src/` | ✅ none |
| Hard-coded secrets / API keys / tokens | ✅ none |
| `localStorage` keys containing `token` / `jwt` / `session` / `auth` / `refresh` | ✅ only `nethub.lang` |
| `postMessage(..., "*")` or `onmessage` listeners | ✅ none |
| `target="_blank"` without `rel="noopener noreferrer"` | ✅ always paired |
| `window.location = X` / `location.replace(X)` / `location.assign(X)` | ✅ none (only read) |
| HTML markup in `data/projects.json` | ✅ none |
| `javascript:` / `data:text/html` / `vbscript:` URLs in `data/projects.json` | ✅ none (all 124 use `http`/`https`) |
| Duplicate `id` in `data/projects.json` | ✅ none |
| `console.log` of sensitive data | ✅ only `console.error` in error boundaries |
| Untracked / TODO / FIXME files | ✅ none |
| Third-party CDN scripts (no SRI needed because all scripts are self-hosted) | ✅ clean |
| Service workers | ✅ none registered |
| `setAttribute("on...")` from string | ✅ none |
| DOM clobbering via `window.X || fallback` | ✅ `window.localStorage` / `window.history` / `window.location` are all explicit property access, not `||` fallbacks |
| Open redirect via `?next=` / `?returnTo=` | ✅ only `?lang=` and `?category=` are read; both are validated against a small allowlist before use |
| `tsconfig.json` `strict: true` | ✅ on |
| ESLint flat config + `eslint-config-next` | ✅ wired up |
| Reproducible CI builds (`pnpm install --frozen-lockfile`) | ✅ on |
| Engines field + `.nvmrc` + `.npmrc` aligned | ✅ Node 22, pnpm 10 |
| CODEOWNERS | ✅ all paths owned by `@badhope` |
| SECURITY.md disclosure policy | ✅ private GitHub Advisories only |
| `pull_request_target` script execution | ✅ release-drafter does not checkout PR head code |
| Lockfile present and tracked | ✅ `pnpm-lock.yaml` |
| `.gitignore` covers `.env*` (with `!.env.example` allowlist) | ✅ |

---

## Recommended fix order

1. **H-2 + H-3** (one commit each) — pin Actions to SHAs and add
   `branches-ignore` to `release-drafter.yml`. Pure defense-in-depth, no
   behavior change.
2. **H-1** — add the CSP meta tag. One-line change to
   `src/app/layout.tsx`.
3. **M-1 + M-2** — one commit, remove duplicate `Lang` and dead `LANG_COOKIE`.
4. **M-3 + M-4 + M-5 + M-6 + M-7** — meta-cleanup commit (or one commit per
   file if you prefer fine-grained history). Pure documentation.
5. **M-8** — fix the four `react-hooks/set-state-in-effect` errors in a
   single PR. Slightly larger diff but still localized.
6. **L-1** — turn on `noUncheckedIndexedAccess`. Small follow-up after M-8.
7. **L-2** — add a `pnpm audit` step to `deploy.yml`.
8. **L-3, L-4, L-5** — only if the maintainer has the time; none block
   shipping.

After fixes 1–6, the next audit cycle should pass with **zero** findings
above `Low`.

---

## Notes on the audit methodology

- **Skill used:** `security-best-practices` (loaded automatically per
  user-rule "在任何任务任何步骤看一下有没有相关的 skill 可用").
- **References consulted:** `javascript-typescript-react-web-frontend-security.md`
  and `javascript-general-web-frontend-security.md` (the two most relevant
  docs in the skill's reference library for a static React 19 / Next.js
  export app). The Next.js-specific doc was **not** relevant because the
  project uses `output: "export"` — there is no server runtime.
- **Verification commands used:**
  - `pnpm build` and `pnpm lint` from a clean `pnpm install --frozen-lockfile`.
  - `grep` sweeps for risky sinks / secrets / unsafe URL sinks.
  - Python script to scan `data/projects.json` for HTML markup, non-`http(s)`
    URLs, and duplicate IDs.
  - `git status --short` for untracked / dead files.
  - Manual read of every file under `src/`, `.github/`, `docs/`, and the
    root metadata.
- **Out of scope:** third-party projects linked from `data/projects.json` (the
  project itself acknowledges these in `SECURITY.md` § Out of scope), and
  the GitHub Pages infrastructure (also acknowledged in `SECURITY.md`).
