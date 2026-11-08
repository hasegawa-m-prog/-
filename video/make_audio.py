#!/usr/bin/env python3
"""Synthesize narration with VOICEVOX 青山龍星 and build a timeline."""

import json
import urllib.parse
import urllib.request
import wave
from pathlib import Path

BASE = "http://127.0.0.1:50021"
OUT = Path(__file__).resolve().parent / "build"
SPEAKER = 13  # 青山龍星 ノーマル
SPEED = 1.05
PITCH = -0.02
INTONATION = 0.9
LEAD = 0.55
TAIL = 1.15

# Plain text is spoken. 《 》 marks words that are red in the subtitles.
MARKED = [
    "お化け屋敷を出た瞬間、隣の人がやけに《素敵》に見えました。",
    "心臓はまだ、どくどくと鳴っています。",
    "さっきまでは、ただの友達だったはずです。",
    "なぜ怖い体験のあとは、相手が《魅力的》に見えるのだろうか？",
    "実は、心臓の高鳴りを、《恋》だと勘違いしているからです。",
    "一九七四年、心理学者のダットンとアロンが、ある実験をしました。",
    "舞台はカナダの、高さ《七十メートル》の吊り橋です。",
    "幅は一・五メートルしかなく、歩くたびに揺れます。",
    "渡り終えた男性に、一人の女性が声をかけます。",
    "簡単な質問のあと、気になれば電話を、と番号を渡しました。",
    "比較のため、揺れない低い橋でも、同じことをしました。",
    "すると、吊り橋では番号を受け取った二十三人のうち、《九人》が電話をかけました。",
    "低い橋では、二十二人のうち、わずか《二人》でした。",
    "およそ《四割》と、一割です。",
    "怖さで高鳴った心臓を、恋のときめきと取り違えたのです。",
    "ただし、ドキドキは好意だけでなく、苦手な気持ちも《強める》そうです。",
    "お化け屋敷を出たあと、隣の人が素敵に見えたあの瞬間です。",
    "あなたの心臓は、まだ《怖さ》で鳴っていただけかもしれません。",
    "隣の人が輝いて見えたのは、恋ではなく、《恐怖の余韻》だったんです。",
    "あなたのそのドキドキは、本当に恋でしょうか？",
]

SCENE_OF = {
    1: 1, 2: 1, 3: 1,
    4: 2,
    5: 3,
    6: 4, 7: 4, 8: 4,
    9: 5, 10: 5, 11: 5,
    12: 6, 13: 6, 14: 6,
    15: 7, 16: 7,
    17: 8, 18: 8,
    19: 9, 20: 9,
}
# Paragraph ends (1-based sentence index) get a 0.8s pause. Others get 0.4s.
BLOCK_ENDS = {3, 4, 5, 11, 15, 16, 18}


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
        text = plain(marked)
        kana = synthesize(text, path)
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
    for i, entry in enumerate(entries):
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
        print(f"  scene {scene['id']}: {scene['start']:.2f}-{scene['end']:.2f} ({scene['end']-scene['start']:.2f}s)")


if __name__ == "__main__":
    main()
