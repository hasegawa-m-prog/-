# -*- coding: utf-8 -*-
"""
脚本データ（ナレーション単位＝字幕単位＝TTS単位）。
各 unit:
  id        : 通し番号
  act       : 幕番号 1〜4
  text      : ナレーション本文（読点・句点つき）
  tts       : 音声合成に渡す読み原稿（読み間違えやすい語をひらがなに開いたもの）
  sub       : 字幕の行リスト（句読点なし、1行10文字以内、最大2行）
  pause     : この unit の発声が終わったあとに置く無音（秒）
  act_break : True なら幕の切り替わり（1.5秒の沈黙＋軽いフェード）
  slow      : True ならさらに1割ゆっくり（フックと最後の一文）
  scene     : 絵コンテのシーン名（render.py が参照）
"""

UNITS = [
    # ---------- ① フック（0〜10秒） ----------
    dict(id=1, act=1, text="今日、何もできなかった", tts="きょう、なにもできなかった",
         sub=["今日", "何もできなかった"], pause=0.35, slow=True, scene="crouch_still"),
    dict(id=2, act=1, text="あなたへ。", tts="あなたへ。",
         sub=["あなたへ"], pause=1.2, slow=True, scene="crouch_lookup"),
    dict(id=3, act=1, text="それでも、自分に、", tts="それでも、じぶんに、",
         sub=["それでも", "自分に"], pause=0.35, slow=True, scene="crouch_question"),
    dict(id=4, act=1, text="おつかれさまと言えますか。", tts="おつかれさまと、言えますか。",
         sub=["おつかれさまと", "言えますか"], pause=1.5, slow=True, act_break=True, scene="crouch_question_hold"),

    # ---------- ② 現実（10〜42秒） ----------
    dict(id=5, act=2, text="本当は、朝から動くつもりだった。", tts="ほんとうは、朝から動くつもりだった。",
         sub=["本当は朝から", "動くつもりだった"], pause=0.9, scene="lie_bubble"),
    dict(id=6, act=2, text="でも、体が起きなくて、", tts="でも、からだが起きなくて、",
         sub=["でも体が", "起きなくて"], pause=0.35, scene="lie_tryup"),
    dict(id=7, act=2, text="気づいたら夕方になっていた。", tts="気づいたら、夕方になっていた。",
         sub=["気づいたら", "夕方になっていた"], pause=0.9, scene="lie_armdrop"),
    dict(id=8, act=2, text="まわりの人は、今日も", tts="まわりの人は、きょうも",
         sub=["まわりの人は", "今日も"], pause=0.3, scene="sit_walkers_a"),
    dict(id=9, act=2, text="当たり前みたいに進んでいく。", tts="あたりまえみたいに、進んでいく。",
         sub=["当たり前みたいに", "進んでいく"], pause=0.9, scene="sit_walkers_b"),
    dict(id=10, act=2, text="私たちは、その背中を見ながら、", tts="わたしたちは、そのせなかを見ながら、",
         sub=["私たちは", "その背中を見ながら"], pause=0.35, scene="sit_dotted"),
    dict(id=11, act=2, text="自分だけ止まっている気がして、", tts="じぶんだけ、止まっている気がして、",
         sub=["自分だけ", "止まっている気がして"], pause=0.35, scene="sit_radial"),
    dict(id=12, act=2, text="胸の奥が、きゅっと痛くなる。", tts="むねのおくが、きゅっと、いたくなる。",
         sub=["胸の奥が", "きゅっと痛くなる"], pause=1.5, act_break=True, scene="sit_red_appear"),

    # ---------- ③ 転換（42〜64秒） ----------
    dict(id=13, act=3, text="だから、思うんです。", tts="だから、思うんです。",
         sub=["だから", "思うんです"], pause=0.9, scene="sit_red_lookup"),
    dict(id=14, act=3, text="頑張れなかった日は、", tts="がんばれなかった日は、",
         sub=["頑張れなかった日は"], pause=0.35, scene="sit_red_still"),
    dict(id=15, act=3, text="さぼった日じゃなくて、", tts="さぼった日じゃなくて、",
         sub=["さぼった日", "じゃなくて"], pause=0.35, scene="sit_red_still2"),
    dict(id=16, act=3, text="もう動けなかった日なんだ。", tts="もう、動けなかった日なんだ。",
         sub=["もう", "動けなかった日なんだ"], pause=0.9, scene="sit_to_lie"),
    dict(id=17, act=3, text="あなたが止まったんじゃなくて、", tts="あなたが、止まったんじゃなくて、",
         sub=["あなたが", "止まったんじゃなくて"], pause=0.35, scene="lie_arch_appear"),
    dict(id=18, act=3, text="体が、止めてくれたのかもしれない。", tts="からだが、止めてくれたのかもしれない。",
         sub=["体が止めてくれた", "のかもしれない"], pause=1.5, act_break=True, scene="lie_arch_hold"),

    # ---------- ④ 着地（64〜82秒） ----------
    dict(id=19, act=4, text="それは、負けたというより、", tts="それは、まけたというより、",
         sub=["それは", "負けたというより"], pause=0.35, scene="sit_hand_chest"),
    dict(id=20, act=4, text="ちゃんと休めた、ってことなんだと思う。", tts="ちゃんと休めた、ってことなんだと思う。",
         sub=["ちゃんと休めた", "ってことなんだと思う"], pause=0.9, scene="sit_hand_lookup"),
    dict(id=21, act=4, text="何もできなかった日を、", tts="なにもできなかった日を、",
         sub=["何もできなかった日を"], pause=0.35, scene="sit_red_shrink"),
    dict(id=22, act=4, text="そっと許すこと。", tts="そっと、ゆるすこと。",
         sub=["そっと許すこと"], pause=0.9, scene="sit_scatter"),
    dict(id=23, act=4, text="それが、自分を大切にする、", tts="それが、じぶんをたいせつにする、",
         sub=["それが", "自分を大切にする"], pause=0.35, slow=True, scene="sit_sun_appear"),
    dict(id=24, act=4, text="いちばん静かな形なのかもしれない。", tts="いちばん、しずかなかたちなのかもしれない。",
         sub=["いちばん静かな", "形なのかもしれない"], pause=0.0, slow=True, scene="sit_sun_hold"),
]

if __name__ == "__main__":
    full = "".join(u["text"] for u in UNITS)
    print(full)
    print("総文字数（句読点込み）:", len(full))
    print("総文字数（句読点なし）:", len(full.replace("、", "").replace("。", "")))
    for u in UNITS:
        for line in u["sub"]:
            assert len(line) <= 10, (u["id"], line)
        assert len(u["sub"]) <= 2
    print("字幕チェックOK")
