# -*- coding: utf-8 -*-
"""線画の共通部品。描く前に begin を呼ぶ。"""

import math

import render_video as R


def begin(fr, t, dur, z0=1.0, z1=1.06, oy=None, ox=None, ang=None, radius=None, scx=None):
    p = 0.0 if dur <= 0 else max(0.0, min(1.0, t / dur))
    e = R.ease(p)
    fr.zoom = R.lerp(z0, z1, e)
    if oy:
        fr.oy = R.lerp(oy[0], oy[1], e)
    if ox:
        fr.ox = R.lerp(ox[0], ox[1], e)
    if ang is not None:
        fr.spot_ang = ang
    if radius is not None:
        fr.spot_r = radius
    if scx is not None:
        fr.spot_cx = scx
    fr.flicker = R.flicker(t)
    fr.prepare()
    return e, p


def poly_stroke(ctx, pts, width=1.5, rgba=None):
    R.stroke_polyline(ctx, pts, width, rgba or R.WHITE)


def curve(x0, y0, x1, y1, bend=0.0, n=36):
    pts = []
    for i in range(n):
        u = i / (n - 1)
        x = (1 - u) * x0 + u * x1 + math.sin(u * math.pi) * bend
        y = (1 - u) * y0 + u * y1
        pts.append((x, y))
    return pts


def shelf(ctx, x, y, n, seed, width=300, base=210):
    rng_step = 0.17
    cx = x
    for i in range(n):
        w = 16 + ((i * 5 + seed) % 4) * 4
        bh = base * (0.55 + ((i * 3 + seed) % 7) * 0.06)
        ctx.new_path()
        ctx.rectangle(cx, y - bh, w - 3, bh)
        R.fill_stroke(ctx, 1.25)
        cx += w
        if cx > x + width:
            break
    R.line(ctx, x - 8, y, x + width + 8, y, 1.8)
    R.line(ctx, x - 8, y, x - 8, y + 18, 1.4)
    R.line(ctx, x + width + 8, y, x + width + 8, y + 18, 1.4)


def coins(ctx, x, y, n, r=11):
    for i in range(n):
        R.circle(ctx, x, y - i * r * 0.55, r, 1.3)


def flowers(ctx, x, y, n=5, h=220, droop=0.0):
    for i in range(n):
        fx = x + i * 54
        top = y - h + droop * (40 + i * 8)
        R.line(ctx, fx, y, fx + droop * 10, top, 1.3)
        R.circle(ctx, fx + droop * 10, top, 16, 1.3)
        R.circle(ctx, fx + droop * 10, top, 5, 1.0, R.FILL)


def bag(ctx, x, y, s=1.0):
    w, h = 78 * s, 86 * s
    ctx.new_path()
    ctx.move_to(x - w / 2, y - h * 0.15)
    ctx.line_to(x - w / 2 + 6, y + h / 2)
    ctx.line_to(x + w / 2 - 6, y + h / 2)
    ctx.line_to(x + w / 2, y - h * 0.15)
    ctx.close_path()
    R.fill_stroke(ctx, 1.5)
    ctx.new_path()
    ctx.move_to(x - w * 0.22, y - h * 0.15)
    ctx.curve_to(x - w * 0.22, y - h * 0.72, x + w * 0.22, y - h * 0.72, x + w * 0.22, y - h * 0.15)
    R.stroke(ctx, 1.5)


def scale(fr, cx, cy, ang, length=240):
    c = fr.ctx
    R.line(c, cx, cy - 150, cx, cy, 1.8)
    R.line(c, cx - 36, cy + 64, cx + 36, cy + 64, 1.6)
    R.line(c, cx - 36, cy + 64, cx, cy + 8, 1.2)
    R.line(c, cx + 36, cy + 64, cx, cy + 8, 1.2)
    x1 = cx - math.cos(ang) * length
    y1 = cy - math.sin(ang) * length
    x2 = cx + math.cos(ang) * length
    y2 = cy + math.sin(ang) * length
    R.line(c, x1, y1, x2, y2, 2.0)
    R.circle(c, cx, cy, 5, 1.3, R.FILL)
    return (x1, y1), (x2, y2)


def pan(ctx, x, y):
    R.line(ctx, x, y, x, y + 36, 1.15, (1, 1, 1, 0.8))
    ctx.new_path()
    ctx.move_to(x - 34, y + 36)
    ctx.curve_to(x - 38, y + 70, x + 38, y + 70, x + 34, y + 36)
    R.stroke(ctx, 1.45)


def frames(ctx, x, y, cols, rows, w=70, h=90, gap=16):
    for r in range(rows):
        for c in range(cols):
            ctx.new_path()
            ctx.rectangle(x + c * (w + gap), y + r * (h + gap), w, h)
            R.stroke(ctx, 1.25, (1, 1, 1, 0.85))


def knot(ctx, x, y, s=1.0):
    pts = []
    for i in range(80):
        t = i / 79 * math.tau
        px = x + math.cos(t) * 34 * s + math.cos(2 * t) * 16 * s
        py = y + math.sin(2 * t) * 22 * s
        pts.append((px, py))
    poly_stroke(ctx, pts, 1.5)
    R.line(ctx, x - 70 * s, y + 8, x - 36 * s, y, 1.3)
    R.line(ctx, x + 36 * s, y, x + 78 * s, y + 10, 1.3)


def candle(ctx, x, y, flame=0.0):
    R.line(ctx, x, y, x, y - 90, 2.2)
    R.line(ctx, x - 16, y, x + 16, y, 1.4)
    if flame > 0.02:
        ctx.new_path()
        ctx.move_to(x, y - 90)
        ctx.curve_to(x - 10, y - 110, x + 10, y - 120, x, y - 132)
        ctx.curve_to(x + 8, y - 118, x - 4, y - 108, x, y - 90)
        R.stroke(ctx, 1.2)


def bowl(ctx, x, y, steam=False):
    ctx.new_path()
    ctx.move_to(x - 46, y)
    ctx.curve_to(x - 40, y + 36, x + 40, y + 36, x + 46, y)
    R.stroke(ctx, 1.5)
    R.line(ctx, x - 52, y, x + 52, y, 1.2)
    if steam:
        for i, dx in enumerate((-12, 0, 12)):
            pts = curve(x + dx, y - 8, x + dx + 6, y - 48, bend=10 if i % 2 == 0 else -10, n=16)
            poly_stroke(ctx, pts, 1.1, (0.84, 0.62, 0.32, 0.9))


def receipt(ctx, x, y, length=520):
    pts = [(x, y)]
    yy = y
    xx = x
    for i in range(8):
        xx += 34
        yy += 18 if i % 2 == 0 else -8
        pts.append((xx, yy))
    poly_stroke(ctx, pts, 1.35)
    R.line(ctx, pts[-1][0], pts[-1][1], pts[-1][0] + 10, pts[-1][1] + length * 0.15, 1.2)


def window(ctx, x, y, w, h):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    R.stroke(ctx, 1.8)
    R.line(ctx, x, y + h * 0.58, x + w, y + h * 0.58, 1.15, (1, 1, 1, 0.75))
    R.line(ctx, x + w * 0.5, y, x + w * 0.5, y + h, 1.15, (1, 1, 1, 0.75))


def plate(ctx, x, y, r=28):
    R.circle(ctx, x, y, r, 1.35)
    R.circle(ctx, x, y, r * 0.55, 1.0, None, (1, 1, 1, 0.7))
