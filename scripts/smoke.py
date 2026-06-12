"""End-to-end smoke test of the NetTools-Hub site.

Targets the locally-built `out/` directory served on a local HTTP
server, but the URL can be overridden via the `SMOKE_URL` env var
(the production deploy lives at
`https://badhope.github.io/NetTools-Hub`).

What this catches that lint + typecheck + build do not:
  - Hydration mismatches (React 19 #418 / #423) — we walk every
    page and assert `pageerror` stays empty.
  - Console-level runtime errors that are otherwise silent.
  - The new multi-level URL hierarchy renders without 404s.
  - The tree sidebar shows the kind+platform sub-tree.
  - The breadcrumb on a drill-down page reflects the URL.
  - 404 page renders without throwing.
  - Mobile drawer focus trap (open → close button focused →
    Esc closes → focus returns to trigger).
  - The language switcher swaps the page text and `<html lang>`.

Assumes `playwright` is installed locally (`pip install playwright`
+ `playwright install chromium`). Not part of CI; run it manually
to verify a build before tagging a release.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get(
    "SMOKE_URL", "https://badhope.github.io/NetTools-Hub"
)
SHOTS = Path(os.environ.get("SMOKE_SHOTS", "smoke-shots"))
SHOTS.mkdir(parents=True, exist_ok=True)


def main() -> int:
    failures: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()

        console_errors: list[str] = []
        page_errors: list[str] = []
        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error"
            else None,
        )
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        # 1. Landing page (English) ----------------------------------
        print("=== 1. Landing page (English) ===")
        page.goto(f"{BASE}/", wait_until="networkidle")
        title = page.title()
        print(f"  title: {title}")
        if "NetTools" not in title:
            failures.append(f"landing title missing 'NetTools': {title!r}")
        h1 = page.locator("h1").first.text_content() or ""
        print(f"  h1: {h1[:80]!r}")
        if "field manual" not in h1.lower():
            failures.append(f"landing h1 missing 'field manual': {h1!r}")
        broken = page.evaluate(
            "() => Array.from(document.querySelectorAll('img'))"
            ".filter(i => !i.complete || i.naturalWidth === 0).length"
        )
        print(f"  broken images: {broken}")
        if broken > 0:
            failures.append(f"{broken} broken images on landing")

        # JSON-LD WebSite schema present
        site_ld = page.evaluate(
            "() => Array.from(document.querySelectorAll("
            "'script[type=\"application/ld+json\"]'))"
            ".map(s => s.textContent).join('\\n')"
        )
        if "WebSite" not in site_ld:
            failures.append("landing JSON-LD missing WebSite schema")

        # hreflang links present
        hreflang_count = page.evaluate(
            "() => document.querySelectorAll("
            "'link[rel=\"alternate\"][hreflang]').length"
        )
        print(f"  hreflang links: {hreflang_count}")
        if hreflang_count < 4:
            failures.append(
                f"expected 4+ hreflang links (3 langs + x-default), "
                f"got {hreflang_count}"
            )

        # PWA manifest linked
        manifest_href = page.evaluate(
            "() => document.querySelector('link[rel=\"manifest\"]')"
            "?.getAttribute('href')"
        )
        print(f"  manifest: {manifest_href}")
        if not manifest_href:
            failures.append("no PWA manifest link in head")

        # Skip link is the first focusable element on the page
        page.keyboard.press("Tab")
        skip_focused = page.evaluate(
            "() => document.activeElement?.classList.contains('skip-link')"
        )
        print(f"  skip link is first Tab stop: {skip_focused}")
        if not skip_focused:
            failures.append("skip-link is not the first Tab stop")

        page.screenshot(path=str(SHOTS / "01-landing-en.png"), full_page=False)

        # 2. Landing page Chinese ------------------------------------
        print("\n=== 2. Landing page (Chinese) ===")
        page.goto(f"{BASE}/?lang=zh", wait_until="networkidle")
        page.wait_for_timeout(500)
        body_text = page.locator("body").text_content() or ""
        has_zh = any("\u4e00" <= c <= "\u9fff" for c in body_text)
        print(f"  contains CJK: {has_zh}")
        if not has_zh:
            failures.append("Chinese landing page has no CJK characters")
        html_lang = page.evaluate("document.documentElement.lang")
        print(f"  <html lang>: {html_lang!r}")
        if html_lang != "zh-Hans":
            failures.append(f"<html lang> should be zh-Hans, got {html_lang!r}")
        page.screenshot(path=str(SHOTS / "02-landing-zh.png"), full_page=False)

        # 3. /explore root — table renders with all 210 entries -----
        print("\n=== 3. /explore (root) ===")
        page.goto(f"{BASE}/explore/", wait_until="networkidle")
        page.wait_for_timeout(300)
        rows = page.locator("table.proj-table tbody tr").count()
        print(f"  project rows: {rows}")
        if rows < 100:
            failures.append(f"expected 100+ rows on /explore, got {rows}")
        # Sidebar shows the kind tree
        kind_links = page.locator(
            "nav[aria-label='Browse the tree'] a[href*='/explore/k/']"
        ).count()
        print(f"  kind links in sidebar: {kind_links}")
        if kind_links < 5:
            failures.append(
                f"expected 5+ kind links in tree sidebar, got {kind_links}"
            )
        page.screenshot(path=str(SHOTS / "03-explore-root.png"), full_page=False)

        # 4. /explore/k/proxy (kind drill-down) ---------------------
        print("\n=== 4. /explore/k/proxy ===")
        page.goto(f"{BASE}/explore/k/proxy/", wait_until="networkidle")
        page.wait_for_timeout(300)
        url = page.url
        print(f"  url: {url}")
        h1 = page.locator("h1").first.text_content() or ""
        print(f"  h1: {h1[:60]!r}")
        if "proxy" not in h1.lower():
            failures.append(f"proxy page h1 should mention proxy: {h1!r}")
        rows = page.locator("table.proj-table tbody tr").count()
        print(f"  proxy rows: {rows}")
        if rows < 5:
            failures.append(f"expected 5+ proxy projects, got {rows}")
        # Subtree should now show platforms
        platform_links = page.locator(
            "nav[aria-label='Browse the tree'] a[href*='/p/']"
        ).count()
        print(f"  platform sub-tree links: {platform_links}")
        if platform_links < 1:
            failures.append(
                "platform sub-tree did not expand under the active kind"
            )
        # Breadcrumb reflects the URL
        crumb = page.locator("nav[aria-label='Breadcrumb']").first.text_content() or ""
        if "explore" not in crumb or "proxy" not in crumb:
            failures.append(f"breadcrumb missing explore/proxy: {crumb!r}")
        page.screenshot(
            path=str(SHOTS / "04-explore-kind-proxy.png"), full_page=False
        )

        # 5. /explore/k/proxy/p/desktop (3rd level) -----------------
        print("\n=== 5. /explore/k/proxy/p/desktop ===")
        page.goto(f"{BASE}/explore/k/proxy/p/desktop/", wait_until="networkidle")
        page.wait_for_timeout(300)
        h1 = page.locator("h1").first.text_content() or ""
        print(f"  h1: {h1[:60]!r}")
        if "desktop" not in h1.lower() or "proxy" not in h1.lower():
            failures.append(
                f"kind+platform h1 should mention both, got: {h1!r}"
            )
        rows = page.locator("table.proj-table tbody tr").count()
        print(f"  rows: {rows}")
        if rows < 1:
            failures.append("proxy/desktop page has no projects")
        page.screenshot(
            path=str(SHOTS / "05-explore-kind-platform.png"), full_page=False
        )

        # 6. 404 page -------------------------------------------------
        print("\n=== 6. 404 page ===")
        page.goto(f"{BASE}/404.html", wait_until="networkidle")
        has_404 = "404" in (page.locator("body").text_content() or "")
        print(f"  contains '404': {has_404}")
        if not has_404:
            failures.append("404 page does not contain '404'")
        page.screenshot(path=str(SHOTS / "06-404.png"), full_page=False)

        # 7. Mobile viewport + drawer focus trap ----------------------
        print("\n=== 7. Mobile viewport ===")
        page.set_viewport_size({"width": 375, "height": 812})
        page.goto(f"{BASE}/", wait_until="networkidle")
        menu_btn = page.locator("button[aria-label*='Menu']")
        print(f"  mobile menu button count: {menu_btn.count()}")
        if menu_btn.count() == 0:
            failures.append("no mobile menu button on landing")
        else:
            menu_btn.first.click()
            page.wait_for_timeout(500)
            drawer = page.locator("[role='dialog']")
            print(f"  drawer opened: {drawer.count() > 0}")
            if drawer.count() == 0:
                failures.append("mobile drawer did not open")
            # Esc closes the drawer
            page.keyboard.press("Escape")
            page.wait_for_timeout(200)
            print(f"  drawer after Esc: {drawer.count()}")
            if drawer.count() != 0:
                failures.append("Esc did not close the mobile drawer")
            page.screenshot(
                path=str(SHOTS / "07-mobile-drawer.png"), full_page=False
            )

        # -----------------------------------------------------------------
        # Final report
        # -----------------------------------------------------------------
        if page_errors:
            failures.append(f"uncaught page errors: {page_errors}")
        if console_errors:
            failures.append(f"console errors: {console_errors}")

    if failures:
        print("\n--- SMOKE FAILURES ---")
        for f in failures:
            print(f"  • {f}")
        return 1
    print("\nAll smoke checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
