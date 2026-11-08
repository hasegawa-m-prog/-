# -*- coding: utf-8 -*-
"""
ナレーション（edge-tts）→ 無音トリム → タイムライン作成 → BGM合成 → ミックス。
出力:
  out/tts/unit_XX.mp3      各フレーズの音声
  out/timeline.json        各 unit の開始/終了秒（render.py と共有）
  out/narration.wav        ナレーションのみ
  out/bgm.wav              BGMのみ
  out/mix.wav              最終音声（ナレーション + BGM）
"""
import asyncio
import json
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from script import UNITS  # noqa: E402

SR = 48000
VOICE = "ja-JP-KeitaNeural"
RATE_NORMAL = "-28%"    # 通常の読み上げの約0.85倍（実測で約4文字/秒になる値）
RATE_SLOW = "-35%"      # フック・最後の一文はさらに約1割ゆっくり
PITCH = "-6Hz"
LEAD_IN = 0.8           # 冒頭の無音（秒）
TAIL = 2.2              # 最後の余韻（秒）
BGM_DB_BELOW = -19.0    # ナレーションに対するBGMの音量差（dB）

OUT = os.path.join(os.path.dirname(__file__), "out")
TTS_DIR = os.path.join(OUT, "tts")
os.makedirs(TTS_DIR, exist_ok=True)


async def synth(unit):
    import edge_tts
    path = os.path.join(TTS_DIR, f"unit_{unit['id']:02d}.mp3")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return path
    rate = RATE_SLOW if unit.get("slow") else RATE_NORMAL
    com = edge_tts.Communicate(unit["tts"], VOICE, rate=rate, pitch=PITCH)
    await com.save(path)
    return path


def load_mono(path):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def trim(x, thresh_db=-42.0, pad=0.06):
    thr = 10 ** (thresh_db / 20)
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(x), idx[-1] + int(pad * SR))
    y = x[a:b].copy()
    # クリックを避けるため両端に短いフェード
    n = int(0.01 * SR)
    y[:n] *= np.linspace(0, 1, n)
    y[-n:] *= np.linspace(1, 0, n)
    return y


def write_wav(path, x):
    import wave
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


# ---------------- BGM: 静かなパッド + まばらなピアノ風の単音 ----------------
def pad_note(freq, dur, amp):
    t = np.arange(int(dur * SR)) / SR
    # わずかにデチューンした正弦波を重ねて厚みを出す（歌声なし、ノイズなし）
    sig = np.zeros_like(t)
    for d, a in ((1.0, 1.0), (1.003, 0.5), (0.997, 0.5), (2.0, 0.15), (3.0, 0.05)):
        sig += a * np.sin(2 * np.pi * freq * d * t)
    # ゆっくりしたうねり
    sig *= 1 + 0.08 * np.sin(2 * np.pi * 0.11 * t)
    # 長いアタック・リリース
    env = np.ones_like(t)
    atk = int(min(2.5, dur / 3) * SR)
    rel = int(min(3.0, dur / 3) * SR)
    env[:atk] = np.linspace(0, 1, atk) ** 2
    env[-rel:] *= np.linspace(1, 0, rel) ** 2
    return amp * sig * env


def piano_note(freq, dur, amp):
    t = np.arange(int(dur * SR)) / SR
    sig = (np.sin(2 * np.pi * freq * t)
           + 0.35 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-3 * t)
           + 0.12 * np.sin(2 * np.pi * 3 * freq * t) * np.exp(-5 * t))
    env = np.exp(-1.6 * t) * (1 - np.exp(-200 * t))
    return amp * sig * env


def make_bgm(total):
    n = int(total * SR)
    bgm = np.zeros(n)
    # コード進行（Am → F → C → G/B 系を低めで、8秒ごと）
    chords = [
        (110.00, 164.81, 220.00, 261.63),   # A2 E3 A3 C4   (Am)
        (87.31, 130.81, 174.61, 261.63),    # F2 C3 F3 C4   (F)
        (98.00, 130.81, 196.00, 246.94),    # G2 C3 G3 B3   (Cadd9/G)
        (82.41, 123.47, 164.81, 246.94),    # E2 B2 E3 B3   (Em)
    ]
    seg = 8.0
    t0 = 0.0
    i = 0
    while t0 < total:
        ch = chords[i % len(chords)]
        dur = min(seg + 2.0, total - t0)  # 次のコードと少し重ねる
        a = int(t0 * SR)
        for k, f in enumerate(ch):
            note = pad_note(f, dur, 0.22 if k == 0 else 0.14)
            b = min(n, a + len(note))
            bgm[a:b] += note[: b - a]
        t0 += seg
        i += 1
    # まばらな単音（ピアノ風）。高めの音を、間をあけて。
    rng = np.random.default_rng(7)
    melody_pool = [440.0, 493.88, 523.25, 587.33, 659.25, 783.99]
    t = 3.0
    while t < total - 4:
        f = melody_pool[rng.integers(len(melody_pool))]
        note = piano_note(f, 5.0, 0.16)
        a = int(t * SR)
        b = min(n, a + len(note))
        bgm[a:b] += note[: b - a]
        t += float(rng.uniform(4.5, 7.5))
    # 2秒フェードイン・2秒フェードアウト
    fi = int(2.0 * SR)
    bgm[:fi] *= np.linspace(0, 1, fi)
    bgm[-fi:] *= np.linspace(1, 0, fi)
    return bgm


def main():
    async def synth_all():
        # 同時接続を抑えるため順番に合成する
        return [await synth(u) for u in UNITS]

    paths = asyncio.run(synth_all())
    clips = [trim(load_mono(p)) for p in paths]

    # 音量をそろえる（各クリップのRMSを基準値へ）
    target = -22.0
    clips = [c * (10 ** ((target - rms_db(c)) / 20)) for c in clips]

    timeline = []
    cursor = LEAD_IN
    for u, c in zip(UNITS, clips):
        dur = len(c) / SR
        timeline.append(dict(id=u["id"], act=u["act"], start=round(cursor, 3), end=round(cursor + dur, 3),
                             sub=u["sub"], scene=u["scene"], act_break=bool(u.get("act_break")),
                             pause=u["pause"], text=u["text"]))
        cursor += dur + u["pause"]
    total = cursor + TAIL

    n = int(total * SR)
    narr = np.zeros(n)
    for tl, c in zip(timeline, clips):
        a = int(tl["start"] * SR)
        narr[a:a + len(c)] += c
    # ピークが -1.5dBFS を超えないようにそろえる
    narr *= min(1.0, 10 ** (-1.5 / 20) / (np.max(np.abs(narr)) + 1e-9))

    bgm = make_bgm(total)
    speech_mask = np.abs(narr) > 0.005
    narr_rms = rms_db(narr[speech_mask])
    bgm *= 10 ** ((narr_rms + BGM_DB_BELOW - rms_db(bgm)) / 20)

    mix = narr + bgm
    peak = np.max(np.abs(mix))
    if peak > 0.98:
        mix *= 0.98 / peak

    write_wav(os.path.join(OUT, "narration.wav"), narr)
    write_wav(os.path.join(OUT, "bgm.wav"), bgm)
    write_wav(os.path.join(OUT, "mix.wav"), mix)
    with open(os.path.join(OUT, "timeline.json"), "w", encoding="utf-8") as f:
        json.dump(dict(total=round(total, 3), fps=30, units=timeline), f, ensure_ascii=False, indent=1)

    print(f"total = {total:.2f}s  narration RMS(speech) = {narr_rms:.1f} dB  BGM RMS = {rms_db(bgm):.1f} dB")
    for tl in timeline:
        print(f"{tl['id']:2d} {tl['start']:6.2f}-{tl['end']:6.2f} ({tl['end']-tl['start']:.2f}s) {tl['text']}")


if __name__ == "__main__":
    main()
