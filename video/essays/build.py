#!/usr/bin/env python3
"""Turn the five essay scripts into vertical videos."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import edge_tts
import numpy as np

from draw import (
    FPS,
    H,
    POSES,
    W,
    blend_pose,
    composite,
    copy_pose,
    ease,
    fade_black,
    make_subtitle,
    pose_at,
    render_scene,
)
from films import FILMS, say_of, validate

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
OUT = ROOT / "out"
SR = 48000
VOICE = "ja-JP-NanamiNeural"
PITCH = "-8Hz"
BODY_RATE = "-12%"
SLOW_RATE = "-21%"
EXTRA_SLOW = "-38%"
LEAD = 0.45
TAIL = 2.2

CYCLIC = {"tilt", "sway", "flinch", "nod", "still"}

ACTION_JA = {
    "tilt": "首をかしげる",
    "sway": "体を小さく揺らす",
    "flinch": "小さく身をすくめる",
    "nod": "うなずく",
    "still": "姿勢を保つ",
    "slump": "肩を落とす",
    "slump_deep": "さらに肩を落とす",
    "look": "顔を上げる",
    "chest": "手を胸に当てる",
    "stand": "背を伸ばす",
    "placid": "楽な姿勢になる",
    "call": "片手を軽く上げる",
    "stepback": "一歩下がる",
    "reach": "手を前に伸ばす",
    "down": "伸ばした手を下ろす",
    "open": "腕を広げる",
    "bow": "少し身をかがめる",
    "palm": "手のひらを前に出す",
    "close": "手を体のそばに戻す",
}
ACTION_EN = {
    "tilt": "slowly tilts the head",
    "sway": "sways the body once, lightly",
    "flinch": "flinches, drawing the shoulders in",
    "nod": "gives one small nod",
    "still": "holds still",
    "slump": "lets the shoulders drop",
    "slump_deep": "drops the shoulders further",
    "look": "slowly lifts the head",
    "chest": "brings one hand to the chest",
    "stand": "straightens the back",
    "placid": "settles into an easy stance",
    "call": "raises one hand a little",
    "stepback": "takes one step back",
    "reach": "reaches one hand forward",
    "down": "lowers the outstretched hand",
    "open": "opens both arms",
    "bow": "bends down a little",
    "palm": "holds one palm forward",
    "close": "draws the hand back toward the body",
}


def side_ja(scene, who):
    if len(scene["people"]) == 1:
        return "中央"
    return "左" if who == 0 else "右"


def side_en(scene, who):
    if len(scene["people"]) == 1:
        return "central"
    return "left" if who == 0 else "right"


def compile_poses(film):
    carried = {}
    compiled = []
    for phrase in film["phrases"]:
        key = phrase["scene"]
        scene = film["scenes"][key]
        if key not in carried:
            carried[key] = [copy_pose(POSES[p["pose"]]) for p in scene["people"]]
        state = carried[key]
        start = [copy_pose(p) for p in state]
        action = phrase["action"]
        who = phrase["who"]
        if action not in CYCLIC:
            if action not in POSES:
                raise KeyError(action)
            state[who] = copy_pose(POSES[action])
        end = [copy_pose(p) for p in state]
        compiled.append({"start": start, "end": end})
    return compiled


def poses_for(comp, phrase, u):
    action = phrase["action"]
    who = phrase["who"]
    ue = ease(u)
    poses = []
    for i, (a, b) in enumerate(zip(comp["start"], comp["end"])):
        if i == who and action in CYCLIC:
            posed, _ = pose_at("", action, u, a)
            poses.append(posed)
        elif i == who:
            poses.append(blend_pose(a, b, ue))
        else:
            poses.append(a)
    return poses


def cache_path(text, rate):
    digest = hashlib.sha1(f"{VOICE}|{rate}|{PITCH}|{text}".encode()).hexdigest()[:16]
    return BUILD / "tts" / f"{digest}.wav"


def ffmpeg_to_float(path):
    raw = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
    )
    return np.frombuffer(raw, dtype=np.float32).copy()


def trim_speech(wav):
    thr = max(0.008, float(np.percentile(np.abs(wav), 92)) * 0.25)
    idx = np.flatnonzero(np.abs(wav) > thr)
    if len(idx) == 0:
        return wav
    pad = int(0.025 * SR)
    a = max(0, int(idx[0]) - pad)
    b = min(len(wav), int(idx[-1]) + pad)
    speech = wav[a:b]
    peak = float(np.max(np.abs(speech))) or 1.0
    return (speech / peak * 0.9).astype(np.float32)


async def synth_one(text, rate, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    mp3 = dest.with_suffix(".mp3")
    for attempt in range(4):
        try:
            await edge_tts.Communicate(text, VOICE, rate=rate, pitch=PITCH).save(str(mp3))
            wav = trim_speech(ffmpeg_to_float(mp3))
            dest.write_bytes(wav.astype(np.float32).tobytes())
            mp3.unlink(missing_ok=True)
            return wav
        except Exception as exc:
            await asyncio.sleep(1.5 * (attempt + 1))
            last = exc
    raise RuntimeError(f"TTS failed for {text!r}: {last}")


async def load_or_synth(text, rate):
    dest = cache_path(text, rate)
    if dest.exists() and dest.stat().st_size > 100:
        return np.frombuffer(dest.read_bytes(), dtype=np.float32).copy()
    return await synth_one(text, rate, dest)


async def ensure_speech(film):
    sem = asyncio.Semaphore(4)

    async def one(phrase, rate):
        text = say_of(phrase["text"])
        async with sem:
            return await load_or_synth(text, rate)

    rates = [SLOW_RATE if p["slow"] else BODY_RATE for p in film["phrases"]]
    speeches = list(await asyncio.gather(*(one(p, r) for p, r in zip(film["phrases"], rates))))
    # A very short line is stretched, so the subtitle can stay up for at least two seconds.
    again = []
    for i, (phrase, speech) in enumerate(zip(film["phrases"], speeches)):
        cap = 1.0 if phrase["text"].endswith("。") or phrase["break"] else 0.55
        if len(speech) / SR + cap < 2.0 and rates[i] != EXTRA_SLOW:
            again.append(i)
    if again:
        extra = await asyncio.gather(*(one(film["phrases"][i], EXTRA_SLOW) for i in again))
        for i, speech in zip(again, extra):
            speeches[i] = speech
    return speeches


def pause_after(phrase, speech_s):
    if phrase["break"]:
        pause = 1.5
        cap = 1.5
        floor = 1.5
    elif phrase["text"].endswith("。"):
        pause = 0.9
        cap = 1.0
        floor = 0.8
    else:
        pause = 0.4
        cap = 0.55
        floor = 0.3
    window = speech_s + pause
    if window < 2.0:
        pause = min(cap, max(pause, 2.0 - speech_s))
    # Keep a subtitle from flashing off when it is only a breath short of two seconds.
    if speech_s + pause < 2.0 and 2.0 - speech_s <= 0.75:
        pause = 2.0 - speech_s
    if speech_s + pause > 4.05 and not phrase["break"]:
        pause = max(floor, 4.0 - speech_s)
    return pause


def assemble(film, speeches):
    pieces = []
    cursor = LEAD
    rows = []
    pieces.append(np.zeros(int(LEAD * SR), dtype=np.float32))
    for phrase, speech in zip(film["phrases"], speeches):
        speech_s = len(speech) / SR
        pause = pause_after(phrase, speech_s)
        start = cursor
        cursor += speech_s + pause
        pieces.append(speech)
        pieces.append(np.zeros(int(round(pause * SR)), dtype=np.float32))
        rows.append({
            "start": round(start, 3),
            "end": round(cursor, 3),
            "speech": round(speech_s, 3),
            "pause": round(pause, 3),
            "text": phrase["text"],
            "sub": phrase["sub"],
            "scene": phrase["scene"],
            "slow": phrase["slow"],
            "break": phrase["break"],
        })
    pieces.append(np.zeros(int(TAIL * SR), dtype=np.float32))
    audio = np.concatenate(pieces)
    return audio, rows, len(audio) / SR


def report_timing(film, rows, duration):
    flags = []
    for row in rows:
        window = row["end"] - row["start"]
        if window < 1.95 or window > 4.15:
            flags.append(f"  window {window:.2f}s  {row['text']}")
        if row["speech"] > 3.7:
            flags.append(f"  speech {row['speech']:.2f}s  {row['text']}")
    print(f"{film['id']} {duration:.1f}s  phrases {len(rows)}  flags {len(flags)}")
    for line in flags:
        print(line)
    return flags


def write_wav(path: Path, stereo):
    import wave
    pcm = np.clip(stereo, -1, 1)
    pcm = (pcm * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(2)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(pcm.tobytes())


def synth_bgm(duration, chords):
    n = int(duration * SR)
    left = np.zeros(n, dtype=np.float32)
    right = np.zeros(n, dtype=np.float32)
    t = np.arange(n, dtype=np.float32) / SR
    seg = n // len(chords)
    for i, freqs in enumerate(chords):
        a = i * seg
        b = n if i == len(chords) - 1 else (i + 1) * seg
        tt = t[a:b]
        env = np.ones(b - a, dtype=np.float32)
        fade = min(int(1.6 * SR), (b - a) // 3)
        env[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        env[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
        for freq in freqs:
            left[a:b] += np.sin(2 * math.pi * freq * tt) * env
            right[a:b] += np.sin(2 * math.pi * freq * 1.004 * tt) * env
            left[a:b] += 0.22 * np.sin(2 * math.pi * freq * 2 * tt) * env
            right[a:b] += 0.18 * np.sin(2 * math.pi * freq * 2.003 * tt) * env
        # one soft piano-like tone near the middle of the chord
        note_at = a + (b - a) // 3
        tone_n = min(int(4.5 * SR), n - note_at)
        if tone_n > 0:
            tn = np.arange(tone_n, dtype=np.float32) / SR
            freq = freqs[0] * 2
            tone = np.sin(2 * math.pi * freq * tn) * np.exp(-tn * 1.3)
            tone += 0.25 * np.sin(2 * math.pi * freq * 2 * tn) * np.exp(-tn * 1.8)
            attack = np.minimum(1, tn / 0.04)
            tone = (0.35 * attack * tone).astype(np.float32)
            left[note_at:note_at + tone_n] += tone
            right[note_at:note_at + tone_n] += tone * 0.9
    trem = (0.9 + 0.1 * np.sin(2 * math.pi * 0.06 * t)).astype(np.float32)
    bed = np.stack([left * trem, right * trem], axis=1)
    # gentle one-pole lowpass
    out = np.zeros_like(bed)
    acc = np.zeros(2, dtype=np.float32)
    coef = 0.08
    for i in range(n):
        acc += coef * (bed[i] - acc)
        out[i] = acc
    return out


def mix(narration, bgm):
    n = max(len(narration), len(bgm))
    nar = np.zeros((n, 2), dtype=np.float32)
    mono = np.zeros(n, dtype=np.float32)
    mono[: len(narration)] = narration
    nar[:, 0] = mono
    nar[:, 1] = mono
    bed = np.zeros((n, 2), dtype=np.float32)
    bed[: len(bgm)] = bgm
    speech = np.abs(mono) > 0.02
    if np.any(speech):
        nar_rms = float(np.sqrt(np.mean(mono[speech] ** 2)))
    else:
        nar_rms = 0.1
    bed_rms = float(np.sqrt(np.mean(bed ** 2))) or 1.0
    bed *= (nar_rms * 10 ** (-19 / 20)) / bed_rms
    fade_in = int(2.0 * SR)
    fade_out = int(2.0 * SR)
    env = np.ones(n, dtype=np.float32)
    env[:fade_in] = np.linspace(0, 1, fade_in, dtype=np.float32)
    env[-fade_out:] = np.linspace(1, 0, fade_out, dtype=np.float32)
    bed *= env[:, None]
    mixed = nar + bed
    peak = float(np.max(np.abs(mixed))) or 1.0
    if peak > 0.98:
        mixed *= 0.98 / peak
    return mixed


def render_video(film, rows, duration, wav_path, dest, preview_dir=None):
    compiled = compile_poses(film)
    overlays = [make_subtitle(p["sub"]) for p in film["phrases"]]
    surface = None
    total = int(math.ceil(duration * FPS))
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", str(wav_path),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart",
        str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    scene_ids = [p["scene"] for p in film["phrases"]]
    saved = set()
    try:
        for frame_i in range(total):
            t = frame_i / FPS
            idx = 0
            while idx < len(rows) - 1 and t >= rows[idx]["end"]:
                idx += 1
            row = rows[idx]
            phrase = film["phrases"][idx]
            scene = film["scenes"][phrase["scene"]]
            speech_end = row["start"] + row["speech"]
            if t < row["start"]:
                u = 0.0
            elif row["speech"] <= 0.05:
                u = 1.0
            else:
                u = min(1.0, max(0.0, (t - row["start"]) / row["speech"]))
            poses = poses_for(compiled[idx], phrase, u)
            scatter = u if any(s["kind"] == "scatter" for s in scene.get("symbols", [])) else 0.0
            rgb, _ = render_scene(scene, poses, scatter_t=scatter)
            # fade in over 0.3s at each new scene, and from black at the very start
            level = 1.0
            if t < 0.35:
                level = min(level, t / 0.35)
            if idx > 0 and scene_ids[idx] != scene_ids[idx - 1]:
                local = t - row["start"]
                if 0 <= local < 0.3:
                    level = min(level, local / 0.3)
            if t > duration - TAIL:
                level = min(level, max(0.0, (duration - t) / TAIL))
            if level < 0.999:
                rgb = fade_black(rgb, level)
            show_sub = row["start"] <= t < row["end"] and level > 0.2
            if show_sub:
                rgb = composite(rgb, overlays[idx])
            if preview_dir and phrase["scene"] not in saved and u > 0.45:
                from PIL import Image
                Image.fromarray(rgb).save(preview_dir / f"{film['id']}_{phrase['scene']}.png")
                saved.add(phrase["scene"])
            proc.stdin.write(rgb.tobytes())
        proc.stdin.close()
        code = proc.wait()
        if code != 0:
            raise RuntimeError(f"ffmpeg exited {code}")
    except Exception:
        proc.kill()
        raise


def fmt_time(seconds):
    return f"{seconds:.1f}"


def reading_script(film):
    lines = []
    for phrase in film["phrases"]:
        say = say_of(phrase["text"])
        say = say.replace("、", "、（間）")
        if phrase["break"]:
            say = say.replace("。", "。（長い間）")
        else:
            say = say.replace("。", "。（間）")
        lines.append(say)
    return "".join(lines)


def write_doc(films_payload, path: Path):
    parts = ["# 黒背景・棒人間・赤一点　五本の台本", ""]
    parts.append("縦型の短い動画、五本分です。声は低めのやわらかい話し方、画面は黒一色に白い棒人間、赤いものは作品ごとに一つだけです。")
    parts.append("")
    style = (
        "minimalist white stick figure line art on pure black background, "
        "single thin hand-drawn horizontal ground line at 62% height, "
        "only one red accent element, static camera, limited animation, no text"
    )
    negative = "color, gradient, realistic, 3D, shading, face details, camera movement, text, watermark, background objects, particles, glow"
    for film, rows, duration in films_payload:
        parts.append(f"## {film['id']}　{film['title']}")
        parts.append("")
        parts.append("### A. 作品の核")
        parts.append(f"- 主題：{film['core']}")
        parts.append(f"- 赤で表すもの：{film['red_name']}。{film['red_meaning']}")
        parts.append("- 象徴：")
        for name, meaning in film["symbols"]:
            parts.append(f"  - {name}：{meaning}")
        parts.append("")
        parts.append("### B. ナレーション原稿")
        parts.append("#### B-1 全文")
        parts.append("")
        sentences, _ = __import__("films").sentences_of(film)
        for sent in sentences:
            parts.append(sent)
        parts.append("")
        parts.append("#### B-2 フレーズごとのタイムコード")
        parts.append("")
        parts.append("| 開始 | 終了 | 字幕 | 原稿 |")
        parts.append("| --- | --- | --- | --- |")
        for row in rows:
            sub = "／".join(row["sub"])
            parts.append(f"| {fmt_time(row['start'])}秒 | {fmt_time(row['end'])}秒 | {sub} | {row['text']} |")
        parts.append("")
        parts.append(f"全体の長さは {duration:.1f} 秒です。")
        parts.append("")
        parts.append("#### B-3 音声合成用の読み原稿")
        parts.append("")
        parts.append(reading_script(film))
        parts.append("")
        parts.append("### C. 絵コンテ")
        parts.append("")
        parts.append("| 時間 | 字幕 | 画面 | 動き | 記号 | 赤 | 切替 |")
        parts.append("| --- | --- | --- | --- | --- | --- | --- |")
        prev = None
        for phrase, row in zip(film["phrases"], rows):
            scene = film["scenes"][phrase["scene"]]
            cut = "フェード0.3秒" if phrase["scene"] != prev else "継続"
            prev = phrase["scene"]
            who = side_ja(scene, phrase["who"])
            parts.append(
                "| {t} | {sub} | {place}。動くのは{who} | {move} | {sym} | {red} | {cut} |".format(
                    t=f"{fmt_time(row['start'])}〜{fmt_time(row['end'])}",
                    sub="／".join(phrase["sub"]),
                    place=scene["ja"],
                    who=who,
                    move=ACTION_JA[phrase["action"]],
                    sym=scene["sym_ja"],
                    red=scene["red_ja"],
                    cut=cut,
                )
            )
        parts.append("")
        parts.append("### D. 映像生成AI向けプロンプト")
        parts.append("#### D-1 全シーン共通")
        parts.append("")
        parts.append(style)
        parts.append("")
        parts.append("#### D-2 シーンごと")
        parts.append("")
        for phrase, row in zip(film["phrases"], rows):
            scene = film["scenes"][phrase["scene"]]
            sentence = (
                f"At {fmt_time(row['start'])}s, {style}. {scene['en']}. "
                f"The {side_en(scene, phrase['who'])} figure {ACTION_EN[phrase['action']]}. "
                f"{scene['sym_en']}. {scene['red_en']}."
            )
            parts.append(f"- {sentence}")
        parts.append("")
        parts.append("#### D-3 ネガティブプロンプト")
        parts.append("")
        parts.append(negative)
        parts.append("")
        parts.append("### E. 音声合成の設定")
        parts.append("")
        parts.append("声の方向は、低めから中くらい、ささやく手前の落ち着いた声。感情は乗せすぎない。文末は静かに下げる。問いかけも、軽く上げるだけ。音量は一定で、強調したい語は少しだけ遅くする。")
        parts.append("")
        parts.append("- ElevenLabs（eleven_multilingual_v2）：Stability 75、Similarity 70、Style 10。速度は本文 0.88、冒頭と最後の一文は 0.79。")
        parts.append("- VOICEVOX（冥鳴ひまり ノーマル、または青山龍星 ノーマル）：speedScale 0.90（冒頭と最後は 0.81）、pitchScale -0.04、intonationScale 0.62。読点のあとに 0.4 秒、句点のあとに 0.9 秒、幕の変わり目に 1.5 秒の無音を足す。")
        parts.append("- Google TTS（ja-JP-Neural2-B）：speakingRate 0.88（冒頭と最後は 0.80）、pitch -2.0。SSML の break で、読点 400ms、句点 900ms、幕の変わり目 1500ms。")
        parts.append("")
        parts.append("今回の完成音声は、同じ速さ・同じ高さになるよう、やわらかい日本語の合成音声（女性、やや低め）で作っています。本文の速さは -12%、冒頭と最後の一文は -21%、高さは -8Hz です。")
        parts.append("")
        parts.append("### F. 編集指示")
        parts.append("")
        parts.append("- 画面は 1080×1920、30fps。背景は #000000。地面の白線は上から 62% の位置。")
        parts.append("- 字幕は Noto Sans CJK JP Bold、文字の高さ約 75px（画面の幅の約 7%）。縁取りも影も帯もなし。中央揃え。1行の中心、2行のときは2行ぶんの中心が、上から 30% の位置。行の間隔は文字の高さの 1.4 倍。")
        parts.append("- 字幕は句読点なし、1行10文字以内、最大2行。そのフレーズの声の出だしで出し、次のフレーズの出だしで切り替える。")
        parts.append("- ナレーションの音量を基準に、BGM はその約 -19dB。BGM は冒頭2秒でフェードイン、最後2秒でフェードアウト。効果音はなし。")
        parts.append("- 場面が変わるときは 0.3 秒で黒から浮かぶ。カメラは動かさない。")
        parts.append("")
        parts.append("### G. 投稿用テキスト")
        parts.append("")
        parts.append(f"{film['post']}")
        parts.append(f"#人生 #エッセイ {film['hashtag']}")
        parts.append("")
    path.write_text("\n".join(parts), encoding="utf-8")


def build_film(film, preview_only=False):
    errors, total, _ = validate(film)
    if errors:
        raise SystemExit(f"{film['id']} script error: {errors}")
    print(f"synth {film['id']} ({total} chars)")
    speeches = asyncio.run(ensure_speech(film))
    narration, rows, duration = assemble(film, speeches)
    flags = report_timing(film, rows, duration)
    BUILD.mkdir(parents=True, exist_ok=True)
    (BUILD / f"{film['id']}_timeline.json").write_text(
        json.dumps({"duration": duration, "rows": rows}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if preview_only:
        return film, rows, duration, flags
    bgm = synth_bgm(duration, film["chords"])
    mixed = mix(narration, bgm)
    wav_path = BUILD / f"{film['id']}.wav"
    write_wav(wav_path, mixed)
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / f"{film['slug']}.mp4"
    preview = OUT / "frames"
    preview.mkdir(parents=True, exist_ok=True)
    print(f"render {dest.name} {duration:.1f}s")
    render_video(film, rows, duration, wav_path, dest, preview)
    print(f"done {dest}")
    return film, rows, duration, flags


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", default="all")
    parser.add_argument("--audio-only", action="store_true")
    args = parser.parse_args()
    chosen = FILMS if args.id == "all" else [f for f in FILMS if f["id"] == args.id]
    if not chosen:
        raise SystemExit("no film")
    payload = []
    for film in chosen:
        film, rows, duration, flags = build_film(film, preview_only=args.audio_only)
        payload.append((film, rows, duration))
    if not args.audio_only and len(payload) == len(FILMS):
        write_doc(payload, ROOT / "台本.md")
        print("wrote 台本.md")


if __name__ == "__main__":
    main()
