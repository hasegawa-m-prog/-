# 「頑張れなかった日は、さぼった日じゃなくて、休めた日」

黒背景 × 白い棒人間 × 赤一点 の哲学エッセイ系ショート動画（TikTok / Reels / Shorts 向け）。
テーマ：**頑張れない日の自分を、どう扱えばいいか**

| 項目 | 値 |
| --- | --- |
| 完成動画 | `site/video.mp4`（1080×1920 / 30fps / H.264 + AAC / 82.8秒 / 約2.7MB） |
| 配布ページ | `site/index.html`（スマホからそのまま再生・ダウンロードできる1枚ページ） |
| 制作スクリプト | `build/`（`script.py` 脚本データ → `make_audio.py` 音声 → `render.py` 映像） |

再生成するには（Python 3.12 / ffmpeg が必要）:

```bash
pip install -r build/requirements.txt
cd build && python3 make_audio.py && python3 render.py   # → build/out/final.mp4
```

---

## A. 作品の核

- **主題（投稿タイトル用）**：「頑張れなかった日は、さぼった日じゃなくて、休めた日」
- **赤で表すもの（1種類）**：**胸の奥の、小さな赤い点＝「何もできなかった自分を責める痛み」**
  - ②の終わり（37.7秒）で胸に現れ、③の間ずっと残り、④で手を当てられて小さくなる。消しはしない（許す＝なかったことにする、ではないため）
- **この作品で使う象徴記号と意味**

| 記号 | 意味 | 使う場面 |
| --- | --- | --- |
| ？（頭の右上） | 自分に「おつかれさま」と言えるか、という問い | ①フック |
| 楕円の吹き出し（中に歩く小さな棒人間） | 「朝から動くはずだった自分」＝思い描いていた理想 | ②現実 |
| ♪（通り過ぎる人の頭上） | まわりの人の無自覚さ・のんきさ | ②現実 |
| 二人の間の点線 | 進んでいく人たちと、止まっている自分との距離 | ②現実 |
| 放射状の短線（頭のまわり） | 自分だけ止まっている焦り | ②現実 |
| 人物を覆うアーチ | 「体が止めてくれた」＝体があなたを守っている | ③転換 |
| 小さな点の散り（胸から外へ） | 許したときに、少しだけほどける気持ち | ④着地 |
| 小さな太陽（右・地平線の少し上） | 明日、という希望。立ち上がらせはしない | ④着地 |

---

## B. ナレーション原稿

### B-1 全文（304文字・句読点込み）

今日、何もできなかったあなたへ。それでも、自分に、おつかれさまと言えますか。

本当は、朝から動くつもりだった。でも、体が起きなくて、気づいたら夕方になっていた。まわりの人は、今日も当たり前みたいに進んでいく。私たちは、その背中を見ながら、自分だけ止まっている気がして、胸の奥が、きゅっと痛くなる。

だから、思うんです。頑張れなかった日は、さぼった日じゃなくて、もう動けなかった日なんだ。あなたが止まったんじゃなくて、体が、止めてくれたのかもしれない。

それは、負けたというより、ちゃんと休めた、ってことなんだと思う。何もできなかった日を、そっと許すこと。それが、自分を大切にする、いちばん静かな形なのかもしれない。

### B-2 フレーズごとのタイムコード（完成動画の実測値）

| # | 幕 | 開始〜終了（発声） | フレーズ |
| --- | --- | --- | --- |
| 1 | ① | 0.8〜3.6 | 今日、何もできなかった |
| 2 | ① | 3.9〜4.7 | あなたへ。 |
| 3 | ① | 5.9〜8.2 | それでも、自分に、 |
| 4 | ① | 8.5〜11.4 | おつかれさまと言えますか。 |
| – | – | 11.4〜12.9 | （長い間・暗転） |
| 5 | ② | 12.9〜16.4 | 本当は、朝から動くつもりだった。 |
| 6 | ② | 17.3〜19.8 | でも、体が起きなくて、 |
| 7 | ② | 20.1〜23.1 | 気づいたら夕方になっていた。 |
| 8 | ② | 24.0〜26.3 | まわりの人は、今日も |
| 9 | ② | 26.6〜29.6 | 当たり前みたいに進んでいく。 |
| 10 | ② | 30.5〜33.8 | 私たちは、その背中を見ながら、 |
| 11 | ② | 34.1〜37.3 | 自分だけ止まっている気がして、 |
| 12 | ② | 37.7〜41.0 | 胸の奥が、きゅっと痛くなる。 |
| – | – | 41.0〜42.5 | （長い間・暗転） |
| 13 | ③ | 42.5〜44.6 | だから、思うんです。 |
| 14 | ③ | 45.5〜47.2 | 頑張れなかった日は、 |
| 15 | ③ | 47.6〜49.2 | さぼった日じゃなくて、 |
| 16 | ③ | 49.5〜52.2 | もう動けなかった日なんだ。 |
| 17 | ③ | 53.1〜55.8 | あなたが止まったんじゃなくて、 |
| 18 | ③ | 56.1〜59.4 | 体が、止めてくれたのかもしれない。 |
| – | – | 59.4〜60.9 | （長い間・暗転） |
| 19 | ④ | 60.9〜63.2 | それは、負けたというより、 |
| 20 | ④ | 63.6〜66.9 | ちゃんと休めた、ってことなんだと思う。 |
| 21 | ④ | 67.8〜69.6 | 何もできなかった日を、 |
| 22 | ④ | 70.0〜72.1 | そっと許すこと。 |
| 23 | ④ | 73.0〜76.2 | それが、自分を大切にする、 |
| 24 | ④ | 76.6〜80.6 | いちばん静かな形なのかもしれない。 |
| – | – | 80.6〜82.8 | （余韻・フェードアウト） |

### B-3 音声合成用の読み原稿

（間）＝0.3〜0.5秒、（句点の間）＝0.8〜1.0秒、（長い間）＝1.5秒の沈黙

```
きょう、（間）なにもできなかった（間）あなたへ。（句点の間）
それでも、（間）じぶんに、（間）おつかれさまと、（間）言えますか。
（長い間）
ほんとうは、（間）朝から動くつもりだった。（句点の間）
でも、（間）からだが起きなくて、（間）気づいたら、（間）夕方になっていた。（句点の間）
まわりの人は、（間）きょうも（間）あたりまえみたいに、（間）進んでいく。（句点の間）
わたしたちは、（間）そのせなかを見ながら、（間）じぶんだけ、（間）止まっている気がして、（間）
むねのおくが、（間）きゅっと、（間）いたくなる。
（長い間）
だから、（間）思うんです。（句点の間）
がんばれなかった日は、（間）さぼった日じゃなくて、（間）もう、（間）動けなかった日なんだ。（句点の間）
あなたが、（間）止まったんじゃなくて、（間）からだが、（間）止めてくれたのかもしれない。
（長い間）
それは、（間）まけたというより、（間）ちゃんと休めた、（間）ってことなんだと思う。（句点の間）
なにもできなかった日を、（間）そっと、（間）ゆるすこと。（句点の間）
それが、（間）じぶんをたいせつにする、（間）いちばん、（間）しずかなかたちなのかもしれない。
```

ひらがなに開いた語：今日→きょう／何も→なにも／自分→じぶん／本当は→ほんとうは／体→からだ／当たり前→あたりまえ／私たち→わたしたち／背中→せなか／胸の奥→むねのおく／痛く→いたく／頑張れ→がんばれ／負けた→まけた／許す→ゆるす／大切→たいせつ／静か→しずか／形→かたち

---

## C. 絵コンテ表

棒人間（主人公）は常に画面中央・右向き。地面は上端から62%の白い細線。

| 時間 | 字幕（／＝改行） | 画面内の人物と配置 | 動き（1アクション） | 記号 | 赤 | 切替 |
| --- | --- | --- | --- | --- | --- | --- |
| 0.0〜3.9 | 今日／何もできなかった | 中央・右向き・しゃがんで膝を抱え、頭を落としている | 呼吸のわずかな上下のみ | なし | なし | 冒頭0.6秒フェードイン |
| 3.9〜5.9 | あなたへ | 中央・しゃがみ | ゆっくり顔を上げる（1.4秒） | なし | なし | カット |
| 5.9〜8.5 | それでも／自分に | 中央・しゃがみ・顔は上げたまま | 静止 | ？が頭の右上に浮かぶ | なし | カット |
| 8.5〜11.9 | おつかれさまと／言えますか | 中央・しゃがみ | 静止 | ？ | なし | 0.3秒フェードアウト→黒 |
| 12.2〜17.3 | 本当は朝から／動くつもりだった | 中央・横たわる（頭が左）・片手は胸の上 | 吹き出しの中の小さな棒人間が歩く | 楕円の吹き出し（中に歩く小人） | なし | 0.3秒フェードイン |
| 17.3〜20.1 | でも体が／起きなくて | 中央・横たわる | 上体を少し起こしかけて、戻る | なし | なし | カット |
| 20.1〜24.0 | 気づいたら／夕方になっていた | 中央・横たわる | 胸の上の腕が地面に落ちる | なし | なし | カット |
| 24.0〜26.6 | まわりの人は／今日も | 主人公：中央・座って肩を落とす／右側：2人が右向きに歩く | 2人が右へ歩く | ♪（後ろの人の頭上） | なし | カット |
| 26.6〜30.5 | 当たり前みたいに／進んでいく | 同上 | 2人が右端へ抜けていく | ♪ | なし | 連続 |
| 30.5〜34.1 | 私たちは／その背中を見ながら | 中央・座る・顔を上げて右を見る | 顔を上げる→点線が右へ伸びる | 二人の間の点線（頭の高さ→右端） | なし | カット |
| 34.1〜37.7 | 自分だけ／止まっている気がして | 中央・座る | 静止 | 点線＋頭のまわりに放射状の短線 | なし | 連続 |
| 37.7〜41.5 | 胸の奥が／きゅっと痛くなる | 中央・座る | 肩を落とす（点線・放射線は消える） | なし | **胸に赤い点が現れる（1個）** | 0.3秒フェードアウト→黒 |
| 41.8〜45.5 | だから／思うんです | 中央・座る（肩を落とした姿勢から） | ゆっくり顔を上げる | なし | 胸の赤い点 | 0.3秒フェードイン |
| 45.5〜47.6 | 頑張れなかった日は | 中央・座る | 静止 | なし | 胸の赤い点 | カット |
| 47.6〜49.5 | さぼった日／じゃなくて | 中央・座る | 首をわずかにかしげる | なし | 胸の赤い点 | カット |
| 49.5〜53.1 | もう／動けなかった日なんだ | 中央・座る→横たわる | ゆっくり横になる（2.3秒） | なし | 胸の赤い点（体と一緒に動く） | カット |
| 53.1〜56.1 | あなたが／止まったんじゃなくて | 中央・横たわる | アーチが左から右へ描かれる | 人物を覆うアーチ | 胸の赤い点 | カット |
| 56.1〜59.9 | 体が止めてくれた／のかもしれない | 中央・横たわる・アーチの中 | 静止（呼吸のみ） | アーチ | 胸の赤い点 | 0.3秒フェードアウト→黒 |
| 60.2〜63.6 | それは／負けたというより | 中央・座る | 片手を胸（赤い点）に当てる | なし | 胸の赤い点 | 0.3秒フェードイン |
| 63.6〜67.8 | ちゃんと休めた／ってことなんだと思う | 中央・座る・手は胸 | わずかに顔を上げる | なし | 胸の赤い点 | カット |
| 67.8〜70.0 | 何もできなかった日を | 中央・座る・手は胸 | 赤い点が半分の大きさに縮む | なし | 胸の赤い点（小） | カット |
| 70.0〜73.0 | そっと許すこと | 中央・座る・手は胸 | 胸から小さな点がゆっくり外へ散って消える | 小さな点の散り | 胸の赤い点（小） | カット |
| 73.0〜76.6 | それが／自分を大切にする | 中央・座る・手は胸 | 右側の地平線の少し上に小さな太陽が浮かぶ | 小さな太陽 | 胸の赤い点（小） | カット |
| 76.6〜82.8 | いちばん静かな／形なのかもしれない | 中央・座る・手は胸／右に太陽 | 静止 | 小さな太陽 | 胸の赤い点（小） | 最後1秒フェードアウト |

---

## D. 映像生成AI向けプロンプト（英語）

### D-1 全シーン共通のスタイル指示文

```
minimalist white stick figure line art on pure black background, single thin hand-drawn horizontal ground line at 62% height, only one red accent element, static camera, limited animation, no text. Vertical 9:16, 1080x1920, 30fps. Background is solid #000000 with no gradient, texture, stars or vignette. The ground is one thin, slightly wobbly, broken (dashed-like) white line and the only background element. The stick figure is drawn with thin white strokes about 0.3% of the frame width: a hollow circle head, one line for the torso, two lines for each arm and leg, no face, no hands, no clothes; it stands about 8-9% of the frame height. Emotion is shown only through posture (slumped shoulders, lifted head, crouching, lying down, walking). Movement is minimal: one small action per shot, like a slow head lift or a single arm motion. Palette is strictly black and white; the only exception is one small red (#E0202A) dot on the figure's chest when specified. Any symbols are simple white outlines: oval thought bubble, musical note, question mark, short radial lines, dotted line, arch, small sun, scattered dots. Flat 2D, no shading, no glow, no particles, no depth, no camera motion.
```

### D-2 シーンごとのプロンプト（Cの各行に対応・各4〜8秒）

1. A white stick figure crouches in the center, hugging its knees with its head hung low, almost motionless except for a faint breathing sway; no symbols; no red.
2. The crouching stick figure slowly lifts its head over about one second and then holds still; no symbols; no red.
3. The crouching stick figure stays still while a small white outlined question mark fades in just above and to the right of its head; no red.
4. The crouching stick figure and the question mark hold perfectly still for a few seconds; no red.
5. A stick figure lies flat on the ground line with its head to the left and one arm resting on its chest, while an oval white thought bubble above it fades in showing a tiny stick figure walking in place; no red.
6. The lying stick figure slowly raises its upper body on one elbow as if trying to get up, then sinks back down onto the ground; no symbols; no red.
7. The lying stick figure remains still while the arm resting on its chest slowly slides down and drops onto the ground; no symbols; no red.
8. A slumped stick figure sits in the center with its head down and arms hanging, while two upright stick figures walk steadily from the center-right toward the right edge, a small white musical note floating above the rear walker; no red.
9. The same two walking figures continue to the right and exit the frame while the seated figure stays slumped and still, the musical note leaving with them; no red.
10. The seated stick figure lifts its head to look right, and a thin white dotted line extends from beside its head toward the right edge where the others left; no red.
11. The seated stick figure holds still while a few short white radial lines appear around its head, the dotted line still visible; no red.
12. The seated stick figure slowly slumps its shoulders as the dotted line and radial lines fade out, and a single small red dot (#E0202A) fades in on its chest; one red element only.
13. The slumped seated stick figure slowly lifts its head and straightens up a little; the small red dot stays on its chest; no other symbols.
14. The seated stick figure sits still with the small red dot on its chest, only a faint breathing motion; no other symbols.
15. The seated stick figure tilts its head slightly to one side and holds, the small red dot still on its chest; no other symbols.
16. The seated stick figure slowly lies down onto the ground over two seconds, the small red dot moving with its chest; no other symbols.
17. The stick figure lies still on the ground while a thin white arch is drawn from left to right over its whole body like a shelter; the small red dot stays on its chest.
18. The lying stick figure rests under the completed white arch with only a faint breathing motion, the small red dot on its chest.
19. The stick figure sits upright in the center and slowly brings one hand to rest on the red dot on its chest; no other symbols.
20. The seated stick figure keeps its hand on its chest and lifts its head slightly; the small red dot remains under its hand.
21. The seated stick figure holds still with its hand on its chest while the red dot shrinks to about half its size.
22. The seated stick figure holds still while a few tiny white dots drift slowly outward from its chest and fade away; the small red dot remains.
23. The seated stick figure stays still with its hand on its chest while a small white outlined sun with short rays fades in low on the right side above the ground line; the small red dot remains.
24. The seated stick figure and the small sun hold perfectly still for several seconds, then the whole frame fades to black; the small red dot remains until the fade.

### D-3 ネガティブプロンプト

```
color, colors, gradient, realistic, photorealistic, 3D, shading, shadows, face details, eyes, mouth, hair, clothes, camera movement, zoom, pan, handheld, text, letters, subtitles, logo, watermark, background objects, scenery, horizon glow, stars, particles, glow, bloom, light rays, texture, noise, grain, blur, multiple red elements, red background
```

---

## E. 音声合成の設定指示

声の方向性：低め〜中くらいの高さ、ささやき手前の落ち着いた声。約4文字/秒（通常の0.85〜0.9倍）。フックと最後の一文はさらに1割ゆっくり。文末は静かに下げる。

| 項目 | ElevenLabs | VOICEVOX | Google Cloud TTS |
| --- | --- | --- | --- |
| 声 | 落ち着いた低〜中音域の日本語対応ボイス（例：Multilingual v2 の "Daniel" / "Charlotte" 系、または自作の落ち着いた声） | 「青山龍星」（低め・落ち着き）または「九州そら（ささやき）」の手前の「ノーマル」 | `ja-JP-Neural2-C`（男声・低め）または `ja-JP-Neural2-B`（女声・落ち着き） |
| 速度 | Speed 0.85〜0.90 | 話速 0.85〜0.90 | `speakingRate` 0.85〜0.90 |
| フック・最後の一文 | Speed 0.78〜0.82 | 話速 0.78〜0.82 | `speakingRate` 0.78〜0.82 |
| ピッチ | 調整不可（声の選択で低めにする） | 音高 −0.05〜−0.10 | `pitch` −2.0〜−3.0 semitones |
| 抑揚 | Stability 0.70〜0.80 / Similarity 0.75 / Style 0.10〜0.20（感情を込めすぎない） | 抑揚 0.80〜0.90 | — （SSML の `<prosody>` で文末を上げない） |
| 音量 | 一定（後段で −16〜−18 LUFS に揃える） | 音量 1.0 | `volumeGainDb` 0 |
| 読点の間 | 「、」で 0.3〜0.5 秒（原稿に `<break time="0.4s"/>` を入れる） | 句読点の無音 0.4 秒 | `<break time="400ms"/>` |
| 句点の間 | `<break time="0.9s"/>` | 文末無音 0.9 秒 | `<break time="900ms"/>` |
| 幕の切り替わり | 1.5 秒の無音を編集で挿入（または `<break time="1.5s"/>`） | 1.5 秒の無音を編集で挿入 | `<break time="1500ms"/>` |
| 仕上げ | リップノイズ除去、息継ぎはわずかに残す。ピーク −1 dBFS | 同左 | 同左 |

※ 今回の完成動画は Microsoft Edge の音声合成（edge-tts）`ja-JP-KeitaNeural`、速度 −28%（フック・最後の一文は −35%）、ピッチ −6Hz で作成。読み間違い防止のため B-3 の読み原稿をそのまま入力している。

---

## F. 編集指示

**字幕**
- 書体：Noto Sans CJK JP Bold（源ノ角ゴシック Bold 相当）。白 #FFFFFF。縁取り・影・背景帯なし
- 大きさ：文字の高さ ≒ 75px（1080px 幅の約 7%）。フォントサイズ指定なら 82px。2行でも同じサイズ
- 位置：中央揃え。1行のときは画面上端から 30%（y=576px）に文字の中心。2行のときは 2 行の中心が y=576px、行間（ベースライン間）は 105px（文字高さの 1.4 倍）
- 改行：1行 10 文字以内。意味の切れ目（助詞の直後）で改行。C の「／」の位置に従う
- タイミング：B-2 の発声開始と同時に表示し、次のフレーズの発声開始と同時に切り替える。1 字幕 2〜4 秒。幕の最後の字幕は、フェードアウト開始（発声終了の 0.45 秒後）で消す
- 句読点は入れない。字幕以外の文字・ロゴ・ウォーターマークは一切出さない

**音声**
- ナレーション：−18 LUFS 前後、ピーク −1 dBFS。各フレーズの音量差はそろえる（RMS で ±1 dB 以内）
- BGM：アンビエントの静かなパッド＋まばらな単音。歌声なし。ナレーションより −18〜−20 dB（今回の実測：ナレーション −22.2 LUFS に対し BGM −40 LUFS）
- BGM は冒頭 2 秒でフェードイン、最後 2 秒でフェードアウト。効果音は入れない
- 間：読点 0.3〜0.5 秒、句点 0.8〜1.0 秒、幕の切り替わり 1.5 秒の沈黙

**映像・フェード**
- カメラ完全固定。ズーム・パン・手ブレ・エフェクトなし
- 幕の切り替わり（11.9 / 41.5 / 59.9 秒付近）だけ、0.3 秒のフェードアウト→0.3 秒のフェードインで軽く暗転する。それ以外の場面転換はすべてカット
- 冒頭 0.6 秒フェードイン、最後 1.0 秒フェードアウト
- 書き出し：1080×1920、30fps、H.264（High / Level 4.1）、CRF 18 程度、AAC 160kbps、`faststart` 付き

---

## G. 投稿用テキスト

「頑張れなかった日は、さぼった日じゃなくて、休めた日なのかもしれない」

#人生 #エッセイ #自分を責めない
