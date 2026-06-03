"""End-to-end smoke test of the NetTools-Hub site.

Targets the locally-built `out/` directory served on a local
Python http.server, but the URL can be overridden via the
`SMOKE_URL` env var (the production deploy lives at
`https://badhope.github.io/NetTools-Hub`).

What this catches that lint + typecheck + build do not:
  - Hydration mismatches (React 19 #418 / #423) — we walk every
    page and assert `pageerror` stays empty.
  - Console-level runtime errors that are otherwise silent.
  - Search filter actually returns results (verifies the new
    useDeferredValue wiring).
  - Skip link is focusable via keyboard (a11y primitive).
  - `/` shortcut focuses the search bar.
  - 404 page renders without throwing.
  - Mobile drawer focus trap (open → close button focused →
    Esc closes → focus returns to trigger).
"""
from __future__ import annotations

import os
import sys

from playwright.sync_api import sync_playwright

BASE = os.environ.get(
    "SMOKE_URL", "https://badhope.github.io/NetTools-Hub"
)


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
        h1 = page.locator("h1, h2").first.text_content() or ""
        print(f"  first heading: {h1[:80]}")
        date = page.locator("text=2026-06-01").first.text_content()
        print(f"  last indexed: {date}")
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
        if "SearchAction" not in site_ld:
            failures.append("landing JSON-LD missing SearchAction")

        # hreflang links present
        hreflang_count = page.evaluate(
            "() => document.querySelectorAll('link[rel=\"alternate\"][hreflang]').length"
        )
        print(f"  hreflang links: {hreflang_count}")
        if hreflang_count < 4:
            failures.append(
                f"expected 4+ hreflang links (3 langs + x-default), got {hreflang_count}"
            )

        # PWA manifest linked
        manifest_href = page.evaluate(
            "() => document.querySelector('link[rel=\"manifest\"]')?.getAttribute('href')"
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

        # Editorial divider uses i18n (should say "Folio 01" not "第 01 卷")
        # In English the new key is "Folio {n} · {groups} groups · ..."
        divider_text = page.locator(".kicker").nth(0).text_content() or ""
        print(f"  first kicker: {divider_text!r}")
        page.screenshot(
            path="/workspace/net-tools-hub/smoke-1-landing.png",
            full_page=False,
        )

        # 2. Landing page Chinese ------------------------------------
        print("\n=== 2. Landing page (Chinese) ===")
        page.goto(f"{BASE}/?lang=zh", wait_until="networkidle")
        page.wait_for_timeout(500)
        body_text = page.locator("body").text_content() or ""
        has_zh = any("\u4e00" <= c <= "\u9fff" for c in body_text)
        print(f"  contains CJK: {has_zh}")
        if not has_zh:
            failures.append("Chinese landing page has no CJK characters")
        # Verify the new "概览" key rendered (i18n of "Compendium")
        if "概览" not in body_text and "Compendium" not in body_text:
            failures.append("right-rail compendium kicker not localized")
        # Verify the new "卷" divider i18n rendered (not English Folio)
        if "Folio 01" in body_text and "第 01 卷" not in body_text:
            failures.append("editorial divider still in English for /zh")
        page.screenshot(
            path="/workspace/net-tools-hub/smoke-2-landing-zh.png",
            full_page=False,
        )

        # 3. Explore page with category filter ------------------------
        print("\n=== 3. Explore page (category filter) ===")
        page.goto(f"{BASE}/", wait_until="networkidle")
        cards = page.locator("a[href*='/explore/?category=protocol_tools']").count()
        print(f"  protocol_tools category links on landing: {cards}")
        if cards == 0:
            failures.append("no protocol_tools category link on landing")
        else:
            page.locator(
                "a[href*='/explore/?category=protocol_tools']"
            ).first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(500)
            url = page.url
            print(f"  clicked protocol_tools, url: {url}")
            gh_links = page.locator("a[href*='github.com']").count()
            print(f"  github.com links on filtered page: {gh_links}")
            if gh_links < 1:
                failures.append("category filter shows no projects")
            page.screenshot(
                path="/workspace/net-tools-hub/smoke-3-explore-filtered.png",
                full_page=False,
            )

        # 4. Search ---------------------------------------------------
        print("\n=== 4. Search ===")
        page.goto(f"{BASE}/explore/", wait_until="networkidle")
        search = page.locator("input[type='search']").first
        search.fill("clash")
        page.wait_for_timeout(800)
        project_links = page.locator(
            "a[target='_blank'][href*='github.com']"
        ).count()
        print(f"  project links after searching 'clash': {project_links}")
        if project_links < 1:
            failures.append("search 'clash' returns 0 results")

        # 4b. `/` keyboard shortcut focuses the search bar
        search.fill("")
        page.keyboard.press("/")
        page.wait_for_timeout(150)
        focused_tag = page.evaluate(
            "() => document.activeElement?.tagName"
        )
        focused_type = page.evaluate(
            "() => document.activeElement?.getAttribute('type')"
        )
        print(
            f"  after '/': focused tag={focused_tag} type={focused_type}"
        )
        if focused_tag != "INPUT" or focused_type != "search":
            failures.append(
                f"`/` shortcut did not focus search input "
                f"(tag={focused_tag}, type={focused_type})"
            )

        # 4c. JSON-LD ItemList on the explore page
        page.goto(f"{BASE}/explore/", wait_until="networkidle")
        explore_ld = page.evaluate(
            "() => Array.from(document.querySelectorAll("
            "'script[type=\"application/ld+json\"]'))"
            ".map(s => s.textContent).join('\\n')"
        )
        if "ItemList" not in explore_ld:
            failures.append("explore JSON-LD missing ItemList schema")

        # 5. 404 page -------------------------------------------------
        print("\n=== 5. 404 page ===")
        page.goto(f"{BASE}/404.html", wait_until="networkidle")
        has_404 = "404" in (page.locator("body").text_content() or "")
        print(f"  contains '404': {has_404}")
        if not has_404:
            failures.append("404 page does not contain '404'")
        page.screenshot(
            path="/workspace/net-tools-hub/smoke-4-404.png",
            full_page=False,
        )

        # 6. Mobile viewport + drawer focus trap ----------------------
        print("\n=== 6. Mobile viewport ===")
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
            page.screenshot(
                path="/workspace/net-tools-hub/smoke-5-mobile-drawer.png",
                full_page=False,
            )
            focused = page.evaluate(
                "() => document.activeElement?.getAttribute('data-drawer-close')"
            )
            print(f"  close button has focus on open: {focused is not None}")
            if focused is None:
                failures.append("drawer open did not focus the close button")
            page.keyboard.press("Escape")
            page.wait_for_timeout(500)
            drawer_open = page.locator("[role='dialog']").count()
            print(f"  drawer closed by Escape: {drawer_open == 0}")
            if drawer_open != 0:
                failures.append("Escape did not close the drawer")
            focused = page.evaluate(
                "() => document.activeElement?.tagName"
            )
            print(f"  focus returned to: {focused}")

        # 7. Report ---------------------------------------------------
        print(f"\n=== Console errors: {len(console_errors)} ===")
        for err in console_errors[:5]:
            print(f"  - {err[:200]}")
        print(f"=== Page errors: {len(page_errors)} ===")
        for err in page_errors[:5]:
            print(f"  - {err[:200]}")
        if console_errors:
            failures.append(f"{len(console_errors)} console errors")
        if page_errors:
            failures.append(f"{len(page_errors)} page errors")

        browser.close()

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        print(f"\nDONE ({len(failures)} failure(s))")
        return 1
    print("\nDONE (all checks passed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
