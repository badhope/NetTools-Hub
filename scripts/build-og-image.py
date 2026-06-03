"""Generate a 1200x630 Open Graph image for NetTools Hub.

The image is a static editorial composition that matches the
landing-page hero: dark warm background, terracotta accent, serif
display for the title, and monospace metadata strip. The script is
re-runnable, deterministic (no random seed) and re-uses only
system-installed fonts so it can be regenerated in CI without a
network round-trip.
"""

from __future__ import annotations

import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = pathlib.Path(__file__).resolve().parent.parent / "public"
W, H = 1200, 630
BG = (14, 12, 10)        # matches `--color-bg` in globals.css
FG = (244, 240, 232)     # matches `--color-fg`
FG2 = (196, 184, 168)    # matches `--color-fg-2`
MUTED = (140, 130, 118)  # matches `--color-muted`
DIM = (62, 56, 50)       # matches `--color-dim`
ACCENT = (212, 96, 58)   # matches `--color-accent`

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Paper-grain noise (very subtle) so the dark background does
    # not look flat. A 1.5x-blurred copy of random monochrome noise
    # is good enough for a 1200x630 OG image. The grain is a
    # full-strength copy of the noise, then we blend it on top of
    # the bg at 5% to keep the texture visible without grunging
    # up the typography.
    import random
    random.seed(20260101)
    noise = Image.new("L", (W, H), 0)
    npx = noise.load()
    for y in range(H):
        for x in range(W):
            npx[x, y] = random.randint(0, 32)
    noise = noise.filter(ImageFilter.GaussianBlur(1.5))
    grain = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, grain, 0.05)
    draw = ImageDraw.Draw(img)

    # Decorative frame: 3 hairline rules along the top to echo
    # the editorial divider in the hero section.
    draw.rectangle([(80, 80), (W - 80, 80)], fill=DIM)
    draw.rectangle([(80, 84), (W - 80, 84)], fill=DIM)
    draw.rectangle([(80, 88), (W - 80, 88)], fill=DIM)

    # Eyebrow / kicker
    draw.text(
        (80, 130),
        "AN ATLAS OF",
        font=font(MONO, 18),
        fill=MUTED,
    )
    draw.line([(220, 142), (W - 80, 142)], fill=DIM, width=1)
    draw.text(
        (W - 120, 130),
        "PLATE 00",
        font=font(MONO, 18),
        fill=MUTED,
    )

    # Title block — two lines, set in a display serif.
    title1 = "Network Tools"
    title2 = "An Atlas"
    f_title = font(SERIF, 130)
    draw.text((80, 180), title1, font=f_title, fill=FG)
    bbox = draw.textbbox((0, 0), title1, font=f_title)
    line1_bottom = bbox[3]
    # Accent dash after first line
    draw.text(
        (80 + bbox[2] + 24, 180 + 18),
        "—",
        font=font(SERIF, 100),
        fill=ACCENT,
    )
    # Second line in accent color
    draw.text(
        (80, 180 + 180),
        title2,
        font=font(SERIF, 130),
        fill=ACCENT,
    )

    # Subtitle
    sub = (
        "A curated compendium of 120+ open-source network tools,\n"
        "organised into six thematic groups and indexed daily."
    )
    sub_font = font(SANS, 22)
    y0 = 180 + 360
    for i, line in enumerate(sub.split("\n")):
        draw.text((80, y0 + i * 34), line, font=sub_font, fill=FG2)

    # Footer rule + monospace metadata strip
    draw.line([(80, H - 90), (W - 80, H - 90)], fill=DIM, width=1)
    f_mono = font(MONO, 16)
    draw.text((80, H - 70), "NETTOOLS-HUB", font=f_mono, fill=ACCENT)
    draw.text(
        (80 + 230, H - 70),
        "BADHOPE · EDITION I · 2026",
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

    # Also generate a PWA icon (square, 512px) by cropping/recentering
    # the OG image. This is a pragmatic shortcut: the icon is the
    # same composition, just with less whitespace around the
    # title. The result is a clean monochrome-on-dark mark that
    # reads at 192/96/48px.
    icon = img.resize((512, 512), Image.LANCZOS)
    # Crop to a 1:1 square centered on the title block.
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
