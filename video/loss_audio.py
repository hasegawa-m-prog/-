#!/usr/bin/env python3
"""ナレーション（VOICEVOX 青山龍星）とシーンの時間表を作る。"""

import json
import urllib.parse
import urllib.request
import wave
from pathlib import Path

BASE = "http://127.0.0.1:50021"
OUT = Path(__file__).resolve().parent / "build" / "loss"
SPEAKER = 13  # 青山龍星 ノーマル
SPEED = 1.05
PITCH = -0.02
INTONATION = 0.9
LEAD = 0.55
TAIL = 1.15

# 《 》で囲んだ語は字幕で赤くする。読み上げからは外す。
MARKED = [
    "帰り道に、《千円札》を落としました。",
    "胸の奥が、すっと重くなります。",
    "翌日、同じ千円を拾っても、昨日ほど揺れません。",
    "なぜ、失う痛みは、得る喜びの《二倍》なのでしょうか。",
    "実は、同じ額でも、失うほうを《二点二五倍》、重く見ているからです。",
    "カーネマンとトベルスキーが、損と得の重さを比べました。",
    "一九七九年、経済誌エコノメトリカで、損は得より大きいと書きました。",
    "同じ額の五分五分を、多くの人は好みませんでした。",
    "一九九二年、五分五分では、得が損のおよそ《二倍》必要でした。",
    "真ん中の数字は、《二点二五倍》です。",
    "ある問いでは、《百》の損が、《二百二》の得と釣り合いました。",
    "その論文は、リスクと不確実性の雑誌に載っています。",
    "すると、拾った千円より、落とした千円のほうを大きく見てしまいます。",
    "ただし、《二点二五倍》は、賭けの答えから出した真ん中の目安です。",
    "帰り道、拾うより落とす《千円札》が胸に重いです。",
    "失うほうが重いのは、損を大きく見ていたからだったんです。",
    "なくした千円と得た千円は、同じ重さでしょうか。",
]

WRAPS = [
    ["帰り道に、", "《千円札》を落としました。"],
    ["胸の奥が、", "すっと重くなります。"],
    ["翌日、同じ千円を", "拾っても、昨日ほど", "揺れません。"],
    ["なぜ、失う痛みは、", "得る喜びの", "《二倍》なのでしょうか。"],
    ["実は、同じ額でも、", "失うほうを", "《二点二五倍》、", "重く見ているからです。"],
    ["カーネマンと", "トベルスキーが、", "損と得の重さを比べました。"],
    ["一九七九年、", "経済誌エコノメトリカで、", "損は得より大きいと", "書きました。"],
    ["同じ額の五分五分を、", "多くの人は", "好みませんでした。"],
    ["一九九二年、", "五分五分では、", "得が損のおよそ", "《二倍》必要でした。"],
    ["真ん中の数字は、", "《二点二五倍》です。"],
    ["ある問いでは、", "《百》の損が、", "《二百二》の得と", "釣り合いました。"],
    ["その論文は、リスクと", "不確実性の雑誌に", "載っています。"],
    ["すると、拾った千円より、", "落とした千円のほうを", "大きく見てしまいます。"],
    ["ただし、", "《二点二五倍》は、", "賭けの答えから出した", "真ん中の目安です。"],
    ["帰り道、", "拾うより落とす", "《千円札》が胸に重いです。"],
    ["失うほうが重いのは、", "損を大きく見ていた", "からだったんです。"],
    ["なくした千円と", "得た千円は、", "同じ重さでしょうか。"],
]

SCENE_OF = {
    1: 1, 2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5, 7: 5,
    8: 6, 9: 6, 10: 6,
    11: 7, 12: 7,
    13: 8, 14: 8,
    15: 9, 16: 9, 17: 9,
}
BLOCK_ENDS = {3, 4, 5, 12, 13, 14, 15, 17}


def plain(marked: str) -> str:
    return marked.replace("《", "").replace("》", "")


def post(url: str, body: bytes | None, content_type: str | None = None) -> bytes:
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=body if body is not None else b"", method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=180) as res:
        return res.read()


def audio_query(text: str) -> dict:
    url = BASE + "/audio_query?" + urllib.parse.urlencode({"text": text, "speaker": SPEAKER})
    return json.loads(post(url, b""))


def reading_of(query: dict) -> str:
    parts = []
    for phrase in query["accent_phrases"]:
        parts.append("".join(m["text"] for m in phrase["moras"]))
    return " | ".join(parts)


def synthesize(text: str, path: Path) -> str:
    query = audio_query(text)
    query["speedScale"] = SPEED
    query["pitchScale"] = PITCH
    query["intonationScale"] = INTONATION
    query["prePhonemeLength"] = 0.06
    query["postPhonemeLength"] = 0.10
    url = f"{BASE}/synthesis?speaker={SPEAKER}"
    wav = post(url, json.dumps(query).encode(), "application/json")
    path.write_bytes(wav)
    return reading_of(query)


def wav_info(path: Path):
    with wave.open(str(path), "rb") as w:
        return w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes(), w.readframes(w.getnframes())


def main() -> None:
    lines = OUT / "lines"
    lines.mkdir(parents=True, exist_ok=True)
    durations = []
    readings = []
    for i, marked in enumerate(MARKED, 1):
        path = lines / f"{i:02d}.wav"
        kana = synthesize(plain(marked), path)
        ch, sw, rate, n, _ = wav_info(path)
        dur = n / rate
        durations.append(dur)
        readings.append(kana)
        print(f"{i:02d} {dur:5.2f}s  {kana}")

    ch, sw, rate, _, _ = wav_info(lines / "01.wav")
    frame_bytes = ch * sw

    def silence(seconds: float) -> bytes:
        n = int(round(seconds * rate))
        return b"\x00" * n * frame_bytes

    entries = []
    t = LEAD
    for i, marked in enumerate(MARKED, 1):
        dur = durations[i - 1]
        pause = 0.0 if i == len(MARKED) else (0.8 if i in BLOCK_ENDS else 0.4)
        entries.append({
            "i": i,
            "scene": SCENE_OF[i],
            "start": round(t, 3),
            "end": round(t + dur, 3),
            "marked": marked,
            "pause_after": pause,
        })
        t += dur + pause

    duration = t + TAIL
    scenes = []
    for scene_id in range(1, 10):
        segs = [e for e in entries if e["scene"] == scene_id]
        speech_start = segs[0]["start"]
        if scene_id == 1:
            start = 0.0
        else:
            prev = [e for e in entries if e["scene"] == scene_id - 1][-1]
            start = (prev["end"] + speech_start) / 2
        scenes.append({"id": scene_id, "start": round(start, 3)})
    for i, scene in enumerate(scenes):
        scene["end"] = round(scenes[i + 1]["start"] if i < len(scenes) - 1 else duration, 3)

    for i, entry in enumerate(entries):
        scene_end = next(s["end"] for s in scenes if s["id"] == entry["scene"])
        nxt = entries[i + 1]["start"] if i < len(entries) - 1 else duration
        entry["hold"] = round(min(nxt, scene_end), 3)

    pcm = bytearray()
    pcm += silence(LEAD)
    for entry in entries:
        _, _, _, _, frames = wav_info(lines / f"{entry['i']:02d}.wav")
        pcm += frames
        if entry["pause_after"]:
            pcm += silence(entry["pause_after"])
    pcm += silence(TAIL)

    narration = OUT / "narration.wav"
    with wave.open(str(narration), "wb") as w:
        w.setnchannels(ch)
        w.setsampwidth(sw)
        w.setframerate(rate)
        w.writeframes(pcm)

    timeline = {
        "duration": round(duration, 3),
        "sample_rate": rate,
        "voice": "VOICEVOX 青山龍星 ノーマル",
        "speedScale": SPEED,
        "pitchScale": PITCH,
        "intonationScale": INTONATION,
        "scenes": scenes,
        "subs": [
            {"start": e["start"], "hold": e["hold"], "marked": e["marked"], "scene": e["scene"]}
            for e in entries
        ],
        "readings": readings,
    }
    (OUT / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nTOTAL {duration:.2f}s  -> {narration}")
    for scene in scenes:
        print(f"  scene {scene['id']}: {scene['start']:.2f}-{scene['end']:.2f} ({scene['end'] - scene['start']:.2f}s)")


if __name__ == "__main__":
    main()
