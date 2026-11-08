"""五本ぶんの場面。比喩は一つずつ、動きは遅く。"""

from engine import (
    AMBER, FILL, RED, RED_LINE, begin, circle, draw_book, draw_chair, draw_clock,
    draw_column, draw_cup, draw_days, draw_door, draw_gift, draw_ledger, draw_mirror,
    draw_path, draw_person, draw_plinth, draw_rail, draw_scale, draw_shoes, draw_stack,
    draw_stairs, draw_thread, draw_ticket, draw_window, heartbeat, lerp, line,
)

SCENES = {}


def reg(film, sid):
    def wrap(fn):
        SCENES[(film, sid)] = fn
        return fn
    return wrap


def couples(ctx, fr, x0, y0, cols, rows, h, gap_x, gap_y, amber=0.0):
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * gap_x
            y = y0 + r * gap_y
            draw_person(ctx, fr, x, y, h, amber=amber)
            draw_person(ctx, fr, x + h * 0.28, y + 6, h * 0.92)


# ---------- 1 嫌えない人 ----------

@reg(0, 1)
def f1s1(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_door(c, 250, 180, 580, 860, ajar=lerp(0.08, 0.2, e))
    draw_shoes(c, 430, 1088)
    draw_shoes(c, 690, 1102)
    draw_person(c, fr, 470, 1040, 360, walk=t * 0.4, turn=lerp(0, 0.4, e), chest=0.25)
    draw_person(c, fr, 690, 1000, 330, alpha=0.9)
    draw_thread(c, 520, 820, 690, 800, sag=30 + 8 * (0.5 - e))


@reg(0, 2)
def f1s2(fr, t, dur):
    p, e = begin(fr, t, dur, 1.03, 1.08)
    c = fr.ctx
    ang = lerp(-0.08, 0.16, e) * (0.65 + 0.35 * (1 - e))

    def left(x, y):
        draw_person(c, fr, x, y + 8, 78)

    def right(x, y):
        line(c, x, y - 70, x, y + 6, 1.5, RED_LINE)
        line(c, x, y - 48, x - 16, y - 30, 1.3, RED_LINE)
        line(c, x, y - 48, x + 16, y - 30, 1.3, RED_LINE)

    draw_scale(c, fr, 540, 430, ang, left, right)
    draw_thread(c, 300, 470, 780, 500, sag=10)


@reg(0, 3)
def f1s3(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 540, 1080, 460)
    gap = lerp(0, 18, e)
    line(c, 540 - gap, 620, 540 - gap, 1080, 1.4)
    line(c, 620, 700, 620, 1040, 1.6, RED_LINE)


@reg(0, 4)
def f1s4(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 390, 1080, 400, turn=0.5)
    draw_person(c, fr, 700, 1060, 370, alpha=lerp(1, 0.55, 0.5), turn=-0.4)
    # 半分かげ
    c.new_path()
    c.rectangle(700, 640, 160, 460)
    c.set_source_rgba(0, 0, 0, 0.45)
    c.fill()
    draw_column(c, fr, 220, 1040, 520, lerp(0.15, 0.78, e), RED)


@reg(0, 5)
def f1s5(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_column(c, fr, 380, 1040, 620, lerp(0.05, 0.45, e), None)
    draw_column(c, fr, 700, 1040, 620, lerp(0.05, 0.82, e), RED)
    draw_person(c, fr, 380, 1120, 180, alpha=0.85)
    draw_person(c, fr, 700, 1120, 180, alpha=0.85)


@reg(0, 6)
def f1s6(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 420, 1080, 380, chest=0.2 + 0.5 * heartbeat(t, 84))
    draw_person(c, fr, 680, 1060, 340, alpha=0.8)
    draw_column(c, fr, 240, 1000, 500, lerp(0.82, 0.30, e), RED)


@reg(0, 7)
def f1s7(fr, t, dur):
    p, e = begin(fr, t, dur, 1.04, 1.06)
    c = fr.ctx
    draw_clock(c, 540, 280, 120, t * 4)
    draw_chair(c, 360, 860, 0.9)
    draw_chair(c, 720, 860, 0.9)
    if e < 0.75:
        draw_person(c, fr, 360, 860, 220, alpha=lerp(0.2, 0.9, min(1, e * 2)))
        draw_person(c, fr, 720, 860, 210, alpha=lerp(0.9, 0.15, max(0, (e - 0.45) / 0.4)))


@reg(0, 8)
def f1s8(fr, t, dur):
    p, e = begin(fr, t, dur, 1.06, 1.02)
    c = fr.ctx
    draw_door(c, 280, 220, 520, 780, ajar=0.16)
    draw_shoes(c, 460, 1060)
    draw_shoes(c, 700, 1072)
    draw_person(c, fr, 520, 1040, 380, chest=0.35 + 0.4 * heartbeat(t, 76))


@reg(0, 9)
def f1s9(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_chair(c, 540, 980, 1.05)
    draw_chair(c, 540, 620, 0.7)
    draw_person(c, fr, 540, 1040, 300, chest=lerp(0.5, 0.08, e))


# ---------- 2 変わらない ----------

@reg(1, 1)
def f2s1(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_plinth(c, 620, 980, 260, 48)
    wobble = lerp(0.15, 0.02, e) * (1 if int(t * 2) % 2 == 0 else -1)
    draw_person(c, fr, 620, 980, 420, turn=wobble)
    draw_person(c, fr, 360, 1080, 360, reach=(500, 760), turn=0.6)


@reg(1, 2)
def f2s2(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_clock(c, 540, 260, 130, t * 6)
    draw_plinth(c, 540, 1040, 240, 44)
    draw_person(c, fr, 540, 1040, 400, turn=lerp(0.3, 0.0, e))


@reg(1, 3)
def f2s3(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_plinth(c, 640, 1000, 240, 44)
    draw_person(c, fr, 640, 1000, 400)
    y = lerp(740, 980, e)
    draw_person(c, fr, 360, 1080, 360, reach=(470, y))


@reg(1, 4)
def f2s4(fr, t, dur):
    p, e = begin(fr, t, dur, 1.0, 1.05)
    c = fr.ctx
    shown_rows = 1 + int(e * 5)
    couples(c, fr, 180, 520, 4, shown_rows, 78, 220, 130)


@reg(1, 5)
def f2s5(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    couples(c, fr, 140, 480, 2, 4, 86, 150, 140, amber=lerp(0.1, 0.55, e))
    couples(c, fr, 620, 520, 2, 4, 80, 150, 140, amber=0.0)
    # 右を少し沈める
    c.set_source_rgba(0, 0, 0, lerp(0, 0.35, e))
    c.rectangle(560, 400, 520, 800)
    c.fill()


@reg(1, 6)
def f2s6(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    # 左は最後まで。右は最初だけ早い。
    draw_stairs(c, 120, 980, 8, lerp(0, 8, e), 42, 52)
    fast = min(1.0, e * 2.2)
    draw_stairs(c, 560, 980, 5, lerp(0, 5, fast), 46, 36)
    fr.glow(160 + 42 * 8, 980 - 52 * 8, 40, AMBER, lerp(0, 0.7, e))


@reg(1, 7)
def f2s7(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_door(c, 390, 180, 300, 460, ajar=0.05)
    draw_chair(c, 300, 980, 0.85)
    draw_chair(c, 780, 980, 0.85)
    draw_chair(c, 540, 900, 0.7)
    draw_person(c, fr, 300, 1040, 250)
    draw_person(c, fr, 780, 1040, 250)


@reg(1, 8)
def f2s8(fr, t, dur):
    p, e = begin(fr, t, dur, 1.05, 1.02)
    c = fr.ctx
    draw_plinth(c, 620, 1000, 240, 44)
    draw_person(c, fr, 620, 1000, 400)
    draw_person(c, fr, 340, 1080, 360)


@reg(1, 9)
def f2s9(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, lerp(420, 380, e), 1080, 400)
    draw_person(c, fr, lerp(660, 720, e), 1080, 390)


# ---------- 3 悪者にしない ----------

@reg(2, 1)
def f3s1(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_door(c, 560, 200, 400, 760, ajar=lerp(0.2, 0.1, e))
    draw_person(c, fr, lerp(480, 420, e), 1080, 380, reach=(lerp(560, 500, e), lerp(780, 860, e)))
    draw_person(c, fr, 760, 1020, 340, alpha=0.85)
    draw_chair(c, 250, 960, 0.8, red=True)


@reg(2, 2)
def f3s2(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_mirror(c, 560, 240, 360, 780)
    draw_person(c, fr, 360, 1100, 400, turn=0.7)
    draw_person(c, fr, 740, 1080, 300, alpha=lerp(0.35, 0.7, e))


@reg(2, 3)
def f3s3(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_path(c, 360, 1180, 420, 70)
    draw_path(c, 760, 1180, 70)
    draw_person(c, fr, 360, lerp(1100, 860, e), lerp(300, 220, e), walk=t * 0.8)
    fr.glow(360, lerp(700, 360, e), 80, AMBER, lerp(0.1, 0.6, e))


@reg(2, 4)
def f3s4(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_rail(c, 980)
    draw_window(c, 400, 360, 300, 180)
    draw_person(c, fr, lerp(300, 460, min(1, e * 1.4)), 1100, 340, walk=t)
    if e > 0.45:
        draw_ticket(c, 620, 760, 1.1, fr)
        draw_person(c, fr, 760, 1080, 320)


@reg(2, 5)
def f3s5(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 340, 1100, 300)
    draw_person(c, fr, 740, 1100, 300)
    draw_ticket(c, 800, 860, 1.0, fr)
    draw_column(c, fr, 340, 760, 360, lerp(0.2, 0.48, e), None)
    draw_column(c, fr, 800, 760, 360, lerp(0.2, 0.70, e), AMBER)


@reg(2, 6)
def f3s6(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_path(c, 420, 1200, 360, 80)
    draw_path(c, 820, 1200, 360, 50)
    reach = lerp(780, 460, e)
    fr.glow(420, reach, 70, AMBER, 0.65)
    draw_person(c, fr, 420, 1120, 260)


@reg(2, 7)
def f3s7(fr, t, dur):
    p, e = begin(fr, t, dur, 1.04, 1.02)
    c = fr.ctx
    draw_clock(c, 540, 280, 110, t * 5)
    draw_rail(c, 1040)
    draw_ticket(c, 500, 640, 1.3, fr)


@reg(2, 8)
def f3s8(fr, t, dur):
    p, e = begin(fr, t, dur, 1.06, 1.02)
    c = fr.ctx
    draw_door(c, 560, 220, 380, 720, ajar=0.12)
    draw_person(c, fr, 400, 1080, 380)
    draw_person(c, fr, 760, 1040, 340, alpha=0.9)


@reg(2, 9)
def f3s9(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_chair(c, 300, 980, 0.95, red=True)
    draw_person(c, fr, 720, 1080, 400, alpha=0.92)


# ---------- 4 尽くす人 ----------

@reg(3, 1)
def f4s1(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 540, 1100, 420, reach=(540, lerp(620, 520, e)))
    for i, x in enumerate((180, 300, 780, 900)):
        line(c, x, 430, 500 + (i - 1.5) * 20, 560, 1.3, (1, 1, 1, 0.75))
        circle(c, x, 410, 18, 1.2, FILL)
    draw_cup(c, 540, 1160, 1.1)
    c.new_path()
    c.arc(540, 1188, 22, 0, 6.28)
    c.set_source_rgba(*RED_LINE[:3], 0.0)
    fr.glow(540, 1188, 30, RED, 0.35)


@reg(3, 2)
def f4s2(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    hand_y = lerp(640, 520, e)
    draw_person(c, fr, 540, 1120, 420, reach=(700, hand_y))
    draw_thread(c, 700, hand_y, 900, 420, sag=20)
    # 胸は空
    line(c, 500, 860, 580, 860, 1.2, (1, 1, 1, 0.4))


@reg(3, 3)
def f4s3(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 540, 1120, 420, reach=(720, 560), amber=lerp(0.45, 0.05, e))
    draw_thread(c, 720, 560, 940, 400, sag=16)


@reg(3, 4)
def f4s4(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 360, 1080, 380, turn=0.4)
    draw_person(c, fr, 720, 1080, 370, turn=-0.4)
    draw_book(c, 540, 900, lerp(0.6, 1.0, e), fr)


@reg(3, 5)
def f4s5(fr, t, dur):
    p, e = begin(fr, t, dur, 1.0, 1.04)
    c = fr.ctx
    draw_days(c, 540, 360, 7, e)


@reg(3, 6)
def f4s6(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 340, 1100, 400, reach=(340, 760), amber=lerp(0.2, 0.7, e))
    draw_person(c, fr, 760, 1100, 400, reach=(900, lerp(700, 560, e)), amber=lerp(0.3, 0.02, e))
    draw_thread(c, 900, lerp(700, 560, e), 980, 420, sag=18)


@reg(3, 7)
def f4s7(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_clock(c, 540, 260, 100, t * 3)
    draw_stairs(c, 250, 1080, 4, lerp(0, 4, e), 70, 40)
    draw_person(c, fr, 360, 1040, 280)
    draw_person(c, fr, 760, 1040, 270)


@reg(3, 8)
def f4s8(fr, t, dur):
    p, e = begin(fr, t, dur, 1.05, 1.02)
    c = fr.ctx
    hy = lerp(520, 820, e)
    draw_person(c, fr, 540, 1100, 420, reach=(540, hy), chest=lerp(0.1, 0.45, e))
    draw_thread(c, 540, hy, 860, lerp(400, 700, e), sag=lerp(10, 50, e))
    draw_cup(c, 540, lerp(900, 1160, e), 1.0)


@reg(3, 9)
def f4s9(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 540, 1120, 440, amber=lerp(0.15, 0.75, e))


# ---------- 5 見返り ----------

@reg(4, 1)
def f5s1(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 400, 1100, 400, reach=(lerp(520, 640, min(1, e * 1.5)), 780))
    if e < 0.55:
        draw_gift(c, lerp(520, 640, e * 1.8), 760, 1.0)
    else:
        draw_gift(c, 760, 820, 1.0)
        draw_person(c, fr, 800, 1080, 360, alpha=lerp(0, 0.8, (e - 0.55) / 0.45))
    # 開いた掌の赤は一度だけ
    pulse = max(0, 1 - abs(e - 0.7) * 6)
    fr.glow(560, 900, 40, RED, 0.6 * pulse)


@reg(4, 2)
def f5s2(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 540, 1120, 440, turn=lerp(0, -0.5, e), reach=(700, 860), chest=0.25 + 0.45 * heartbeat(t, 80))


@reg(4, 3)
def f5s3(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    ang = lerp(0.18, 0.02, e)

    def left(x, y):
        draw_cup(c, x, y - 36, 0.8)

    def right(x, y):
        draw_gift(c, x, y - 20, 0.7)

    draw_scale(c, fr, 540, 460, ang, left, right)


@reg(4, 4)
def f5s4(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_person(c, fr, 340, 1100, 380, reach=(lerp(420, 560, e), 800))
    draw_person(c, fr, 780, 1100, 380, reach=(lerp(700, 620, e), 820))
    draw_cup(c, lerp(400, 680, e), 760, 1.15, fr)


@reg(4, 5)
def f5s5(fr, t, dur):
    p, e = begin(fr, t, dur, 1.0, 1.05)
    c = fr.ctx
    grow = lerp(0.2, 1, e)
    draw_stack(c, fr, 180, 980, 5 * grow, False)
    draw_stack(c, fr, 500, 980, 9 * grow, True)
    draw_stack(c, fr, 800, 980, 6 * grow, False)


@reg(4, 6)
def f5s6(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_stack(c, fr, 180, 980, 5, False)
    draw_stack(c, fr, 500, 980, lerp(8, 10, e), True)
    draw_stack(c, fr, 800, 980, 6, False)
    draw_cup(c, 560, 520, 0.9, fr)


@reg(4, 7)
def f5s7(fr, t, dur):
    p, e = begin(fr, t, dur, 1.08, 1.02)
    c = fr.ctx
    draw_clock(c, 540, 240, 90, t * 4)
    line(c, 260, 860, 820, 860, 1.5)
    line(c, 260, 860, 220, 1040, 1.3)
    line(c, 820, 860, 860, 1040, 1.3)
    draw_person(c, fr, 380, 1080, 300)
    draw_person(c, fr, 720, 1080, 300)


@reg(4, 8)
def f5s8(fr, t, dur):
    p, e = begin(fr, t, dur, 1.05, 1.02)
    c = fr.ctx
    draw_person(c, fr, 500, 1100, 420, reach=(680, 840))
    draw_gift(c, 800, 860, 0.9)


@reg(4, 9)
def f5s9(fr, t, dur):
    p, e = begin(fr, t, dur)
    c = fr.ctx
    draw_ledger(c, 220, 620, 640, 420)
    ang = lerp(0.08, 0.0, e)

    def left(x, y):
        circle(c, x, y - 16, 10, 1.2, FILL)

    def right(x, y):
        circle(c, x, y - 16, 10, 1.2, FILL)

    draw_scale(c, fr, 540, 360, ang, left, right)
