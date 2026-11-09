#!/usr/bin/env python3
"""Vertical line-art short: the suspension-bridge misattribution film."""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from make_audio import MARKED

W, H = 1080, 1920
FPS = 24
FONT_PATH = "/tmp/NotoSerifCJKjp-Regular.otf"
FONT_SIZE = 76  # 1080 * 0.07
RED = (200, 16, 46)
AMBER = (214, 150, 64)
BLUE = (120, 156, 196)
FILL = (0.38, 0.38, 0.41)
WHITE = (1, 1, 1, 1)

XS = np.arange(W, dtype=np.float32)[None, :]
YS = np.arange(H, dtype=np.float32)[:, None]
GUARD = np.ones(H, dtype=np.float32)
_gs, _ge = 1220, 1420
_m = (np.arange(H) - _gs) / (_ge - _gs)
GUARD = np.where(np.arange(H) < _gs, 1.0, np.clip(1.0 - _m, 0.0, 1.0)).astype(np.float32)
GUARD = np.where(np.arange(H) > _ge, 0.0, GUARD)

FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)


def ease(p):
    p = 0.0 if p < 0 else 1.0 if p > 1 else p
    return p * p * (3 - 2 * p)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def heartbeat(t, bpm=94):
    period = 60.0 / bpm
    p = (t % period) / period
    a = math.exp(-((p - 0.09) / 0.038) ** 2)
    b = 0.58 * math.exp(-((p - 0.20) / 0.048) ** 2)
    return a + b


def flicker(t):
    base = 0.965 + 0.035 * math.sin(t * 0.55)
    p = (t % 4.3) / 4.3
    dip = 0.0
    if 0.46 < p < 0.54:
        dip = math.sin((p - 0.46) / 0.08 * math.pi) * 0.10
    return base - dip


def parse_marked(marked):
    chars = []
    ranges = []
    i = 0
    while i < len(marked):
        if marked[i] == "《":
            j = marked.index("》", i)
            word = marked[i + 1 : j]
            start = len(chars)
            chars.extend(word)
            ranges.append((start, start + len(word)))
            i = j + 1
        else:
            chars.append(marked[i])
            i += 1
    return "".join(chars), ranges


def wrap_text(text, limit=13):
    lines = []
    i = 0
    n = len(text)
    while i < n:
        window = text[i : min(n, i + limit)]
        if i + limit >= n:
            lines.append((window, i))
            break
        br = None
        for k in range(len(window) - 1, 3, -1):
            if window[k] in "、。":
                br = k + 1
                break
        if br is None:
            for k in range(len(window) - 1, 4, -1):
                if window[k] in "はがをにのとでもへ":
                    br = k + 1
                    break
        if br is None:
            br = len(window)
        lines.append((text[i : i + br], i))
        i += br
    return lines


# Hand-broken so no line exceeds 13 characters and です is never orphaned.
WRAPS = [
    ["お化け屋敷を出た瞬間、", "隣の人がやけに《素敵》に", "見えました。"],
    ["心臓はまだ、", "どくどくと鳴っています。"],
    ["さっきまでは、", "ただの友達だったはずです。"],
    ["なぜ怖い体験のあとは、", "相手が《魅力的》に", "見えるのだろうか？"],
    ["実は、心臓の高鳴りを、", "《恋》だと勘違いしている", "からです。"],
    ["一九七四年、心理学者の", "ダットンとアロンが、", "ある実験をしました。"],
    ["舞台はカナダの、", "高さ《七十メートル》の", "吊り橋です。"],
    ["幅は一・五メートル", "しかなく、歩くたびに", "揺れます。"],
    ["渡り終えた男性に、", "一人の女性が声をかけます。"],
    ["簡単な質問のあと、", "気になれば電話を、", "と番号を渡しました。"],
    ["比較のため、", "揺れない低い橋でも、", "同じことをしました。"],
    ["すると、吊り橋では番号を", "受け取った二十三人のうち、", "《九人》が電話をかけました。"],
    ["低い橋では、", "二十二人のうち、", "わずか《二人》でした。"],
    ["およそ《四割》と、", "一割です。"],
    ["怖さで高鳴った心臓を、", "恋のときめきと", "取り違えたのです。"],
    ["ただし、ドキドキは", "好意だけでなく、苦手な", "気持ちも《強める》そうです。"],
    ["お化け屋敷を出たあと、", "隣の人が素敵に見えた", "あの瞬間です。"],
    ["あなたの心臓は、", "まだ《怖さ》で鳴って", "いただけかもしれません。"],
    ["隣の人が輝いて見えた", "のは、恋ではなく、", "《恐怖の余韻》だったんです。"],
    ["あなたのそのドキドキは、", "本当に恋でしょうか？"],
]


def draw_subtitles(img, marked):
    if not marked:
        return img
    lines = WRAPS[MARKED.index(marked)]
    im = Image.fromarray(img, "RGB")
    draw = ImageDraw.Draw(im)
    line_h = int(FONT_SIZE * 1.22)
    bottom = int(H * 0.82)
    y = bottom - line_h * len(lines)
    for marked_line in lines:
        text, ranges = parse_marked(marked_line)
        spans = []
        buf = ""
        red = None
        for k, ch in enumerate(text):
            is_red = any(a <= k < b for a, b in ranges)
            if red is None:
                red = is_red
                buf = ch
            elif is_red == red:
                buf += ch
            else:
                spans.append((buf, red))
                buf = ch
                red = is_red
        if buf:
            spans.append((buf, red))
        width = sum(FONT.getlength(s) for s, _ in spans)
        x = (W - width) / 2
        for s, is_red in spans:
            draw.text((x, y), s, font=FONT, fill=RED if is_red else (255, 255, 255))
            x += FONT.getlength(s)
        y += line_h
    return np.asarray(im)


class Frame:
    def __init__(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_antialias(cairo.ANTIALIAS_BEST)
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ctx.paint()
        self.zoom = 1.0
        self.ox = W / 2
        self.oy = H / 2
        self.spot_cx = W / 2
        self.spot_cy = -80
        self.spot_r = 1720
        self.spot_ang = 0.52
        self.ambient = 0.0
        self.glows = []
        self._ready = False

    def w2s(self, x, y):
        return (x - self.ox) * self.zoom + W / 2, (y - self.oy) * self.zoom + H / 2

    def glow(self, x, y, radius, color, intensity):
        if intensity > 0.01:
            self.glows.append((x, y, radius, color, intensity))

    def prepare(self):
        c = self.ctx
        c.set_source_rgba(1, 1, 1, 0.11)
        c.set_line_width(1.25)
        c.move_to(self.spot_cx, self.spot_cy)
        c.line_to(self.spot_cx - 560, H + 40)
        c.move_to(self.spot_cx, self.spot_cy)
        c.line_to(self.spot_cx + 560, H + 40)
        c.stroke()
        c.translate(W / 2, H / 2)
        c.scale(self.zoom, self.zoom)
        c.translate(-self.ox, -self.oy)
        self._ready = True


def stroke(ctx, width=1.7, rgba=WHITE):
    ctx.set_source_rgba(*rgba)
    ctx.set_line_width(width)
    ctx.stroke()


def fill_stroke(ctx, width=1.7, fill=FILL, rgba=WHITE):
    ctx.set_source_rgb(*fill)
    ctx.fill_preserve()
    stroke(ctx, width, rgba)


def poly(ctx, pts):
    ctx.new_path()
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)


def line(ctx, x1, y1, x2, y2, width=1.6, rgba=WHITE):
    ctx.new_path()
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    stroke(ctx, width, rgba)


def circle(ctx, x, y, r, width=1.7, fill=None, rgba=WHITE):
    ctx.new_path()
    ctx.arc(x, y, r, 0, math.tau)
    if fill is not None:
        fill_stroke(ctx, width, fill, rgba)
    else:
        stroke(ctx, width, rgba)


def heart_points(cx, cy, s):
    pts = []
    for i in range(90):
        t = i / 90 * math.tau
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + x * s, cy - y * s))
    return pts


def draw_heart(ctx, cx, cy, s, width=1.6):
    poly(ctx, heart_points(cx, cy, s))
    ctx.close_path()
    fill_stroke(ctx, width, (0.16, 0.05, 0.07), (1, 1, 1, 0.95))


def draw_arm(ctx, x1, y1, x2, y2, r):
    ang = math.atan2(y2 - y1, x2 - x1)
    ox = math.cos(ang + math.pi / 2) * r
    oy = math.sin(ang + math.pi / 2) * r
    ctx.new_path()
    ctx.move_to(x1 + ox, y1 + oy)
    ctx.line_to(x2 + ox, y2 + oy)
    ctx.line_to(x2 - ox, y2 - oy)
    ctx.line_to(x1 - ox, y1 - oy)
    ctx.close_path()
    fill_stroke(ctx, max(1.2, r * 0.35))
    circle(ctx, x2, y2, r, max(1.2, r * 0.35), FILL)


def draw_handset(ctx, x, y, s=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(-0.65)
    ctx.scale(s, s)
    ctx.set_line_width(1.5)
    ctx.set_source_rgba(1, 1, 1, 0.95)
    ctx.new_path()
    ctx.arc(-9, 0, 3.4, 0, math.tau)
    ctx.stroke()
    ctx.arc(9, 0, 3.4, 0, math.tau)
    ctx.stroke()
    ctx.move_to(-7, 1)
    ctx.curve_to(-3, -7, 3, -7, 7, 1)
    ctx.stroke()
    ctx.restore()


def draw_person(ctx, fr, cx, fy, h, walk=0.0, turn=0.0, hair=False, back=False,
                reach=None, phone=False, chest=0.0, alpha=1.0, amber=0.0):
    def body():
        bob = math.sin(walk * math.pi) ** 2 * h * 0.018
        foot = fy - bob
        head_r = h * 0.118
        hy = foot - h + head_r * 1.05
        hx = cx + turn * head_r * 0.62
        neck = head_r * 0.42
        neck_y = hy + head_r * 0.72
        sw = h * 0.20
        shoulder_y = hy + head_r * 1.55
        waist = h * 0.125
        waist_y = foot - h * 0.40
        hem = h * 0.175
        hem_y = foot - h * 0.012
        step = math.sin(walk * math.pi) * h * 0.03
        lw = max(1.15, 1.85 * (h / 340))
        if hair:
            circle(ctx, hx, hy + head_r * 0.45, head_r * 1.18, lw * 0.9, FILL)
        pts = [
            (cx - neck, neck_y),
            (cx - sw, shoulder_y),
            (cx - sw * 0.90, shoulder_y + h * 0.07),
            (cx - waist, waist_y),
            (cx - hem + step, hem_y),
            (cx + hem + step, hem_y),
            (cx + waist, waist_y),
            (cx + sw * 0.90, shoulder_y + h * 0.07),
            (cx + sw, shoulder_y),
            (cx + neck, neck_y),
        ]
        poly(ctx, pts)
        ctx.close_path()
        fill_stroke(ctx, lw)
        circle(ctx, hx, hy, head_r, lw, FILL)
        if back:
            line(ctx, cx, shoulder_y + h * 0.06, cx, hem_y - h * 0.12, max(1.0, lw * 0.7), (1, 1, 1, 0.75))
        chest_pt = (cx + turn * h * 0.015, shoulder_y + h * 0.15)
        if reach is not None:
            tx, ty = reach
            side = 1 if tx >= cx else -1
            sx = cx + side * sw * 0.55
            sy = shoulder_y + h * 0.10
            draw_arm(ctx, sx, sy, tx, ty, max(2.6, h * 0.016))
        if phone:
            px = cx + sw * 0.95
            py = shoulder_y + h * 0.22
            if h > 150:
                draw_handset(ctx, px, py, max(0.45, h / 420))
            else:
                circle(ctx, px, py, max(2.4, h * 0.04), 1.1, FILL)
            fr.glow(px, py, max(22, h * 0.30), AMBER, 1.05)
        if chest > 0:
            fr.glow(chest_pt[0], chest_pt[1], h * 0.20, RED, chest)
        if amber > 0:
            fr.glow(cx, shoulder_y + h * 0.05, h * 0.85, AMBER, amber)

    if alpha >= 0.99:
        body()
    else:
        ctx.push_group()
        body()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(alpha)


def draw_door(ctx, x, y, w, h, ajar=0.16):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    stroke(ctx, 1.9)
    m = max(10, w * 0.035)
    ctx.new_path()
    ctx.rectangle(x + m, y + m, w - 2 * m, h - 2 * m)
    stroke(ctx, 1.2, (1, 1, 1, 0.75))
    slab = (w - 2 * m) * (1 - 0.42 * ajar)
    ctx.new_path()
    ctx.move_to(x + m, y + m)
    ctx.line_to(x + m + slab, y + m + h * 0.015)
    ctx.line_to(x + m + slab, y + h - m - h * 0.015)
    ctx.line_to(x + m, y + h - m)
    ctx.close_path()
    fill_stroke(ctx, 1.4, (0.05, 0.05, 0.06), (1, 1, 1, 0.9))
    knob_x = x + m + slab - w * 0.045
    knob_y = y + h * 0.58
    circle(ctx, knob_x, knob_y, max(3.5, w * 0.012), 1.3)


def draw_chair(ctx, x, y, s=1.0):
    w = 168 * s
    h = 250 * s
    lw = 1.6
    line(ctx, x - w / 2, y + h * 0.62, x - w / 2, y - h * 0.95, lw)
    line(ctx, x + w / 2, y + h * 0.62, x + w / 2, y - h * 0.95, lw)
    line(ctx, x - w / 2, y - h * 0.72, x + w / 2, y - h * 0.72, lw)
    line(ctx, x - w / 2, y, x + w / 2, y, lw)
    line(ctx, x - w / 2 + 10, y, x - w / 2 - 8, y + h * 0.62, lw)
    line(ctx, x + w / 2 - 10, y, x + w / 2 + 8, y + h * 0.62, lw)


def draw_seated(ctx, fr, cx, seat_y, h, chest=0.0):
    head_r = h * 0.16
    hy = seat_y - h * 0.72
    sw = h * 0.30
    lw = 1.7
    pts = [
        (cx - head_r * 0.45, hy + head_r * 0.85),
        (cx - sw, hy + head_r * 1.35),
        (cx - sw * 0.82, seat_y - 2),
        (cx + sw * 0.82, seat_y - 2),
        (cx + sw, hy + head_r * 1.35),
        (cx + head_r * 0.45, hy + head_r * 0.85),
    ]
    poly(ctx, pts)
    ctx.close_path()
    fill_stroke(ctx, lw)
    circle(ctx, cx, hy, head_r, lw, FILL)
    # folded arm, hand on the chest
    chest_pt = (cx + h * 0.02, hy + head_r * 1.7)
    draw_arm(ctx, cx + sw * 0.65, hy + head_r * 1.45, chest_pt[0], chest_pt[1], h * 0.035)
    # legs
    leg = [
        (cx - h * 0.06, seat_y),
        (cx + h * 0.34, seat_y - 2),
        (cx + h * 0.48, seat_y + h * 0.08),
        (cx + h * 0.52, seat_y + h * 0.30),
        (cx + h * 0.34, seat_y + h * 0.32),
        (cx + h * 0.30, seat_y + h * 0.12),
        (cx + h * 0.16, seat_y + 4),
        (cx + h * 0.02, seat_y),
    ]
    poly(ctx, leg)
    ctx.close_path()
    fill_stroke(ctx, lw)
    if chest > 0:
        fr.glow(chest_pt[0], chest_pt[1], h * 0.22, RED, chest)


def draw_clock(ctx, cx, cy, r, seconds):
    circle(ctx, cx, cy, r, 1.7)
    circle(ctx, cx, cy, 3.2, 1.2, FILL)
    for i in range(12):
        ang = i / 12 * math.tau - math.pi / 2
        inner = r * (0.78 if i % 3 == 0 else 0.86)
        line(ctx, cx + math.cos(ang) * inner, cy + math.sin(ang) * inner,
             cx + math.cos(ang) * r * 0.94, cy + math.sin(ang) * r * 0.94,
             1.8 if i % 3 == 0 else 1.15)
    # 10:10 plus the moving second hand, so the face feels like a real clock
    base = 10 * 3600 + 10 * 60 + seconds
    sec = (base % 60) / 60 * math.tau - math.pi / 2
    minute = ((base / 60) % 60) / 60 * math.tau - math.pi / 2
    hour = ((base / 3600) % 12) / 12 * math.tau - math.pi / 2

    def hand(ang, length, width):
        line(ctx, cx - math.cos(ang) * r * 0.08, cy - math.sin(ang) * r * 0.08,
             cx + math.cos(ang) * length, cy + math.sin(ang) * length, width)

    hand(hour, r * 0.48, 2.4)
    hand(minute, r * 0.70, 1.8)
    hand(sec, r * 0.78, 1.05)


def rot(x, y, cx, cy, a):
    dx, dy = x - cx, y - cy
    ca, sa = math.cos(a), math.sin(a)
    return cx + dx * ca - dy * sa, cy + dx * sa + dy * ca


def catenary(x0, x1, y_end, y_mid, n=36):
    pts = []
    for i in range(n):
        u = i / (n - 1)
        x = lerp(x0, x1, u)
        y = y_end + (y_mid - y_end) * math.sin(u * math.pi)
        pts.append((x, y))
    return pts


def stroke_polyline(ctx, pts, width=1.5, rgba=WHITE):
    poly(ctx, pts)
    stroke(ctx, width, rgba)


def draw_canyon(ctx, deck_y):
    """Jagged cliffs falling away from the bridge, fading before the subtitles."""

    def fade_line(pts, width=1.55):
        for a, b in zip(pts, pts[1:]):
            y = (a[1] + b[1]) / 2
            alpha = clamp((1260 - y) / 480, 0, 0.85)
            if alpha < 0.05:
                continue
            line(ctx, a[0], a[1], b[0], b[1], width, (1, 1, 1, alpha))

    fade_line([(130, deck_y + 18), (60, deck_y + 160), (120, deck_y + 300),
               (30, deck_y + 470), (80, deck_y + 620)])
    fade_line([(210, deck_y + 28), (160, deck_y + 220), (230, deck_y + 400),
               (170, deck_y + 560)], 1.2)
    fade_line([(950, deck_y + 18), (1020, deck_y + 170), (960, deck_y + 320),
               (1050, deck_y + 480), (990, deck_y + 620)])
    fade_line([(860, deck_y + 28), (910, deck_y + 230), (840, deck_y + 410),
               (900, deck_y + 560)], 1.2)


def gorge():
    rng = np.random.default_rng(3)
    lines = []
    specs = [
        (80, 760, 40, 1280, 14, 26),
        (160, 800, 210, 1240, 11, 18),
        (1000, 740, 1040, 1260, 14, 26),
        (900, 790, 820, 1220, 11, 18),
        (70, 980, 250, 1180, 8, 14),
        (1010, 960, 830, 1160, 8, 14),
    ]
    for x0, y0, x1, y1, n, amp in specs:
        pts = [(x0, y0)]
        for i in range(1, n):
            u = i / n
            pts.append((
                lerp(x0, x1, u) + float(rng.uniform(-amp, amp)),
                lerp(y0, y1, u) + float(rng.uniform(-amp * 0.25, amp * 0.25)),
            ))
        pts.append((x1, y1))
        lines.append(pts)
    return lines


GORGE = gorge()


def draw_fade_lines(ctx, lines, width=1.35, y0=760, y1=1240):
    for pts in lines:
        for a, b in zip(pts, pts[1:]):
            y = (a[1] + b[1]) / 2
            alpha = clamp((y1 - y) / (y1 - y0), 0, 0.8)
            if alpha < 0.05:
                continue
            line(ctx, a[0], a[1], b[0], b[1], width, (1, 1, 1, alpha))


def draw_suspension(ctx, deck_y, sway):
    left, right = 130, 950
    cx = 540

    def T(x, y):
        return rot(x, y, cx, deck_y, sway)

    def L(x1, y1, x2, y2, width=1.5, rgba=WHITE):
        a = T(x1, y1)
        b = T(x2, y2)
        line(ctx, a[0], a[1], b[0], b[1], width, rgba)

    for tx in (left + 28, right - 28):
        L(tx, deck_y + 6, tx, deck_y - 280, 1.9)
        L(tx - 16, deck_y - 258, tx + 16, deck_y - 258, 1.45)
    cable = catenary(left, right, deck_y - 230, deck_y - 70, 40)
    stroke_polyline(ctx, [T(*p) for p in cable], 1.55)
    # suspenders and deck
    for i in range(1, 16):
        u = i / 16
        x = lerp(left, right, u)
        # cable height at u
        y_c = (deck_y - 230) + ((deck_y - 70) - (deck_y - 230)) * math.sin(u * math.pi)
        L(x, y_c, x, deck_y - 18, 1.0, (1, 1, 1, 0.8))
    L(left - 10, deck_y - 26, right + 10, deck_y - 26, 1.3)
    L(left - 20, deck_y, right + 20, deck_y, 2.0)
    L(left - 16, deck_y + 12, right + 16, deck_y + 12, 1.2, (1, 1, 1, 0.7))
    return T


def deck_point(u, deck_y, sway):
    left, right = 150, 930
    x = lerp(left, right, u)
    return rot(x, deck_y - 2, 540, deck_y, sway)


def draw_low_bridge(ctx, y):
    ctx.push_group()
    line(ctx, 250, y, 830, y, 2.2)
    line(ctx, 250, y + 16, 830, y + 16, 1.3, (1, 1, 1, 0.8))
    for x in (310, 770):
        line(ctx, x, y + 16, x - 16, y + 78, 1.4)
        line(ctx, x, y + 16, x + 16, y + 78, 1.4)
        line(ctx, x - 16, y + 78, x + 16, y + 78, 1.2)
    # shallow water
    pts = []
    for i in range(24):
        u = i / 23
        pts.append((lerp(280, 800, u), y + 110 + math.sin(u * math.pi * 3) * 4))
    stroke_polyline(ctx, pts, 1.15, (0.75, 0.82, 0.9, 0.9))
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(0.7)


def draw_rope_platform(ctx, y, sway=0.0):
    def yy(x):
        u = (x - 140) / 800
        return y + math.sin(u * math.pi) * 10 + sway

    pts_top = [(x, yy(x) - 34) for x in range(150, 940, 20)]
    pts_bot = [(x, yy(x)) for x in range(150, 940, 20)]
    stroke_polyline(ctx, pts_top, 1.25, (1, 1, 1, 0.75))
    stroke_polyline(ctx, pts_bot, 1.7)
    for x in range(180, 930, 42):
        line(ctx, x, yy(x) - 34, x, yy(x) + 6, 1.05, (1, 1, 1, 0.7))


def draw_card(ctx, x, y):
    w, h, r = 58, 38, 4
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()
    fill_stroke(ctx, 1.4, (0.12, 0.09, 0.05), (1, 0.93, 0.8, 0.95))


def draw_balance(ctx, fr, cx, cy, ang, pulse):
    ctx.new_path()
    ctx.move_to(cx, cy + 6)
    ctx.line_to(cx - 36, cy + 86)
    ctx.line_to(cx + 36, cy + 86)
    ctx.close_path()
    stroke(ctx, 1.7)
    L = 270
    x1 = cx - math.cos(ang) * L
    y1 = cy - math.sin(ang) * L
    x2 = cx + math.cos(ang) * L
    y2 = cy + math.sin(ang) * L
    line(ctx, x1, y1, x2, y2, 2.0)
    circle(ctx, cx, cy, 5, 1.4, FILL)
    draw_heart(ctx, cx, cy - 30, 0.95 + 0.08 * pulse, 1.5)
    fr.glow(cx, cy - 24, 64, RED, 0.40 + 0.7 * pulse)

    def pan(x, y):
        rim = y + 118
        line(ctx, x, y, x - 20, rim, 1.15, (1, 1, 1, 0.85))
        line(ctx, x, y, x + 20, rim, 1.15, (1, 1, 1, 0.85))
        line(ctx, x, y, x, rim, 1.0, (1, 1, 1, 0.55))
        ctx.new_path()
        ctx.move_to(x - 32, rim)
        ctx.curve_to(x - 36, rim + 36, x + 36, rim + 36, x + 32, rim)
        stroke(ctx, 1.5)
        draw_person(ctx, fr, x, rim + 2, 62)

    pan(x1, y1)
    pan(x2, y2)


# ---------------------------------------------------------------- scenes


def scene_door(fr, t, dur, away=False):
    p = t / dur
    e = ease(p)
    fr.zoom = lerp(1.02, 1.07, e)
    if away:
        fr.zoom = lerp(1.06, 1.0, e)
    fr.prepare()
    if not away:
        step = ease(clamp(p / 0.45, 0, 1))
        turn = ease(clamp((p - 0.28) / 0.4, 0, 1)) * 1.0
        draw_door(fr.ctx, 300, 210, 480, 820, ajar=lerp(0.06, 0.22, step))
        pulse = heartbeat(t, 108)
        draw_person(fr.ctx, fr, lerp(500, 400, step), lerp(960, 1100, step),
                    lerp(240, 330, step), walk=t * 1.2, turn=turn,
                    chest=0.30 + 0.70 * pulse)
        draw_person(fr.ctx, fr, lerp(580, 700, step), lerp(980, 1110, step),
                    lerp(230, 310, step), walk=t * 1.2 + 0.4)
    else:
        draw_door(fr.ctx, 390, 260, 300, 500, ajar=lerp(0.22, 0.08, e))
        pulse = heartbeat(t, 100) * (1 - e)
        phase = t * 1.5
        draw_person(fr.ctx, fr, lerp(400, 500, e), lerp(1120, 800, e),
                    lerp(340, 150, e), walk=phase, back=True, chest=pulse, alpha=lerp(1, 0.85, e))
        draw_person(fr.ctx, fr, lerp(700, 600, e), lerp(1140, 820, e),
                    lerp(320, 140, e), walk=phase + 0.5, back=True, alpha=lerp(1, 0.8, e))


def scene_crowd(fr, t, dur):
    p = t / dur
    fr.zoom = lerp(1.0, 1.05, ease(p))
    fr.flicker = flicker(t)
    fr.spot_ang = 0.78
    fr.spot_r = 2100
    fr.prepare()
    xs = [150, 290, 430, 540, 680, 820, 960]
    for i, x in enumerate(xs):
        special = i == 3
        h = 210 if special else 175
        fy = 545 if special else 560
        draw_person(fr.ctx, fr, x, fy, h, amber=0.34 if special else 0.0)
        if special:
            circle(fr.ctx, x, fy - h * 0.48, h * 0.62, 1.15, None, (1, 1, 1, 0.4))
    draw_person(fr.ctx, fr, 540, 1180, 460, back=True)


def scene_threads(fr, t, dur):
    p = t / dur
    e = ease(p)
    fr.oy = lerp(H / 2 - 20, H / 2 + 90, e)
    fr.zoom = lerp(1.0, 1.06, e)
    fr.prepare()
    join = ease(clamp(p / 0.5, 0, 1))
    pulse = heartbeat(t, 88)
    cx = 540
    meet_y = lerp(480, 600, join)
    heart_s = lerp(1.35, 2.45, max(join, 0.2)) * (1 + 0.045 * pulse)
    heart_y = lerp(760, 880, join)

    def thread(x0, tremble, phase):
        pts = []
        n = 48
        for i in range(n):
            u = i / (n - 1)
            y = lerp(120, meet_y, u)
            x = lerp(x0, cx, u * join + u * 0.15 * (1 - join))
            sag = math.sin(u * math.pi) * 36
            wob = math.sin(u * 16 + t * 7 + phase) * tremble * math.sin(u * math.pi)
            pts.append((x + wob, y + sag))
        return pts

    stroke_polyline(fr.ctx, thread(300, 1.5, 0.0), 1.5)
    stroke_polyline(fr.ctx, thread(780, 8.5, 1.4), 1.5)
    cord_end = heart_y - heart_s * 15
    cord = []
    for i in range(36):
        u = i / 35
        y = lerp(meet_y, cord_end, u)
        amp = (1 - u) * 22 * join
        x = cx + math.sin(u * math.pi * 3 + t * 1.6) * amp
        cord.append((x, y))
    stroke_polyline(fr.ctx, cord, 1.6)
    if join > 0.2:
        draw_heart(fr.ctx, cx, heart_y, heart_s)
        fr.glow(cx, heart_y - 4, 86, RED, 0.38 + 0.72 * pulse)


def scene_bridge(fr, t, dur):
    p = t / dur
    e = ease(p)
    deck_y = 640 + math.sin(t * 1.35) * 7
    sway = math.sin(t * 1.05) * 0.014 + math.sin(t * 2.4) * 0.004
    u = lerp(0.14, 0.82, e)
    wx, wy = deck_point(u, deck_y, sway)
    fr.zoom = lerp(1.0, 1.08, e)
    fr.oy = lerp(H / 2 - 40, H / 2 + 70, e)
    sx, sy = fr.w2s(wx, wy - 360)
    fr.spot_cx = clamp(sx, 260, 820)
    fr.spot_cy = -60
    fr.spot_r = 1500
    fr.spot_ang = 0.46
    fr.ambient = 0.16
    fr.prepare()
    draw_suspension(fr.ctx, deck_y, sway)
    draw_canyon(fr.ctx, deck_y)
    river = []
    for i in range(30):
        uu = i / 29
        river.append((lerp(200, 880, uu), 1120 + math.sin(uu * math.pi * 2 + t * 0.4) * 5))
    stroke_polyline(fr.ctx, river, 1.15, (0.62, 0.74, 0.86, 0.55))
    draw_person(fr.ctx, fr, wx, wy, 88, walk=t * 2.2)


def scene_card(fr, t, dur):
    p = t / dur
    e = ease(p)
    give = ease(clamp((p - 0.12) / 0.55, 0, 1))
    card_x = lerp(630, 500, give)
    card_y = lerp(760, 805, give)
    fr.zoom = lerp(1.0, 1.075, e)
    fr.ox = lerp(W / 2, card_x, e * 0.35)
    fr.prepare()
    sway = math.sin(t * 1.2) * 4
    platform_y = 1020
    draw_rope_platform(fr.ctx, platform_y, sway)
    female_h = 300
    male_h = 315
    draw_person(fr.ctx, fr, 700, platform_y + sway * 0.2, female_h, hair=True,
                reach=(card_x + 20, card_y + 16))
    draw_person(fr.ctx, fr, 390, platform_y + 6, male_h,
                reach=(card_x - 8, card_y + 22))
    draw_card(fr.ctx, card_x - 29, card_y - 19)
    fr.glow(card_x, card_y, 46, AMBER, 0.55)
    draw_low_bridge(fr.ctx, 1105)


def scene_rows(fr, t, dur):
    p = t / dur
    e = ease(p)
    fr.ox = lerp(W / 2 - 28, W / 2 + 28, e)
    fr.zoom = lerp(1.0, 1.04, e)
    fr.prepare()
    upper_phone = {0, 3, 5, 8, 10, 13, 15, 18, 21}
    lower_phone = {6, 16}

    def xs(n):
        return [80 + (920 * i / (n - 1)) for i in range(n)]

    # rope under the suspension-bridge group
    rope = []
    for i, x in enumerate(xs(23)):
        u = i / 22
        y = 470 + math.sin(t * 1.15) * 4 + math.sin(u * math.pi) * 16
        rope.append((x, y + 8))
    stroke_polyline(fr.ctx, rope, 1.25, (1, 1, 1, 0.7))
    for i, x in enumerate(xs(23)):
        u = i / 22
        y = 500 + math.sin(t * 1.15) * 4 + math.sin(u * math.pi) * 16
        draw_person(fr.ctx, fr, x, y, 96, phone=(i in upper_phone))
    line(fr.ctx, 70, 760, 1010, 760, 1.0, (1, 1, 1, 0.45))
    # solid bridge under the calm group
    line(fr.ctx, 70, 1040, 1010, 1040, 2.0)
    line(fr.ctx, 70, 1054, 1010, 1054, 1.15, (1, 1, 1, 0.65))
    for i, x in enumerate(xs(22)):
        draw_person(fr.ctx, fr, x, 1005, 96, phone=(i in lower_phone))


def scene_scale(fr, t, dur):
    p = t / dur
    e = ease(p)
    fr.zoom = lerp(1.0, 1.05, e)
    fr.prepare()
    pulse = heartbeat(t, 90)
    ang = lerp(0.01, 0.20, e) + pulse * 0.012
    draw_balance(fr.ctx, fr, 540, 560, ang, pulse)


def scene_chairs(fr, t, dur):
    p = t / dur
    e = ease(p)
    fr.zoom = lerp(1.0, 1.06, e)
    fr.prepare()
    draw_clock(fr.ctx, 540, 300, 108, t)
    draw_chair(fr.ctx, 390, 900, 1.0)
    draw_chair(fr.ctx, 730, 900, 1.0)
    pulse = heartbeat(t, lerp(100, 72, e))
    draw_seated(fr.ctx, fr, 390, 900, 250, chest=pulse * lerp(0.9, 0.08, e))


SCENES = {
    1: lambda fr, t, d: scene_door(fr, t, d, away=False),
    2: scene_crowd,
    3: scene_threads,
    4: scene_bridge,
    5: scene_card,
    6: scene_rows,
    7: scene_scale,
    8: lambda fr, t, d: scene_door(fr, t, d, away=True),
    9: scene_chairs,
}


def spot_mask(cx, cy, radius, half_ang):
    dx = XS - np.float32(cx)
    dy = YS - np.float32(cy)
    dist = np.sqrt(dx * dx + dy * dy)
    radial = np.clip(1.0 - dist / radius, 0, 1) ** 1.25
    ang = np.abs(np.arctan2(dx, np.maximum(dy, 1.0)))
    cone = np.clip(1.0 - ang / half_ang, 0, 1)
    cone = np.where(dy > -30, cone, 0)
    return (radial * cone).astype(np.float32)


def render_scene_image(scene_id, t, dur, marked, fade, seed=0):
    fr = Frame()
    if not hasattr(fr, "flicker"):
        fr.flicker = flicker(t)
    SCENES[scene_id](fr, t, dur)
    if not getattr(fr, "flicker", None):
        pass
    flick = getattr(fr, "flicker", flicker(t))
    fr.surface.flush()
    buf = np.ndarray((H, W, 4), dtype=np.uint8, buffer=fr.surface.get_data())
    rgb = np.ascontiguousarray(buf[:, :, [2, 1, 0]]).astype(np.float32)

    mask = spot_mask(fr.spot_cx, fr.spot_cy, fr.spot_r, fr.spot_ang) * flick
    factor = 0.03 + 0.97 * np.clip(mask ** 0.8, 0, 1)
    if fr.ambient:
        amb = np.clip((YS[:, 0] - 820) / 500, 0, 1) * fr.ambient
        factor = np.maximum(factor, amb[:, None])
    img = rgb * factor[:, :, None]
    img += (np.clip(mask, 0, 1) ** 1.15)[:, :, None] * 32
    img *= GUARD[:, None, None]
    for x, y, radius, color, intensity in fr.glows:
        sx, sy = fr.w2s(x, y)
        add_glow(img, sx, sy, radius * fr.zoom, color, intensity)
    add_glow(img, fr.spot_cx, 16, 70, (255, 255, 255), 0.16 * flick)
    # Grain sits on the lit image only, so the surrounding black stays black.
    rng = np.random.default_rng(seed + 11)
    noise = rng.integers(-14, 15, size=(H, W), dtype=np.int16).astype(np.float32)
    lit = np.clip(img.mean(axis=2) / 36.0, 0.0, 1.0)
    img += (noise * lit)[:, :, None]
    np.clip(img, 0, 255, out=img)
    out = img.astype(np.uint8)
    out = draw_subtitles(out, marked)
    if fade < 0.999:
        out = np.clip(out.astype(np.float32) * fade, 0, 255).astype(np.uint8)
    return out


def add_glow(img, x, y, radius, color, intensity):
    if intensity <= 0.01 or radius < 1:
        return
    r = int(math.ceil(radius))
    x0 = max(0, int(x) - r)
    x1 = min(W, int(x) + r + 1)
    y0 = max(0, int(y) - r)
    y1 = min(H, int(y) + r + 1)
    if x1 <= x0 or y1 <= y0:
        return
    yy, xx = np.ogrid[y0:y1, x0:x1]
    d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2)
    a = np.clip(1 - d / radius, 0, 1) ** 2 * intensity
    region = img[y0:y1, x0:x1]
    region[:, :, 0] += a * color[0]
    region[:, :, 1] += a * color[1]
    region[:, :, 2] += a * color[2]


def edge_fade(t, start, end, fin=0.28, fout=0.28):
    f = 1.0
    if t - start < fin:
        f = (t - start) / fin
    if end - t < fout:
        f = min(f, (end - t) / fout)
    return clamp(f, 0.0, 1.0)


def frame_at(timeline, t, index):
    scenes = timeline["scenes"]
    subs = timeline["subs"]
    scene = scenes[-1]
    for s in scenes:
        if s["start"] <= t < s["end"]:
            scene = s
            break
    marked = None
    for sub in subs:
        if sub["start"] <= t < sub["hold"]:
            marked = sub["marked"]
            break
    local = t - scene["start"]
    dur = max(0.3, scene["end"] - scene["start"])
    last = scene["id"] == scenes[-1]["id"]
    fade = edge_fade(t, scene["start"], scene["end"], 0.30, 1.0 if last else 0.30)
    return render_scene_image(scene["id"], local, dur, marked, fade, seed=index)


def preview(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    sample_idx = [0, 3, 4, 6, 9, 11, 15, 16, 19]
    durations = [12, 6, 6, 14, 13, 13, 11, 10, 10]
    thumbs = []
    for i, (idx, dur) in enumerate(zip(sample_idx, durations), 1):
        text, _ = parse_marked(MARKED[idx])
        lines = wrap_text(text)
        print(f"scene {i} subtitle lines:")
        for line, _s in lines:
            flag = " !" if len(line) > 13 else ""
            print(f"  {len(line):2d} {line}{flag}")
        img = render_scene_image(i, dur * 0.62, dur, MARKED[idx], 1.0, seed=i)
        path = out_dir / f"scene_{i:02d}.png"
        Image.fromarray(img, "RGB").save(path)
        thumbs.append(img)
        print(f"  wrote {path}")
    # contact sheet
    tw, th = 270, 480
    sheet = Image.new("RGB", (tw * 3, th * 3), "black")
    for i, img in enumerate(thumbs):
        im = Image.fromarray(img, "RGB").resize((tw, th), Image.Resampling.LANCZOS)
        sheet.paste(im, ((i % 3) * tw, (i // 3) * th))
    sheet_path = out_dir / "contact.png"
    sheet.save(sheet_path)
    print(sheet_path)


def render_video(timeline_path: Path, audio_path: Path, out_path: Path, max_seconds=None):
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    duration = timeline["duration"] if max_seconds is None else min(timeline["duration"], max_seconds)
    nframes = int(round(duration * FPS))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "pipe:0",
        "-i", str(audio_path),
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0",
        "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "1",
        "-shortest", str(out_path),
    ]
    log_path = out_path.with_suffix(".ffmpeg.log")
    log = open(log_path, "w")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    try:
        for i in range(nframes):
            t = i / FPS
            frame = frame_at(timeline, t, i)
            proc.stdin.write(frame.tobytes())
            if i % FPS == 0:
                proc.stdin.flush()
                print(f"\rframe {i}/{nframes}  t={t:.1f}s", end="", flush=True)
        proc.stdin.close()
        code = proc.wait()
    except BrokenPipeError:
        code = proc.wait()
    log.close()
    print()
    if code != 0:
        print(log_path.read_text()[-2000:], file=sys.stderr)
        raise SystemExit(f"ffmpeg exited {code}")
    print(out_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--timeline", type=Path)
    parser.add_argument("--audio", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-seconds", type=float)
    args = parser.parse_args()
    if args.preview:
        preview(args.preview)
    elif args.timeline and args.audio and args.out:
        render_video(args.timeline, args.audio, args.out, args.max_seconds)
    else:
        parser.error("use --preview DIR or --timeline --audio --out")


if __name__ == "__main__":
    main()
