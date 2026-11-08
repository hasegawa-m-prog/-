#!/usr/bin/env python3
"""五本のナレーションを作り、縦型の線画動画に書き出す。"""

import json
import subprocess
import sys
import urllib.parse
import urllib.request
import wave
from pathlib import Path

from engine import FPS, H, W, Frame, compose
from scenes import SCENES
from series_data import FILMS, plain

BASE = "http://127.0.0.1:50021"
SPEAKER = 13  # 青山龍星 ノーマル
SPEED = 1.05
PITCH = -0.02
INTONATION = 0.9
LEAD = 0.45
TAIL = 1.05
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"


def post(url, body=None, content_type=None):
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    data = b"" if body is None else body
    req = urllib.request.Request(url, data=data, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=180) as res:
        return res.read()


def audio_query(text):
    url = BASE + "/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": SPEAKER})
    return json.loads(post(url, b""))


def synthesize(text, path: Path):
    query = audio_query(text)
    query["speedScale"] = SPEED
    query["pitchScale"] = PITCH
    query["intonationScale"] = INTONATION
    query["prePhonemeLength"] = 0.06
    query["postPhonemeLength"] = 0.10
    wav = post(f"{BASE}/synthesis?speaker={SPEAKER}", json.dumps(query).encode(), "application/json")
    path.write_bytes(wav)


def wav_info(path: Path):
    with wave.open(str(path), "rb") as w:
        return w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes(), w.readframes(w.getnframes())


def build_timeline(film, durations):
    """文の長さから場面の開始と終了を決める。短い場面は五秒まで足す。"""
    entries = []
    t = LEAD
    for i, ((marked, scene, block_end), dur) in enumerate(zip(film["lines"], durations), 1):
        pause = 0.8 if block_end else 0.4
        if i == len(film["lines"]):
            pause = 0.0
        entries.append({
            "i": i,
            "scene": scene,
            "start": round(t, 3),
            "end": round(t + dur, 3),
            "marked": marked,
            "pause_after": pause,
        })
        t += dur + pause

    # 場面が五秒未満なら、その場面のうしろに無音を足して後ろをずらす。
    scene_ids = sorted({e["scene"] for e in entries})
    for sid in scene_ids:
        segs = [e for e in entries if e["scene"] == sid]
        span_end = segs[-1]["end"] + segs[-1]["pause_after"]
        span = span_end - (0.0 if sid == 1 else segs[0]["start"])
        # 場面1は先頭の無音も含めて数える
        if sid == 1:
            span = segs[-1]["end"] + segs[-1]["pause_after"]
        if span < 5.0:
            extra = 5.0 - span
            segs[-1]["pause_after"] = round(segs[-1]["pause_after"] + extra, 3)
            shift = extra
            for e in entries:
                if e["start"] > segs[-1]["start"]:
                    e["start"] = round(e["start"] + shift, 3)
                    e["end"] = round(e["end"] + shift, 3)

    duration = entries[-1]["end"] + entries[-1]["pause_after"] + TAIL
    scenes = []
    for sid in scene_ids:
        segs = [e for e in entries if e["scene"] == sid]
        if sid == scene_ids[0]:
            start = 0.0
        else:
            prev = [e for e in entries if e["scene"] == sid - 1][-1]
            start = prev["end"] + prev["pause_after"]
        scenes.append({"id": sid, "start": round(start, 3)})
    for i, scene in enumerate(scenes):
        scene["end"] = round(scenes[i + 1]["start"] if i + 1 < len(scenes) else duration, 3)

    for e in entries:
        scene_end = next(s["end"] for s in scenes if s["id"] == e["scene"])
        nxt = None
        later = [x for x in entries if x["start"] > e["start"]]
        if later:
            nxt = later[0]["start"]
        e["hold"] = round(min(nxt if nxt is not None else duration, scene_end), 3)

    return {
        "duration": round(duration, 3),
        "scenes": scenes,
        "subs": [
            {"start": e["start"], "hold": e["hold"], "marked": e["marked"], "scene": e["scene"]}
            for e in entries
        ],
    }, entries


# 字幕は漢字の数字のまま、読みだけ声が誤らない形にする。
SPEAK = {
    "何ももらわないと、零点九二枚でした。": "何ももらわないと、れいてんきゅうに枚でした。",
}


def write_narration(film, line_dir: Path):
    line_dir.mkdir(parents=True, exist_ok=True)
    durations = []
    readings = []
    for i, (marked, _s, _b) in enumerate(film["lines"], 1):
        path = line_dir / f"{i:02d}.wav"
        text = SPEAK.get(plain(marked), plain(marked))
        query = audio_query(text)
        kana = " | ".join("".join(m["text"] for m in ph["moras"]) for ph in query["accent_phrases"])
        query["speedScale"] = SPEED
        query["pitchScale"] = PITCH
        query["intonationScale"] = INTONATION
        query["prePhonemeLength"] = 0.06
        query["postPhonemeLength"] = 0.10
        wav = post(f"{BASE}/synthesis?speaker={SPEAKER}", json.dumps(query).encode(), "application/json")
        path.write_bytes(wav)
        _ch, _sw, rate, n, _frames = wav_info(path)
        dur = n / rate
        durations.append(dur)
        readings.append(kana)
        print(f"  {i:02d} {dur:5.2f}s  {text}")
    return durations, readings


def mix_audio(line_dir, entries, sample_meta, out_path: Path):
    ch, sw, rate, _, _ = sample_meta
    frame_bytes = ch * sw

    def silence(seconds):
        n = int(round(seconds * rate))
        return b"\x00" * n * frame_bytes

    pcm = bytearray()
    pcm += silence(LEAD)
    cursor = LEAD
    for e in entries:
        gap = e["start"] - cursor
        if gap > 0.01:
            pcm += silence(gap)
            cursor += gap
        _c, _s, _r, _n, frames = wav_info(line_dir / f"{e['i']:02d}.wav")
        pcm += frames
        cursor = e["end"]
        if e["pause_after"]:
            pcm += silence(e["pause_after"])
            cursor += e["pause_after"]
    tail = (entries[-1]["end"] + entries[-1]["pause_after"] + TAIL) - cursor
    if tail > 0:
        pcm += silence(tail)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(rate)
        w.writeframes(pcm)


def frame_at(film_index, timeline, t, index):
    scenes = timeline["scenes"]
    scene = scenes[-1]
    for s in scenes:
        if s["start"] <= t < s["end"]:
            scene = s
            break
    marked = None
    for sub in timeline["subs"]:
        if sub["start"] <= t < sub["hold"]:
            marked = sub["marked"]
            break
    local = t - scene["start"]
    dur = max(0.3, scene["end"] - scene["start"])
    fade = 1.0
    fin = 0.5
    fout = 0.5
    if t - scene["start"] < fin:
        fade = (t - scene["start"]) / fin
    if scene["end"] - t < fout:
        fade = min(fade, (scene["end"] - t) / fout)
    fade = 0.0 if fade < 0 else 1.0 if fade > 1 else fade
    fr = Frame()
    SCENES[(film_index, scene["id"])](fr, local, dur)
    return compose(fr, marked, fade, index)


def render_video(film_index, timeline, audio_path: Path, out_path: Path):
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
            frame = frame_at(film_index, timeline, i / FPS, i)
            proc.stdin.write(frame.tobytes())
            if i % FPS == 0:
                proc.stdin.flush()
                print(f"\r  frame {i}/{nframes}", end="", flush=True)
        proc.stdin.close()
        code = proc.wait()
    except BrokenPipeError:
        code = proc.wait()
    log.close()
    print()
    if code != 0:
        sys.stderr.write(log_path.read_text()[-2000:])
        raise SystemExit(f"ffmpeg exited {code}")


def preview(film_index, dest: Path):
    from PIL import Image
    dest.mkdir(parents=True, exist_ok=True)
    film = FILMS[film_index]
    thumbs = []
    for sid in range(1, 10):
        marked = next(m for m, s, _b in film["lines"] if s == sid)
        fr = Frame()
        SCENES[(film_index, sid)](fr, 3.2, 8.0)
        img = compose(fr, marked, 1.0, sid)
        path = dest / f"scene_{sid:02d}.png"
        Image.fromarray(img, "RGB").save(path)
        thumbs.append(img)
        print("  wrote", path)
    tw, th = 180, 320
    sheet = Image.new("RGB", (tw * 3, th * 3), "black")
    for i, img in enumerate(thumbs):
        im = Image.fromarray(img, "RGB").resize((tw, th), Image.Resampling.LANCZOS)
        sheet.paste(im, ((i % 3) * tw, (i // 3) * th))
    sheet.save(dest / "contact.png")


def thumbnail(film_index, dest: Path):
    from PIL import Image, ImageDraw, ImageFont
    from engine import FONT_PATH, RED
    film = FILMS[film_index]
    fr = Frame()
    SCENES[(film_index, 1)](fr, 4.0, 8.0)
    img = compose(fr, None, 1.0, 3)
    im = Image.fromarray(img, "RGB")
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT_PATH, 72, index=0)
    small = ImageFont.truetype(FONT_PATH, 40, index=0)
    title = film["title"].split("／")
    y = 150
    for line in title:
        width = font.getlength(line)
        draw.text(((W - width) / 2, y), line, font=font, fill=(255, 255, 255))
        y += 96
    draw.line((W / 2 - 70, y + 10, W / 2 + 70, y + 10), fill=RED, width=4)
    label = "心理学"
    lw = small.getlength(label)
    draw.text(((W - lw) / 2, y + 28), label, font=small, fill=(255, 255, 255))
    hook = plain(film["lines"][0][0])
    # 十三字で折る
    rows = [hook[i:i + 13] for i in range(0, len(hook), 13)]
    y = int(H * 0.78)
    for row in rows:
        width = font.getlength(row)
        draw.text(((W - width) / 2, y), row, font=font, fill=(255, 255, 255))
        y += 90
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest)
    print("  thumb", dest)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    which = sys.argv[2] if len(sys.argv) > 2 else None
    targets = list(enumerate(FILMS))
    if which is not None:
        targets = [(i, f) for i, f in targets if f["id"] == which or str(i) == which]
    if mode == "preview":
        for i, film in targets:
            print(film["id"])
            preview(i, OUT / film["id"] / "preview")
        return
    if mode == "thumbs":
        for i, film in targets:
            thumbnail(i, OUT / film["id"] / "thumbnail.png")
        return
    for i, film in targets:
        print("\n==", film["id"])
        work = OUT / film["id"]
        durations, readings = write_narration(film, work / "lines")
        timeline, entries = build_timeline(film, durations)
        ch, sw, rate, _, _ = wav_info(work / "lines" / "01.wav")
        mix_audio(work / "lines", entries, (ch, sw, rate, 0, None), work / "narration.wav")
        timeline["readings"] = readings
        timeline["sample_rate"] = rate
        (work / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  total {timeline['duration']:.1f}s")
        for s in timeline["scenes"]:
            length = s["end"] - s["start"]
            flag = ""
            if length < 4.95:
                flag = " SHORT"
            if length > 15.05:
                flag = " LONG"
            print(f"  scene {s['id']}: {length:.2f}s{flag}")
        if mode == "audio":
            continue
        out = work / film["file"]
        render_video(i, timeline, work / "narration.wav", out)
        thumbnail(i, work / "thumbnail.png")
        print("  wrote", out)


if __name__ == "__main__":
    main()
