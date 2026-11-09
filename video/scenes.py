# -*- coding: utf-8 -*-
"""5本ぶんの比喩図。顔は描かない。"""

import math

import render_video as R
from stage import (
    bag,
    begin,
    bowl,
    candle,
    coins,
    curve,
    flowers,
    frames,
    knot,
    pan,
    plate,
    poly_stroke,
    receipt,
    scale,
    shelf,
    window,
)


def _head(fy, h):
    return fy - h * 0.88


# ----- 1 美男美女 -----

def binan_1(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    c = fr.ctx
    R.line(c, 140, 1088, 940, 1088, 2.0)
    R.line(c, 540, 1088, 390, 760, 1.15, (1, 1, 1, 0.35))
    R.line(c, 540, 1088, 690, 760, 1.15, (1, 1, 1, 0.35))
    for x in (170, 300, 790, 930):
        R.draw_person(c, fr, x, 1040, 150, alpha=0.45)
    turn = R.lerp(0.4, 1.35, e)
    R.draw_person(c, fr, 430, 1165, 390, turn=-turn)
    R.draw_person(c, fr, 660, 1165, 400, turn=turn, hair=True)
    for cx, sgn, h in ((430, -1, 390), (660, 1, 400)):
        hy = _head(1165, h)
        poly_stroke(c, curve(cx + sgn * 20, hy - 10, cx + sgn * 220, hy - 220, bend=sgn * 20), 1.45)


def binan_2(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    ang = R.lerp(-0.02, 0.22, e)
    (lft, rgt) = scale(fr, 540, 620, ang, 250)
    pan(fr.ctx, lft[0], lft[1])
    pan(fr.ctx, rgt[0], rgt[1])
    R.draw_person(fr.ctx, fr, lft[0] - 16, lft[1] + 18, 78)
    R.draw_person(fr.ctx, fr, lft[0] + 18, lft[1] + 16, 74, hair=True)
    R.draw_person(fr.ctx, fr, rgt[0], rgt[1] + 16, 86, amber=0.85)


def binan_clock(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    c = fr.ctx
    R.draw_clock(c, 540, 420, 150, t)
    for i in range(4):
        R.circle(c, 360 + i * 120, 720, 28, 1.4)
    R.draw_person(c, fr, 420, 1160, 280)
    R.draw_person(c, fr, 680, 1160, 290, hair=True)


def binan_3(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06, oy=(900, 980))
    c = fr.ctx
    frames(c, 150, 430, 5, 4, 120, 150, 22)
    R.draw_clock(c, 540, 280, 92, t)
    R.line(c, 990, 430, 990, 1080, 1.2, (1, 1, 1, 0.55))
    for i in range(12):
        R.line(c, 978, 470 + i * 48, 1004, 470 + i * 48, 1.15)
    R.draw_person(c, fr, 400, 1180, 250, alpha=0.9)
    R.draw_person(c, fr, 680, 1180, 260, hair=True, alpha=0.9)


def binan_4(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    c = fr.ctx
    for i in range(5):
        y = 1040 - i * 78
        x = 470 + (i % 2) * 40
        c.new_path()
        c.save()
        c.translate(x, y)
        c.scale(1.3, 0.7)
        c.arc(0, 0, 11, 0, math.tau)
        c.restore()
        R.stroke(c, 1.25)
    R.draw_door(c, 620, 280, 280, 520, ajar=R.lerp(0.08, 0.28, e))
    R.draw_person(c, fr, 430, 1160, 340, turn=0.7)
    R.draw_person(c, fr, 560, 1170, 320, hair=True)
    R.draw_person(c, fr, 760, 860, 180, amber=0.2)
    fr.glow(760, 760, 70, R.RED, 0.55)
    poly_stroke(c, curve(470, _head(1160, 340), 760, 780, bend=40), 1.25, (0.78, 0.12, 0.2, 0.95))


def binan_5(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    c = fr.ctx
    x, y, w, h = 330, 240, 420, 760
    c.new_path()
    c.rectangle(x, y, w, h)
    R.stroke(c, 1.8)
    c.new_path()
    c.move_to(x + w * 0.55, y + 80)
    c.line_to(x + w * 0.62, y + 280)
    c.line_to(x + w * 0.48, y + 520)
    R.stroke(c, 1.3)
    R.draw_person(c, fr, 540, 1165, 420, turn=0.15)
    R.draw_person(c, fr, 620, 980, 230, alpha=0.35)


def binan_6(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.06, 1.0)
    c = fr.ctx
    gap = R.lerp(180, 280, e)
    R.line(c, 140, 1100, 940, 1100, 2.0)
    R.draw_person(c, fr, 540 - gap / 2, 1165, 390, turn=-1.0)
    R.draw_person(c, fr, 540 + gap / 2, 1165, 400, turn=1.0, hair=True)


def binan_7(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.08)
    c = fr.ctx
    R.line(c, 140, 1080, 940, 1080, 2.0)
    c.new_path()
    c.rectangle(690, 1000, 90, 80)
    R.stroke(c, 1.5, (1, 1, 1, 0.85))
    R.draw_person(c, fr, 400, 1160, 400, turn=1.1)
    poly_stroke(c, curve(460, _head(1160, 400), 900, 640, bend=40), 1.6, (0.78, 0.12, 0.2, 0.95))


# ----- 2 似た者 -----

def nita_1(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06)
    shelf(fr.ctx, 140, 620, 12, 1, 340, 230)
    shelf(fr.ctx, 600, 620, 12, 1, 340, 230)
    R.draw_person(fr.ctx, fr, 300, 1160, 360)
    R.draw_person(fr.ctx, fr, 760, 1160, 370, hair=True)


def nita_2(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    c = fr.ctx
    u = R.lerp(0.15, 0.82, e)
    left = curve(220, 1100, 540, 520, bend=-80)
    right = curve(860, 1100, 540, 520, bend=80)
    poly_stroke(c, left, 1.6)
    poly_stroke(c, right, 1.6)
    i = int(u * (len(left) - 1))
    R.draw_person(c, fr, left[i][0], left[i][1] + 20, 150)
    R.draw_person(c, fr, right[i][0], right[i][1] + 20, 150, hair=True)


def nita_3(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.05, ang=0.7, radius=2000)
    c = fr.ctx
    for row in range(4):
        for col in range(4):
            x = 180 + col * 230
            y = 420 + row * 180
            R.draw_person(c, fr, x - 16, y, 90, alpha=0.85)
            R.draw_person(c, fr, x + 16, y, 90, hair=True, alpha=0.85)
            R.line(c, x - 10, y - 40, x + 10, y - 40, 1.15)


def nita_4(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.07)
    c = fr.ctx
    R.line(c, 120, 360, 960, 360, 1.8)
    for i in range(22):
        x = 150 + i * 36
        slack = i in (3, 9, 15, 20)
        if slack:
            pts = curve(x, 360, x + 18, 980, bend=26)
            poly_stroke(c, pts, 1.25, (0.78, 0.16, 0.22, 0.95))
        else:
            R.line(c, x, 360, x, 980, 1.2)
    R.draw_person(c, fr, 300, 1140, 180, alpha=0.8)
    R.draw_person(c, fr, 780, 1140, 180, hair=True, alpha=0.8)


def nita_5(fr, t, dur):
    e, _ = begin(fr, t, dur, ox=(500, 620), z0=1.0, z1=1.05)
    c = fr.ctx
    for k, x in enumerate((220, 400)):
        for i in range(6):
            c.new_path()
            c.rectangle(x, 520 - i * 16, 70, 14)
            R.stroke(c, 1.15)
    c.new_path()
    c.rectangle(230, 680, 50, 70)
    R.stroke(c, 1.3)
    c.new_path()
    c.rectangle(400, 680, 50, 70)
    R.stroke(c, 1.3)
    R.draw_clock(c, 700, 520, 78, t)
    R.draw_clock(c, 900, 560, 78, t + 18)
    R.draw_person(c, fr, 540, 1160, 300)


def nita_6(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.05)
    ang = math.sin(t * 0.4) * 0.03
    (lft, rgt) = scale(fr, 540, 640, ang, 230)
    pan(fr.ctx, lft[0], lft[1])
    pan(fr.ctx, rgt[0], rgt[1])
    R.draw_person(fr.ctx, fr, lft[0] - 14, lft[1] + 16, 70)
    R.draw_person(fr.ctx, fr, lft[0] + 16, lft[1] + 14, 68, hair=True)
    R.draw_heart(fr.ctx, rgt[0], rgt[1] + 8, 1.1)
    fr.glow(rgt[0], rgt[1], 50, R.RED, 0.45)


def nita_7(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06)
    c = fr.ctx
    shelf(c, 250, 560, 14, 2, 560, 250)
    x = R.lerp(220, 430, e)
    R.draw_person(c, fr, x, 1160, 360, walk=t * 1.2)
    R.draw_person(c, fr, R.lerp(900, 690, e), 1160, 370, hair=True, walk=t * 1.2)


def nita_8(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    c = fr.ctx
    shelf(c, 300, 640, 8, 4, 220, 240)
    c.new_path()
    c.rectangle(560, 470, 36, 170)
    R.stroke(c, 1.15, (1, 1, 1, 0.35))
    shelf(c, 620, 640, 6, 5, 180, 240)
    R.draw_person(c, fr, 540, 1165, 380, reach=(578, 620))


# ----- 3 結婚式 -----

def kekkon_1(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06, radius=1900, ang=0.62)
    c = fr.ctx
    R.line(c, 120, 860, 960, 860, 2.0)
    flowers(c, 220, 860, 7, 250, droop=0.0)
    R.draw_seated(c, fr, 360, 980, 230)
    R.draw_seated(c, fr, 720, 980, 240)


def kekkon_2(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    receipt(fr.ctx, 150, 520, 280)
    ang = R.lerp(0.02, 0.2, e)
    (lft, rgt) = scale(fr, 620, 700, ang, 200)
    pan(fr.ctx, lft[0], lft[1])
    pan(fr.ctx, rgt[0], rgt[1])
    coins(fr.ctx, lft[0], lft[1] + 10, 7, 8)
    R.circle(fr.ctx, rgt[0] - 10, rgt[1] + 20, 12, 1.4)
    R.circle(fr.ctx, rgt[0] + 12, rgt[1] + 20, 12, 1.4)


def kekkon_3(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.05, oy=(860, 940))
    c = fr.ctx
    for row in range(6):
        for col in range(8):
            x = 120 + col * 110
            y = 380 + row * 130
            R.draw_person(c, fr, x, y, 70, alpha=0.8)
            c.new_path()
            c.rectangle(x + 16, y - 40, 18, 24)
            R.stroke(c, 1.0, (1, 1, 1, 0.7))


def kekkon_4(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    ang = R.lerp(0.05, 0.28, e)
    (lft, rgt) = scale(fr, 540, 560, ang, 250)
    pan(fr.ctx, lft[0], lft[1])
    pan(fr.ctx, rgt[0], rgt[1])
    coins(fr.ctx, lft[0], lft[1] - 10, 14, 10)
    coins(fr.ctx, rgt[0], rgt[1] + 8, 4, 10)
    fr.glow(lft[0], lft[1] - 40, 80, R.RED, 0.4)
    R.draw_person(fr.ctx, fr, 220, 1160, 340, hair=True)


def kekkon_5(fr, t, dur):
    e, _ = begin(fr, t, dur, ox=(420, 620))
    coins(fr.ctx, 300, 780, 4, 16)
    R.draw_person(fr.ctx, fr, 300, 1140, 300)
    knot(fr.ctx, 740, 700, 1.8)


def kekkon_6(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.04, 1.08, ang=0.42, radius=1400)
    c = fr.ctx
    R.line(c, 140, 900, 940, 900, 1.8)
    flowers(c, 240, 900, 6, 180, droop=1.0)
    R.draw_seated(c, fr, 380, 1020, 210)
    R.draw_seated(c, fr, 700, 1020, 220)


def kekkon_7(fr, t, dur):
    e, _ = begin(fr, t, dur, ox=(480, 640))
    c = fr.ctx
    c.new_path()
    c.move_to(180, 980)
    c.line_to(250, 820)
    c.line_to(430, 820)
    c.line_to(470, 980)
    c.close_path()
    R.stroke(c, 1.5)
    for i, x in enumerate((620, 760, 900)):
        R.draw_chair(c, x, 860, 0.7)
    R.draw_person(c, fr, 360, 1160, 300, turn=0.8)


# ----- 4 静かな二人 -----

def kenka_1(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06)
    c = fr.ctx
    window(c, 180, 180, 720, 520)
    R.line(c, 260, 980, 820, 980, 1.8)
    plate(c, 420, 960)
    plate(c, 660, 960)
    R.draw_seated(c, fr, 400, 1040, 200)
    R.draw_seated(c, fr, 690, 1040, 210)


def kenka_2(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    c = fr.ctx
    R.line(c, 180, 900, 900, 900, 1.8)
    R.draw_door(c, 430, 460, 220, 430, ajar=0.02)
    R.draw_seated(c, fr, 300, 980, 200)
    R.draw_seated(c, fr, 790, 980, 200)


def kenka_3(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06)
    c = fr.ctx
    R.draw_clock(c, 540, 300, 140, t * 0.15)
    for i in range(18):
        ang = -2.4 + i * 0.22
        x = 540 + math.cos(ang) * 280
        y = 820 + math.sin(ang) * 80
        R.circle(c, x, y, 7, 1.15)
        R.circle(c, x + 14, y + 2, 7, 1.15)
    R.draw_person(c, fr, 400, 1180, 220)
    R.draw_person(c, fr, 680, 1180, 230, hair=True)


def kenka_book(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    c = fr.ctx
    c.new_path()
    c.move_to(430, 340)
    c.line_to(470, 340)
    c.line_to(490, 980)
    c.line_to(410, 980)
    c.close_path()
    R.fill_stroke(c, 1.6)
    R.line(c, 470, 360, 470, 960, 1.2, (1, 1, 1, 0.7))
    R.draw_person(c, fr, 280, 1160, 320)
    R.draw_person(c, fr, 800, 1160, 330, hair=True)


def kenka_4(fr, t, dur):
    e, _ = begin(fr, t, dur, oy=(780, 900))
    c = fr.ctx
    pts = []
    x = 180
    y = 560
    for i in range(8):
        x += 80
        y += -28 if i % 2 == 0 else 40
        pts.append((x, y))
    poly_stroke(c, pts, 1.7, (0.8, 0.15, 0.22, 0.95))
    R.draw_person(c, fr, 200, 640, 120)
    R.draw_person(c, fr, 900, 620, 120, hair=True)
    R.draw_chair(c, 380, 1080, 0.9)
    R.draw_chair(c, 720, 1080, 0.9)
    candle(c, 540, 980, flame=0.0)
    R.line(c, 540, 890, 540, 860, 1.3)


def kenka_5(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    c = fr.ctx
    pts = []
    for i in range(40):
        a = -math.pi * 0.5 + i / 39 * math.tau * 0.93
        pts.append((540 + math.cos(a) * 260, 700 + math.sin(a) * 260))
    poly_stroke(c, pts, 1.6)
    R.draw_person(c, fr, 500, 760, 80, alpha=0.8)
    R.draw_person(c, fr, 580, 760, 80, hair=True, alpha=0.8)


def kenka_6(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.07)
    c = fr.ctx
    R.draw_person(c, fr, 340, 1100, 360)
    R.draw_person(c, fr, 740, 1100, 370, hair=True)
    pts = curve(340, 900, 740, 910, bend=70)
    poly_stroke(c, pts, 1.35)


def kenka_7(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.03, 1.08, ang=0.4, radius=1300)
    c = fr.ctx
    window(c, 220, 200, 640, 460)
    R.line(c, 280, 980, 800, 980, 1.6)
    plate(c, 430, 960)
    plate(c, 690, 968)
    R.draw_seated(c, fr, 400, 1040, 190)
    R.draw_seated(c, fr, 700, 1040, 200)


def kenka_8(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.08)
    c = fr.ctx
    R.line(c, 180, 860, 900, 860, 1.7)
    bowl(c, 360, 820, steam=True)
    bowl(c, 720, 820, steam=False)
    R.draw_person(c, fr, 540, 1165, 340, turn=R.lerp(-0.4, 0.5, e))
    fr.glow(360, 760, 40, R.AMBER, 0.45)


# ----- 5 頼みごと -----

def tanomi_1(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    c = fr.ctx
    give = R.lerp(0.2, 0.75, e)
    bx = R.lerp(470, 610, give)
    by = R.lerp(780, 820, give) + 12
    R.draw_person(c, fr, 360, 1160, 400, reach=(bx - 20, by))
    R.draw_person(c, fr, 760, 1160, 390, hair=True, turn=R.lerp(0.1, 0.8, e), reach=(bx + 16, by))
    bag(c, bx, by, 1.05)


def tanomi_2(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    c = fr.ctx
    R.draw_person(c, fr, 540, 1165, 460, reach=(700, 860))
    hy = 1165 - 460 * 0.42
    R.draw_arm(c, 620, 900, R.lerp(700, 560, e), R.lerp(860, hy, e), 8)
    fr.glow(560, hy, 70, R.RED, R.lerp(0.15, 0.85, e))


def tanomi_3(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06)
    c = fr.ctx
    R.line(c, 160, 780, 920, 780, 1.8)
    coins(c, 420, 760, 6, 12)
    c.new_path()
    c.rectangle(620, 680, 120, 90)
    R.stroke(c, 1.3)
    fr.glow(420, 700, 40, R.AMBER, 0.4)
    for i, x in enumerate(range(140, 980, 120)):
        R.draw_person(c, fr, x, 1120, 160, alpha=0.75)
    R.draw_person(c, fr, 780, 1040, 280)


def tanomi_4(fr, t, dur):
    p = 0.0 if dur <= 0 else max(0.0, min(1.0, t / dur))
    slide = R.ease(p)
    e, _ = begin(fr, t, dur, ox=(R.lerp(360, 760, slide), 540), z0=1.02, z1=1.05)
    c = fr.ctx
    # left: return coins to the person
    R.draw_person(c, fr, 180, 980, 240)
    R.draw_person(c, fr, 340, 1000, 180, reach=(230, 860))
    coins(c, 250, 820, 4, 8)
    fr.glow(250, 800, 36, R.RED, 0.45)
    # middle: doorway secretary
    R.draw_door(c, 470, 620, 180, 360, ajar=0.2)
    R.draw_person(c, fr, 560, 1000, 170, hair=True)
    R.draw_person(c, fr, 700, 1040, 150)
    # right: leaving with coins
    R.draw_person(c, fr, 900, 1080, 200, turn=0.6)
    coins(c, 960, 900, 3, 8)


def tanomi_5(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.07)
    coins(fr.ctx, 300, 820, 8, 20)
    coins(fr.ctx, 780, 900, 3, 20)
    fr.glow(300, 560, 70, R.RED, 0.55)
    fr.glow(780, 760, 70, R.RED, 0.55)
    R.draw_person(fr.ctx, fr, 540, 1180, 300, turn=R.lerp(-0.6, 0.6, e))


def tanomi_6(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    c = fr.ctx
    R.draw_person(c, fr, 280, 1120, 360)
    R.draw_person(c, fr, 860, 1040, 220, alpha=0.55)
    pts = curve(360, 900, 700, 860, bend=30)
    # fray the end
    poly_stroke(c, pts[:28], 1.4)
    end = pts[27]
    for k, b in enumerate((-18, 0, 16)):
        poly_stroke(c, curve(end[0], end[1], end[0] + 70, end[1] + 40 + b, bend=b), 1.05, (1, 1, 1, 0.7))


def tanomi_7(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.0, 1.06)
    c = fr.ctx
    bx = R.lerp(560, 680, e)
    R.draw_person(c, fr, 380, 1160, 400, reach=(bx - 30, 830))
    R.draw_person(c, fr, 820, 1120, 320, hair=True, turn=1.0, alpha=R.lerp(1.0, 0.45, e))
    bag(c, bx, 840, 1.0)
    fr.glow(430, 900, 60, R.RED, 0.55)


def tanomi_8(fr, t, dur):
    e, _ = begin(fr, t, dur, 1.02, 1.08)
    c = fr.ctx
    R.draw_person(c, fr, 540, 1180, 420, reach=(540, 760))
    cx, cy = 540, 700
    c.new_path()
    c.move_to(cx - 78, cy)
    c.curve_to(cx - 90, cy + 70, cx + 90, cy + 74, cx + 86, cy)
    c.line_to(cx - 78, cy)
    R.fill_stroke(c, 1.6)
    for i, dx in enumerate((-48, -16, 16, 46)):
        R.line(c, cx + dx, cy, cx + dx, cy - 78 - (i % 2) * 14, 1.7)
    R.line(c, cx - 78, cy + 16, cx - 130, cy - 36, 1.8)
    poly_stroke(c, curve(cx - 30, cy + 28, cx + 36, cy + 24, bend=6), 1.4, (0.78, 0.12, 0.2, 0.95))


SCENES = {
    "binan": {1: binan_1, 2: binan_2, 3: binan_clock, 4: binan_3, 5: binan_4, 6: binan_5, 7: binan_6, 8: binan_7},
    "nitamono": {1: nita_1, 2: nita_2, 3: nita_3, 4: nita_4, 5: nita_5, 6: nita_6, 7: nita_7, 8: nita_8},
    "kekkonshiki": {1: kekkon_1, 2: kekkon_2, 3: kekkon_3, 4: kekkon_4, 5: kekkon_5, 6: kekkon_6, 7: kekkon_7},
    "kenka": {
        1: kenka_1, 2: kenka_2, 3: kenka_3, 4: kenka_book, 5: kenka_4,
        6: kenka_5, 7: kenka_6, 8: kenka_7, 9: kenka_8,
    },
    "tanomi": {1: tanomi_1, 2: tanomi_2, 3: tanomi_3, 4: tanomi_4, 5: tanomi_5, 6: tanomi_6, 7: tanomi_7, 8: tanomi_8},
}
