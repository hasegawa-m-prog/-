#!/usr/bin/env python3
"""Pure-black stick-figure frames for the essay shorts.

Visual rules are fixed: 1080x1920, one thin ground line at 62% height,
white stick figures about 8.5% of the frame tall, line width 0.3% of width,
and at most one red accent.
"""

from __future__ import annotations

import math
from copy import deepcopy

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
GROUND_Y = int(round(H * 0.62))  # 1190
LINE_W = W * 0.003  # 3.24px
RED = (0xE0 / 255, 0x20 / 255, 0x2A / 255)
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_SIZE = 75  # glyph height lands near 75px, ~7% of width
FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE, index=0)

HEAD_R = 17
BODY = 56
UPPER = 30
LOWER = 26


def ease(p: float) -> float:
    p = 0.0 if p < 0 else 1.0 if p > 1 else p
    return p * p * (3 - 2 * p)


def lerp(a, b, t):
    return a + (b - a) * t


def copy_pose(p):
    return dict(p)


# Angles: 0 points down, positive turns toward screen-right.
POSES = {
    "slump": dict(hip=70, lean=10, head_x=8, head_y=6, la0=-28, la1=-10, ra0=22, ra1=16, stance=16, knee=7, xoff=0),
    "slump_deep": dict(hip=64, lean=16, head_x=12, head_y=10, la0=-24, la1=-8, ra0=26, ra1=18, stance=15, knee=8, xoff=0),
    "look": dict(hip=74, lean=2, head_x=-6, head_y=-2, la0=-22, la1=-8, ra0=20, ra1=10, stance=17, knee=6, xoff=0),
    "chest": dict(hip=70, lean=8, head_x=6, head_y=4, la0=-24, la1=-8, ra0=40, ra1=292, stance=16, knee=7, xoff=0),
    "stand": dict(hip=76, lean=0, head_x=0, head_y=0, la0=-18, la1=-6, ra0=18, ra1=6, stance=18, knee=5, xoff=0),
    "placid": dict(hip=76, lean=-2, head_x=-2, head_y=0, la0=-34, la1=-8, ra0=30, ra1=12, stance=18, knee=5, xoff=0),
    "call": dict(hip=76, lean=-2, head_x=-2, head_y=-1, la0=-30, la1=-6, ra0=108, ra1=24, stance=18, knee=5, xoff=0),
    "stepback": dict(hip=72, lean=6, head_x=4, head_y=4, la0=-26, la1=-8, ra0=24, ra1=14, stance=20, knee=8, xoff=-48),
    "reach": dict(hip=74, lean=6, head_x=2, head_y=1, la0=-20, la1=-6, ra0=74, ra1=68, stance=17, knee=6, xoff=0),
    "down": dict(hip=74, lean=0, head_x=0, head_y=2, la0=-16, la1=-4, ra0=16, ra1=6, stance=17, knee=5, xoff=0),
    "open": dict(hip=76, lean=0, head_x=0, head_y=-2, la0=-62, la1=-18, ra0=62, ra1=18, stance=18, knee=5, xoff=0),
    "bow": dict(hip=58, lean=20, head_x=14, head_y=8, la0=-18, la1=8, ra0=52, ra1=28, stance=22, knee=16, xoff=0),
    "palm": dict(hip=74, lean=2, head_x=0, head_y=0, la0=-18, la1=-6, ra0=70, ra1=64, stance=17, knee=6, xoff=0),
    "close": dict(hip=72, lean=6, head_x=4, head_y=3, la0=-20, la1=-6, ra0=24, ra1=40, stance=16, knee=7, xoff=0),
    "nod": dict(hip=74, lean=6, head_x=6, head_y=8, la0=-18, la1=-4, ra0=20, ra1=8, stance=16, knee=6, xoff=0),
}


def _end(x, y, length, deg):
    r = math.radians(deg)
    return x + math.sin(r) * length, y + math.cos(r) * length


def _stroke(ctx, x1, y1, x2, y2):
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    ctx.stroke()


def draw_ground(ctx):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.3)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    y_base = GROUND_Y
    pts = []
    x = 64
    while x <= W - 64:
        y = y_base + math.sin(x * 0.021) * 2.0 + math.sin(x * 0.061 + 1.2) * 1.1
        pts.append((x, y))
        x += 7
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        bucket = int(x1) // 96
        if bucket % 9 == 4 and (int(x1) % 96) > 72:
            continue
        ctx.move_to(x1, y1)
        ctx.line_to(x2, y2)
        ctx.stroke()


def figure_joints(x, pose):
    """Return joint positions for a front-view stick figure standing on the ground."""
    px = x + pose["xoff"]
    hip = (px + pose["lean"] * 0.25, GROUND_Y - pose["hip"])
    shoulder = (px + pose["lean"], hip[1] - BODY)
    head = (shoulder[0] + pose["head_x"], shoulder[1] - HEAD_R - 7 + pose["head_y"])
    chest = ((shoulder[0] + hip[0]) / 2, (shoulder[1] + hip[1]) / 2 + 4)
    la_e = _end(*shoulder, UPPER, pose["la0"])
    la_h = _end(*la_e, LOWER, pose["la1"])
    ra_e = _end(*shoulder, UPPER, pose["ra0"])
    ra_h = _end(*ra_e, LOWER, pose["ra1"])
    foot_l = (px - pose["stance"], GROUND_Y)
    foot_r = (px + pose["stance"], GROUND_Y)
    knee_l = (
        (hip[0] + foot_l[0]) / 2 - pose["knee"] * 0.35,
        (hip[1] + GROUND_Y) / 2 - pose["knee"],
    )
    knee_r = (
        (hip[0] + foot_r[0]) / 2 + pose["knee"] * 0.35,
        (hip[1] + GROUND_Y) / 2 - pose["knee"],
    )
    return {
        "hip": hip,
        "shoulder": shoulder,
        "head": head,
        "chest": chest,
        "la_e": la_e,
        "la_h": la_h,
        "ra_e": ra_e,
        "ra_h": ra_h,
        "knee_l": knee_l,
        "knee_r": knee_r,
        "foot_l": foot_l,
        "foot_r": foot_r,
    }


def draw_figure(ctx, x, pose, color=(1, 1, 1)):
    j = figure_joints(x, pose)
    ctx.set_source_rgb(*color)
    ctx.set_line_width(LINE_W)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    hx, hy = j["head"]
    ctx.arc(hx, hy, HEAD_R, 0, math.tau)
    ctx.stroke()
    _stroke(ctx, *j["shoulder"], *j["hip"])
    _stroke(ctx, *j["shoulder"], *j["la_e"])
    _stroke(ctx, *j["la_e"], *j["la_h"])
    _stroke(ctx, *j["shoulder"], *j["ra_e"])
    _stroke(ctx, *j["ra_e"], *j["ra_h"])
    _stroke(ctx, *j["hip"], *j["knee_l"])
    _stroke(ctx, *j["knee_l"], *j["foot_l"])
    _stroke(ctx, *j["hip"], *j["knee_r"])
    _stroke(ctx, *j["knee_r"], *j["foot_r"])
    return j


def draw_note(ctx, x, y):
    """A single eighth note, drawn as a symbol rather than a character."""
    ctx.set_source_rgb(1, 1, 1)
    ctx.save()
    ctx.translate(x, y + 10)
    ctx.rotate(-0.45)
    ctx.scale(1.35, 0.78)
    ctx.arc(0, 0, 5.0, 0, math.tau)
    ctx.fill()
    ctx.restore()
    ctx.set_line_width(2.5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x + 6, y + 8)
    ctx.line_to(x + 6, y - 20)
    ctx.stroke()
    ctx.move_to(x + 6, y - 20)
    ctx.curve_to(x + 20, y - 16, x + 18, y - 6, x + 8, y - 8)
    ctx.stroke()


def draw_question(ctx, x, y):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x - 8, y + 2)
    ctx.curve_to(x - 10, y - 14, x + 12, y - 16, x + 8, y - 2)
    ctx.curve_to(x + 5, y + 6, x, y + 6, x, y + 10)
    ctx.stroke()
    ctx.arc(x, y + 18, 2.1, 0, math.tau)
    ctx.fill()


def draw_radial(ctx, x, y, n=7, inner=22, outer=36):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.2)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(n):
        a = -math.pi / 2 + i * math.tau / n
        ctx.move_to(x + math.cos(a) * inner, y + math.sin(a) * inner)
        ctx.line_to(x + math.cos(a) * outer, y + math.sin(a) * outer)
        ctx.stroke()


def draw_dots_between(ctx, x1, x2, y, gap=16):
    ctx.set_source_rgb(1, 1, 1)
    if x2 < x1:
        x1, x2 = x2, x1
    x = x1
    while x <= x2:
        ctx.arc(x, y, 2.15, 0, math.tau)
        ctx.fill()
        x += gap


def draw_chain(ctx, x1, y1, x2, y2, n=5):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.2)
    pts = []
    for i in range(n):
        t = (i + 0.5) / n
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t + math.sin(t * math.pi) * 10
        pts.append((x, y))
    for i, (x, y) in enumerate(pts):
        ctx.arc(x, y, 5.2, 0, math.tau)
        ctx.stroke()
        if i:
            px, py = pts[i - 1]
            ctx.move_to(px + 5, py)
            ctx.line_to(x - 5, y)
            ctx.stroke()


def draw_arch(ctx, x, y, r=86):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.4)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.arc(x, y + 18, r, math.pi * 1.08, math.pi * 1.92)
    ctx.stroke()


def draw_sun(ctx, x, y, r=11):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.3)
    ctx.arc(x, y, r, 0, math.tau)
    ctx.stroke()
    for i in range(8):
        a = i * math.tau / 8
        ctx.move_to(x + math.cos(a) * (r + 5), y + math.sin(a) * (r + 5))
        ctx.line_to(x + math.cos(a) * (r + 14), y + math.sin(a) * (r + 14))
        ctx.stroke()


def draw_scatter(ctx, x, y, t=0.0):
    ctx.set_source_rgb(1, 1, 1)
    seeds = ((-18, -6), (14, -16), (26, 4), (-8, -28), (6, 12), (-28, 8), (20, -30))
    rise = t * 14
    for i, (dx, dy) in enumerate(seeds):
        ctx.arc(x + dx, y + dy - rise, 2.0, 0, math.tau)
        ctx.fill()


def draw_bubble(ctx, x, y, kind="mini"):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.3)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(1.15, 0.82)
    ctx.arc(0, 0, 34, 0, math.tau)
    ctx.restore()
    ctx.stroke()
    ctx.move_to(x - 10, y + 24)
    ctx.line_to(x - 22, y + 40)
    ctx.stroke()
    if kind == "empty":
        return
    if kind == "mini":
        # tiny stick figure inside the bubble
        ctx.arc(x, y - 8, 5, 0, math.tau)
        ctx.stroke()
        _stroke(ctx, x, y - 3, x, y + 12)
        _stroke(ctx, x, y + 2, x - 8, y + 8)
        _stroke(ctx, x, y + 2, x + 8, y + 8)
        _stroke(ctx, x, y + 12, x - 6, y + 20)
        _stroke(ctx, x, y + 12, x + 6, y + 20)


def draw_wound(ctx, x, y):
    ctx.save()
    ctx.translate(x, y)
    ctx.set_source_rgb(*RED)
    ctx.move_to(0, -7)
    ctx.curve_to(7, -2, 5, 6, 0, 10)
    ctx.curve_to(-5, 6, -7, -2, 0, -7)
    ctx.fill()
    ctx.restore()


def draw_thread(ctx, x1, y1, x2, y2, slack=0.15):
    ctx.set_source_rgb(*RED)
    ctx.set_line_width(2.6)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2 + slack * 180
    ctx.move_to(x1, y1)
    ctx.curve_to(x1, y1 + 20, mx, my, x2, y2)
    ctx.stroke()


def draw_tag(ctx, x, y, grounded=False):
    ctx.save()
    ctx.translate(x, y)
    if grounded:
        ctx.rotate(-0.5)
    ctx.set_source_rgb(*RED)
    ctx.new_path()
    ctx.arc(-8, 0, 7, math.pi / 2, math.pi * 1.5)
    ctx.line_to(10, -7)
    ctx.line_to(16, 0)
    ctx.line_to(10, 7)
    ctx.close_path()
    ctx.fill()
    ctx.set_source_rgb(0, 0, 0)
    ctx.arc(-8, 0, 2.1, 0, math.tau)
    ctx.fill()
    ctx.restore()


def draw_hollow(ctx, x, y):
    ctx.set_source_rgb(*RED)
    ctx.set_line_width(2.4)
    ctx.arc(x, y, 8.5, 0, math.tau)
    ctx.stroke()


def draw_palm_mark(ctx, x, y):
    ctx.set_source_rgb(*RED)
    ctx.arc(x, y, 5.2, 0, math.tau)
    ctx.fill()


def blend_pose(a, b, t):
    out = {}
    keys = set(a) | set(b)
    for k in keys:
        out[k] = lerp(a.get(k, 0), b.get(k, 0), t)
    return out


def pose_at(base_name, action, t, carried):
    """Return (pose, new_carried). Cyclic actions return to the carried pose."""
    t = ease(t)
    if action in ("tilt", "sway", "flinch", "nod", "still"):
        p = copy_pose(carried)
        if action == "tilt":
            p["head_x"] = carried["head_x"] + math.sin(t * math.pi) * 10
        elif action == "sway":
            p["xoff"] = carried["xoff"] + math.sin(t * math.pi * 2) * 7
            p["ra0"] = carried["ra0"] + math.sin(t * math.pi * 2) * 8
        elif action == "flinch":
            p["head_y"] = carried["head_y"] + math.sin(t * math.pi) * 5
            p["hip"] = carried["hip"] + math.sin(t * math.pi) * 3
        elif action == "nod":
            p["head_y"] = carried["head_y"] + math.sin(t * math.pi) * 8
        return p, carried
    target = POSES[action]
    return blend_pose(carried, target, t), target if t >= 0.999 else carried


def render_scene(scene, poses, scatter_t=0.0, surface=None):
    if surface is None:
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    draw_ground(ctx)

    joints = []
    for i, person in enumerate(scene["people"]):
        joints.append(draw_figure(ctx, person["x"], poses[i]))

    # symbols use joint positions
    for sym in scene.get("symbols", []):
        kind = sym["kind"]
        if kind == "note":
            h = joints[sym["who"]]["head"]
            draw_note(ctx, h[0] + sym.get("dx", 42), h[1] + sym.get("dy", -38))
        elif kind == "question":
            h = joints[sym["who"]]["head"]
            draw_question(ctx, h[0] + sym.get("dx", 50), h[1] + sym.get("dy", -44))
        elif kind == "radial":
            h = joints[sym["who"]]["head"]
            draw_radial(ctx, h[0], h[1] - 8)
        elif kind == "dotted":
            a = joints[sym["a"]]["chest"]
            b = joints[sym["b"]]["chest"]
            draw_dots_between(ctx, a[0] + 28, b[0] - 28, (a[1] + b[1]) / 2)
        elif kind == "chain":
            a = joints[sym["a"]]["chest"]
            b = joints[sym["b"]]["chest"]
            draw_chain(ctx, a[0] + 20, a[1], b[0] - 20, b[1])
        elif kind == "arch":
            h = joints[sym["who"]]["head"]
            draw_arch(ctx, h[0], h[1])
        elif kind == "sun":
            draw_sun(ctx, sym.get("x", 820), sym.get("y", 820))
        elif kind == "scatter":
            h = joints[sym["who"]]["head"]
            draw_scatter(ctx, h[0] + 10, h[1] - 20, scatter_t)
        elif kind == "bubble":
            h = joints[sym["who"]]["head"]
            draw_bubble(ctx, h[0] + sym.get("dx", 78), h[1] - 46, sym.get("inside", "mini"))

    red = scene.get("red")
    if red == "wound":
        c = joints[scene.get("red_who", 0)]["chest"]
        draw_wound(ctx, c[0] + 2, c[1])
    elif red == "thread":
        a = joints[scene.get("red_from", 0)]["ra_h"]
        if len(joints) > 1:
            b = joints[scene.get("red_to", 1)]["chest"]
            draw_thread(ctx, a[0], a[1], b[0] - 10, b[1], slack=scene.get("slack", 0.18))
        else:
            draw_thread(ctx, a[0], a[1], min(W - 80, a[0] + 280), GROUND_Y - 8, slack=scene.get("slack", 0.35))
    elif red == "tag":
        if scene.get("tag_ground"):
            foot = joints[scene.get("red_who", 0)]["foot_r"]
            draw_tag(ctx, foot[0] + 36, GROUND_Y - 8, grounded=True)
        else:
            h = joints[scene.get("red_who", 0)]["head"]
            dx = 78
            for sym in scene.get("symbols", []):
                if sym.get("kind") == "bubble":
                    dx = sym.get("dx", 78)
            draw_tag(ctx, h[0] + dx, h[1] - 46)
    elif red == "hollow":
        c = joints[scene.get("red_who", 0)]["chest"]
        draw_hollow(ctx, c[0] + 14, c[1])
    elif red == "palm":
        hnd = joints[scene.get("red_who", 0)]["ra_h"]
        draw_palm_mark(ctx, hnd[0], hnd[1])

    return surface_to_rgb(surface), joints


def surface_to_rgb(surface):
    arr = np.ndarray((H, W, 4), dtype=np.uint8, buffer=surface.get_data())
    # Cairo ARGB32 is premultiplied BGRA in memory on little-endian.
    rgb = np.empty((H, W, 3), dtype=np.uint8)
    rgb[:, :, 0] = arr[:, :, 2]
    rgb[:, :, 1] = arr[:, :, 1]
    rgb[:, :, 2] = arr[:, :, 0]
    return rgb


def make_subtitle(lines):
    """Transparent overlay. One line is centered at 30% height; two lines share that center."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    ascent, descent = FONT.getmetrics()
    step = FONT_SIZE * 1.4
    cy = H * 0.30
    if len(lines) == 1:
        bbox = FONT.getbbox(lines[0])
        gh = bbox[3] - bbox[1]
        width = FONT.getlength(lines[0])
        top = cy - gh / 2 - bbox[1]
        x = (W - width) / 2
        draw.text((x, top), lines[0], font=FONT, fill=(255, 255, 255, 255))
    else:
        widths = [FONT.getlength(ln) for ln in lines]
        b1 = cy - step / 2
        b2 = cy + step / 2
        for baseline, line, width in ((b1, lines[0], widths[0]), (b2, lines[1], widths[1])):
            x = (W - width) / 2
            draw.text((x, baseline - ascent), line, font=FONT, fill=(255, 255, 255, 255))
    return np.asarray(img)


def composite(rgb, overlay):
    if overlay is None:
        return rgb
    a = overlay[:, :, 3:4].astype(np.float32) / 255.0
    if not np.any(a):
        return rgb
    # subtitles only live in the upper band; limit the blend
    y0, y1 = int(H * 0.18), int(H * 0.44)
    base = rgb[y0:y1].astype(np.float32)
    ov = overlay[y0:y1, :, :3].astype(np.float32)
    aa = a[y0:y1]
    rgb = rgb.copy()
    rgb[y0:y1] = np.clip(base * (1 - aa) + ov * aa, 0, 255).astype(np.uint8)
    return rgb


def fade_black(rgb, level):
    """level 1 = full image, 0 = black."""
    if level >= 0.999:
        return rgb
    if level <= 0.001:
        return np.zeros_like(rgb)
    out = rgb.astype(np.float32) * level
    return out.astype(np.uint8)


def measure_figure():
    j = figure_joints(540, POSES["stand"])
    top = j["head"][1] - HEAD_R
    height = GROUND_Y - top
    return height, height / H, LINE_W / W
