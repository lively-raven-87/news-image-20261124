#!/usr/bin/env python3
"""Draw the front page for 24 November 2026 as a single 1024x1024 PNG.

Layout: masthead, one big lead story with a schematic radar panel, a
two-column grid of supporting stories, a numbers box, and a dark ticker
strip at the bottom. Run: python3 draw.py  ->  entry.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (178, 34, 34)
NAVY = (16, 28, 54)
GREY = (110, 110, 110)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, max_w, text, fnt, leading, fill=INK):
    """Draw a wrapped paragraph; return y just below the last line."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, x1, y, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def kicker(draw, x, y, text, fnt):
    draw.text((x, y), text, font=fnt, fill=RED)
    return y + 22


def headline(draw, x, y, max_w, text, fnt, leading):
    return para(draw, x, y, max_w, text, fnt, leading)


def radar_panel(draw, x, y, w, h):
    """Schematic radar: concentric rings, dashed border, red drone path."""
    draw.rectangle([x, y, x + w, y + h], fill=NAVY)
    cx, cy = x + w // 2, y + h // 2
    for r in (28, 52, 76):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(90, 130, 180), width=1)
    draw.line([(cx, y + 8), (cx, y + h - 8)], fill=(90, 130, 180), width=1)
    draw.line([(x + 8, cy), (x + w - 8, cy)], fill=(90, 130, 180), width=1)
    # dashed frontier line
    for i in range(0, w - 12, 16):
        draw.line([(x + 6 + i, y + h - 42), (x + 6 + i + 9, y + h - 48)],
                  fill=(220, 220, 220), width=2)
    pts = [(x + 18, y + h - 16), (x + 110, y + 96), (x + 168, y + 82),
           (x + 225, y + 100), (x + 300, y + 52)]
    draw.line(pts, fill=(235, 70, 50), width=4, joint="curve")
    tx, ty = pts[-1]
    draw.polygon([(tx, ty - 9), (tx + 16, ty + 2), (tx, ty + 9)], fill=(235, 70, 50))
    draw.text((x + 12, y + 10), "POLAND", font=font(SANS_BOLD, 15), fill=(255, 255, 255))
    draw.text((x + 12, y + h - 26), "UKRAINE", font=font(SANS_BOLD, 15), fill=(255, 255, 255))
    draw.text((x + 12, y + 58), "AWACS DEPLOYED", font=font(SANS_BOLD, 12), fill=(140, 190, 235))
    draw.text((x + 168, y + 30), "DRONE PATH", font=font(SANS_BOLD, 12), fill=(235, 110, 90))


def stat_rows(draw, x, y, w, rows, num_fnt, txt_fnt):
    """Rows of (big number, label) inside the numbers box."""
    for num, label in rows:
        draw.text((x, y), num, font=num_fnt, fill=INK)
        ly = para(draw, x + 104, y + 2, w - 114, label, txt_fnt, 20)
        y = max(y + 30, ly + 4)
    return y


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 9, H - 9], outline=INK, width=3)
    d.rectangle([16, 16, W - 17, H - 17], outline=INK, width=1)

    mx = 36                      # left margin
    rx = W - 36                  # right margin
    y = 30

    # ---- masthead ----
    mast = font(SERIF, 96)
    tw = d.textlength("THE WORLD", font=mast)
    d.text(((W - tw) / 2, y), "THE WORLD", font=mast, fill=INK)
    y += 112
    rule(d, mx, rx, y, 3)
    y += 10
    small = font(SANS, 15)
    d.text((mx, y), "No. 328", font=small, fill=GREY)
    date = "TUESDAY 24 NOVEMBER 2026"
    dw = d.textlength(date, font=font(SANS_BOLD, 17))
    d.text(((W - dw) / 2, y - 1), date, font=font(SANS_BOLD, 17), fill=RED)
    rt = "ONE DAY  •  ONE IMAGE"
    d.text((rx - d.textlength(rt, font=small), y), rt, font=small, fill=GREY)
    y += 28
    rule(d, mx, rx, y, 1)
    y += 14

    # ---- lead ----
    y = kicker(d, mx, y, "LEAD STORY  —  NATO'S EASTERN FLANK", font(SANS_BOLD, 16))
    y = headline(d, mx, y, rx - mx, "RUSSIAN DRONE BREACHES POLISH AIRSPACE",
                 font(SERIF, 52), 58)
    y += 6
    lead = ("A Russian drone crossed into Polish airspace on the night of 23–24 "
            "November during a strike on western Ukraine. Poland authorised its "
            "jets to shoot it down, but stood them down after the drone turned "
            "back east. NATO will deploy AWACS surveillance aircraft to Poland "
            "in response, and Polish and Swedish jets were scrambled. It follows "
            "Friday 20 November, when three Russian Kh-101 missiles landed in "
            "Poland.")
    lead_w = 540
    radar_x, radar_w, radar_h = 606, 352, 196
    radar_panel(d, radar_x, y + 2, radar_w, radar_h)
    cap = "Schematic: drone entered, then turned back east."
    d.text((radar_x, y + 2 + radar_h + 8), cap, font=font(SERIF_REG, 13), fill=GREY)
    lead_end = para(d, mx, y, lead_w, lead, font(SERIF_REG, 19), 26)
    y = max(lead_end, y + 2 + radar_h + 8 + 18) + 12
    rule(d, mx, rx, y, 2)
    y += 10

    # ---- also today ----
    y = kicker(d, mx, y, "ALSO TODAY", font(SANS_BOLD, 16))
    rule(d, mx, rx, y, 1)
    y += 12

    col_w = (rx - mx - 28) // 2
    left_x, right_x = mx, mx + col_w + 28
    top_y = y

    # left column: markets, then diplomacy
    yy = kicker(d, left_x, top_y, "MARKETS", font(SANS_BOLD, 14))
    yy = headline(d, left_x, yy, col_w, "HUANG IS BACK AT NVIDIA",
                  font(SERIF, 26), 30)
    yy = para(d, left_x, yy, col_w,
              "Jensen Huang returns as Nvidia CEO after Trump intervenes, just "
              "~12 days after stepping down on 12 Nov. Shares jump +31.5%, adding "
              "~$952bn in a day; Nasdaq +6.5%, S&P 500 +4.7%.",
              font(SERIF_REG, 16), 21)
    yy += 16
    yy = kicker(d, left_x, yy, "DIPLOMACY", font(SANS_BOLD, 14))
    yy = headline(d, left_x, yy, col_w, "ABU DHABI TALKS FAIL",
                  font(SERIF, 26), 30)
    yy = para(d, left_x, yy, col_w,
              "Trilateral Ukraine–Russia–US talks in Abu Dhabi end with no "
              "breakthrough, as Russia launches 160+ missiles and drones at "
              "Ukraine's energy grid.",
              font(SERIF_REG, 16), 21)

    # right column: mediterranean, then numbers box
    yy2 = kicker(d, right_x, top_y, "MEDITERRANEAN", font(SANS_BOLD, 14))
    yy2 = headline(d, right_x, yy2, col_w, "UKRAINE SINKS RUSSIAN WARSHIP OFF LIBYA",
                   font(SERIF, 26), 30)
    yy2 = para(d, right_x, yy2, col_w,
               "Ukrainian sea drones sink the Russian corvette Merkury in Benghazi "
               "harbour, Libya, on 23 November — the war spreads to the "
               "Mediterranean.",
               font(SERIF_REG, 16), 21)
    yy2 += 14
    box_x, box_y = right_x, yy2
    box_w, box_h = col_w, 176
    d.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], outline=INK, width=1)
    d.text((box_x + 12, box_y + 8), "BY THE NUMBERS", font=font(SANS_BOLD, 14), fill=RED)
    stat_rows(d, box_x + 12, box_y + 34, box_w - 24, [
        ("160+", "missiles & drones fired at Ukraine's grid"),
        ("3", "Kh-101 missiles landed in Poland, Fri 20 Nov"),
        ("~12", "days Huang spent away from Nvidia"),
        ("+$952bn", "Nvidia's one-day market-value gain"),
    ], font(SANS_BOLD, 19), font(SERIF_REG, 14))

    # ---- ticker strip ----
    tick_y = H - 96
    d.rectangle([16, tick_y, W - 17, H - 17], fill=(18, 18, 18))
    ticker = ("Russia warns Estonia its actions risk open war — border closing 1 Dec  •  "
              "Allies warn of possible Russian nuclear weapon in space  •  UK sanctions "
              "Myanmar generals after ICJ genocide ruling  •  Cikande factory fire death "
              "toll 24  •  Himalayan floods: 4 dead, ~100 missing  •  Solomon Islands to "
              "end China security pact")
    lines = wrap(d, ticker, font(SANS, 15), rx - mx - 8)
    ty = tick_y + (H - 17 - tick_y - len(lines) * 20) // 2
    for line in lines:
        lw = d.textlength(line, font=font(SANS, 15))
        d.text(((W - lw) / 2, ty), line, font=font(SANS, 15), fill=(240, 240, 240))
        ty += 20

    img.save(OUT, "PNG")
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
