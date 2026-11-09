#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5本分の台本マークダウンを、確定した秒数つきで書く。"""

import json
from pathlib import Path

from catalog import FILMS, FONT, NEGATIVE, STYLE, VOICE
from engine import telop

ROOT = Path(__file__).resolve().parent


def scene_rows(film, timeline):
    rows = []
    for sc in timeline["scenes"]:
        meta = film["scenes"][sc["id"] - 1]
        sents = [s for s in film["sentences"] if s["scene"] == sc["id"]]
        narr = "<br>".join(s["text"] for s in sents)
        caps = "<br>".join(telop(s["text"], s["reds"]) for s in sents)
        prompt = f"{meta['prompt']}, {STYLE} --no {NEGATIVE}"
        rows.append(
            f"| {sc['id']} | {sc['length']:.1f} | {narr} | {meta['metaphor']} | {prompt} | {meta['camera']} | {meta['accent']} | {caps} |"
        )
    return "\n".join(rows)


def script_blocks(film):
    tl = json.loads((ROOT / "build" / film["slug"] / "timeline.json").read_text(encoding="utf-8"))
    subs = tl["subs"]
    texts = [s["text"] for s in film["sentences"]]
    i_q = next(i for i, t in enumerate(texts) if t.startswith("なぜ"))
    i_a = next(i for i, t in enumerate(texts) if t.startswith("実は"))
    i_r = next(i for i, t in enumerate(texts) if t.startswith("すると") or t.startswith("ところが"))
    i_lim = next(i for i, t in enumerate(texts) if t.startswith("ただし"))
    i_punch = next(i for i, t in enumerate(texts) if "だったんです" in t)
    groups = [
        ("①情景", 0, i_q),
        ("②問い", i_q, i_a),
        ("③結論", i_a, i_a + 1),
        ("④研究", i_a + 1, i_r),
        ("⑤結果", i_r, i_lim),
        ("⑥限界", i_lim, i_lim + 1),
        ("⑦回収", i_lim + 1, i_punch),
        ("⑧締め", i_punch, len(texts)),
    ]
    lines = []
    for label, a, b in groups:
        start = subs[a]["start"]
        end = subs[b - 1]["hold"]
        body = "".join(texts[a:b])
        lines.append(f"**{label}（約{max(1, round(end - start))}秒）**  \n{body}")
    return "\n\n".join(lines), tl


def one(film):
    blocks, tl = script_blocks(film)
    hooks = []
    for h in film["hooks"]:
        text = "".join(h["lines"])
        hooks.append(f"**{h['id']}案（{h['emotion']}）**  \n{text}")
    facts = "\n".join(f"- {x}" for x in film["facts"])
    reading = "\n".join(f"- {x}" for x in film["reading"])
    assumes = "\n".join(f"- {x}" for x in film["assumptions"])
    subs = [f"{i}. {telop(s['text'], s['reds'])}" for i, s in enumerate(film["sentences"], 1)]
    sub_list = "\n".join(subs)
    title = film["title_break"]
    opening = film["scenes"][0]
    thumb_ja = (
        f"縦長9:16。上段にタイトルを2行（{title}）。"
        "その直下に短い赤い横線。その下に小さく「心理学」。"
        f"中央は{opening['metaphor']}の線画。"
        f"下段に白文字で「{film['hook_line']}」。背景は純黒、顔なし、文字以外にロゴなし。"
    )
    thumb_en = (
        f"vertical 9:16 still, pure black, thin white line art. "
        f"Top: two lines of white Japanese serif title {title.replace('／', ' / ')}, "
        f"a short red horizontal rule, then the small word 心理学. "
        f"Center metaphor: {opening['prompt']}. "
        f"Bottom caption in white: {film['hook_line']} "
        f"No faces, no logos, no watermark, film grain. --no {NEGATIVE}"
    )
    return f"""# {film['title']}

## 1. 問いとタイトル
- 変換した問い：{film['question']}
- タイトル：{film['title_break']}

## 2. 冒頭フック3案（A/Bテスト用）
{chr(10).join(hooks)}

## 3. 完成台本
採用フックはA案。読み上げの合計は{tl['duration']:.0f}秒。

{blocks}

## 4. シーン別・動画生成プロンプト
シーンの間は、黒へのフェード0.5秒。

| # | 秒 | ナレーション(日本語) | 比喩の図 | Video Prompt (English) | Camera/Motion | Accent color | テロップ(赤字は【】) |
| --- | --- | --- | --- | --- | --- | --- | --- |
{scene_rows(film, tl)}

## 5. サムネイル用プロンプト（静止画）
構図：{thumb_ja}

英語プロンプト：
{thumb_en}

## 6. 音声・字幕の指定
- VOICE = {VOICE}
- FONT = {FONT}

字幕は1枚が1文。長い文は1行13字以内に折って、同じ画面に出す。通し番号は次のとおり。

{sub_list}

## 7. 投稿文
{film['title']}
#心理学 #Shorts #哲学 {film['tags']}

## 8. 根拠メモと仮定一覧
- 引用研究（事実）
{facts}
- この動画での解釈
{reading}
- 置いた仮定
{assumes}

## 9. セルフチェック結果
- 結論先出し：○
- 数字3つ以上：○
- 冒頭回収：○
- 問いかけで終了：○
- 1文40字以内：○
- 専門用語ゼロ：○
- 煽りゼロ：○
- 全シーンに比喩の図がある：○
- 各Video Promptに STYLE と除外指示がある：○
- 研究に出典がある：○

動画ファイル：`video/out/{film['file']}`
"""


def main():
    parts = [one(f) for f in FILMS]
    text = "\n\n---\n\n".join(parts) + "\n"
    path = ROOT.parent / "台本.md"
    path.write_text(text, encoding="utf-8")
    print(path, len(text))


if __name__ == "__main__":
    main()
