# Security Policy

## 🛡 Supported Versions

NetTools Hub is a **purely static** navigation platform — it ships pre-rendered HTML, CSS, and JavaScript to GitHub Pages. There is no server, no database, no user accounts, and no API keys stored in the application code or the deployed bundle.

| Version | Supported |
| --- | --- |
| `main` (latest) | ✅ Active |
| Older deployments | ⚠️ Best-effort — re-deploy from `main` |

Because the project is static and dependency-light, security exposure is limited to:

1. **Build-time supply chain** — npm packages and GitHub Actions versions pinned in `pnpm-lock.yaml` and `.github/workflows/deploy.yml`.
2. **Content integrity of `data/projects.json`** — links and descriptions only; no executable code.

## 📣 Reporting a Vulnerability

**Please do not open a public GitHub Issue for security-sensitive reports.**

The recommended private channel is **GitHub Security Advisories**:
<https://github.com/badhope/NetTools-Hub/security/advisories/new>

> 📌 **No dedicated security email** is published. Using GitHub Advisories
> keeps the report encrypted, scoped, and tracked — please prefer it.

### What to include

- A clear, descriptive title
- A reproduction path (URL, build command, browser, OS)
- An assessment of **impact** and **likelihood**
- A suggested fix or mitigation, if you have one
- Whether you'd like to be credited in the advisory

### What to **expect**

| Step | Timeline |
| --- | --- |
| Acknowledgement | within **3 business days** |
| Initial triage & severity assessment | within **7 business days** |
| Patch (or documented mitigation) | within **30 days** for `Critical` / `High` issues |
| Public disclosure | coordinated with the reporter, typically **after** a fix is shipped |

We follow [coordinated disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure) — please give us a reasonable window before publishing details.

## 🔐 Scope of This Project

### In scope

- Cross-site scripting (XSS) via the static build, sitemap, or robots output
- Content injection in `data/projects.json` that could lead to XSS in the deployed site
- Vulnerable dependencies in `package.json` / `pnpm-lock.yaml`
- Tampered CI artifacts or compromised GitHub Actions versions
- Unsafe defaults in `.github/workflows/deploy.yml` (e.g. overly broad `permissions:`)

### Out of scope

- **Third-party projects** linked from `data/projects.json` — please report those to the upstream maintainers directly.
- **GitHub Pages infrastructure** itself — escalate to GitHub Support.
- **Network policies of the user's environment** — the project has no influence over which tools users can or cannot run.

## 🧰 Security Best Practices for Contributors

- **Never commit secrets** (API keys, tokens, credentials) — the repo is public and history rewrites are destructive.
  Even a one-line `.env` is enough; use `.env.example` as a template.
- **Pin GitHub Actions** to a full commit SHA in `.github/workflows/deploy.yml` for high-risk steps, or stay on a current major tag (`@v4`) for routine ones.
- **Validate `data/projects.json`** with `pnpm lint` before pushing — schema drift can break the build.
- **Don't load remote scripts** at runtime in components; the project is intentionally self-hosted.

## 🪪 Disclosure & Credits

We are happy to credit reporters in the security advisory (or to keep it anonymous — your choice).
By submitting a report, you confirm the information is provided in good faith and that you will keep the details confidential until coordinated disclosure.

Thank you for helping keep NetTools Hub and its users safe. 🙏
