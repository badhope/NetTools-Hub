#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成对外展示的品牌资产（banner / 竖版海报 / OG 分享图）。

产物：
  docs/banner.png          2560x800  仓库头图（README 顶部）
  demo/promo-poster.jpg    1080x1920 宣传片封面 / 海报
  docs/assets/og.jpg       1200x630  Open Graph 分享图

所有素材从仓库内的真实截图与数据生成，可重复执行、结果稳定（无随机数）。
用法：python tools/make_brand_assets.py
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DEMO = ROOT / "demo"

CYAN = (0, 229, 255)
GREEN = (0, 255, 156)
MAGENTA = (255, 45, 120)
YELLOW = (247, 255, 0)
BG0 = (7, 9, 15)
BG1 = (11, 18, 32)
TEXT_HI = (230, 241, 255)
TEXT_MID = (143, 163, 191)

FONT_CN = "C:/Windows/Fonts/msyhbd.ttc"
FONT_CN_REG = "C:/Windows/Fonts/msyh.ttc"
FONT_MONO = "C:/Windows/Fonts/consolab.ttf"
FONT_MONO_REG = "C:/Windows/Fonts/consola.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def grid(draw, w, h, step=64, color=(0, 229, 255, 18)):
    for x in range(0, w, step):
        draw.line([(x, 0), (x, h)], fill=color, width=1)
    for y in range(0, h, step):
        draw.line([(0, y), (w, y)], fill=color, width=1)


def corners(draw, w, h, pad=28, length=72, color=CYAN, width=3):
    for x, y, dx, dy in (
        (pad, pad, 1, 1), (w - pad, pad, -1, 1),
        (pad, h - pad, 1, -1), (w - pad, h - pad, -1, -1),
    ):
        draw.line([(x, y), (x + dx * length, y)], fill=color, width=width)
        draw.line([(x, y), (x, y + dy * length)], fill=color, width=width)


def vertical_gradient(w, h, top=BG1, bottom=BG0):
    img = Image.new("RGB", (w, h), top)
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    return img


def spaced(draw, xy, text, fnt, fill, spacing=8):
    """逐字加字距绘制（PIL 没有 letter-spacing）。"""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + spacing
    return x


def banner():
    w, h = 2560, 800
    img = vertical_gradient(w, h)
    d = ImageDraw.Draw(img, "RGBA")
    grid(d, w, h, 64, (0, 229, 255, 20))
    corners(d, w, h, pad=34, length=90)

    d.text((110, 92), "M A S H A N G   ·   S I X   L A N G U A G E S   ·   O F F L I N E",
           font=font(FONT_MONO_REG, 30), fill=GREEN)
    d.text((104, 170), "码上", font=font(FONT_CN, 200), fill=CYAN)
    d.text((520, 208), "MASHANG", font=font(FONT_MONO, 120), fill=MAGENTA)
    d.text((112, 420), "码上，就是马上。六门语言，真跑，全离线",
           font=font(FONT_CN, 62), fill=TEXT_HI)
    d.text((112, 510), "Python · JavaScript · TypeScript · C · Lua · SQL  ·  79 lessons  ·  assert-judged",
           font=font(FONT_MONO_REG, 30), fill=TEXT_MID)

    chips = [("六门语言真实运行", CYAN), ("79 讲闯关", GREEN), ("assert 自动判题", CYAN), ("MIT 开源", YELLOW)]
    x = 112
    for label, color in chips:
        f = font(FONT_CN_REG, 30)
        tw = d.textlength(label, font=f)
        box = (x, 594, x + tw + 52, 664)
        d.rounded_rectangle(box, radius=35, outline=color, width=2, fill=(color[0], color[1], color[2], 20))
        d.text((x + 26, 610), label, font=f, fill=color)
        x = box[2] + 22

    d.text((2330, 700), "79 LESSONS · 8 CHALLENGES · 6 LANGUAGES",
           font=font(FONT_MONO_REG, 24), fill=(90, 105, 130), anchor="ra")
    img.save(DOCS / "banner.png", optimize=True)
    print("docs/banner.png", img.size)


def phone_paste(canvas, shot_path, box):
    shot = Image.open(shot_path).convert("RGB")
    tw, th = box[2] - box[0], box[3] - box[1]
    scale = min(tw / shot.width, th / shot.height)
    resized = shot.resize((int(shot.width * scale), int(shot.height * scale)), Image.LANCZOS)
    x = box[0] + (tw - resized.width) // 2
    y = box[1] + (th - resized.height) // 2
    canvas.paste(resized, (x, y))


def promo_poster():
    w, h = 1080, 1920
    img = vertical_gradient(w, h)
    d = ImageDraw.Draw(img, "RGBA")
    grid(d, w, h, 72, (0, 229, 255, 16))
    corners(d, w, h, pad=30, length=80)
    d.text((74, 86), "MASHANG · 码上", font=font(FONT_CN, 34), fill=GREEN)
    d.text((72, 150), "码上，", font=font(FONT_CN, 116), fill=TEXT_HI)
    d.text((72, 280), "就是马上。", font=font(FONT_CN, 116), fill=CYAN)
    d.text((76, 434), "装进口袋的赛博朋克编程学习终端",
           font=font(FONT_CN_REG, 42), fill=TEXT_MID)
    d.text((76, 496), "CPython 3.13  ·  38 讲  ·  assert 判题  ·  全离线",
           font=font(FONT_CN_REG, 28), fill=GREEN)

    phone_paste(img, DEMO / "app" / "home.png", (250, 570, 830, 1490))
    d.rounded_rectangle((250, 570, 830, 1490), radius=34, outline=CYAN, width=3)

    d.text((540, 1630), "离线写码 · 变量快照 · 六段位成长", font=font(FONT_CN_REG, 38),
           fill=TEXT_HI, anchor="ma")
    d.text((540, 1700), "github.com/badhope/mashang", font=font(FONT_MONO_REG, 30),
           fill=MAGENTA, anchor="ma")
    d.text((540, 1800), "MIT LICENSE · ANDROID 7.0+ · FREE", font=font(FONT_CN_REG, 22),
           fill=(90, 105, 130), anchor="ma")
    img.convert("RGB").save(DEMO / "promo-poster.jpg", quality=88, optimize=True, progressive=True)
    print("demo/promo-poster.jpg", img.size)


def og_image():
    w, h = 1200, 630
    img = vertical_gradient(w, h)
    d = ImageDraw.Draw(img, "RGBA")
    grid(d, w, h, 56, (0, 229, 255, 18))
    d.text((60, 54), "MASHANG · 码上", font=font(FONT_MONO, 26), fill=GREEN)
    d.text((56, 104), "码上，就是马上。", font=font(FONT_CN, 74), fill=TEXT_HI)
    d.text((58, 208), "CPython 3.13 装进口袋 · 38 讲 · assert 判题 · 全离线",
           font=font(FONT_CN_REG, 30), fill=TEXT_MID)
    phone_paste(img, DEMO / "app" / "lesson_exercise.png", (790, 60, 1160, 600))
    d.rounded_rectangle((790, 60, 1160, 600), radius=26, outline=CYAN, width=2)
    d.text((60, 500), "ANDROID 7.0+  ·  MIT  ·  GITHUB.COM/BADHOPE/MASHANG",
           font=font(FONT_MONO_REG, 22), fill=MAGENTA)
    img.save(DOCS / "assets" / "og.jpg", quality=88, optimize=True, progressive=True)
    print("docs/assets/og.jpg", img.size)


def feature_graphic():
    """Google Play 特色图片 1024x500（多数市场的通用横幅尺寸）。

    Play 规范要点：文字要在缩略图下仍可辨认、不得有大面积留白、
    不得出现与应用无关的误导性内容。

    布局（实测调整过两轮）：
      - 左侧：主标题 + 副标题 + 六语言标签，宽度限制在 660px 内
      - 右侧：独立数据卡片（x=690 起），避免与主标题重叠
      - 主标题字号按实测宽度收敛，宁小不溢出
    """
    w, h = 1024, 500
    img = vertical_gradient(w, h)
    d = ImageDraw.Draw(img, "RGBA")
    grid(d, w, h, 48, (0, 229, 255, 16))
    corners(d, w, h, pad=22, length=56)

    LEFT_RIGHT = 656  # 左栏可用右边界

    # 主标题：先量宽度，超了就降字号（避免压到右侧卡片）
    title_font_size = 76
    while title_font_size > 40:
        f = font(FONT_CN, title_font_size)
        if d.textlength("码上 MASHANG", font=f) <= LEFT_RIGHT - 60:
            break
        title_font_size -= 4
    d.text((60, 86), "码上 MASHANG", font=font(FONT_CN, title_font_size), fill=CYAN)

    d.text((62, 200), "六门语言，真跑，全离线", font=font(FONT_CN, 42), fill=TEXT_HI)
    d.text((62, 262), "断网也能写代码、判题、升级", font=font(FONT_CN_REG, 25), fill=TEXT_MID)

    # 六语言标签（两行，宽度不越过左栏）
    langs = [("Python", CYAN), ("JavaScript", YELLOW), ("TypeScript", CYAN),
             ("C", GREEN), ("Lua", GREEN), ("SQL", MAGENTA)]
    x, y = 62, 330
    for name, color in langs:
        f = font(FONT_MONO, 20)
        tw = d.textlength(name, font=f)
        box_w = tw + 26
        if x + box_w > LEFT_RIGHT:
            x, y = 62, y + 46
        box = (x, y, x + box_w, y + 36)
        d.rounded_rectangle(box, radius=18, outline=color, width=2,
                            fill=(color[0], color[1], color[2], 26))
        d.text((x + 13, y + 7), name, font=f, fill=color)
        x = box[2] + 10

    # 右侧数据卡片
    bx0, by0, bx1, by1 = 690, 96, 984, 404
    d.rounded_rectangle((bx0, by0, bx1, by1), radius=18,
                        outline=(0, 229, 255, 90), width=2, fill=(11, 18, 32, 210))

    # 三行数据：卡片高度 308，留出底部 46px 给脚注
    # 行高 80，起点 by0+28 → 三行占 240，脚注在 by1-42，不重叠
    stats = [("79", "讲课程"), ("6", "门语言"), ("0", "广告 · 账号")]
    sy = by0 + 28
    for num, label in stats:
        d.text((bx0 + 30, sy), num, font=font(FONT_MONO, 46), fill=CYAN)
        d.text((bx0 + 108, sy + 14), label, font=font(FONT_CN_REG, 22), fill=TEXT_MID)
        sy += 78

    # 脚注单独一行，与上方数字保持 20px 以上间距
    d.text((bx0 + 30, by1 - 40), "MIT 开源 · 数据不出手机",
           font=font(FONT_CN_REG, 18), fill=GREEN)

    out = DOCS / "assets" / "feature-graphic-1024x500.png"
    img.save(out, optimize=True)
    print("docs/assets/feature-graphic-1024x500.png", img.size)


def main():
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    banner()
    feature_graphic()
    promo_poster()
    og_image()


if __name__ == "__main__":
    main()


# ===== 商店截图（带标题标注） =====
# Play / 各市场要求截图能一眼看懂卖点；纯界面截图信息密度太高。
# 做法：把原截图等比缩放放进画布，顶部留出标题条，底部留白。
STORE_SHOTS = [
    ("home.png", "六门语言，一个终端", "Six languages, one terminal"),
    ("lessons.png", "79 讲课程，从入门到实战", "79 lessons, beginner to capstone"),
    ("lesson_detail.png", "每讲都有讲解、图解、随堂问", "Explanations, diagrams, inline quizzes"),
    ("lesson_exercise.png", "写完就跑，跑完就判", "Write, run, get judged"),
    ("judge_pass.png", "用例全过才放行", "All tests must pass"),
    ("judge_fail.png", "失败时告诉你哪条断言没过", "Told exactly which assertion failed"),
    ("terminal.png", "内置终端，随时试验", "Built-in terminal, experiment freely"),
    ("tracks.png", "真实课程路线，不掺水分", "Real curriculum, no filler"),
    ("contenthub.png", "语言中心，按需下载", "Language Center, on-demand packs"),
    ("settings.png", "外观、字号、诊断都能调", "Appearance, font size, diagnostics"),
]


def store_screenshots():
    """生成商店用截图：1080x1920 画布 + 顶部标题条。

    输出到 store/screenshots/，文件名带序号便于按顺序上传。
    """
    out_dir = ROOT / "store" / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)

    CW, CH = 1080, 1920
    TOP_H = 210          # 标题条高度
    PAD = 40             # 内容左右留白

    for idx, (fname, zh, en) in enumerate(STORE_SHOTS, start=1):
        src_path = DEMO / "app" / fname
        if not src_path.exists():
            print(f"  跳过（缺文件）：{fname}")
            continue

        canvas = vertical_gradient(CW, CH)
        d = ImageDraw.Draw(canvas, "RGBA")
        grid(d, CW, CH, 60, (0, 229, 255, 12))

        # 顶部标题
        d.text((PAD, 54), zh, font=font(FONT_CN, 54), fill=TEXT_HI)
        d.text((PAD, 132), en, font=font(FONT_MONO_REG, 22), fill=TEXT_MID)

        # 截图等比缩放进剩余空间
        shot = Image.open(src_path).convert("RGB")
        avail_h = CH - TOP_H - PAD
        avail_w = CW - PAD * 2
        scale = min(avail_w / shot.width, avail_h / shot.height)
        nw, nh = int(shot.width * scale), int(shot.height * scale)
        shot = shot.resize((nw, nh), Image.LANCZOS)

        x = (CW - nw) // 2
        y = TOP_H
        # 截图加细边框，避免与背景糊在一起
        d.rounded_rectangle((x - 3, y - 3, x + nw + 3, y + nh + 3),
                            radius=18, outline=(0, 229, 255, 70), width=2)
        canvas.paste(shot, (x, y))

        out = out_dir / f"{idx:02d}-{fname.replace('.png', '')}.png"
        canvas.convert("RGB").save(out, optimize=True, quality=92)
        print(f"  store/screenshots/{out.name}")


if __name__ == "__main__":
    store_screenshots()
