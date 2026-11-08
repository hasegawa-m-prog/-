# -*- coding: utf-8 -*-
"""
黒背景 × 白い棒人間 × 赤一点 の映像をフレーム描画して ffmpeg に流し込む。
  1080x1920 / 30fps / 固定カメラ / リミテッドアニメーション
  入力: out/timeline.json, out/mix.wav
  出力: out/final.mp4
"""
import json
import math
import os
import random
import subprocess
import sys
from multiprocessing import Pool

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

W, H = 1080, 1920
SS = 2                      # スーパーサンプリング倍率（線のギザつきを抑える）
FPS = 30
GROUND_Y = int(H * 0.62)    # 地面の高さ（上端から62%）
FIG_H = H * 0.085           # 棒人間の高さ（画面の約8.5%）
LW = max(1, round(W * 0.003))  # 線幅（画面幅の約0.3%）
HEAD_R = 0.105              # 頭の半径（身長比）

WHITE = (255, 255, 255)
RED = (224, 32, 42)         # #E0202A

FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SUB_SIZE = 82               # 文字高さ ≒ 75px（画面幅の約7%）
SUB_CENTER_Y = int(H * 0.30)
SUB_LINE_GAP = int(75 * 1.4)

with open(os.path.join(OUT, "timeline.json"), encoding="utf-8") as f:
    TL = json.load(f)
UNITS = TL["units"]
TOTAL = TL["total"]
START = {u["id"]: u["start"] for u in UNITS}
END = {u["id"]: u["end"] for u in UNITS}

FADE = 0.3                  # 幕切り替えの軽いフェード（秒）
BREAK_FADE_OUT = 0.45       # 幕最後のフレーズ終了から、フェードアウト開始までの秒数


# ---------------------------------------------------------------- ユーティリティ
def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ramp(t, t0, t1):
    """t が t0→t1 の間で 0→1 に滑らかに変化"""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return smooth((t - t0) / (t1 - t0))


def mix_pose(a, b, t):
    t = smooth(t)
    return {k: (lerp(a[k][0], b[k][0], t), lerp(a[k][1], b[k][1], t)) for k in a}


def gray(a):
    v = int(round(255 * max(0.0, min(1.0, a))))
    return (v, v, v)


def red(a):
    a = max(0.0, min(1.0, a))
    return tuple(int(round(c * a)) for c in RED)


# ---------------------------------------------------------------- ポーズ定義
# 座標系: 原点＝足元の地面、x は右、y は上。単位は身長（FIG_H）。
def pose(**kw):
    return kw


STAND = pose(head=(0, 0.89), neck=(0, 0.78), hip=(0, 0.44),
             le=(-0.06, 0.62), lh=(-0.09, 0.46), re=(0.06, 0.62), rh=(0.09, 0.46),
             lk=(-0.04, 0.22), lf=(-0.07, 0.0), rk=(0.04, 0.22), rf=(0.07, 0.0))

# しゃがんで膝を抱える（頭を落としている）
CROUCH_DOWN = pose(head=(0.09, 0.43), neck=(0.05, 0.35), hip=(-0.10, 0.12),
                   le=(0.09, 0.22), lh=(0.19, 0.27), re=(0.07, 0.20), rh=(0.17, 0.25),
                   lk=(0.14, 0.27), lf=(0.16, 0.0), rk=(0.11, 0.25), rf=(0.12, 0.0))
# しゃがんだまま、顔を少し上げた
CROUCH = pose(head=(0.03, 0.50), neck=(0.02, 0.39), hip=(-0.10, 0.12),
              le=(0.09, 0.22), lh=(0.19, 0.27), re=(0.07, 0.20), rh=(0.17, 0.25),
              lk=(0.14, 0.27), lf=(0.16, 0.0), rk=(0.11, 0.25), rf=(0.12, 0.0))

# 膝を立てて座る（上体は起きている）
SIT = pose(head=(-0.02, 0.58), neck=(-0.02, 0.47), hip=(-0.12, 0.06),
           le=(0.02, 0.30), lh=(0.12, 0.31), re=(0.0, 0.28), rh=(0.10, 0.29),
           lk=(0.12, 0.30), lf=(0.20, 0.0), rk=(0.10, 0.28), rf=(0.17, 0.0))
# 座ったまま肩を落とす（頭が前に落ち、腕がだらんと下がる）
SIT_SLUMP = pose(head=(0.05, 0.49), neck=(0.01, 0.40), hip=(-0.12, 0.06),
                 le=(0.03, 0.22), lh=(0.06, 0.08), re=(0.01, 0.20), rh=(0.04, 0.06),
                 lk=(0.12, 0.30), lf=(0.20, 0.0), rk=(0.10, 0.28), rf=(0.17, 0.0))
# 座って、片手を胸に当てる
SIT_HAND = pose(head=(-0.02, 0.58), neck=(-0.02, 0.47), hip=(-0.12, 0.06),
                le=(0.02, 0.30), lh=(0.12, 0.31), re=(0.08, 0.31), rh=(-0.03, 0.36),
                lk=(0.12, 0.30), lf=(0.20, 0.0), rk=(0.10, 0.28), rf=(0.17, 0.0))
# 胸に手を当てたまま、わずかに顔を上げる
SIT_HAND_UP = pose(head=(-0.04, 0.60), neck=(-0.03, 0.48), hip=(-0.12, 0.06),
                   le=(0.02, 0.30), lh=(0.12, 0.31), re=(0.08, 0.31), rh=(-0.03, 0.36),
                   lk=(0.12, 0.30), lf=(0.20, 0.0), rk=(0.10, 0.28), rf=(0.17, 0.0))

# 横たわる（頭が左）
LIE = pose(head=(-0.44, 0.105), neck=(-0.33, 0.09), hip=(0.02, 0.07),
           le=(-0.20, 0.03), lh=(-0.06, 0.02), re=(-0.22, 0.15), rh=(-0.10, 0.12),
           lk=(0.20, 0.17), lf=(0.40, 0.0), rk=(0.22, 0.15), rf=(0.42, 0.0))
# 起き上がろうとして上体だけ少し持ち上がる
LIE_TRYUP = pose(head=(-0.34, 0.31), neck=(-0.28, 0.22), hip=(0.02, 0.07),
                 le=(-0.30, 0.06), lh=(-0.37, 0.0), re=(-0.18, 0.19), rh=(-0.08, 0.14),
                 lk=(0.20, 0.17), lf=(0.40, 0.0), rk=(0.22, 0.15), rf=(0.42, 0.0))
# 横たわったまま、腕が地面に落ちる
LIE_ARMDROP = pose(head=(-0.44, 0.105), neck=(-0.33, 0.09), hip=(0.02, 0.07),
                   le=(-0.20, 0.03), lh=(-0.06, 0.02), re=(-0.30, 0.03), rh=(-0.38, 0.0),
                   lk=(0.20, 0.17), lf=(0.40, 0.0), rk=(0.22, 0.15), rf=(0.42, 0.0))


def walk_pose(phase):
    s = math.sin(2 * math.pi * phase)
    c = abs(math.cos(2 * math.pi * phase))
    bob = 0.012 * c
    return pose(head=(0, 0.89 + bob), neck=(0, 0.78 + bob), hip=(0, 0.44 + bob),
                le=(-0.05 * s, 0.62 + bob), lh=(-0.11 * s, 0.47 + bob),
                re=(0.05 * s, 0.62 + bob), rh=(0.11 * s, 0.47 + bob),
                lk=(0.08 * s, 0.23), lf=(0.15 * s, 0.045 * max(0.0, s)),
                rk=(-0.08 * s, 0.23), rf=(-0.15 * s, 0.045 * max(0.0, -s)))


def chest_of(p):
    """胸の位置（首と腰の間、首寄り）"""
    return (lerp(p["neck"][0], p["hip"][0], 0.27), lerp(p["neck"][1], p["hip"][1], 0.27))


# ---------------------------------------------------------------- 描画プリミティブ（SS 倍の座標で描く）
class Canvas:
    def __init__(self):
        self.img = Image.new("RGB", (W * SS, H * SS), (0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.lw = LW * SS

    def line(self, p0, p1, color=WHITE, lw=None):
        lw = lw or self.lw
        x0, y0 = p0[0] * SS, p0[1] * SS
        x1, y1 = p1[0] * SS, p1[1] * SS
        self.d.line([(x0, y0), (x1, y1)], fill=color, width=lw)
        r = lw / 2
        for x, y in ((x0, y0), (x1, y1)):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=color)

    def polyline(self, pts, color=WHITE, lw=None):
        for a, b in zip(pts, pts[1:]):
            self.line(a, b, color, lw)

    def circle(self, c, r, color=WHITE, lw=None, fill=False):
        lw = lw or self.lw
        x, y = c[0] * SS, c[1] * SS
        r = r * SS
        box = [x - r, y - r, x + r, y + r]
        if fill:
            self.d.ellipse(box, fill=color)
        else:
            self.d.ellipse(box, outline=color, width=lw)

    def ellipse(self, c, rx, ry, color=WHITE, lw=None):
        lw = lw or self.lw
        x, y = c[0] * SS, c[1] * SS
        self.d.ellipse([x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS], outline=color, width=lw)

    def arc(self, c, rx, ry, a0, a1, color=WHITE, lw=None):
        lw = lw or self.lw
        x, y = c[0] * SS, c[1] * SS
        self.d.arc([x - rx * SS, y - ry * SS, x + rx * SS, y + ry * SS], a0, a1, fill=color, width=lw)

    def text(self, c, s, font, color=WHITE):
        self.d.text((c[0] * SS, c[1] * SS), s, font=font, fill=color, anchor="mm")

    def finish(self, alpha=1.0):
        img = self.img.resize((W, H), Image.LANCZOS)
        if alpha < 1.0:
            img = img.point(lambda v: int(v * alpha))
        return img


# ---------------------------------------------------------------- 地面（手描き風の途切れた横線、静止）
def make_ground():
    rng = random.Random(42)
    segs = []
    x = -10
    while x < W + 10:
        length = rng.uniform(70, 230)
        pts = []
        n = max(2, int(length / 18))
        for i in range(n + 1):
            px = x + length * i / n
            py = GROUND_Y + rng.uniform(-1.4, 1.4)
            pts.append((px, py))
        segs.append(pts)
        x += length + rng.uniform(9, 26)
    return segs


GROUND = make_ground()


def draw_ground(cv):
    for pts in GROUND:
        cv.polyline(pts, WHITE, lw=max(1, int(LW * SS * 0.7)))


# ---------------------------------------------------------------- 棒人間
def to_screen(p, x0, scale=1.0, flip=False):
    sx = -1 if flip else 1
    return (x0 + sx * p[0] * FIG_H * scale, GROUND_Y - p[1] * FIG_H * scale)


def draw_figure(cv, p, x0, scale=1.0, color=WHITE, flip=False, lw=None):
    S = lambda k: to_screen(p[k], x0, scale, flip)  # noqa: E731
    cv.circle(S("head"), HEAD_R * FIG_H * scale, color, lw=lw)
    cv.line(S("neck"), S("hip"), color, lw)
    cv.polyline([S("neck"), S("le"), S("lh")], color, lw)
    cv.polyline([S("neck"), S("re"), S("rh")], color, lw)
    cv.polyline([S("hip"), S("lk"), S("lf")], color, lw)
    cv.polyline([S("hip"), S("rk"), S("rf")], color, lw)


def draw_red_dot(cv, p, x0, alpha=1.0, r=7.0):
    if alpha <= 0:
        return
    cv.circle(to_screen(chest_of(p), x0), r, red(alpha), fill=True)


# ---------------------------------------------------------------- 記号
SYM_FONT = ImageFont.truetype(FONT_PATH, int(96 * SS), index=0)


def draw_question(cv, head_screen, alpha):
    cv.text((head_screen[0] + 62, head_screen[1] - 70), "？", SYM_FONT, gray(alpha))


def draw_note(cv, head_screen, alpha, t):
    y = head_screen[1] - 70 - 4 * math.sin(t * 1.7)
    cv.text((head_screen[0] + 40, y), "♪", SYM_FONT, gray(alpha))


def draw_radial(cv, head_screen, alpha, n=7):
    """頭のまわりの放射状の短線（焦り）"""
    hx, hy = head_screen
    r0 = HEAD_R * FIG_H + 14
    for i in range(n):
        a = math.radians(200 + i * (140 / (n - 1)))
        a = -a  # 画面座標は y が下向き
        p0 = (hx + r0 * math.cos(a), hy + r0 * math.sin(a))
        p1 = (hx + (r0 + 22) * math.cos(a), hy + (r0 + 22) * math.sin(a))
        cv.line(p0, p1, gray(alpha), lw=max(1, int(LW * SS * 0.8)))


def draw_dotted(cv, p0, p1, progress, alpha=1.0):
    """二人の間の点線（距離）。progress で左から伸びる"""
    n = 22
    for i in range(n):
        f0 = i / n
        f1 = f0 + 0.5 / n
        if f1 > progress:
            break
        a = (lerp(p0[0], p1[0], f0), lerp(p0[1], p1[1], f0))
        b = (lerp(p0[0], p1[0], f1), lerp(p0[1], p1[1], f1))
        cv.line(a, b, gray(alpha), lw=max(1, int(LW * SS * 0.8)))


def draw_bubble(cv, head_screen, alpha, walk_phase):
    """楕円の吹き出し。中に歩く小さな棒人間（思い描いていた自分）"""
    cx = head_screen[0] + 150
    cy = head_screen[1] - 250
    rx, ry = 150, 100
    col = gray(alpha)
    cv.ellipse((cx, cy), rx, ry, col)
    # 吹き出しの尻尾（小さな丸を2つ）
    cv.circle((head_screen[0] + 70, head_screen[1] - 130), 8, col)
    cv.circle((head_screen[0] + 45, head_screen[1] - 85), 5, col)
    # 中の小人：吹き出し内に地面はなく、足元の高さを ground に見立てる
    small = walk_pose(walk_phase)
    sc = 0.45
    gy = cy + 55
    S = lambda k: (cx + small[k][0] * FIG_H * sc, gy - small[k][1] * FIG_H * sc)  # noqa: E731
    lw = max(1, int(LW * SS * 0.75))
    cv.circle(S("head"), HEAD_R * FIG_H * sc, col, lw=lw)
    cv.line(S("neck"), S("hip"), col, lw)
    cv.polyline([S("neck"), S("le"), S("lh")], col, lw)
    cv.polyline([S("neck"), S("re"), S("rh")], col, lw)
    cv.polyline([S("hip"), S("lk"), S("lf")], col, lw)
    cv.polyline([S("hip"), S("rk"), S("rf")], col, lw)


def draw_arch(cv, x0, progress, alpha=1.0):
    """人物を覆うアーチ（守り）。progress で左から右へ描かれる"""
    if progress <= 0:
        return
    rx, ry = 190, 200
    c = (x0, GROUND_Y)
    # 角度は PIL 基準（0°=右、時計回り）。左端 180° → 右端 360°
    a0 = 180
    a1 = 180 + 180 * progress
    cv.arc(c, rx, ry, a0, a1, gray(alpha))


def draw_sun(cv, alpha):
    """小さな太陽（明日・希望）。右側、地平線の少し上"""
    if alpha <= 0:
        return
    cx, cy = 840, GROUND_Y - 95
    r = 22
    col = gray(alpha)
    cv.circle((cx, cy), r, col)
    for i in range(8):
        a = math.radians(i * 45 + 22.5)
        p0 = (cx + (r + 12) * math.cos(a), cy + (r + 12) * math.sin(a))
        p1 = (cx + (r + 26) * math.cos(a), cy + (r + 26) * math.sin(a))
        cv.line(p0, p1, col, lw=max(1, int(LW * SS * 0.8)))


SCATTER = [(math.radians(a), 1.0 + 0.3 * ((i * 7) % 5) / 5) for i, a in enumerate(range(-150, 150, 38))]


def draw_scatter(cv, center, progress):
    """小さな点の散り（解放）。胸から外へゆっくり広がりながら薄くなる"""
    if progress <= 0:
        return
    for ang, spd in SCATTER:
        d = 18 + 95 * progress * spd
        a = max(0.0, 1.0 - progress) * 0.9
        x = center[0] + d * math.cos(ang)
        y = center[1] - d * math.sin(ang) - 20 * progress
        cv.circle((x, y), 3.2, gray(a), fill=True)


# ---------------------------------------------------------------- 字幕
SUB_FONT = ImageFont.truetype(FONT_PATH, SUB_SIZE * SS, index=0)


def draw_subtitle(cv, lines):
    if len(lines) == 1:
        cv.text((W / 2, SUB_CENTER_Y), lines[0], SUB_FONT, WHITE)
    else:
        cv.text((W / 2, SUB_CENTER_Y - SUB_LINE_GAP / 2), lines[0], SUB_FONT, WHITE)
        cv.text((W / 2, SUB_CENTER_Y + SUB_LINE_GAP / 2), lines[1], SUB_FONT, WHITE)


# ---------------------------------------------------------------- シーン進行
def scene_begin(idx):
    """idx 番目の unit のシーンが始まる時刻（前の幕切りフェードの中点以降）"""
    if idx == 0:
        return 0.0
    prev = UNITS[idx - 1]
    if prev["act_break"]:
        return prev["end"] + BREAK_FADE_OUT + FADE
    return prev["start"] if False else UNITS[idx]["start"]


SCENE_BEGIN = [scene_begin(i) for i in range(len(UNITS))]


def current_unit(t):
    """時刻 t に表示するシーンの unit インデックス"""
    idx = 0
    for i in range(len(UNITS)):
        if t >= SCENE_BEGIN[i]:
            idx = i
    return idx


def subtitle_at(t):
    for i, u in enumerate(UNITS):
        nxt = UNITS[i + 1]["start"] if i + 1 < len(UNITS) else TOTAL
        hide = u["end"] + BREAK_FADE_OUT if u["act_break"] else nxt
        if u["start"] <= t < min(nxt, hide):
            return u["sub"]
    return None


def global_alpha(t):
    a = 1.0
    a = min(a, ramp(t, 0.0, 0.6))                       # 冒頭フェードイン
    a = min(a, 1.0 - ramp(t, TOTAL - 1.0, TOTAL - 0.05))  # 最後のフェードアウト
    for u in UNITS:
        if u["act_break"]:
            o0 = u["end"] + BREAK_FADE_OUT
            a = min(a, 1.0 - ramp(t, o0, o0 + FADE) + ramp(t, o0 + FADE, o0 + 2 * FADE))
    return a


CX = W / 2  # 主人公は常に中央


def breathe(p, t, amp=0.004):
    """ごく小さな呼吸の揺れ（頭と首だけ）"""
    dy = amp * math.sin(t * 1.3)
    q = dict(p)
    q["head"] = (p["head"][0], p["head"][1] + dy)
    q["neck"] = (p["neck"][0], p["neck"][1] + dy * 0.6)
    return q


def draw_scene(cv, t):
    idx = current_unit(t)
    u = UNITS[idx]
    name = u["scene"]
    tl = t - SCENE_BEGIN[idx]      # シーン内の経過秒
    red_r = 7.0

    # ---------- ① しゃがむ
    if name == "crouch_still":
        p = breathe(CROUCH_DOWN, t)
        draw_figure(cv, p, CX)
    elif name == "crouch_lookup":
        p = breathe(mix_pose(CROUCH_DOWN, CROUCH, ramp(tl, 0.1, 1.5)), t)
        draw_figure(cv, p, CX)
    elif name == "crouch_question":
        p = breathe(CROUCH, t)
        draw_figure(cv, p, CX)
        draw_question(cv, to_screen(p["head"], CX), ramp(tl, 0.3, 0.9))
    elif name == "crouch_question_hold":
        p = breathe(CROUCH, t)
        draw_figure(cv, p, CX)
        draw_question(cv, to_screen(p["head"], CX), 1.0)

    # ---------- ② 横たわる・まわりは進む
    elif name == "lie_bubble":
        p = LIE
        draw_figure(cv, p, CX)
        draw_bubble(cv, to_screen(p["head"], CX), ramp(tl, 0.6, 1.3), walk_phase=(tl * 0.9) % 1.0)
    elif name == "lie_tryup":
        k = ramp(tl, 0.2, 1.1) - ramp(tl, 1.5, 2.6)
        p = mix_pose(LIE, LIE_TRYUP, k)
        draw_figure(cv, p, CX)
    elif name == "lie_armdrop":
        p = mix_pose(LIE, LIE_ARMDROP, ramp(tl, 0.6, 1.8))
        draw_figure(cv, p, CX)
    elif name in ("sit_walkers_a", "sit_walkers_b"):
        p = breathe(SIT_SLUMP, t)
        draw_figure(cv, p, CX)
        tw = t - START[8]           # 歩く人たちは unit 8 の開始から動き続ける
        speed = 92.0
        for x0, lead, has_note in ((770, 0.0, False), (665, 0.5, True)):
            x = x0 + speed * tw
            if x < W + 60:
                wp = walk_pose((tw * 1.5 + lead) % 1.0)
                draw_figure(cv, wp, x)
                if has_note:
                    draw_note(cv, to_screen(wp["head"], x), 1.0, t)
    elif name == "sit_dotted":
        # 顔を上げて、去っていった背中の方を見る → 二人の間に点線
        p = breathe(mix_pose(SIT_SLUMP, SIT, ramp(tl, 0.1, 0.9)), t)
        draw_figure(cv, p, CX)
        hs = to_screen(SIT["head"], CX)
        draw_dotted(cv, (hs[0] + 60, hs[1] + 10), (W - 40, hs[1] + 10), ramp(tl, 0.8, 2.2))
    elif name == "sit_radial":
        p = breathe(SIT, t)
        draw_figure(cv, p, CX)
        hs = to_screen(p["head"], CX)
        draw_dotted(cv, (hs[0] + 60, hs[1] + 10), (W - 40, hs[1] + 10), 1.0)
        draw_radial(cv, hs, ramp(tl, 0.2, 0.8))
    elif name == "sit_red_appear":
        k = ramp(tl, 0.3, 1.8)
        p = breathe(mix_pose(SIT, SIT_SLUMP, k), t)
        draw_figure(cv, p, CX)
        hs0 = to_screen(SIT["head"], CX)
        draw_dotted(cv, (hs0[0] + 60, hs0[1] + 10), (W - 40, hs0[1] + 10), 1.0, alpha=1.0 - k)
        draw_radial(cv, to_screen(p["head"], CX), 1.0 - k)
        draw_red_dot(cv, p, CX, ramp(tl, 0.6, 1.6))

    # ---------- ③ 転換
    elif name == "sit_red_lookup":
        p = breathe(mix_pose(SIT_SLUMP, SIT, ramp(tl, 0.5, 2.2)), t)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX)
    elif name in ("sit_red_still", "sit_red_still2"):
        p = breathe(SIT, t)
        if name == "sit_red_still2":
            # 首をわずかにかしげる
            k = ramp(tl, 0.2, 1.2)
            p = dict(p)
            p["head"] = (p["head"][0] + 0.03 * k, p["head"][1] - 0.01 * k)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX)
    elif name == "sit_to_lie":
        p = mix_pose(SIT, LIE, ramp(tl, 0.3, 2.6))
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX)
    elif name == "lie_arch_appear":
        p = LIE
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX)
        draw_arch(cv, CX, ramp(tl, 0.3, 2.0))
    elif name == "lie_arch_hold":
        p = breathe(LIE, t, amp=0.003)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX)
        draw_arch(cv, CX, 1.0)

    # ---------- ④ 着地
    elif name == "sit_hand_chest":
        p = breathe(mix_pose(SIT, SIT_HAND, ramp(tl, 0.5, 1.9)), t)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX)
    elif name == "sit_hand_lookup":
        p = breathe(mix_pose(SIT_HAND, SIT_HAND_UP, ramp(tl, 0.4, 2.0)), t)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX)
    elif name == "sit_red_shrink":
        p = breathe(SIT_HAND_UP, t)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX, r=lerp(7.0, 3.5, ramp(tl, 0.2, 1.6)))
    elif name == "sit_scatter":
        p = breathe(SIT_HAND_UP, t)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX, r=3.5)
        draw_scatter(cv, to_screen(chest_of(p), CX), ramp(tl, 0.2, 2.4))
    elif name == "sit_sun_appear":
        p = breathe(SIT_HAND_UP, t)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX, r=3.5)
        draw_sun(cv, ramp(tl, 0.4, 2.0))
    elif name == "sit_sun_hold":
        p = breathe(SIT_HAND_UP, t)
        draw_figure(cv, p, CX)
        draw_red_dot(cv, p, CX, r=3.5)
        draw_sun(cv, 1.0)
    else:
        raise ValueError(name)


def render_frame(i):
    t = i / FPS
    cv = Canvas()
    draw_ground(cv)
    draw_scene(cv, t)
    sub = subtitle_at(t)
    if sub:
        draw_subtitle(cv, sub)
    return cv.finish(global_alpha(t)).tobytes()


def main():
    nframes = int(math.ceil(TOTAL * FPS))
    out_path = os.path.join(OUT, "final.mp4")
    audio = os.path.join(OUT, "mix.wav")
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", audio,
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-profile:v", "high", "-level", "4.1", "-movflags", "+faststart",
           # 全体を約 -18 LUFS まで持ち上げ、ピークだけ軽く抑える（音量は一定のまま）
           "-af", "volume=4dB,alimiter=limit=0.89:attack=5:release=60:level=false",
           "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
           "-shortest", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(processes=max(1, os.cpu_count() or 1)) as pool:
        for n, frame in enumerate(pool.imap(render_frame, range(nframes), chunksize=8)):
            proc.stdin.write(frame)
            if n % 300 == 0:
                print(f"frame {n}/{nframes}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("done:", out_path, "frames:", nframes, "duration:", TOTAL)


def stills(times, prefix="still"):
    """確認用の静止画を書き出す"""
    for k, t in enumerate(times):
        cv = Canvas()
        draw_ground(cv)
        draw_scene(cv, t)
        sub = subtitle_at(t)
        if sub:
            draw_subtitle(cv, sub)
        cv.finish(global_alpha(t)).save(os.path.join(OUT, f"{prefix}_{k:02d}_{t:05.1f}s.png"))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stills":
        times = [float(x) for x in sys.argv[2:]] or [u["start"] + 1.2 for u in UNITS]
        stills(times)
    else:
        main()
