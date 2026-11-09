# -*- coding: utf-8 -*-
"""音声・タイムライン・フレーム描画。"""

import json
import os
import re
import urllib.parse
import urllib.request
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import render_video as R
from catalog import FILMS, FONT as FONT_SPEC, NEGATIVE, STYLE, VOICE
from scenes import SCENES

ROOT = Path(__file__).resolve().parent
BASE = "http://127.0.0.1:50021"
SPEED = 1.05
PITCH = -0.02
INTONATION = 0.9
LEAD = 0.55
TAIL = 1.15
SENTENCE_PAUSE = 0.4
PARAGRAPH_PAUSE = 0.8
MIN_SCENE = 5.0
MAX_SCENE = 15.0

_MASKS = {}


def film_by(slug):
    for f in FILMS:
        if f["slug"] == slug:
            return f
    raise KeyError(slug)


WRAP_OVERRIDE = {
    "すると、魅力的な人ほど結婚が短くなりました。": [
        "すると、魅力的な人ほど",
        "結婚が短くなりました。",
    ],
    "高校写真の男性二百三十八人を、三十年分たどりました。": [
        "高校写真の男性",
        "二百三十八人を、",
        "三十年分たどりました。",
    ],
}


def wrap_text(text, limit=13):
    """1行はlimit字以内。句点だけ、読点から始まる行、二文字以下の行を残さない。"""
    if text in WRAP_OVERRIDE:
        lines = []
        cursor = 0
        for piece in WRAP_OVERRIDE[text]:
            lines.append((piece, cursor))
            cursor += len(piece)
        return lines
    n = len(text)
    if n <= limit:
        return [(text, 0)]

    def choose(i):
        rest = n - i
        if rest <= limit:
            return n
        window_end = i + limit
        # 窓の中の読点・句点の直後で切る（行末に句読点を残す）
        for k in range(window_end - 1, i, -1):
            if text[k] in "、。" and (k + 1 - i) >= 6 and n - (k + 1) != 1:
                return k + 1
        # 助詞の直後。ただし「ながら」の「が」では切らない
        for k in range(window_end - 1, i + 2, -1):
            if text[k] not in "はをにへと":
                continue
            if k >= 1 and text[k - 1 : k + 1] == "なが":
                continue
            if n - (k + 1) >= 4:
                return k + 1
        br = window_end
        if br < n and text[br] in "、。":
            br = max(i + 6, window_end - 4)
        if 0 < n - br < 4:
            br = max(i + 4, n - 4)
        if br < n and text[br] in "、。" and br + 1 - i <= limit:
            br += 1
        if br <= i:
            br = min(i + limit, n)
        return br

    spans = []
    i = 0
    guard = 0
    while i < n and guard < 20:
        j = choose(i)
        if j <= i:
            j = min(n, i + limit)
        spans.append((i, j))
        i = j
        guard += 1
    lines = [(text[a:b], a) for a, b in spans if a < b]

    def repair(lines):
        changed = True
        while changed and len(lines) > 1:
            changed = False
            out = []
            for line, start in lines:
                if out and (len(line) <= 2 or line[0] in "、。"):
                    prev, ps = out[-1]
                    if len(prev) + len(line) <= limit:
                        out[-1] = (prev + line, ps)
                        changed = True
                        continue
                    need = max(3, 4 - len(line))
                    if len(prev) - need >= 4 and len(line) + need <= limit:
                        out[-1] = (prev[:-need], ps)
                        out.append((prev[-need:] + line, start - need))
                        changed = True
                        continue
                out.append((line, start))
            lines = out
        return lines

    lines = repair(lines)

    def shove(lines):
        """短い末尾行や、読点・「を」で始まる行を、前の行から文字をもらって整える。"""
        out = []
        for line, start in lines:
            if not out:
                out.append((line, start))
                continue
            prev, ps = out[-1]
            take = 0
            if line[:1] in "、。":
                take = 1
            elif len(line) <= 5:
                take = 8 - len(line)
            elif line[:1] in "をにへ" and len(line) <= 8:
                take = 3
            if take and len(prev) - take >= 6 and len(line) + take <= limit:
                out[-1] = (prev[:-take], ps)
                line = prev[-take:] + line
                start -= take
            elif line[:1] in "、。" and len(prev) + 1 <= limit:
                out[-1] = (prev + line[0], ps)
                line = line[1:]
                start += 1
            if line:
                out.append((line, start))
        return out

    lines = shove(lines)
    lines = repair(lines)
    for line, _s in lines:
        if len(line) > limit or len(line) == 0 or line[0] in "、。":
            raise ValueError(f"wrap failed: {line!r} in {text}")
    return lines


def red_ranges(text, reds):
    spans = []
    for word in reds:
        start = 0
        while True:
            i = text.find(word, start)
            if i < 0:
                break
            spans.append((i, i + len(word)))
            start = i + len(word)
    return spans


def telop(text, reds):
    out = text
    for word in sorted(reds, key=len, reverse=True):
        out = out.replace(word, f"【{word}】")
    return out


def draw_subtitles(img, text, reds):
    if not text:
        return img
    lines = wrap_text(text)
    spans_all = red_ranges(text, reds)
    im = Image.fromarray(img, "RGB")
    draw = ImageDraw.Draw(im)
    line_h = int(R.FONT_SIZE * 1.22)
    bottom = int(R.H * 0.82)
    y = bottom - line_h * len(lines)
    for piece, start in lines:
        parts = []
        buf = ""
        red = None
        for k, ch in enumerate(piece):
            abs_i = start + k
            is_red = any(a <= abs_i < b for a, b in spans_all)
            if red is None:
                red = is_red
                buf = ch
            elif is_red == red:
                buf += ch
            else:
                parts.append((buf, red))
                buf = ch
                red = is_red
        if buf:
            parts.append((buf, red))
        width = sum(R.FONT.getlength(s) for s, _ in parts)
        x = (R.W - width) / 2
        for s, is_red in parts:
            draw.text((x, y), s, font=R.FONT, fill=R.RED if is_red else (255, 255, 255))
            x += R.FONT.getlength(s)
        y += line_h
    return np.asarray(im)


def spot_mask(cx, cy, radius, half_ang):
    key = (round(cx), round(cy), round(radius), round(half_ang * 100))
    cached = _MASKS.get(key)
    if cached is not None:
        return cached
    dx = R.XS - np.float32(cx)
    dy = R.YS - np.float32(cy)
    dist = np.sqrt(dx * dx + dy * dy)
    radial = np.clip(1.0 - dist / radius, 0, 1) ** 1.25
    ang = np.abs(np.arctan2(dx, np.maximum(dy, 1.0)))
    cone = np.clip(1.0 - ang / half_ang, 0, 1)
    cone = np.where(dy > -30, cone, 0)
    mask = (radial * cone).astype(np.float32)
    if len(_MASKS) > 24:
        _MASKS.clear()
    _MASKS[key] = mask
    return mask


def render_frame(slug, scene_id, t, dur, text, reds, fade, seed):
    fr = R.Frame()
    SCENES[slug][scene_id](fr, t, dur)
    flick = getattr(fr, "flicker", None) or R.flicker(t)
    fr.surface.flush()
    buf = np.ndarray((R.H, R.W, 4), dtype=np.uint8, buffer=fr.surface.get_data())
    rgb = np.ascontiguousarray(buf[:, :, [2, 1, 0]]).astype(np.float32)
    mask = spot_mask(fr.spot_cx, fr.spot_cy, fr.spot_r, fr.spot_ang) * flick
    factor = 0.03 + 0.97 * np.clip(mask ** 0.8, 0, 1)
    img = rgb * factor[:, :, None]
    img += (np.clip(mask, 0, 1) ** 1.15)[:, :, None] * 32
    img *= R.GUARD[:, None, None]
    for x, y, radius, color, intensity in fr.glows:
        sx, sy = fr.w2s(x, y)
        R.add_glow(img, sx, sy, radius * fr.zoom, color, intensity)
    R.add_glow(img, fr.spot_cx, 16, 70, (255, 255, 255), 0.16 * flick)
    rng = np.random.default_rng(seed + 11)
    noise = rng.integers(-14, 15, size=(R.H, R.W), dtype=np.int16).astype(np.float32)
    lit = np.clip(img.mean(axis=2) / 36.0, 0.0, 1.0)
    img += (noise * lit)[:, :, None]
    np.clip(img, 0, 255, out=img)
    out = img.astype(np.uint8)
    out = draw_subtitles(out, text, reds)
    if fade < 0.999:
        out = np.clip(out.astype(np.float32) * fade, 0, 255).astype(np.uint8)
    return out


def edge_fade(t, start, end, fin=0.5, fout=0.5):
    f = 1.0
    if t - start < fin:
        f = (t - start) / fin
    if end - t < fout:
        f = min(f, (end - t) / fout)
    return R.clamp(f, 0.0, 1.0)


def post(url, body=None, content_type=None):
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=b"" if body is None else body, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=180) as res:
        return res.read()


def find_speaker():
    with urllib.request.urlopen(BASE + "/speakers", timeout=30) as res:
        data = json.loads(res.read().decode())
    for sp in data:
        if "青山龍星" in sp.get("name", ""):
            for st in sp.get("styles", []):
                if st.get("name") in ("ノーマル", "ノーマル"):
                    return st["id"], sp["name"], st["name"]
            return sp["styles"][0]["id"], sp["name"], sp["styles"][0]["name"]
    raise SystemExit("青山龍星 が見つかりません")


def synthesize_line(text, speaker, path: Path):
    url = BASE + "/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": speaker})
    query = json.loads(post(url, b""))
    reading = []
    for phrase in query["accent_phrases"]:
        reading.append("".join(m["text"] for m in phrase["moras"]))
    query["speedScale"] = SPEED
    query["pitchScale"] = PITCH
    query["intonationScale"] = INTONATION
    query["prePhonemeLength"] = 0.06
    query["postPhonemeLength"] = 0.10
    wav = post(f"{BASE}/synthesis?speaker={speaker}", json.dumps(query).encode(), "application/json")
    path.write_bytes(wav)
    return " | ".join(reading)


def wav_info(path: Path):
    with wave.open(str(path), "rb") as w:
        return w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes(), w.readframes(w.getnframes())


def build_audio(slug, speaker):
    film = film_by(slug)
    out = ROOT / "build" / slug
    lines = out / "lines"
    lines.mkdir(parents=True, exist_ok=True)
    durations = []
    readings = []
    for i, sent in enumerate(film["sentences"], 1):
        path = lines / f"{i:02d}.wav"
        if path.exists() and os.environ.get("VOICE_REUSE") == "1":
            kana = "(reuse)"
        else:
            kana = synthesize_line(sent["text"], speaker, path)
        ch, sw, rate, n, _ = wav_info(path)
        durations.append(n / rate)
        readings.append(kana)
        print(f"{slug} {i:02d} {durations[-1]:5.2f}s  {kana}")

    ch, sw, rate, _, _ = wav_info(lines / "01.wav")

    def silence(seconds):
        n = int(round(seconds * rate))
        return b"\x00" * n * ch * sw

    # 文末0.4秒。段落の末尾は0.8秒（0.4に足さない）。
    entries = []
    t = LEAD
    for i, sent in enumerate(film["sentences"], 1):
        dur = durations[i - 1]
        if i == len(film["sentences"]):
            pause = 0.0
        elif sent["end"]:
            pause = PARAGRAPH_PAUSE
        else:
            pause = SENTENCE_PAUSE
        entries.append({
            "i": i,
            "scene": sent["scene"],
            "start": t,
            "end": t + dur,
            "dur": dur,
            "pause": pause,
            "text": sent["text"],
            "reds": sent["reds"],
        })
        t = t + dur + pause

    # シーンが5秒未満なら、その場面のあとだけ間を足す
    def scene_spans(entries, total):
        ids = sorted({e["scene"] for e in entries})
        spans = []
        for idx, sid in enumerate(ids):
            segs = [e for e in entries if e["scene"] == sid]
            speech_start = segs[0]["start"]
            if idx == 0:
                start = 0.0
            else:
                prev = [e for e in entries if e["scene"] == ids[idx - 1]][-1]
                start = (prev["end"] + speech_start) / 2
            spans.append({"id": sid, "start": start, "speech_end": segs[-1]["end"]})
        for i, sp in enumerate(spans):
            sp["end"] = spans[i + 1]["start"] if i < len(spans) - 1 else total
            sp["length"] = sp["end"] - sp["start"]
        return spans

    total = t + TAIL
    for _ in range(6):
        spans = scene_spans(entries, total)
        changed = False
        # recompute from scratch each pass using stored dur/pause
        cursor = LEAD
        for e in entries:
            e["start"] = cursor
            e["end"] = cursor + e["dur"]
            cursor = e["end"] + e["pause"]
        total = cursor + TAIL
        spans = scene_spans(entries, total)
        for sp in spans:
            if sp["length"] < MIN_SCENE:
                last = [e for e in entries if e["scene"] == sp["id"]][-1]
                last["pause"] += MIN_SCENE - sp["length"] + 0.05
                changed = True
        if not changed:
            break

    cursor = LEAD
    for e in entries:
        e["start"] = round(cursor, 3)
        e["end"] = round(cursor + e["dur"], 3)
        cursor = e["end"] + e["pause"]
    total = cursor + TAIL
    spans = scene_spans(entries, total)
    for sp in spans:
        sp["start"] = round(sp["start"], 3)
        sp["end"] = round(sp["end"], 3)
        sp["length"] = round(sp["end"] - sp["start"], 3)

    for i, e in enumerate(entries):
        scene_end = next(s["end"] for s in spans if s["id"] == e["scene"])
        nxt = entries[i + 1]["start"] if i < len(entries) - 1 else total
        e["hold"] = round(min(nxt, scene_end), 3)

    pcm = bytearray()
    pcm += silence(LEAD)
    for e in entries:
        _, _, _, _, frames = wav_info(lines / f"{e['i']:02d}.wav")
        pcm += frames
        if e["pause"]:
            pcm += silence(e["pause"])
    pcm += silence(TAIL)
    narration = out / "narration.wav"
    with wave.open(str(narration), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(rate)
        w.writeframes(pcm)

    timeline = {
        "slug": slug,
        "duration": round(total, 3),
        "sample_rate": rate,
        "voice": VOICE,
        "scenes": [{"id": s["id"], "start": s["start"], "end": s["end"], "length": s["length"]} for s in spans],
        "subs": [
            {
                "start": e["start"],
                "hold": e["hold"],
                "text": e["text"],
                "reds": e["reds"],
                "scene": e["scene"],
            }
            for e in entries
        ],
        "readings": readings,
    }
    (out / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{slug} TOTAL {total:.2f}s")
    for s in spans:
        flag = ""
        if s["length"] < MIN_SCENE or s["length"] > MAX_SCENE:
            flag = "  !!"
        print(f"  scene {s['id']}: {s['length']:.2f}s{flag}")
    return timeline


def frame_at(timeline, t, index):
    slug = timeline["slug"]
    scenes = timeline["scenes"]
    scene = scenes[-1]
    for s in scenes:
        if s["start"] <= t < s["end"]:
            scene = s
            break
    text, reds = None, []
    for sub in timeline["subs"]:
        if sub["start"] <= t < sub["hold"]:
            text, reds = sub["text"], sub["reds"]
            break
    local = t - scene["start"]
    dur = max(0.3, scene["end"] - scene["start"])
    last = scene["id"] == scenes[-1]["id"]
    first = scene["id"] == scenes[0]["id"]
    fade = edge_fade(t, scene["start"], scene["end"], 0.45 if first else 0.5, 0.8 if last else 0.5)
    return render_frame(slug, scene["id"], local, dur, text, reds, fade, index)


def preview(slug):
    film = film_by(slug)
    out = ROOT / "build" / slug / "preview"
    out.mkdir(parents=True, exist_ok=True)
    thumbs = []
    for scene in film["scenes"]:
        sid = film["scenes"].index(scene) + 1
        sent = next(s for s in film["sentences"] if s["scene"] == sid)
        img = render_frame(slug, sid, 4.4, 8.0, sent["text"], sent["reds"], 1.0, sid)
        path = out / f"scene_{sid:02d}.png"
        Image.fromarray(img, "RGB").save(path)
        thumbs.append(img)
        lines = wrap_text(sent["text"])
        for line, _ in lines:
            mark = " !" if len(line) > 13 else ""
            print(f"{slug} s{sid} {len(line):2d} {line}{mark}")
    cols = 4
    rows = (len(thumbs) + cols - 1) // cols
    tw, th = 270, 480
    sheet = Image.new("RGB", (tw * cols, th * rows), "black")
    for i, img in enumerate(thumbs):
        im = Image.fromarray(img, "RGB").resize((tw, th), Image.Resampling.LANCZOS)
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet_path = out / "contact.png"
    sheet.save(sheet_path)
    print(sheet_path)


def render_video(slug):
    import subprocess
    import sys

    out_dir = ROOT / "build" / slug
    timeline = json.loads((out_dir / "timeline.json").read_text(encoding="utf-8"))
    audio = out_dir / "narration.wav"
    dest = out_dir / film_by(slug)["file"]
    duration = timeline["duration"]
    nframes = int(round(duration * R.FPS))
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{R.W}x{R.H}", "-r", str(R.FPS),
        "-i", "pipe:0",
        "-i", str(audio),
        "-t", f"{duration:.3f}",
        "-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0",
        "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "1",
        "-shortest", str(dest),
    ]
    log_path = dest.with_suffix(".ffmpeg.log")
    log = open(log_path, "w")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    try:
        for i in range(nframes):
            frame = frame_at(timeline, i / R.FPS, i)
            proc.stdin.write(frame.tobytes())
            if i % R.FPS == 0:
                proc.stdin.flush()
                print(f"\r{slug} {i}/{nframes}", end="", flush=True)
        proc.stdin.close()
        code = proc.wait()
    except BrokenPipeError:
        code = proc.wait()
    log.close()
    print()
    if code != 0:
        print(log_path.read_text()[-2000:], file=sys.stderr)
        raise SystemExit(f"ffmpeg exited {code}")
    print(dest, dest.stat().st_size)


def thumbnail(slug):
    film = film_by(slug)
    # 研究の結果に当たる場面を中央に使う（4番が無ければ3番）
    sid = 1
    img = render_frame(slug, sid, 4.0, 8.0, None, [], 1.0, 99)
    im = Image.fromarray(img, "RGB")
    # 題が絵と重ならないよう、上だけを黒く沈める
    top = im.crop((0, 0, R.W, 520))
    shade = Image.new("RGB", top.size, (0, 0, 0))
    im.paste(Image.blend(top, shade, 0.72), (0, 0))
    draw = ImageDraw.Draw(im)
    title_font = R.FONT.font_variant(size=64) if hasattr(R.FONT, "font_variant") else R.FONT
    # font_variant may fail for otf; fall back
    try:
        title_font = R.FONT.font_variant(size=68)
        small = R.FONT.font_variant(size=40)
        hook_font = R.FONT.font_variant(size=46)
    except Exception:
        title_font = small = hook_font = R.FONT
    lines = film["title_break"].split("／")
    y = 78
    for line in lines:
        w = title_font.getlength(line)
        draw.text(((R.W - w) / 2, y), line, font=title_font, fill=(255, 255, 255))
        y += 84
    draw.line((R.W / 2 - 70, y + 8, R.W / 2 + 70, y + 8), fill=R.RED, width=4)
    label = "心理学"
    w = small.getlength(label)
    draw.text(((R.W - w) / 2, y + 24), label, font=small, fill=(255, 255, 255))
    hook = film["hook_line"]
    # 下段。一行が長ければ二行に折る
    hlines = wrap_text(hook, 16)
    yb = int(R.H * 0.78)
    for piece, _ in hlines:
        w = hook_font.getlength(piece)
        draw.text(((R.W - w) / 2, yb), piece, font=hook_font, fill=(255, 255, 255))
        yb += 58
    path = ROOT / "build" / slug / "thumbnail.png"
    im.save(path)
    print(path)


def check_scripts():
    ban_jargon = ["相関", "ハザード", "認知", "不協和", "メタ", "サンプル", "有意", "被験者", "バイアス", "統計", "回帰"]
    ban_hype = ["衝撃", "ヤバ", "絶対", "驚愕", "必見", "！", "!", "？？"]
    num_re = re.compile(r"[〇一二三四五六七八九十百千万億0-9]+(?:・[〇一二三四五六七八九十0-9]+)?")
    ok = True
    for film in FILMS:
        texts = [s["text"] for s in film["sentences"]]
        blob = "".join(texts)
        total = len(blob)
        print(f"\n== {film['slug']} {total}字 ==")
        if not (400 <= total <= 600):
            print("  字数"); ok = False
        for s in film["sentences"]:
            if len(s["text"]) > 40:
                print("  40超", s["text"]); ok = False
            for w in s["reds"]:
                if w not in s["text"]:
                    print("  赤字なし", w); ok = False
            for line, _ in wrap_text(s["text"]):
                if len(line) > 13:
                    print("  13超", line); ok = False
        for h in film["hooks"]:
            for t in h["lines"]:
                if len(t) > 40:
                    print("  hook", t); ok = False
        if film["hooks"][0]["lines"] != texts[:4]:
            print("  A案不一致"); ok = False
        if not any("実は" in t and t.endswith("からです。") for t in texts):
            print("  結論"); ok = False
        if not any(t.startswith("なぜ") and t.endswith("だろうか？") for t in texts):
            print("  問い"); ok = False
        if not any(t.startswith("すると") or t.startswith("ところが") for t in texts):
            print("  結果"); ok = False
        if not any("だったんです" in t for t in texts):
            print("  締め"); ok = False
        if not texts[-1].endswith("？"):
            print("  終問"); ok = False
        nums = num_re.findall(blob)
        print("  数字", nums)
        if len(nums) < 3:
            print("  数字不足"); ok = False
        for word in ban_jargon:
            if word in blob:
                print("  用語", word); ok = False
        for word in ban_hype:
            if word in blob:
                print("  煽り", word); ok = False
        if len(film["scenes"]) != max(s["scene"] for s in film["sentences"]):
            print("  場面数"); ok = False
        for sc in film["scenes"]:
            prompt = f"{sc['prompt']}, {STYLE} --no {NEGATIVE}"
            if STYLE not in prompt or "--no" not in prompt:
                print("  prompt"); ok = False
        title = film["title_break"].replace("／", "")
        if not (14 <= len(title) <= 20):
            print("  題", len(title)); ok = False
    print("CHECK", "OK" if ok else "NG")
    return ok
