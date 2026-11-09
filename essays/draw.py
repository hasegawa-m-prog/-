"""Pure-black stick-figure frames for the essay shorts.

Style is fixed: 1080x1920, one thin ground line at 62% height,
white stick figures about 8.6% of the screen tall, one red accent.
"""

from __future__ import annotations

import math

import cairo
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
GROUND_Y = H * 0.62
FIG_H = H * 0.086
LW = W * 0.003  # about 0.3% of the screen width
RED = (224 / 255, 32 / 255, 42 / 255)
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
# Noto Sans CJK Bold collection: index 0 is Japanese.
FONT_INDEX = 0

POS = {
    "L": 0.30 * W,
    "C": 0.50 * W,
    "R": 0.70 * W,
    "FL": 0.23 * W,
    "FR": 0.77 * W,
}


def ease(p: float) -> float:
    p = 0.0 if p < 0 else 1.0 if p > 1 else p
    return p * p * (3 - 2 * p)


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def load_font(target_h: float | None = None):
    """Pick a font size whose kanji ink is about 7% of the screen width."""
    target = W * 0.07 if target_h is None else target_h
    size = 80
    font = None
    ink = target
    for _ in range(8):
        font = ImageFont.truetype(FONT_PATH, size=size, index=FONT_INDEX)
        box = font.getbbox("傷")
        ink = box[3] - box[1]
        if abs(ink - target) < 1.2:
            break
        size = max(12, int(round(size * target / max(ink, 1))))
    return font, ink


FONT, CHAR_H = load_font()


# Angles are degrees from straight down (or straight up for the torso).
# Positive angles swing toward the direction the figure faces.
POSES = {
    "stand": dict(torso=3, head=2, arm_f=(22, 16), arm_b=(14, 10), leg_f=(8, 4), leg_b=(-7, 3)),
    "down": dict(torso=14, head=20, arm_f=(12, 8), arm_b=(8, 6), leg_f=(6, 5), leg_b=(-5, 4)),
    "up": dict(torso=-6, head=-14, arm_f=(26, 16), arm_b=(12, 8), leg_f=(7, 4), leg_b=(-6, 3)),
    "easy": dict(torso=-3, head=-6, arm_f=(36, 42), arm_b=(10, 14), leg_f=(5, 3), leg_b=(-11, 6)),
    "reach": dict(torso=16, head=4, arm_f=(78, 70), arm_b=(18, 12), leg_f=(16, 8), leg_b=(-8, 4)),
    "open": dict(torso=0, head=-2, arm_f=(86, 72), arm_b=(-74, -48), leg_f=(8, 4), leg_b=(-8, 4)),
    "chest": dict(torso=8, head=14, arm_f=(52, -6), arm_b=(34, -16), leg_f=(7, 4), leg_b=(-6, 4)),
    "squat": dict(torso=18, head=12, arm_f=(42, 28), arm_b=(24, 16), leg_f=(58, 78), leg_b=(42, 64)),
}


def lerp_pose(a: dict, b: dict, t: float) -> dict:
    out = {}
    for key in a:
        va, vb = a[key], b[key]
        if isinstance(va, tuple):
            out[key] = tuple(lerp(x, y, t) for x, y in zip(va, vb))
        else:
            out[key] = lerp(va, vb, t)
    return out


def dest(x, y, ang_deg, length, face, up=False):
    rad = math.radians(ang_deg)
    dx = math.sin(rad) * length * face
    dy = math.cos(rad) * length
    if up:
        dy = -dy
    return x + dx, y + dy


def apply_action(pose_name: str, action, u: float) -> tuple[dict, float]:
    """Return the pose at progress u, and a pixel x shift."""
    base = POSES[pose_name]
    if not action or action[1] == "still":
        return dict(base), 0.0
    kind = action[1]
    if kind == "head":
        posed = dict(base)
        posed["head"] = base["head"] + action[2] * ease(min(1.0, u / 0.86))
        return posed, 0.0
    if kind == "to":
        return lerp_pose(base, POSES[action[2]], ease(min(1.0, u / 0.8))), 0.0
    if kind == "arm":
        posed = dict(base)
        swing = math.sin(u * math.pi) * 12
        posed["arm_f"] = (base["arm_f"][0] + swing, base["arm_f"][1] + swing * 0.4)
        return posed, 0.0
    if kind == "walk":
        s = math.sin(u * math.tau)
        posed = dict(base)
        posed["leg_f"] = (24 * s, 8 + 18 * max(0.0, s))
        posed["leg_b"] = (-24 * s, 8 + 18 * max(0.0, -s))
        posed["arm_f"] = (base["arm_f"][0] - 14 * s, base["arm_f"][1] - 8 * s)
        posed["arm_b"] = (base["arm_b"][0] + 14 * s, base["arm_b"][1] + 8 * s)
        posed["bob"] = abs(math.sin(u * math.tau * 2)) * 3.0
        return posed, action[2] * u
    return dict(base), 0.0


def skeleton(pose: dict, face: int):
    """Stick figure in local space (hip at origin, y grows downward)."""
    head_r = 112
    torso_l = 340
    thigh_l = 255
    shin_l = 235
    ua = 215
    fa = 195
    hip = (0.0, 0.0)
    shoulder = dest(*hip, pose["torso"], torso_l, face, up=True)
    head_c = dest(*shoulder, pose["torso"] + pose["head"], head_r + 8, face, up=True)
    vx, vy = shoulder[0] - head_c[0], shoulder[1] - head_c[1]
    vlen = math.hypot(vx, vy) or 1.0
    neck = (head_c[0] + vx / vlen * head_r, head_c[1] + vy / vlen * head_r)
    elbow_f = dest(*shoulder, pose["arm_f"][0], ua, face)
    hand_f = dest(*elbow_f, pose["arm_f"][1], fa, face)
    elbow_b = dest(*shoulder, pose["arm_b"][0], ua, face)
    hand_b = dest(*elbow_b, pose["arm_b"][1], fa, face)
    knee_f = dest(*hip, pose["leg_f"][0], thigh_l, face)
    foot_f = dest(*knee_f, pose["leg_f"][1], shin_l, face)
    knee_b = dest(*hip, pose["leg_b"][0], thigh_l, face)
    foot_b = dest(*knee_b, pose["leg_b"][1], shin_l, face)
    return {
        "hip": hip,
        "shoulder": shoulder,
        "head": head_c,
        "head_r": head_r,
        "neck": neck,
        "elbow_f": elbow_f,
        "hand_f": hand_f,
        "elbow_b": elbow_b,
        "hand_b": hand_b,
        "knee_f": knee_f,
        "foot_f": foot_f,
        "knee_b": knee_b,
        "foot_b": foot_b,
    }


def map_skeleton(sk, x, ground_y, fig_h, bob=0.0):
    lowest = max(sk["foot_f"][1], sk["foot_b"][1])
    top = sk["head"][1] - sk["head_r"]
    height = lowest - top
    scale = fig_h / height

    def mp(pt):
        return x + pt[0] * scale, ground_y - (lowest - pt[1]) * scale - bob

    out = {k: (mp(v) if isinstance(v, tuple) else v * scale) for k, v in sk.items()}
    out["head_r"] = sk["head_r"] * scale
    hx, hy = out["hip"]
    nx, ny = out["neck"]
    out["chest"] = ((hx + nx) / 2 + (1 if x else 1) * 0, (hy + ny) / 2)
    return out


def figure_geometry(x, ground_y, face, pose_name, action, u, fig_h=FIG_H):
    pose, dx = apply_action(pose_name, action, u)
    sk = skeleton(pose, face)
    bob = pose.get("bob", 0.0)
    geo = map_skeleton(sk, x + dx, ground_y, fig_h, bob=bob)
    # Chest sits slightly on the forward side of the torso.
    hx, hy = geo["hip"]
    nx, ny = geo["neck"]
    geo["chest"] = ((hx + nx) / 2 + face * 5, (hy + ny) / 2)
    geo["face"] = face
    return geo


def _stroke(ctx, width, color):
    ctx.set_line_width(width)
    ctx.set_source_rgb(*color)
    ctx.stroke()


def _line(ctx, a, b):
    ctx.new_sub_path()
    ctx.move_to(*a)
    ctx.line_to(*b)


def draw_figure(ctx, geo, color=(1, 1, 1)):
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    pairs = [
        (geo["hip"], geo["knee_b"]),
        (geo["knee_b"], geo["foot_b"]),
        (geo["shoulder"], geo["elbow_b"]),
        (geo["elbow_b"], geo["hand_b"]),
        (geo["hip"], geo["neck"]),
        (geo["hip"], geo["knee_f"]),
        (geo["knee_f"], geo["foot_f"]),
        (geo["shoulder"], geo["elbow_f"]),
        (geo["elbow_f"], geo["hand_f"]),
    ]
    ctx.set_source_rgb(*color)
    ctx.set_line_width(LW)
    for a, b in pairs:
        ctx.move_to(*a)
        ctx.line_to(*b)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(geo["head"][0], geo["head"][1], geo["head_r"], 0, math.tau)
    ctx.stroke()


def draw_ground(ctx):
    rng_x = 68.0
    y = GROUND_Y
    # Fixed hand-drawn breaks, so the line never flickers between frames.
    spans = [
        (68, 104), (118, 168), (182, 214), (230, 292), (308, 340),
        (356, 430), (446, 488), (506, 590), (608, 646), (664, 742),
        (760, 804), (822, 910), (928, 972), (990, 1012),
    ]
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.15)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    wobble = (-1.1, 0.4, 0.9, -0.6, 1.0, -0.3, 0.7, -0.9, 0.2, 1.1, -0.4, 0.5, -0.8, 0.3)
    for i, (x0, x1) in enumerate(spans):
        ctx.move_to(x0, y + wobble[i])
        ctx.line_to(x1, y + wobble[i] * 0.4)
    ctx.stroke()
    # rng_x is only documentation that the line stays inset from the edges.
    del rng_x


def draw_note(ctx, x, y):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(LW)
    ctx.save()
    ctx.translate(x - 2, y + 4)
    ctx.rotate(-0.45)
    ctx.scale(1.15, 0.72)
    ctx.new_sub_path()
    ctx.arc(0, 0, 7, 0, math.tau)
    ctx.stroke()
    ctx.restore()
    ctx.move_to(x + 5, y + 1)
    ctx.line_to(x + 5, y - 28)
    ctx.stroke()
    ctx.move_to(x + 5, y - 28)
    ctx.curve_to(x + 20, y - 24, x + 16, y - 10, x + 5, y - 13)
    ctx.stroke()


def draw_question(ctx, x, y):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(LW)
    ctx.move_to(x - 9, y - 4)
    ctx.curve_to(x - 10, y - 20, x + 12, y - 20, x + 8, y - 8)
    ctx.curve_to(x + 5, y, x, y + 2, x, y + 8)
    ctx.stroke()
    ctx.new_sub_path()
    ctx.arc(x, y + 16, 2.3, 0, math.tau)
    ctx.fill()


def draw_radial(ctx, x, y):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(LW)
    for i in range(6):
        ang = -math.pi + 0.35 + i * 0.38
        ctx.move_to(x + math.cos(ang) * 26, y + math.sin(ang) * 26)
        ctx.line_to(x + math.cos(ang) * 44, y + math.sin(ang) * 44)
    ctx.stroke()


def draw_dashed(ctx, x1, y1, x2, y2, dash=8, gap=10, color=(1, 1, 1), width=LW):
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1.0
    ux, uy = dx / dist, dy / dist
    ctx.set_source_rgb(*color)
    ctx.set_line_width(width)
    t = 0.0
    while t < dist:
        t2 = min(dist, t + dash)
        ctx.move_to(x1 + ux * t, y1 + uy * t)
        ctx.line_to(x1 + ux * t2, y1 + uy * t2)
        t = t2 + gap
    ctx.stroke()


def draw_chain(ctx, geo, drop=0.0, origin="ankle"):
    """Four linked rings. An ankle chain lies on the ground.
    A hand chain falls onto the ground as drop goes from 0 to 1."""
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(2.2)
    r = 6.4
    step = r * 2 + 5
    n = 4
    e = 1.0 if origin == "ankle" else ease(min(1.0, max(0.0, drop)))
    start = geo["foot_b"] if origin == "ankle" else geo["hand_b"]
    centers = []
    for i in range(n):
        held = (start[0] - geo["face"] * i * (r * 1.7), start[1] + 8 + i * (r * 1.8))
        pooled = (geo["foot_b"][0] - geo["face"] * (12 + i * step), GROUND_Y - r - 1)
        centers.append((lerp(held[0], pooled[0], e), lerp(held[1], pooled[1], e)))
    for i, (cx, cy) in enumerate(centers):
        if i:
            px, py = centers[i - 1]
            dx, dy = cx - px, cy - py
            dist = math.hypot(dx, dy) or 1.0
            ctx.move_to(px + dx / dist * (r + 0.5), py + dy / dist * (r + 0.5))
            ctx.line_to(cx - dx / dist * (r + 0.5), cy - dy / dist * (r + 0.5))
        ctx.new_sub_path()
        ctx.arc(cx, cy, r, 0, math.tau)
    ctx.stroke()


def draw_arch(ctx, x):
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(LW)
    # Taller than the figure, so the head sits clearly inside the arch.
    radius = FIG_H * 1.42
    ctx.new_sub_path()
    # Cairo angles grow clockwise because y points down, so pi -> 2pi passes through the top.
    ctx.arc(x, GROUND_Y, radius, math.pi, math.tau)
    ctx.stroke()


def draw_sun(ctx):
    x, y = W * 0.80, GROUND_Y - FIG_H * 1.35
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(LW)
    ctx.new_sub_path()
    ctx.arc(x, y, 11, 0, math.tau)
    ctx.stroke()
    for i in range(8):
        ang = i * math.pi / 4 + 0.2
        ctx.move_to(x + math.cos(ang) * 16, y + math.sin(ang) * 16)
        ctx.line_to(x + math.cos(ang) * 24, y + math.sin(ang) * 24)
    ctx.stroke()


def draw_scatter(ctx, geo, u):
    ctx.set_source_rgb(1, 1, 1)
    seeds = ((-62, -36), (48, -58), (74, -18), (-28, -78), (36, -24), (-70, -8))
    rise = ease(u) * 22
    for dx, dy in seeds:
        ctx.new_sub_path()
        ctx.arc(geo["chest"][0] + dx, geo["chest"][1] + dy - rise, 2.5, 0, math.tau)
    ctx.fill()


def draw_bubble(ctx, geo):
    hx, hy = geo["head"]
    r = geo["head_r"]
    bw, bh = 86, 54
    cx, cy = hx + geo["face"] * 8, hy - r - 18 - bh / 2
    ctx.set_source_rgb(1, 1, 1)
    ctx.set_line_width(LW)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(1, bh / bw)
    ctx.new_sub_path()
    ctx.arc(0, 0, bw / 2, 0, math.tau)
    ctx.stroke()
    ctx.restore()
    ctx.move_to(cx - geo["face"] * 10, cy + bh / 2 - 2)
    ctx.line_to(hx + geo["face"] * 4, hy - r + 1)
    ctx.stroke()
    ctx.set_line_width(1.8)
    head_c = (cx, cy - 8)
    ctx.new_sub_path()
    ctx.arc(*head_c, 5.5, 0, math.tau)
    ctx.stroke()
    ctx.move_to(cx, cy - 2)
    ctx.line_to(cx, cy + 12)
    ctx.move_to(cx, cy + 2)
    ctx.line_to(cx - 8, cy + 8)
    ctx.move_to(cx, cy + 2)
    ctx.line_to(cx + 8, cy + 7)
    ctx.move_to(cx, cy + 12)
    ctx.line_to(cx - 6, cy + 22)
    ctx.move_to(cx, cy + 12)
    ctx.line_to(cx + 6, cy + 22)
    ctx.stroke()


def draw_wound(ctx, chest, face):
    x, y = chest
    ctx.set_source_rgb(*RED)
    ctx.set_line_width(3.1)
    ctx.move_to(x - 2, y - 11)
    ctx.line_to(x + face * 12, y + 8)
    ctx.move_to(x - 10, y + 1)
    ctx.line_to(x + face * 8, y - 5)
    ctx.stroke()


def draw_shard(ctx, x, y, rot=0.5, scale=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    s = 8 * scale
    ctx.move_to(0, -s)
    ctx.line_to(s * 0.55, s * 0.15)
    ctx.line_to(-s * 0.1, s * 0.95)
    ctx.line_to(-s * 0.7, -s * 0.05)
    ctx.close_path()
    ctx.set_source_rgb(*RED)
    ctx.fill()
    ctx.restore()


def draw_mark(ctx, x, y, radius=14):
    ctx.set_source_rgb(*RED)
    ctx.set_line_width(2.6)
    ctx.new_sub_path()
    ctx.arc(x, y, radius, 0, math.tau)
    ctx.stroke()
    d = radius * 0.52
    ctx.move_to(x - d, y - d)
    ctx.line_to(x + d, y + d)
    ctx.move_to(x + d, y - d)
    ctx.line_to(x - d, y + d)
    ctx.stroke()


def draw_curve(ctx, a, b, sag, color=RED, width=2.5):
    ctx.set_source_rgb(*color)
    ctx.set_line_width(width)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + sag
    ctx.move_to(*a)
    ctx.curve_to(mx, my, mx, my, *b)
    ctx.stroke()


def _geo_map(phrase, u):
    geos = {}
    action = phrase.get("action")
    for fid, pos, face, pose_name in phrase["figs"]:
        act = action if action and action[0] == fid else None
        geos[fid] = figure_geometry(POS[pos], GROUND_Y, face, pose_name, act, u)
    return geos


def _outside(p1, p2, dist):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    norm = math.hypot(dx, dy) or 1.0
    ux, uy = dx / norm, dy / norm
    return (p1[0] + ux * dist, p1[1] + uy * dist), (p2[0] - ux * dist, p2[1] - uy * dist)


def draw_scene(ctx, phrase, u: float):
    draw_ground(ctx)
    geos = _geo_map(phrase, u)
    # Symbols that sit behind the body.
    for sym in phrase.get("syms", ()):
        if sym == "dots" and "a" in geos and "b" in geos:
            a, b = _outside(geos["a"]["chest"], geos["b"]["chest"], 20)
            draw_dashed(ctx, *a, *b, dash=7, gap=11)
        elif sym == "sun":
            draw_sun(ctx)
        elif sym.startswith("arch:"):
            who = sym.split(":")[1]
            draw_arch(ctx, geos[who]["hip"][0])
    for geo in geos.values():
        draw_figure(ctx, geo)
    red = phrase.get("red", "none")
    _draw_red(ctx, geos, red, u)
    for sym in phrase.get("syms", ()):
        _draw_front_symbol(ctx, geos, sym, u)
    return geos


def _draw_front_symbol(ctx, geos, sym, u):
    if sym.startswith("note:"):
        g = geos[sym.split(":")[1]]
        draw_note(ctx, g["head"][0] + g["face"] * 4, g["head"][1] - g["head_r"] - 28)
    elif sym.startswith("q:"):
        g = geos[sym.split(":")[1]]
        draw_question(ctx, g["head"][0] + g["face"] * 10, g["head"][1] - g["head_r"] - 34)
    elif sym.startswith("radial:"):
        g = geos[sym.split(":")[1]]
        draw_radial(ctx, g["head"][0] + g["face"] * 6, g["head"][1] - 6)
    elif sym.startswith("chain:"):
        draw_chain(ctx, geos[sym.split(":")[1]], 0.0, "ankle")
    elif sym.startswith("chain_fall:"):
        draw_chain(ctx, geos[sym.split(":")[1]], ease(u), "hand")
    elif sym.startswith("bubble:"):
        draw_bubble(ctx, geos[sym.split(":")[1]])
    elif sym.startswith("gift:"):
        g = geos[sym.split(":")[1]]
        ctx.set_source_rgb(1, 1, 1)
        ctx.set_line_width(LW)
        ctx.new_sub_path()
        ctx.arc(g["hand_f"][0], g["hand_f"][1], 7.5, 0, math.tau)
        ctx.stroke()
    elif sym.startswith("scatter:"):
        draw_scatter(ctx, geos[sym.split(":")[1]], u)


def _ground_pt(x, face_shift=0):
    return (x + face_shift, GROUND_Y - 4)


def _draw_red(ctx, geos, red, u):
    if red in (None, "none"):
        return
    a = geos.get("a")
    b = geos.get("b")
    if red == "wound" and a:
        draw_wound(ctx, a["chest"], a["face"])
    elif red == "string" and a and b:
        draw_curve(ctx, a["hand_f"], b["chest"], 16)
    elif red == "string_fall" and a and b:
        e = ease(u)
        start = (lerp(a["hand_f"][0], a["foot_f"][0] + a["face"] * 20, e), lerp(a["hand_f"][1], GROUND_Y - 4, e))
        end = (lerp(b["chest"][0], (a["hip"][0] + b["hip"][0]) / 2 + 30, e), lerp(b["chest"][1], GROUND_Y - 4, e))
        draw_curve(ctx, start, end, lerp(16, 5, e))
    elif red == "string_down" and a and b:
        x1 = a["hip"][0] + a["face"] * 28
        x2 = b["hip"][0] + b["face"] * 28
        # Bow upward so the dropped thread is not mistaken for the ground line.
        draw_curve(ctx, (x1, GROUND_Y - 4), (x2, GROUND_Y - 4), -16)
    elif red == "mark" and a:
        hx, hy = a["hand_f"]
        draw_mark(ctx, hx + a["face"] * 18, hy - 26)
    elif red == "mark_fall" and a:
        e = ease(u)
        hx, hy = a["hand_f"]
        x = lerp(hx + a["face"] * 18, a["foot_f"][0] + a["face"] * 28, e)
        y = lerp(hy - 26, GROUND_Y - 16, e)
        draw_mark(ctx, x, y)
    elif red == "mark_down" and a:
        draw_mark(ctx, a["foot_f"][0] + a["face"] * 34, GROUND_Y - 16)
    elif red == "crumb_fall" and a:
        e = ease(u)
        x = lerp(a["chest"][0], a["foot_f"][0] + a["face"] * 18, e)
        y = lerp(a["chest"][1], GROUND_Y - 8, e)
        draw_shard(ctx, x, y, rot=0.4 + e)
    elif red == "crumb_ground" and a:
        draw_shard(ctx, a["foot_f"][0] + a["face"] * 20, GROUND_Y - 7, rot=0.9)
    elif red == "crumb_hand" and a:
        draw_shard(ctx, a["hand_f"][0] + a["face"] * 2, a["hand_f"][1] - 2, rot=0.3, scale=1.05)
    elif red == "expect" and a and b:
        x2 = lerp(a["hand_f"][0], b["chest"][0], 0.58)
        y2 = lerp(a["hand_f"][1], b["chest"][1], 0.58)
        draw_dashed(ctx, *a["hand_f"], x2, y2, dash=6, gap=8, color=RED, width=2.5)
    elif red == "expect_chest" and a and b:
        x2 = lerp(a["chest"][0], b["chest"][0], 0.42)
        y2 = lerp(a["chest"][1], b["chest"][1], 0.42)
        draw_dashed(ctx, *a["chest"], x2, y2, dash=6, gap=8, color=RED, width=2.5)


def render_art(phrase, u: float) -> np.ndarray:
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    ctx.set_antialias(cairo.ANTIALIAS_BEST)
    ctx.set_source_rgb(0, 0, 0)
    ctx.paint()
    draw_scene(ctx, phrase, u)
    surface.flush()
    stride = surface.get_stride()
    raw = np.frombuffer(surface.get_data(), dtype=np.uint8)
    if stride == W * 4:
        bgra = raw.reshape(H, W, 4)
    else:
        bgra = raw.reshape(H, stride)[:, : W * 4].reshape(H, W, 4)
    return bgra[:, :, [2, 1, 0]].copy()


def draw_subtitle(rgb: np.ndarray, lines: list[str] | None) -> np.ndarray:
    if not lines:
        return rgb
    image = Image.fromarray(rgb, "RGB")
    pen = ImageDraw.Draw(image)
    sample = FONT.getbbox("傷")
    glyph_top = sample[1]
    glyph_h = sample[3] - sample[1]
    center_y = H * 0.30
    if len(lines) == 1:
        width = FONT.getlength(lines[0])
        top = center_y - glyph_h / 2 - glyph_top
        pen.text(((W - width) / 2, top), lines[0], font=FONT, fill=(255, 255, 255))
    else:
        baseline_gap = CHAR_H * 1.4
        y0 = center_y - baseline_gap / 2 - (glyph_top + glyph_h / 2)
        for i, line in enumerate(lines):
            width = FONT.getlength(line)
            pen.text(((W - width) / 2, y0 + i * baseline_gap), line, font=FONT, fill=(255, 255, 255))
    return np.asarray(image)


def render_frame(phrase, u: float, lines, fade_from=None, fade_u=1.0) -> np.ndarray:
    art = render_art(phrase, u)
    if fade_from is not None and fade_u < 1:
        art = ((1 - fade_u) * fade_from + fade_u * art).astype(np.uint8)
    return draw_subtitle(art, lines)
