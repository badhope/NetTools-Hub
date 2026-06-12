"""Generate a 1200x630 Open Graph image for NetTools Hub.

The image is a static composition that matches the landing-page
hero of the "field manual" design system: cool near-black
background, steel-blue accent, a single sans-serif face (IBM Plex
Sans — closest system fallback is DejaVu Sans), and a monospace
metadata strip. The script is re-runnable, deterministic (no
random seed) and re-uses only system-installed fonts so it can be
regenerated in CI without a network round-trip.

Colour values mirror `src/app/globals.css` `@theme`:
  --color-bg       #0b0d10
  --color-fg       #e6edf3
  --color-fg-2     #b8c1cc
  --color-muted    #7d8590
  --color-dim      #3a424b
  --color-accent   #6ea8fe   (steel blue, links)
  --color-accent-2 #4fd1a1   (mint, active tree node)
"""

from __future__ import annotations

import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "public"
W, H = 1200, 630
BG     = (11, 13, 16)     # #0b0d10  --color-bg
FG     = (230, 237, 243)  # #e6edf3  --color-fg
FG2    = (184, 193, 204)  # #b8c1cc  --color-fg-2
MUTED  = (125, 133, 144)  # #7d8590  --color-muted
DIM    = (58, 66, 75)     # #3a424b  --color-dim
ACCENT = (110, 168, 254)  # #6ea8fe  --color-accent (steel blue)

SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Subtle paper-grain noise so the dark background does not look
    # flat. A 1.5x-blurred copy of low-amplitude random monochrome
    # noise, blended at 4% to keep the texture visible without
    # dirtying the typography.
    import random
    random.seed(20260611)
    noise = Image.new("L", (W, H), 0)
    npx = noise.load()
    for y in range(H):
        for x in range(W):
            npx[x, y] = random.randint(0, 24)
    noise = noise.filter(ImageFilter.GaussianBlur(1.5))
    grain = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, grain, 0.04)
    draw = ImageDraw.Draw(img)

    # Top hairline — single 1px rule in --color-dim. The
    # "field manual" design uses hairlines, not double rules.
    draw.rectangle([(80, 80), (W - 80, 80)], fill=DIM)

    # Eyebrow / kicker — monospace, dim, mirrored from the
    # site-wide "manual-index" component.
    draw.text(
        (80, 130),
        "00 ── INDEX",
        font=font(MONO, 18),
        fill=MUTED,
    )
    draw.line([(240, 142), (W - 80, 142)], fill=DIM, width=1)
    draw.text(
        (W - 200, 130),
        "EDITION I",
        font=font(MONO, 18),
        fill=MUTED,
    )

    # Title block — two lines of the field-manual heading. The
    # site no longer uses a serif display face, so the title is
    # set in a single sans family. The accent renders only the
    # accent word; everything else stays in --color-fg.
    title1 = "A field manual of"
    title2 = "open-source"
    title3 = "network tools."
    f_title = font(SANS, 96)
    draw.text((80, 200), title1, font=f_title, fill=FG)

    # Line 2 with one accent word.
    f_title_mid = font(SANS, 96)
    bbox1 = draw.textbbox((0, 0), "open-source ", font=f_title_mid)
    draw.text((80, 310), "open-source", font=f_title_mid, fill=FG)
    draw.text((80 + bbox1[2] + 8, 310), "tools", font=f_title_mid, fill=ACCENT)
    draw.text((80 + bbox1[2] + 8 + bbox1[2] + 8, 310), ".",
              font=f_title_mid, fill=FG)

    # Subtitle in --color-fg-2, monospace for the technical feel.
    sub = (
        "210 projects, indexed by kind and by platform.\n"
        "Open-source. MIT. No tracking. No ads."
    )
    sub_font = font(MONO, 20)
    y0 = 440
    for i, line in enumerate(sub.split("\n")):
        draw.text((80, y0 + i * 30), line, font=sub_font, fill=FG2)

    # Footer rule + monospace metadata strip
    draw.line([(80, H - 90), (W - 80, H - 90)], fill=DIM, width=1)
    f_mono = font(MONO, 16)
    draw.text((80, H - 70), "NETTOOLS-HUB", font=f_mono, fill=ACCENT)
    draw.text(
        (80 + 240, H - 70),
        "BADHOPE · /EXPLORE",
        font=f_mono,
        fill=MUTED,
    )
    draw.text(
        (W - 80 - 220, H - 70),
        "EN · 中文 · 日本語",
        font=f_mono,
        fill=MUTED,
    )

    out = OUT_DIR / "og-image.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")

    # PWA icon (square, 512px). We re-use the same composition,
    # cropped to the title block. The result is a clean
    # monochrome-on-dark mark that reads at 192/96/48px.
    icon = img.resize((512, 512), Image.LANCZOS)
    crop = icon.crop((0, 80, 512, 512))
    out_icon = OUT_DIR / "icon-512.png"
    crop.save(out_icon, format="PNG", optimize=True)
    out_icon_192 = OUT_DIR / "icon-192.png"
    crop_192 = crop.resize((192, 192), Image.LANCZOS)
    crop_192.save(out_icon_192, format="PNG", optimize=True)
    print(f"wrote {out_icon} ({out_icon.stat().st_size} bytes)")
    print(f"wrote {out_icon_192} ({out_icon_192.stat().st_size} bytes)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
