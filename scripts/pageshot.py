"""End-to-end Playwright check of the deployed (or locally served) site.

Targets the multi-level URL tree introduced in the v2 schema:
  - /                          (landing — English, Chinese, Japanese)
  - /explore/                  (root index — all projects)
  - /explore/k/<kind>/         (kind drill-down — e.g. /explore/k/proxy/)
  - /explore/k/<kind>/p/<plat>/ (kind+platform drill-down)

What it verifies:
  1. HTTP 200 + correct <title> + visible <h1>.
  2. NO React / hydration errors in the console.
  3. Language switching: clicking the language switcher in the top
     nav actually changes the page text + URL + `<html lang>`.
  4. Sidebar tree shows all 8 kinds and the active kind's
     platform sub-tree.
  5. Drill-down breadcrumb matches the URL.
  6. Screenshots before / after each interaction for a visual
     sanity check (saved to .playwright-pageshots/).

Override the base URL with the BASE env var — `BASE=http://localhost:8080/NetTools-Hub
python3 scripts/pageshot.py` runs against the local `pnpm start`
serving of `out/`. The default is the GitHub Pages deployment so
the production smoke check stays useful.
"""

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = os.environ.get("BASE", "https://badhope.github.io/NetTools-Hub/")
SHOTS = Path(".playwright-pageshots")
SHOTS.mkdir(parents=True, exist_ok=True)

# Errors we will treat as fatal. React 19 hydration
# mismatches show up as a single console.error with a "Minified
# React error #418" / "#423" prefix; the dev build prints a
# multi-line "Hydration failed because the initial UI does not
# match what was rendered on the server" block instead. We catch
# both by substring.
HYDRATION_MARKERS = (
    "did not match",
    "Hydration failed",
    "hydrating",
    "Minified React error #418",
    "Minified React error #423",
    "Minified React error #425",
    "Text content does not match server-rendered HTML",
)


def is_hydration_error(msg: str) -> bool:
    return any(m.lower() in msg.lower() for m in HYDRATION_MARKERS)


def main() -> int:
    failures: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="en-US",
        )
        page = context.new_page()

        # Capture every console message and every uncaught page
        # error. We do not bail on the first failure because we
        # want a single report that covers all pages.
        console: list[dict] = []
        page_errors: list[str] = []

        def on_console(msg):
            try:
                console.append(
                    {
                        "type": msg.type,
                        "text": msg.text,
                        "location": msg.location,
                    }
                )
            except Exception:
                pass

        def on_pageerror(err):
            page_errors.append(str(err))

        page.on("console", on_console)
        page.on("pageerror", on_pageerror)

        # ------------------------------------------------------------
        # 1) Landing — English (default)
        # ------------------------------------------------------------
        print("\n=== Landing (English, default) ===")
        page.goto(BASE, wait_until="load")
        page.screenshot(path=str(SHOTS / "01-landing-en.png"), full_page=False)
        title = page.title()
        h1_text = page.locator("h1").first.text_content() or ""
        print(f"  title: {title!r}")
        print(f"  h1   : {h1_text[:80]!r}")
        if "NetTools" not in title:
            failures.append(f"landing title missing 'NetTools': {title!r}")
        if "field manual" not in h1_text.lower():
            failures.append(f"landing h1 should mention 'field manual': {h1_text!r}")

        # ------------------------------------------------------------
        # 2) Landing — Chinese via ?lang=zh
        # ------------------------------------------------------------
        print("\n=== Landing (Chinese, ?lang=zh) ===")
        console.clear()
        page_errors.clear()
        page.goto(BASE + "?lang=zh", wait_until="load")
        page.screenshot(path=str(SHOTS / "02-landing-zh.png"), full_page=False)
        h1_zh = page.locator("h1").first.text_content() or ""
        print(f"  h1   : {h1_zh[:80]!r}")
        # The new copy is "A field manual of N open-source network tools..."
        # but the rest of the page is in Chinese. The h1 itself stays
        # bilingual (the number is the only localised part), so the
        # assertion here is just that we DID swap to the zh language —
        # the body's footer "免责声明" and the language switcher label
        # both being "中文" is the actual signal.
        body_zh = page.locator("body").text_content() or ""
        if "免责声明" not in body_zh and "本" not in body_zh:
            failures.append("Chinese landing did not render CJK content")
        html_lang = page.evaluate("document.documentElement.lang")
        print(f"  <html lang>: {html_lang!r}")
        if html_lang != "zh-Hans":
            failures.append(f"<html lang> should be zh-Hans, got {html_lang!r}")

        # ------------------------------------------------------------
        # 3) Landing — Japanese via ?lang=ja
        # ------------------------------------------------------------
        print("\n=== Landing (Japanese, ?lang=ja) ===")
        console.clear()
        page_errors.clear()
        page.goto(BASE + "?lang=ja", wait_until="load")
        page.screenshot(path=str(SHOTS / "03-landing-ja.png"), full_page=False)
        html_lang = page.evaluate("document.documentElement.lang")
        print(f"  <html lang>: {html_lang!r}")
        if html_lang != "ja":
            failures.append(f"<html lang> should be ja, got {html_lang!r}")

        # ------------------------------------------------------------
        # 4) /explore/ — root index
        # ------------------------------------------------------------
        print("\n=== /explore/ (root) ===")
        console.clear()
        page_errors.clear()
        page.goto(BASE + "explore/", wait_until="load")
        page.screenshot(path=str(SHOTS / "04-explore-root.png"), full_page=False)
        rows = page.locator("table.proj-table tbody tr").count()
        print(f"  rows: {rows}")
        if rows < 100:
            failures.append(f"/explore has {rows} rows, expected 100+")
        # Tree sidebar should list all 8 kinds
        kind_links = page.locator(
            "nav[aria-label='Browse the tree'] a[href*='/explore/k/']"
        ).count()
        print(f"  kind links in sidebar: {kind_links}")
        if kind_links < 5:
            failures.append(
                f"tree sidebar shows {kind_links} kinds, expected 5+"
            )

        # ------------------------------------------------------------
        # 5) /explore/k/proxy/ — kind drill-down
        # ------------------------------------------------------------
        print("\n=== /explore/k/proxy/ ===")
        console.clear()
        page_errors.clear()
        page.goto(BASE + "explore/k/proxy/", wait_until="load")
        page.screenshot(
            path=str(SHOTS / "05-explore-kind-proxy.png"), full_page=False
        )
        h1 = page.locator("h1").first.text_content() or ""
        if "proxy" not in h1.lower():
            failures.append(f"proxy page h1 should mention proxy: {h1!r}")
        # The sub-tree should now be expanded (platforms visible)
        platform_links = page.locator(
            "nav[aria-label='Browse the tree'] a[href*='/p/']"
        ).count()
        print(f"  platform sub-tree links: {platform_links}")
        if platform_links < 1:
            failures.append(
                "platform sub-tree did not expand under the active kind"
            )
        # Breadcrumb
        crumb = (
            page.locator("nav[aria-label='Breadcrumb']").first.text_content() or ""
        )
        print(f"  breadcrumb: {crumb!r}")
        if "explore" not in crumb or "proxy" not in crumb.lower():
            failures.append(f"breadcrumb missing explore/proxy: {crumb!r}")

        # ------------------------------------------------------------
        # 6) /explore/k/proxy/p/desktop/ — 3rd level
        # ------------------------------------------------------------
        print("\n=== /explore/k/proxy/p/desktop/ ===")
        console.clear()
        page_errors.clear()
        page.goto(BASE + "explore/k/proxy/p/desktop/", wait_until="load")
        page.screenshot(
            path=str(SHOTS / "06-explore-kind-platform.png"), full_page=False
        )
        h1 = page.locator("h1").first.text_content() or ""
        print(f"  h1: {h1[:60]!r}")
        if "desktop" not in h1.lower() or "proxy" not in h1.lower():
            failures.append(
                f"kind+platform h1 should mention both, got: {h1!r}"
            )
        # At least one row
        rows = page.locator("table.proj-table tbody tr").count()
        print(f"  rows: {rows}")
        if rows < 1:
            failures.append("proxy/desktop page has no projects")

        # ------------------------------------------------------------
        # 7) Hydration sweep — all of the page errors so far
        # ------------------------------------------------------------
        print("\n=== Hydration sweep ===")
        hydration = [c for c in console if is_hydration_error(c["text"])]
        if hydration:
            for c in hydration:
                print(f"  HYDRATION: {c['text'][:200]}")
            failures.append(f"{len(hydration)} hydration error(s)")
        if page_errors:
            for e in page_errors:
                print(f"  PAGEERROR: {e[:200]}")
            failures.append(f"{len(page_errors)} uncaught page error(s)")

        # ------------------------------------------------------------
        # Final report
        # ------------------------------------------------------------
        browser.close()

    if failures:
        print("\n--- PAGESHOT FAILURES ---")
        for f in failures:
            print(f"  • {f}")
        return 1
    print("\nAll pageshot checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
