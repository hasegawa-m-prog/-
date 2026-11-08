"""黒地に白い線画、という共通の画面を描く。"""

import math

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from series_data import plain, wraps_for

W, H = 1080, 1920
FPS = 24
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
FONT_SIZE = 76  # 画面幅の約7%
RED = (200, 16, 46)
AMBER = (214, 150, 64)
BLUE = (120, 156, 196)
FILL = (0.38, 0.38, 0.41)
WHITE = (1, 1, 1, 1)
RED_LINE = (0.78, 0.06, 0.18, 0.95)

XS = np.arange(W, dtype=np.float32)[None, :]
YS = np.arange(H, dtype=np.float32)[:, None]
_gs, _ge = 1220, 1420
_m = (np.arange(H) - _gs) / (_ge - _gs)
GUARD = np.where(np.arange(H) < _gs, 1.0, np.clip(1.0 - _m, 0.0, 1.0)).astype(np.float32)
GUARD = np.where(np.arange(H) > _ge, 0.0, GUARD)
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=0)
_MASKS = {}


def ease(p):
    p = 0.0 if p < 0 else 1.0 if p > 1 else p
    return p * p * (3 - 2 * p)


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, a, b):
    return a if v < a else b if v > b else v


def heartbeat(t, bpm=78):
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


def draw_person(ctx, fr, cx, fy, h, walk=0.0, turn=0.0, reach=None, chest=0.0, alpha=1.0, amber=0.0):
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
        if reach is not None:
            tx, ty = reach
            side = 1 if tx >= cx else -1
            sx = cx + side * sw * 0.55
            sy = shoulder_y + h * 0.10
            draw_arm(ctx, sx, sy, tx, ty, max(2.4, h * 0.016))
        chest_pt = (cx + turn * h * 0.015, shoulder_y + h * 0.16)
        if chest > 0:
            fr.glow(chest_pt[0], chest_pt[1], h * 0.22, RED, chest)
        if amber > 0:
            fr.glow(cx, shoulder_y + h * 0.08, h * 0.7, AMBER, amber)
        fr._last_chest = chest_pt
        fr._last_hand = reach

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
    circle(ctx, x + m + slab - w * 0.045, y + h * 0.58, max(3.5, w * 0.012), 1.3)


def draw_chair(ctx, x, y, s=1.0, red=False):
    w = 168 * s
    h = 250 * s
    col = RED_LINE if red else WHITE
    lw = 1.6
    line(ctx, x - w / 2, y + h * 0.62, x - w / 2, y - h * 0.95, lw, col)
    line(ctx, x + w / 2, y + h * 0.62, x + w / 2, y - h * 0.95, lw, col)
    line(ctx, x - w / 2, y - h * 0.72, x + w / 2, y - h * 0.72, lw, col)
    line(ctx, x - w / 2, y, x + w / 2, y, lw, col)
    line(ctx, x - w / 2 + 10, y, x - w / 2 - 8, y + h * 0.62, lw, col)
    line(ctx, x + w / 2 - 10, y, x + w / 2 + 8, y + h * 0.62, lw, col)


def draw_clock(ctx, cx, cy, r, seconds):
    circle(ctx, cx, cy, r, 1.7)
    circle(ctx, cx, cy, 3.2, 1.2, FILL)
    for i in range(12):
        ang = i / 12 * math.tau - math.pi / 2
        inner = r * (0.78 if i % 3 == 0 else 0.86)
        line(ctx, cx + math.cos(ang) * inner, cy + math.sin(ang) * inner,
             cx + math.cos(ang) * r * 0.94, cy + math.sin(ang) * r * 0.94,
             1.8 if i % 3 == 0 else 1.15)
    base = 10 * 3600 + 10 * 60 + seconds
    for ang, length, width in (
        ((base % 60) / 60 * math.tau - math.pi / 2, 0.78, 1.15),
        (((base / 60) % 60) / 60 * math.tau - math.pi / 2, 0.62, 1.7),
        (((base / 3600) % 12) / 12 * math.tau - math.pi / 2, 0.42, 2.2),
    ):
        line(ctx, cx - math.cos(ang) * r * 0.08, cy - math.sin(ang) * r * 0.08,
             cx + math.cos(ang) * r * length, cy + math.sin(ang) * r * length, width)


def draw_thread(ctx, x1, y1, x2, y2, sag=36):
    ctx.new_path()
    ctx.move_to(x1, y1)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + sag
    ctx.curve_to(mx, my, mx, my, x2, y2)
    stroke(ctx, 1.35, RED_LINE)


def draw_shoes(ctx, x, y):
    for dx, flip in ((-34, 1), (28, -1)):
        ctx.new_path()
        ctx.move_to(x + dx, y)
        ctx.curve_to(x + dx + 36 * flip, y + 8, x + dx + 40 * flip, y + 22, x + dx + 8 * flip, y + 26)
        ctx.curve_to(x + dx - 16 * flip, y + 24, x + dx - 10 * flip, y + 8, x + dx, y)
        fill_stroke(ctx, 1.3, (0.08, 0.08, 0.09))


def draw_cup(ctx, x, y, s=1.0, glow_fr=None):
    w, h = 36 * s, 48 * s
    ctx.new_path()
    ctx.move_to(x - w / 2, y)
    ctx.curve_to(x - w / 2 - 4 * s, y + h, x + w / 2 + 4 * s, y + h, x + w / 2, y)
    stroke(ctx, 1.5)
    ctx.new_path()
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(w / 2, 8 * s)
    ctx.arc(0, 0, 1, 0, math.tau)
    ctx.restore()
    stroke(ctx, 1.4)
    ctx.new_path()
    ctx.arc(x + w / 2 + 8 * s, y + h * 0.45, 10 * s, -1.2, 1.2)
    stroke(ctx, 1.4)
    if glow_fr is not None:
        glow_fr.glow(x, y + h * 0.4, 40 * s, AMBER, 0.7)


def draw_gift(ctx, x, y, s=1.0):
    w, h = 54 * s, 40 * s
    ctx.new_path()
    ctx.rectangle(x - w / 2, y - h / 2, w, h)
    fill_stroke(ctx, 1.4, (0.1, 0.1, 0.12))
    line(ctx, x, y - h / 2, x, y + h / 2, 1.2, RED_LINE)
    line(ctx, x - w / 2, y, x + w / 2, y, 1.2, RED_LINE)
    ctx.new_path()
    ctx.arc(x - 8 * s, y - h / 2 - 6 * s, 8 * s, 0, math.tau)
    stroke(ctx, 1.2, RED_LINE)
    ctx.arc(x + 8 * s, y - h / 2 - 6 * s, 8 * s, 0, math.tau)
    stroke(ctx, 1.2, RED_LINE)


def draw_book(ctx, x, y, s=1.0, glow_fr=None):
    w, h = 70 * s, 48 * s
    ctx.new_path()
    ctx.move_to(x, y)
    ctx.line_to(x - w, y - 6 * s)
    ctx.line_to(x - w, y - h)
    ctx.line_to(x, y - h + 6 * s)
    ctx.close_path()
    fill_stroke(ctx, 1.3, (0.1, 0.09, 0.08))
    ctx.new_path()
    ctx.move_to(x, y)
    ctx.line_to(x + w, y - 6 * s)
    ctx.line_to(x + w, y - h)
    ctx.line_to(x, y - h + 6 * s)
    ctx.close_path()
    fill_stroke(ctx, 1.3, (0.14, 0.12, 0.1))
    if glow_fr is not None:
        glow_fr.glow(x, y - h / 2, 50 * s, AMBER, 0.55)


def draw_column(ctx, fr, x, base, height, level, accent=None):
    top = base - height
    line(ctx, x - 16, base, x - 16, top, 1.35)
    line(ctx, x + 16, base, x + 16, top, 1.35)
    line(ctx, x - 16, base, x + 16, base, 1.35)
    level = clamp(level, 0.02, 1)
    fh = height * level
    ctx.new_path()
    ctx.rectangle(x - 12, base - fh, 24, fh)
    ctx.set_source_rgba(1, 1, 1, 0.42)
    ctx.fill()
    line(ctx, x - 14, base - fh, x + 14, base - fh, 1.7)
    if accent:
        fr.glow(x, base - fh, 34, accent, 0.85)


def draw_stairs(ctx, x, y, steps, shown, step_w=36, step_h=28):
    cx, cy = x, y
    n = int(math.floor(shown))
    for i in range(max(0, n)):
        line(ctx, cx, cy, cx + step_w, cy, 1.45)
        line(ctx, cx + step_w, cy, cx + step_w, cy - step_h, 1.45)
        cx += step_w
        cy -= step_h
    frac = shown - n
    if 0 < frac < 1 and n < steps:
        line(ctx, cx, cy, cx + step_w * frac, cy, 1.45)


def draw_plinth(ctx, x, y, w=220, h=36):
    ctx.new_path()
    ctx.move_to(x - w / 2, y)
    ctx.line_to(x + w / 2, y)
    ctx.line_to(x + w / 2 - 18, y + h)
    ctx.line_to(x - w / 2 + 18, y + h)
    ctx.close_path()
    fill_stroke(ctx, 1.5, (0.06, 0.06, 0.07))


def draw_path(ctx, x, y0, y1, spread=70):
    line(ctx, x - spread, y0, x - spread * 0.35, y1, 1.35, (1, 1, 1, 0.85))
    line(ctx, x + spread, y0, x + spread * 0.35, y1, 1.35, (1, 1, 1, 0.85))


def draw_rail(ctx, y):
    line(ctx, 120, y, 960, y, 1.6)
    line(ctx, 120, y + 28, 960, y + 28, 1.25, (1, 1, 1, 0.7))
    for x in range(150, 980, 90):
        line(ctx, x, y - 70, x, y + 28, 1.25)


def draw_window(ctx, x, y, w=280, h=160):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    stroke(ctx, 1.7)
    line(ctx, x, y + h * 0.62, x + w, y + h * 0.62, 1.4)
    line(ctx, x + w * 0.5, y, x + w * 0.5, y + h * 0.62, 1.15, (1, 1, 1, 0.7))


def draw_ticket(ctx, x, y, s=1.0, glow_fr=None):
    w, h = 46 * s, 28 * s
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    fill_stroke(ctx, 1.3, (0.12, 0.1, 0.07), (1, 0.93, 0.8, 0.95))
    if glow_fr is not None:
        glow_fr.glow(x + w / 2, y + h / 2, 36 * s, AMBER, 0.7)


def draw_stack(ctx, fr, x, y, sheets, glow=False):
    for i in range(int(sheets)):
        yy = y - i * 10
        ctx.new_path()
        ctx.rectangle(x, yy, 78, 8)
        fill_stroke(ctx, 1.15, (0.12, 0.11, 0.1), (1, 1, 1, 0.9))
    if glow and sheets:
        fr.glow(x + 39, y - sheets * 5, 50, AMBER, 0.75)


def draw_days(ctx, cx, cy, count, progress):
    shown = count * clamp(progress, 0, 1)
    lit = 0
    for r in range(7):
        for c in range(2):
            x = cx + (c - 0.5) * 120
            y = cy + r * 78
            ctx.new_path()
            ctx.rectangle(x, y, 86, 58)
            stroke(ctx, 1.25)
            idx = r * 2 + c
            # 十四日のうち約半分。点の位置は固定。
            if idx in (0, 2, 3, 5, 8, 9, 12) and lit < shown:
                circle(ctx, x + 43, y + 29, 5, 1.2, (0.45, 0.32, 0.14))
                lit += 1


def draw_mirror(ctx, x, y, w, h):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    stroke(ctx, 1.8, RED_LINE)
    ctx.new_path()
    ctx.rectangle(x + 14, y + 14, w - 28, h - 28)
    stroke(ctx, 1.15, (1, 1, 1, 0.75))


def draw_ledger(ctx, x, y, w, h):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    fill_stroke(ctx, 1.4, (0.07, 0.07, 0.08))
    line(ctx, x + w / 2, y, x + w / 2, y + h, 1.5, RED_LINE)
    for i in range(1, 6):
        yy = y + h * i / 6
        line(ctx, x + 18, yy, x + w / 2 - 16, yy, 1.0, (1, 1, 1, 0.35))
        line(ctx, x + w / 2 + 16, yy, x + w - 18, yy, 1.0, (1, 1, 1, 0.35))


def draw_scale(ctx, fr, cx, cy, ang, left_draw, right_draw):
    ctx.new_path()
    ctx.move_to(cx, cy + 6)
    ctx.line_to(cx - 28, cy + 78)
    ctx.line_to(cx + 28, cy + 78)
    ctx.close_path()
    stroke(ctx, 1.6)
    L = 250
    x1 = cx - math.cos(ang) * L
    y1 = cy - math.sin(ang) * L
    x2 = cx + math.cos(ang) * L
    y2 = cy + math.sin(ang) * L
    line(ctx, x1, y1, x2, y2, 1.9)
    circle(ctx, cx, cy, 5, 1.3, FILL)
    fr.glow(cx, cy, 28, AMBER, 0.35)

    def pan(x, y, draw):
        rim = y + 90
        line(ctx, x, y, x - 16, rim, 1.15, (1, 1, 1, 0.8))
        line(ctx, x, y, x + 16, rim, 1.15, (1, 1, 1, 0.8))
        ctx.new_path()
        ctx.move_to(x - 36, rim)
        ctx.curve_to(x - 40, rim + 26, x + 40, rim + 26, x + 36, rim)
        stroke(ctx, 1.4)
        draw(x, rim - 4)

    pan(x1, y1, left_draw)
    pan(x2, y2, right_draw)


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
        self.glows = []
        self.flicker = 1.0

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


def begin(fr, t, dur, z0=1.02, z1=1.07):
    p = 0.0 if dur <= 0 else clamp(t / dur, 0, 1)
    e = ease(p)
    fr.zoom = lerp(z0, z1, e)
    fr.flicker = flicker(t)
    fr.prepare()
    return p, e


def spot_mask(cx, cy, radius, half_ang):
    key = (round(cx), round(cy), round(radius), round(half_ang * 1000))
    cached = _MASKS.get(key)
    if cached is not None:
        return cached
    dx = XS - np.float32(cx)
    dy = YS - np.float32(cy)
    dist = np.sqrt(dx * dx + dy * dy)
    radial = np.clip(1.0 - dist / radius, 0, 1) ** 1.25
    ang = np.abs(np.arctan2(dx, np.maximum(dy, 1.0)))
    cone = np.clip(1.0 - ang / half_ang, 0, 1)
    cone = np.where(dy > -30, cone, 0)
    mask = (radial * cone).astype(np.float32)
    _MASKS[key] = mask
    return mask


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


def draw_subtitles(img, marked):
    if not marked:
        return img
    lines = wraps_for(marked)
    im = Image.fromarray(img, "RGB")
    draw = ImageDraw.Draw(im)
    line_h = int(FONT_SIZE * 1.22)
    bottom = int(H * 0.82)
    y = bottom - line_h * len(lines)
    for marked_line in lines:
        text = plain(marked_line)
        # 赤字の位置
        reds = []
        bare = []
        i = 0
        src = marked_line
        while i < len(src):
            if src[i] == "《":
                j = src.index("》", i)
                word = src[i + 1 : j]
                reds.append((len(bare), len(bare) + len(word)))
                bare.extend(word)
                i = j + 1
            else:
                bare.append(src[i])
                i += 1
        spans = []
        buf = ""
        red = None
        for k, ch in enumerate(text):
            is_red = any(a <= k < b for a, b in reds)
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


def compose(fr, marked, fade, seed):
    fr.surface.flush()
    buf = np.ndarray((H, W, 4), dtype=np.uint8, buffer=fr.surface.get_data())
    rgb = np.ascontiguousarray(buf[:, :, [2, 1, 0]]).astype(np.float32)
    flick = fr.flicker
    mask = spot_mask(fr.spot_cx, fr.spot_cy, fr.spot_r, fr.spot_ang) * flick
    factor = 0.03 + 0.97 * np.clip(mask ** 0.8, 0, 1)
    img = rgb * factor[:, :, None]
    img += (np.clip(mask, 0, 1) ** 1.15)[:, :, None] * 32
    img *= GUARD[:, None, None]
    for x, y, radius, color, intensity in fr.glows:
        sx = (x - fr.ox) * fr.zoom + W / 2
        sy = (y - fr.oy) * fr.zoom + H / 2
        add_glow(img, sx, sy, radius * fr.zoom, color, intensity)
    add_glow(img, fr.spot_cx, 16, 70, (255, 255, 255), 0.16 * flick)
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
