"""
Take screenshots of the static-exported pages of NetTools Hub.

The site is built via `pnpm build` to `out/`, then served with
`npx serve out -p 8080` (matching the `pnpm start` script). The
`basePath` is `/NetTools-Hub`, so the URLs are
`http://localhost:8080/NetTools-Hub/...`.

Override the base URL with the BASE env var:
  BASE=http://localhost:8080/NetTools-Hub python3 scripts/snap.py

Saves to `screenshots/` (override with `OUT`).
"""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

OUT = Path(os.environ.get("OUT", "screenshots"))
OUT.mkdir(parents=True, exist_ok=True)
BASE = os.environ.get("BASE", "http://localhost:8080/NetTools-Hub")


def shot(page, path: str, full: bool = True) -> None:
    page.goto(f"{BASE}{path}", wait_until="networkidle")
    page.wait_for_timeout(900)
    out_path = OUT / f"{path.strip('/').replace('/', '-') or 'landing'}.png"
    page.screenshot(path=str(out_path), full_page=full)
    print(f"  {out_path.name}  ({path})")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # 1) Desktop landing
        print("== Desktop ==")
        ctx = browser.new_context(viewport={"width": 1280, "height": 800})
        page = ctx.new_page()
        shot(page, "/", full=False)
        shot(page, "/", full=True)
        shot(page, "/explore/", full=False)
        shot(page, "/explore/", full=True)
        shot(page, "/explore/k/proxy/", full=False)
        shot(page, "/explore/k/proxy/p/desktop/", full=False)
        shot(page, "/explore/k/security/p/cli/", full=False)
        shot(page, "/this-does-not-exist", full=False)
        shot(page, "/?lang=zh", full=False)
        shot(page, "/?lang=ja", full=False)
        ctx.close()

        # 2) Mobile
        print("== Mobile (390x844) ==")
        ctx = browser.new_context(viewport={"width": 390, "height": 844})
        page = ctx.new_page()
        shot(page, "/", full=False)
        shot(page, "/explore/", full=False)
        ctx.close()

        browser.close()
    print("all done")


if __name__ == "__main__":
    main()
