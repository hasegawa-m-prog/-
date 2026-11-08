#!/usr/bin/env python3
"""失う痛みの縦型ショートを、線画で書き出す。"""

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import render_video as rv
from loss_audio import MARKED, WRAPS

W, H, FPS = rv.W, rv.H, rv.FPS
RED = (200, 16, 46)
AMBER = (214, 150, 64)
BLUE = (120, 156, 196)
OUT_DIR = Path(__file__).resolve().parent / "build" / "loss"


def draw_subtitles(img, marked):
    if not marked:
        return img
    lines = WRAPS[MARKED.index(marked)]
    im = Image.fromarray(img, "RGB")
    draw = ImageDraw.Draw(im)
    line_h = int(rv.FONT_SIZE * 1.22)
    bottom = int(H * 0.82)
    y = bottom - line_h * len(lines)
    for marked_line in lines:
        text, ranges = rv.parse_marked(marked_line)
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
        width = sum(rv.FONT.getlength(s) for s, _ in spans)
        x = (W - width) / 2
        for s, is_red in spans:
            draw.text((x, y), s, font=rv.FONT, fill=RED if is_red else (255, 255, 255))
            x += rv.FONT.getlength(s)
        y += line_h
    return np.asarray(im)


def draw_bill(ctx, x, y, tilt=0.08, w=78, h=40):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(tilt)
    ctx.new_path()
    ctx.rectangle(-w / 2, -h / 2, w, h)
    rv.fill_stroke(ctx, 1.5, rv.FILL)
    ctx.restore()


def draw_disc(ctx, x, y, r=16):
    rv.circle(ctx, x, y, r, 1.45, rv.FILL)


def draw_book(ctx, x, y, w=92, h=120):
    ctx.new_path()
    ctx.rectangle(x, y, w, h)
    rv.fill_stroke(ctx, 1.6, (0.10, 0.11, 0.13))
    rv.line(ctx, x + 14, y + 8, x + 14, y + h - 8, 1.15, (1, 1, 1, 0.55))


def draw_street(ctx):
    rv.line(ctx, 160, 1160, 920, 1160, 1.25, (1, 1, 1, 0.28))
    rv.line(ctx, 210, 360, 210, 1160, 1.05, (1, 1, 1, 0.18))
    rv.line(ctx, 870, 420, 870, 1160, 1.05, (1, 1, 1, 0.18))


def draw_scale(ctx, fr, cx, cy, ang):
    ctx.new_path()
    ctx.move_to(cx, cy + 8)
    ctx.line_to(cx - 28, cy + 150)
    ctx.line_to(cx + 28, cy + 150)
    ctx.close_path()
    rv.stroke(ctx, 1.7)
    rv.line(ctx, cx - 70, cy + 150, cx + 70, cy + 150, 1.8)
    length = 250
    x1 = cx - math.cos(ang) * length
    y1 = cy - math.sin(ang) * length
    x2 = cx + math.cos(ang) * length
    y2 = cy + math.sin(ang) * length
    rv.line(ctx, x1, y1, x2, y2, 2.1)
    rv.circle(ctx, cx, cy, 5.5, 1.4, rv.FILL)

    def pan(x, y):
        rim = y + 108
        rv.line(ctx, x, y, x - 22, rim, 1.15, (1, 1, 1, 0.8))
        rv.line(ctx, x, y, x + 22, rim, 1.15, (1, 1, 1, 0.8))
        ctx.new_path()
        ctx.move_to(x - 46, rim)
        ctx.curve_to(x - 50, rim + 28, x + 50, rim + 28, x + 46, rim)
        rv.stroke(ctx, 1.5)
        return x, rim - 8

    return pan(x1, y1), pan(x2, y2)


def scene_drop(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.0, 1.06, e)
    fr.oy = rv.lerp(H / 2 - 40, H / 2 + 30, e)
    fr.prepare()
    draw_street(fr.ctx)
    fall = rv.ease(rv.clamp(p / 0.72, 0, 1))
    paper_x = rv.lerp(690, 640, fall)
    paper_y = rv.lerp(860, 1120, fall)
    tilt = rv.lerp(0.15, -0.35, fall) + math.sin(t * 2.2) * 0.04
    rv.draw_person(fr.ctx, fr, 500, 1160, 560, reach=(690, 900))
    draw_bill(fr.ctx, paper_x, paper_y, tilt)
    fr.glow(paper_x, paper_y, 70, RED, 0.55)


def scene_pick(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.02, 1.07, e)
    fr.prepare()
    draw_street(fr.ctx)
    lift = rv.ease(rv.clamp((p - 0.15) / 0.6, 0, 1))
    paper_x = 620
    paper_y = rv.lerp(1105, 980, lift)
    rv.draw_person(fr.ctx, fr, 500, 1160, 560, reach=(paper_x - 10, paper_y))
    draw_bill(fr.ctx, paper_x, paper_y, rv.lerp(-0.2, 0.05, lift))
    fr.glow(paper_x, paper_y, 64, AMBER, 0.42)


def scene_level(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.0, 1.05, e)
    fr.prepare()
    wobble = math.sin(t * 0.8) * 0.012
    (left, right) = draw_scale(fr.ctx, fr, 540, 560, wobble)
    draw_bill(fr.ctx, left[0], left[1] - 18, 0.02, 64, 34)
    draw_bill(fr.ctx, right[0], right[1] - 18, -0.02, 64, 34)


def scene_tip(fr, t, dur):
    p = t / dur
    e = rv.ease(rv.clamp(p / 0.75, 0, 1))
    fr.zoom = rv.lerp(1.0, 1.06, p)
    fr.ox = rv.lerp(W / 2, W / 2 + 40, e)
    fr.prepare()
    ang = rv.lerp(0.02, 0.34, e)
    (left, right) = draw_scale(fr.ctx, fr, 540, 560, ang)
    draw_bill(fr.ctx, left[0], left[1] - 16, -0.08, 64, 34)
    rv.circle(fr.ctx, right[0], right[1] - 10, 18, 1.6, (0.22, 0.05, 0.08), (0.85, 0.15, 0.22, 1))
    fr.glow(right[0], right[1], 80, RED, 0.7)


def scene_desk(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.0, 1.05, e)
    fr.prepare()
    rv.line(fr.ctx, 180, 980, 900, 980, 1.7)
    rv.line(fr.ctx, 220, 980, 200, 1120, 1.3, (1, 1, 1, 0.6))
    rv.line(fr.ctx, 860, 980, 880, 1120, 1.3, (1, 1, 1, 0.6))
    draw_book(fr.ctx, 494, 860)
    fr.glow(540, 920, 90, BLUE, 0.35)
    rv.draw_person(fr.ctx, fr, 300, 1140, 500)
    rv.draw_person(fr.ctx, fr, 790, 1140, 520, turn=-0.4)


def scene_clock(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.0, 1.05, e)
    fr.prepare()
    rv.draw_clock(fr.ctx, 540, 280, 96, t * 8)
    ang = rv.lerp(0.05, 0.30, e)
    (left, right) = draw_scale(fr.ctx, fr, 540, 700, ang)
    rv.circle(fr.ctx, left[0], left[1] - 36, 14, 1.4, rv.FILL)
    rv.circle(fr.ctx, right[0], right[1] - 12, 20, 1.6, (0.22, 0.05, 0.08), (0.85, 0.15, 0.22, 1))
    fr.glow(right[0], right[1], 70, RED, 0.55)


def scene_discs(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.0, 1.045, e)
    fr.prepare()
    ang = 0.28 + math.sin(t * 0.6) * 0.01
    (left, right) = draw_scale(fr.ctx, fr, 470, 620, ang)
    draw_disc(fr.ctx, left[0], left[1] - 14, 18)
    fr.glow(left[0], left[1], 50, AMBER, 0.28)
    draw_disc(fr.ctx, right[0] - 16, right[1] - 14, 16)
    draw_disc(fr.ctx, right[0] + 16, right[1] - 12, 16)
    fr.glow(right[0], right[1], 70, RED, 0.5)
    draw_book(fr.ctx, 820, 760, 78, 100)
    fr.glow(860, 810, 60, BLUE, 0.22)


def scene_threads(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.0, 1.06, e)
    fr.prepare()
    rv.draw_person(fr.ctx, fr, 540, 1120, 520)
    chest = (540, 760)
    paper = (760, rv.lerp(1040, 1080, e))
    loose = (340, 1000)

    def thread(a, b, sag, wobble, width, rgba):
        pts = []
        for i in range(28):
            u = i / 27
            x = rv.lerp(a[0], b[0], u)
            y = rv.lerp(a[1], b[1], u) + math.sin(u * math.pi) * sag
            y += math.sin(u * 10 + t * 1.4) * wobble * math.sin(u * math.pi)
            pts.append((x, y))
        rv.stroke_polyline(fr.ctx, pts, width, rgba)

    thread(chest, paper, 18, 1.2, 1.6, (0.78, 0.12, 0.2, 0.95))
    thread(chest, loose, 70, 2.4, 1.35, (0.84, 0.62, 0.32, 0.85))
    draw_bill(fr.ctx, paper[0], paper[1], -0.12)
    fr.glow(paper[0], paper[1], 56, RED, 0.45)
    fr.glow(loose[0], loose[1], 40, AMBER, 0.2)
    fr.glow(chest[0], chest[1], 50, RED, 0.25)


def scene_return(fr, t, dur):
    p = t / dur
    e = rv.ease(p)
    fr.zoom = rv.lerp(1.04, 1.0, e)
    fr.prepare()
    draw_street(fr.ctx)
    fall = rv.ease(rv.clamp(p / 0.55, 0, 1))
    paper_y = rv.lerp(820, 1125, fall)
    rv.draw_person(fr.ctx, fr, 520, 1160, 560)
    draw_bill(fr.ctx, 690, paper_y, rv.lerp(0.2, -0.4, fall))
    fr.glow(690, paper_y, 68, RED, rv.lerp(0.6, 0.12, e))


SCENES = {
    1: scene_drop,
    2: scene_pick,
    3: scene_level,
    4: scene_tip,
    5: scene_desk,
    6: scene_clock,
    7: scene_discs,
    8: scene_threads,
    9: scene_return,
}


def render_scene_image(scene_id, t, dur, marked, fade, seed=0):
    fr = rv.Frame()
    SCENES[scene_id](fr, t, dur)
    flick = rv.flicker(t)
    fr.surface.flush()
    buf = np.ndarray((H, W, 4), dtype=np.uint8, buffer=fr.surface.get_data())
    rgb = np.ascontiguousarray(buf[:, :, [2, 1, 0]]).astype(np.float32)
    mask = rv.spot_mask(fr.spot_cx, fr.spot_cy, fr.spot_r, fr.spot_ang) * flick
    factor = 0.03 + 0.97 * np.clip(mask ** 0.8, 0, 1)
    img = rgb * factor[:, :, None]
    img += (np.clip(mask, 0, 1) ** 1.15)[:, :, None] * 32
    img *= rv.GUARD[:, None, None]
    for x, y, radius, color, intensity in fr.glows:
        sx, sy = fr.w2s(x, y)
        rv.add_glow(img, sx, sy, radius * fr.zoom, color, intensity)
    rv.add_glow(img, fr.spot_cx, 16, 70, (255, 255, 255), 0.16 * flick)
    rng = np.random.default_rng(seed + 11)
    noise = rng.integers(-14, 15, size=(H, W), dtype=np.int16).astype(np.float32)
    lit = np.clip(img.mean(axis=2) / 36.0, 0.0, 1.0)
    img += (noise * lit)[:, :, None]
    np.clip(img, 0, 255, out=img)
    out = draw_subtitles(img.astype(np.uint8), marked)
    if fade < 0.999:
        out = np.clip(out.astype(np.float32) * fade, 0, 255).astype(np.uint8)
    return out


def edge_fade(t, start, end, fin=0.5, fout=0.5):
    f = 1.0
    if t - start < fin:
        f = (t - start) / fin
    if end - t < fout:
        f = min(f, (end - t) / fout)
    return rv.clamp(f, 0.0, 1.0)


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
    fade = edge_fade(t, scene["start"], scene["end"], 0.5, 0.9 if last else 0.5)
    return render_scene_image(scene["id"], local, dur, marked, fade, seed=index)


def preview(timeline_path: Path, out_dir: Path):
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    out_dir.mkdir(parents=True, exist_ok=True)
    for scene in timeline["scenes"]:
        t = (scene["start"] + scene["end"]) / 2
        img = frame_at(timeline, t, scene["id"] * 17)
        path = out_dir / f"scene_{scene['id']:02d}.png"
        Image.fromarray(img, "RGB").save(path, optimize=True)
        print(path)


def render_video(timeline_path: Path, audio_path: Path, out_path: Path):
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))
    duration = timeline["duration"]
    nframes = int(round(duration * FPS))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
        "-i", "pipe:0",
        "-i", str(audio_path),
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "160k",
        "-shortest", str(out_path),
    ]
    log_path = out_path.with_suffix(".ffmpeg.log")
    log = open(log_path, "w")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    try:
        for i in range(nframes):
            frame = frame_at(timeline, i / FPS, i)
            proc.stdin.write(frame.tobytes())
            if i % FPS == 0:
                proc.stdin.flush()
                print(f"\rframe {i}/{nframes}  t={i / FPS:.1f}s", end="", flush=True)
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
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    timeline = OUT_DIR / "timeline.json"
    audio = OUT_DIR / "narration.wav"
    if args.preview:
        preview(timeline, args.preview)
    elif args.render:
        render_video(timeline, audio, args.out or (OUT_DIR / "loss.mp4"))
    else:
        parser.error("use --preview DIR or --render")


if __name__ == "__main__":
    main()
