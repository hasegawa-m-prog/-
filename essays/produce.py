#!/usr/bin/env python3
"""Turn the five essays into narration, picture, and the A-G notes."""

from __future__ import annotations

import asyncio
import json
import subprocess
import wave
from pathlib import Path

import edge_tts
import numpy as np

from draw import (
    CHAR_H,
    FPS,
    H,
    W,
    draw_subtitle,
    render_art,
)
from stories import STORIES, manuscript, sentences_of, validate

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / "build"
OUT = ROOT / "out"
DOCS = ROOT / "docs"
BGM = ROOT / "bgm" / "nagareboshi.mp3"

SR = 48000
VOICE = "ja-JP-NanamiNeural"
PITCH = "-3Hz"
BODY_RATE = "-22%"
SLOW_RATE = "-32%"  # hook and the final sentence, about 10% slower
LEAD = 0.45
COMMA_GAP = 0.40
PERIOD_GAP = 0.92
ACT_GAP = 1.50
END_GAP = 1.00
TAIL_KEEP = 0.06

POSE_JA = {
    "stand": "まっすぐ立っている",
    "down": "肩を落として顔を下げている",
    "up": "顔を上げている",
    "easy": "力を抜いて立っている",
    "reach": "片手を前に伸ばしている",
    "open": "両腕を開いている",
    "chest": "手を胸に添えている",
    "squat": "しゃがんでいる",
}
POS_JA = {"L": "左", "C": "中央", "R": "右", "FL": "左の遠く", "FR": "右の遠く"}
FACE_JA = {1: "右向き", -1: "左向き"}
SYM_JA = {
    "note": "♪",
    "q": "？",
    "radial": "放射状の短線",
    "dots": "二人のあいだの点線",
    "chain": "鎖",
    "chain_fall": "落ちていく鎖",
    "arch": "アーチ",
    "sun": "小さな太陽",
    "bubble": "吹き出し",
    "gift": "手の中の白い丸",
    "scatter": "小さな点の散り",
}
RED_JA = {
    "none": "なし",
    "wound": "胸に赤い傷",
    "string": "伸ばした手から相手へ、赤い糸",
    "string_fall": "赤い糸が手から地面へ落ちる",
    "string_down": "赤い糸が地面に置いてある",
    "mark": "手の先に赤いばつ印",
    "mark_fall": "赤いばつ印を地面へ下ろす",
    "mark_down": "赤いばつ印が地面にある",
    "crumb_fall": "赤いかけらが落ちる",
    "crumb_ground": "足元に赤いかけら",
    "crumb_hand": "手の中に赤いかけら",
    "expect": "手から相手の手前で途切れる赤い点線",
    "expect_chest": "胸から相手の手前で途切れる赤い点線",
}
POSE_EN = {
    "stand": "standing straight",
    "down": "shoulders dropped and head lowered",
    "up": "head raised",
    "easy": "standing loosely",
    "reach": "one arm extended forward",
    "open": "both arms open",
    "chest": "one hand held to the chest",
    "squat": "crouching",
}
POS_EN = {"L": "on the left", "C": "in the center", "R": "on the right", "FL": "far left", "FR": "far right"}


def spoken(text: str) -> str:
    return "".join(ch for ch in text if ch not in "、。？")


def decode_mp3(data: bytes) -> np.ndarray:
    proc = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", str(SR), "pipe:1"],
        input=data,
        capture_output=True,
        check=True,
    )
    return np.frombuffer(proc.stdout, dtype=np.int16).copy()


async def synthesize(text: str, rate: str):
    comm = edge_tts.Communicate(
        text, voice=VOICE, rate=rate, pitch=PITCH, boundary="WordBoundary"
    )
    audio = bytearray()
    words = []
    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio.extend(chunk["data"])
        elif chunk["type"] == "WordBoundary":
            words.append(
                {
                    "t0": chunk["offset"] / 1e7,
                    "t1": (chunk["offset"] + chunk["duration"]) / 1e7,
                    "text": chunk["text"].replace(" ", ""),
                }
            )
    if not words:
        raise RuntimeError("音声の区切りが返りませんでした: " + text[:40])
    return decode_mp3(bytes(audio)), words


def align(say: str, words: list[dict]) -> None:
    expect = spoken(say)
    got = "".join(w["text"] for w in words)
    if got != expect:
        raise RuntimeError(f"読みの対応がずれました\n原稿: {expect}\n音声: {got}")
    indexes = [i for i, ch in enumerate(say) if ch not in "、。？"]
    cursor = 0
    for word in words:
        span = indexes[cursor : cursor + len(word["text"])]
        word["lo"] = span[0]
        word["hi"] = span[-1]
        cursor += len(word["text"])


def rebuild(samples: np.ndarray, words: list[dict], say: str):
    """Keep the breaths the voice already made, and lengthen short commas."""
    total = len(samples) / SR
    spans = []
    extras = []
    cursor = max(0.0, words[0]["t0"] - 0.05)
    for i, word in enumerate(words):
        if i < len(words) - 1:
            nxt = words[i + 1]
            natural = max(0.0, nxt["t0"] - word["t1"])
            mid = word["t1"] + natural * 0.5
            between = say[word["hi"] + 1 : nxt["lo"]]
            extra = COMMA_GAP - natural if "、" in between and natural < COMMA_GAP else 0.0
            spans.append((cursor, min(mid, total)))
            extras.append(extra)
            cursor = mid
        else:
            spans.append((cursor, min(total, word["t1"] + TAIL_KEEP)))
            extras.append(0.0)
    pieces = []
    mapped = []
    out_at = 0.0
    n = len(samples)
    for (a, b), extra in zip(spans, extras):
        i0 = max(0, min(n, int(round(a * SR))))
        i1 = max(i0, min(n, int(round(b * SR))))
        pieces.append(samples[i0:i1])
        mapped.append((a, b, out_at))
        out_at += (i1 - i0) / SR
        if extra > 0:
            pieces.append(np.zeros(int(round(extra * SR)), dtype=np.int16))
            out_at += extra
    audio = np.concatenate(pieces) if pieces else np.zeros(0, dtype=np.int16)

    def map_t(src: float) -> float:
        for a, b, start in mapped:
            if a - 0.03 <= src <= b + 0.03:
                return start + (src - a)
        return mapped[-1][2] + max(0.0, mapped[-1][1] - mapped[-1][0])

    timed = []
    for word in words:
        timed.append({**word, "t0": map_t(word["t0"]), "t1": map_t(word["t1"])})
    return audio, timed


def assign(phrases, words):
    """Group spoken words onto phrases. A word that crosses a phrase boundary is split by length."""
    stream = "".join(spoken(p["say"]) for p in phrases)
    got = "".join(w["text"] for w in words)
    if stream != got:
        raise RuntimeError(f"読みの対応がずれました\n原稿: {stream}\n音声: {got}")
    ranges = []
    cursor = 0
    for phrase in phrases:
        n = len(spoken(phrase["say"]))
        ranges.append((cursor, cursor + n))
        cursor += n
    groups = [[] for _ in phrases]
    pos = 0
    for word in words:
        wlen = len(word["text"])
        span = max(0.01, word["t1"] - word["t0"])
        for i, (start, end) in enumerate(ranges):
            ov0 = max(start, pos)
            ov1 = min(end, pos + wlen)
            if ov1 <= ov0:
                continue
            groups[i].append(
                {
                    **word,
                    "t0": word["t0"] + span * ((ov0 - pos) / wlen),
                    "t1": word["t0"] + span * ((ov1 - pos) / wlen),
                    "text": word["text"][ov0 - pos : ov1 - pos],
                }
            )
        pos += wlen
    for phrase, group in zip(phrases, groups):
        if not group:
            raise RuntimeError("空のフレーズ: " + phrase["say"])
    return groups


def pad_slots(audio, rows, minimum=2.02, ceiling=89.5):
    """Lengthen very short subtitle slots, keeping the whole film inside 90 seconds."""
    extras = []
    for row in rows:
        slot = row["end"] - row["start"]
        if slot < minimum:
            extras.append([row["end"], minimum - slot])
    room = ceiling - (len(audio) / SR)
    total = sum(extra for _, extra in extras)
    if total > max(0.0, room):
        scale = max(0.0, room) / total if total else 0.0
        for item in extras:
            item[1] *= scale
    for at_time, extra in sorted(extras, reverse=True):
        if extra < 0.02:
            continue
        at = max(0, min(len(audio), int(round(at_time * SR))))
        silence = np.zeros(int(round(extra * SR)), dtype=np.int16)
        audio = np.concatenate([audio[:at], silence, audio[at:]])
        for row in rows:
            if row["end"] >= at_time - 0.03:
                row["end"] += extra
            if row["start"] >= at_time - 0.03:
                row["start"] += extra
    return audio, rows


def write_wav(path: Path, samples: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SR)
        handle.writeframes(samples.astype(np.int16).tobytes())


def fade_edges(samples: np.ndarray) -> np.ndarray:
    out = samples.astype(np.float32)
    n = min(int(0.012 * SR), len(out) // 4)
    ramp = np.linspace(0, 1, n, dtype=np.float32)
    out[:n] *= ramp
    out[-n:] *= ramp[::-1]
    return out.astype(np.int16)


async def build_audio(story) -> dict:
    groups = sentences_of(story["phrases"])
    jobs = []
    for index, sentence in enumerate(groups):
        say = "".join(p["say"] for p in sentence)
        slow = sentence[0]["act"] == 1 or index == len(groups) - 1
        jobs.append((say, SLOW_RATE if slow else BODY_RATE))

    sem = asyncio.Semaphore(3)

    async def one(say, rate):
        async with sem:
            last = None
            for attempt in range(4):
                try:
                    return await synthesize(say, rate)
                except Exception as exc:  # network hiccup
                    last = exc
                    await asyncio.sleep(1.2 * (attempt + 1))
            raise last

    synthesized = await asyncio.gather(*(one(say, rate) for say, rate in jobs))

    pieces = [np.zeros(int(round(LEAD * SR)), dtype=np.int16)]
    cursor = LEAD
    rows = []
    for index, (sentence, (samples, words)) in enumerate(zip(groups, synthesized)):
        say = jobs[index][0]
        align(say, words)
        audio, words = rebuild(samples, words, say)
        grouped = assign(sentence, words)
        act_end = index + 1 == len(groups) or groups[index + 1][0]["act"] != sentence[0]["act"]
        if index == len(groups) - 1:
            desired = END_GAP
        elif act_end:
            desired = ACT_GAP
        else:
            desired = PERIOD_GAP
        pause = max(0.2, desired - TAIL_KEEP)
        dur = len(audio) / SR
        for pi, (phrase, ws) in enumerate(zip(sentence, grouped)):
            start = cursor + ws[0]["t0"]
            end = cursor + grouped[pi + 1][0]["t0"] if pi + 1 < len(grouped) else cursor + dur + pause
            rows.append({"index": len(rows), "start": start, "end": end, "act": phrase["act"]})
        pieces.append(audio)
        pieces.append(np.zeros(int(round(pause * SR)), dtype=np.int16))
        cursor += dur + pause

    narration = fade_edges(np.concatenate(pieces))
    narration, rows = pad_slots(narration, rows)
    duration = len(narration) / SR
    scenes = []
    for i, row in enumerate(rows):
        vis_start = 0.0 if i == 0 else row["start"]
        scenes.append({**row, "vis_start": vis_start})
    for i, scene in enumerate(scenes):
        scene["vis_end"] = scenes[i + 1]["vis_start"] if i + 1 < len(scenes) else duration
        prev = story["phrases"][i - 1] if i else None
        cur = story["phrases"][i]
        if prev is None:
            scene["trans"] = "cut"
        elif prev["act"] != cur["act"]:
            scene["trans"] = "cut"
        elif _places(prev) != _places(cur):
            scene["trans"] = "cut"
        else:
            scene["trans"] = "fade"
    folder = BUILD / story["id"]
    folder.mkdir(parents=True, exist_ok=True)
    write_wav(folder / "narration.wav", narration)
    payload = {"duration": duration, "scenes": scenes, "rate_body": BODY_RATE, "rate_slow": SLOW_RATE}
    (folder / "timeline.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _report(story, scenes, duration)
    return payload


def _places(phrase):
    return tuple((fig[0], fig[1], fig[2]) for fig in phrase["figs"])


def _report(story, scenes, duration):
    print(f"\n{story['id']} {story['title']}  {duration:.1f}秒  {story['_chars']}字")
    bad = 0
    for scene in scenes:
        slot = scene["end"] - scene["start"]
        flag = ""
        if slot < 1.85 or slot > 4.25:
            bad += 1
            flag = "  ←字幕の秒数が目安の外"
        text = story["phrases"][scene["index"]]["show"]
        print(f"  {scene['start']:6.2f}-{scene['end']:6.2f}  {slot:4.2f}s  {text}{flag}")
    if bad:
        print(f"  目安外の字幕: {bad}")


def mix_bgm(narration: Path, duration: float, dest: Path) -> None:
    fade_at = max(0.0, duration - 2.0)
    # loudnorm は内部で 192kHz に上げる。そのまま AAC に渡すと尺が数秒短くなるので、
    # 混ぜる前に 48kHz・モノラルへ戻す。
    filt = (
        "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=mono[n];"
        f"[1:a]aformat=channel_layouts=mono,aresample=48000,atrim=0:{duration:.3f},asetpts=PTS-STARTPTS,"
        "loudnorm=I=-35:TP=-9:LRA=8,aresample=48000,"
        f"afade=t=in:st=0:d=2,afade=t=out:st={fade_at:.3f}:d=2[b];"
        "[n][b]amix=inputs=2:duration=first:normalize=0:dropout_transition=0,aresample=48000[a]"
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(narration), "-stream_loop", "-1", "-i", str(BGM),
            "-filter_complex", filt, "-map", "[a]", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "1", str(dest),
        ],
        check=True,
    )


def render_video(story, timeline) -> Path:
    phrases = story["phrases"]
    scenes = timeline["scenes"]
    duration = timeline["duration"]
    folder = BUILD / story["id"]
    mixed = folder / "mixed.m4a"
    mix_bgm(folder / "narration.wav", duration, mixed)
    out = OUT / f"{story['slug']}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "pipe:0",
        "-i", str(mixed),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-profile:v", "high", "-crf", "18",
        "-preset", "veryfast", "-c:a", "copy",
        "-movflags", "+faststart", str(out),
    ]
    err_path = folder / "ffmpeg.log"
    err_file = open(err_path, "w")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=err_file)
    nframes = int(round(duration * FPS))
    prev_art = None
    assert proc.stdin is not None
    try:
        for frame_i in range(nframes):
            t = frame_i / FPS
            scene_i = 0
            for i, scene in enumerate(scenes):
                if scene["vis_start"] <= t:
                    scene_i = i
            scene = scenes[scene_i]
            local = t - scene["vis_start"]
            span = max(0.05, scene["vis_end"] - scene["vis_start"])
            progress = min(1.0, max(0.0, local / span))
            art = render_art(phrases[scene["index"]], progress)
            shown = art
            if scene["trans"] == "fade" and local < 0.30 and prev_art is not None:
                alpha = local / 0.30
                shown = ((1 - alpha) * prev_art + alpha * art).astype(np.uint8)
            if t < 0.30:
                shown = (shown.astype(np.float32) * (t / 0.30)).astype(np.uint8)
            lines = list(phrases[scene["index"]]["sub"]) if t + 1e-6 >= scene["start"] else None
            frame = draw_subtitle(shown, lines)
            try:
                proc.stdin.write(frame.tobytes())
            except BrokenPipeError:
                break
            if frame_i + 1 >= nframes or (frame_i + 1) / FPS >= scene["vis_end"] - 1e-4:
                prev_art = art
            if frame_i % 300 == 0:
                print(f"  {story['id']} {frame_i / nframes * 100:.0f}%", flush=True)
    finally:
        try:
            proc.stdin.close()
        except BrokenPipeError:
            pass
        code = proc.wait()
        err_file.close()
    if code != 0:
        err = err_path.read_text(errors="replace")
        raise RuntimeError(err[-2000:])
    print(f"  wrote {out}")
    return out


def _fmt(t: float) -> str:
    return f"{t:.1f}"


def _people(phrase) -> str:
    bits = []
    for _fid, pos, face, pose in phrase["figs"]:
        bits.append(f"{POS_JA[pos]}・{FACE_JA[face]}・{POSE_JA[pose]}")
    return " ／ ".join(bits)


def _move(phrase) -> str:
    action = phrase["action"]
    if not action or action[1] == "still":
        return "静止"
    kind = action[1]
    if kind == "head":
        return "顔をゆっくり上げる" if action[2] < 0 else "顔をゆっくり下げる"
    if kind == "to":
        return f"姿勢を{POSE_JA[action[2]]}へ変える"
    if kind == "arm":
        return "腕を一度だけ上げて下ろす"
    if kind == "walk":
        return "前へ小さく一歩" if action[2] > 0 else "後ろへ小さく一歩"
    return "記号だけが動く"


def _symbols(phrase) -> str:
    if not phrase["syms"]:
        return "なし"
    names = []
    for sym in phrase["syms"]:
        names.append(SYM_JA.get(sym.split(":")[0], sym))
    return "、".join(names)


def _english(phrase) -> str:
    bits = []
    for _fid, pos, face, pose in phrase["figs"]:
        way = "facing right" if face == 1 else "facing left"
        bits.append(f"a white stick figure {POS_EN[pos]}, {way}, {POSE_EN[pose]}")
    subject = " and ".join(bits)
    action = phrase["action"]
    if action and action[1] == "head":
        motion = "slowly raises the head" if action[2] < 0 else "slowly lowers the head"
    elif action and action[1] == "to":
        motion = f"slowly changes posture until {POSE_EN[action[2]]}"
    elif action and action[1] == "arm":
        motion = "lifts one arm once and lowers it"
    elif action and action[1] == "walk":
        motion = "takes one small step"
    else:
        motion = "holds still while a symbol shifts"
    symbols = _symbols(phrase)
    red = RED_JA[phrase["red"]]
    return (
        f"{subject.capitalize()}, {motion}; white symbols: {symbols}; red accent: {red}; "
        "static camera, limited animation, no text."
    )


def write_docs(story, timeline) -> Path:
    phrases = story["phrases"]
    scenes = timeline["scenes"]
    duration = timeline["duration"]
    groups = sentences_of(phrases)
    lines = []
    a = lines.append
    a(f"# {story['title']}")
    a("")
    a(f"尺の実測: {duration:.1f}秒（30fps、1080×1920）")
    a(f"原稿の文字数: {len(manuscript(phrases))}文字")
    a("")
    a("## A. 作品の核")
    a("")
    a(f"主題（投稿タイトル）: 「{story['title']}」")
    a("")
    a(f"赤で表すもの: {story['red_label']}。{story['red_meaning']}。")
    a("")
    a("この作品で使う象徴:")
    for mark, meaning in story["symbols"]:
        a(f"- {mark}: {meaning}")
    a("")
    a("## B. ナレーション原稿")
    a("")
    a("### B-1 全文")
    a("")
    text = manuscript(phrases)
    pretty = text.replace("。", "。\n")
    a(pretty.strip())
    a("")
    a("### B-2 フレーズごとの時間")
    a("")
    a("字幕は、そのフレーズの声が始まる瞬間に出て、次のフレーズが始まる瞬間に消えます。")
    a("")
    for scene in scenes:
        phrase = phrases[scene["index"]]
        sub = "／".join(phrase["sub"])
        a(f"- {_fmt(scene['start'])}秒〜{_fmt(scene['end'])}秒　{phrase['show']}　字幕「{sub}」")
    a("")
    a("### B-3 音声合成用の読み原稿")
    a("")
    a("声に出す文です。読み誤りやすい語はひらがなにしてあります。（間）は0.4秒ほど、（長い間）は幕の変わり目で1.5秒です。")
    a("")
    chunks = []
    for i, phrase in enumerate(phrases):
        say = phrase["say"].replace("、", "、（間）")
        if say.endswith("。") or say.endswith("？"):
            mark = "。（間）"
            nxt = phrases[i + 1]["act"] if i + 1 < len(phrases) else None
            if nxt is not None and nxt != phrase["act"]:
                mark = "。（長い間）"
            say = say[:-1] + mark
        chunks.append(say)
    a("".join(chunks))
    a("")
    a("## C. 絵コンテ")
    a("")
    a("| 時間 | 字幕 | 人物と配置 | 動き | 記号 | 赤 | 切替 |")
    a("| --- | --- | --- | --- | --- | --- | --- |")
    for scene in scenes:
        phrase = phrases[scene["index"]]
        sub = "／".join(phrase["sub"])
        switch = "カット" if scene["trans"] == "cut" else "0.3秒のフェード"
        a(
            f"| {_fmt(scene['start'])}〜{_fmt(scene['end'])}秒 | {sub} | {_people(phrase)} | {_move(phrase)} | {_symbols(phrase)} | {RED_JA[phrase['red']]} | {switch} |"
        )
    a("")
    a("## D. 映像生成AI向けプロンプト")
    a("")
    a("### D-1 全シーン共通")
    a("")
    a(
        "minimalist white stick figure line art on pure black background, single thin hand-drawn "
        "horizontal ground line at 62% height, only one red accent element, static camera, "
        "limited animation, no text. Vertical 9:16, 1080x1920, 30fps. Background is pure black "
        "#000000 with no gradient, texture, stars, or scenery. The stick figure is about 8.6% of "
        "the frame height: hollow circular head, one torso line, two-segment arms and legs, no face, "
        "line width about 0.3% of the frame width. Emotion is shown only by posture. At most one "
        "small action per shot. The only non-white color is red #E0202A, used for a single thematic "
        "accent, at most one or two marks in a shot. Cuts, or a 0.3 second fade. No zoom, pan, "
        "shake, 3D, particles, glow, logos, or subtitles inside the generated picture."
    )
    a("")
    a("### D-2 シーンごと")
    a("")
    for scene in scenes:
        phrase = phrases[scene["index"]]
        a(f"{_fmt(scene['start'])}秒: {_english(phrase)}")
        a("")
    a("### D-3 ネガティブプロンプト")
    a("")
    a(
        "color, gradient, realistic, 3D, shading, face details, camera movement, text, watermark, "
        "background objects, particles, glow, zoom, pan, motion blur, stars, scenery, multiple red colors"
    )
    a("")
    a("## E. 音声合成の設定")
    a("")
    a("声の方向: 低めから中くらい。ささやく直前のやわらかさ。寝る前に聴いても疲れない声。感情は乗せすぎない。文の終わりは静かに下げる。問いかけも、軽く上げるだけ。強調したい語は大きくせず、わずかに遅くする。")
    a("")
    a("今回の動画で実際に使った声は、マイクロソフトの日本語音声（七海）です。速さはふだんの約0.78倍、冒頭と最後の一文はさらに約1割遅くしています。音の高さは少しだけ下げています。")
    a("")
    a("ElevenLabs で作る場合の目安:")
    a("- 安定性（Stability）: 75。感情の振れを抑える")
    a("- 似せ度（Similarity）: 70")
    a("- スタイルの強さ（Style）: 10。演技を足さない")
    a("- 速さ: 0.86。冒頭と最後の一文は 0.77")
    a("- 声の高さ: 少し低めの落ち着いたナレーター")
    a("")
    a("VOICEVOX で作る場合の目安:")
    a("- 話者: 白上虎太郎（ふだん）。低すぎる実況声にはしない")
    a("- 話速: 0.86。冒頭と最後の一文は 0.77")
    a("- 音高: -0.03")
    a("- 抑揚: 0.70")
    a("- 音量: 1.0")
    a("- 読点のあと 0.4秒、句点のあと 0.9秒、幕の変わり目は 1.5秒の無音を別に入れる")
    a("")
    a("Google TTS で作る場合の目安:")
    a("- 声: ja-JP-Neural2-C（やわらかめ）")
    a("- speakingRate: 0.86。冒頭と最後の一文は 0.77")
    a("- pitch: -2.0")
    a("- 読点と句点は、上と同じ無音をSSMLの break で入れる")
    a("")
    a("## F. 編集指示")
    a("")
    a(f"- 画面: 縦 1080×1920、30fps。今回の尺は {duration:.1f}秒")
    a(f"- 字幕の書体: Noto Sans CJK JP Bold。文字の高さは約{CHAR_H:.0f}px（画面の幅の約7%）")
    a("- 字幕に縁取り、影、帯はつけない。色は白だけ")
    a("- 1行のときは、その行の中心が画面の上から30%の位置。2行のときは、2行をまとめた中心が同じ位置")
    a("- 2行のとき、行の間隔（次の行までの高さ）は文字の高さの1.4倍")
    a("- 1行は10文字以内。句読点は字幕に入れない")
    a("- 字幕は、そのフレーズの声と同時に出し、次のフレーズと同時に切り替える")
    a("- 場面が続くときは0.3秒のフェード。人が増える、場所が変わる、幕が変わるときはカット")
    a("- ナレーションの音量を基準に、BGMはおよそ19dB小さくする（かなり小さく、声の下に敷く）")
    a("- BGMは最初の2秒でフェードイン、最後の2秒でフェードアウト。効果音は入れない")
    a("- BGM: ながれぼし／もっぴーさうんど（フリーBGM OpenTracks、旧DOVA-SYNDROME）")
    a("- 画面にロゴ、クレジット、字幕以外の文字は出さない")
    a("")
    a("## G. 投稿用テキスト")
    a("")
    a(f"「{story['closing']}」")
    a("")
    a(f"#人生 #エッセイ {story['hashtag']}")
    a("")
    DOCS.mkdir(parents=True, exist_ok=True)
    path = DOCS / f"{story['id']}_{story['title']}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  docs {path.name}")
    return path


def load_timeline(story) -> dict:
    return json.loads((BUILD / story["id"] / "timeline.json").read_text(encoding="utf-8"))


def main():
    import sys

    errs = validate()
    if errs:
        for err in errs:
            print(err)
        raise SystemExit(1)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    chosen = sys.argv[2] if len(sys.argv) > 2 else None
    stories = [s for s in STORIES if chosen in (None, s["id"], s["id"].lstrip("0"))]
    if cmd in ("audio", "all"):
        async def run():
            for story in stories:
                print("audio", story["id"], flush=True)
                await build_audio(story)
        asyncio.run(run())
    if cmd in ("render", "all"):
        for story in stories:
            print("render", story["id"], flush=True)
            render_video(story, load_timeline(story))
    if cmd in ("docs", "all"):
        for story in stories:
            write_docs(story, load_timeline(story))


if __name__ == "__main__":
    main()
