"""台本データ。読み上げ文は《》で赤字にする語を囲む。"""

STYLE = (
    "pure black background, minimalist thin white line-art, faceless human silhouettes "
    "with soft grey fill, single overhead spotlight creating a cone of light, cinematic "
    "chiaroscuro, slow and subtle motion only (gentle camera push-in, slow fade, light "
    "flicker), no faces, no text baked into the video, no color except faint red accent "
    "or blue/amber glow where specified, film grain 10%, vertical 9:16, 1080x1920, 24fps"
)
NEGATIVE = (
    "no realistic humans, no photos, no bright colors, no fast cuts, no shaky camera, "
    "no text, no logos, no watermarks, no emojis, no cartoon style, no 3D render look"
)

VOICE = "VOICEVOX 青山龍星、話速1.05、音高-0.02、抑揚0.9、文末ごとに0.4秒ポーズ、段落ごとに0.8秒ポーズ"
FONT = "明朝体（例：Noto Serif JP / 游明朝）、白、文字サイズは画面幅の7%、1行最大13字、重要語のみ赤（#C8102E）、画面下から18%の位置に中央揃え"


def prompt(scene: str, accent: str) -> str:
    return f"{scene}, {STYLE} --no {NEGATIVE}. Accent: {accent}."


# 各文: marked, scene(1始まり), block_end
# scene は映像の場面番号。block_end は段落末（0.8秒ポーズ）。

FILMS = [
    {
        "id": "01-kirenai",
        "file": "01_なぜ嫌えない人は苦しいのか.mp4",
        "question": "なぜ、傷つけられても嫌いになれないのか？",
        "title": "なぜ『嫌えない人』は／苦しいのか",
        "title_plain": "なぜ『嫌えない人』は苦しいのか",
        "emotion_hooks": [
            ("共感", "玄関で靴を脱いだ夜、あの人の言葉がまだ残っていました。嫌いだと決めれば、楽になると分かっています。それでも、嫌いの一言が出てきません。なぜ、傷つけられても嫌いになれないのだろうか？"),
            ("違和感", "味方だと呼んでいる人に、今夜も胸を刺されました。敵なら、もう扉を閉めているはずです。なのに靴を揃えたまま、部屋の灯を消せません。なぜ、傷つける人を嫌いにできないのだろうか？"),
            ("自己投影", "嫌いの一言を、喉の手前で何度も飲み込みました。楽になれるのに、その楽を選べません。自分の甘さだと、今夜も自分を責めています。なぜ、嫌えない自分を責め続けるのだろうか？"),
        ],
        "hook_emotions": ["共感", "違和感", "自己投影"],
        "post_tags": "#心理学 #Shorts #哲学 #人間関係 #アンビバレント #境界線 #自己否定",
        "lines": [
            ("玄関で靴を脱いだ夜、あの人の言葉がまだ残っていました。", 1, False),
            ("嫌いだと決めれば、楽になると分かっています。", 1, False),
            ("それでも、嫌いの一言が出てきません。", 1, True),
            ("なぜ、傷つけられても嫌いになれないのだろうか？", 2, True),
            ("実は、嫌いと好きが一人の中で並ぶと、心が《休まらない》からです。", 3, True),
            ("二千七年、ホルト＝ランスダッドたちが調べました。", 4, False),
            ("健康な大人、百七人が参加しています。", 4, False),
            ("載ったのは、行動医学の学術誌です。", 4, True),
            ("好きと嫌いが混ざる友人に話すと、血圧は《九・六》上がりました。", 5, False),
            ("支え合う友人では、上がり幅は《五・四》でした。", 5, False),
            ("すると、味方のつもりでいる人の前で、体が一番緊張したのです。", 5, True),
            ("ところが、うれしい話では《三・四》にとどまりました。", 6, False),
            ("話す前から、心拍の安静時も高めだったのです。", 6, True),
            ("ただし、測ったのは短い会話のあいだだけです。", 7, True),
            ("玄関で靴を脱いだ夜が、また胸に戻ってきます。", 8, False),
            ("靴を脱いだまま、嫌いの一言を探しています。", 8, True),
            ("嫌いが出ないまま痛いのは、《敵でも味方でもない》人だからだったんです。", 9, False),
            ("その痛みを、あなたの甘さだと思っていませんか？", 9, True),
        ],
        "scenes": [
            {
                "sec": "情景",
                "metaphor": "玄関のドアと、二足の靴、一本の糸でつながれた二人",
                "accent": "糸だけ薄い赤",
                "camera": "ゆっくり寄る。光が小さく揺れる。終わりに黒へ〇・五秒",
                "telop_note": "情景三文",
                "en": "At a barely open door, two pairs of shoes on the floor, two faceless figures standing close, a single thin thread tied from one wrist to the other, neither stepping away",
            },
            {
                "sec": "問い",
                "metaphor": "天秤。片方は人、片方は棘。糸が天秤を固定している",
                "accent": "棘だけ薄い赤",
                "camera": "天秤がわずかに傾き、糸に引かれて戻る。黒へ〇・五秒",
                "telop_note": "なぜ、の一文",
                "en": "A balance scale under the spotlight, a small faceless figure on one pan and a single thorn on the other, a thin thread holding the beam so it cannot settle",
            },
            {
                "sec": "結論",
                "metaphor": "一人の影が縦に割れ、左は灰、右の縁だけ赤",
                "accent": "割れ目の縁だけ薄い赤",
                "camera": "割れ目がゆっくり開いて止まる。黒へ〇・五秒",
                "telop_note": "休まらない",
                "en": "One faceless silhouette split by a vertical crack, the left half soft grey and the right edge faintly red, both halves still one body under the spotlight",
            },
            {
                "sec": "研究",
                "metaphor": "向かい合う二人。片方は半分かげ。横に上がっていく細い液柱",
                "accent": "液柱の先端だけ薄い赤",
                "camera": "液柱がゆっくり上がる。黒へ〇・五秒",
                "telop_note": "九・六",
                "en": "Two faceless figures facing each other, one half in shadow, a thin vertical glass column beside them whose level slowly rises",
            },
            {
                "sec": "結果",
                "metaphor": "二本の光の柱。右が左より高い",
                "accent": "高い柱の先端だけ薄い赤",
                "camera": "右の柱だけが遅れて伸びる。黒へ〇・五秒",
                "telop_note": "五・四",
                "en": "Two vertical columns of light, the left column shorter and calm, the right column taller with a faint red tip, both rising slowly then holding",
            },
            {
                "sec": "限界",
                "metaphor": "時計と、短いあいだだけ向かい合う二つの椅子",
                "accent": "なし",
                "camera": "秒針だけが進む。黒へ〇・五秒",
                "telop_note": "限界の一文",
                "en": "A round clock above two empty chairs that briefly hold two faceless figures, the second hand moving slowly, then the figures fade",
            },
            {
                "sec": "対比",
                "metaphor": "高い光の柱が、うれしい話になると下がる。胸の小さな脈だけ残る",
                "accent": "脈だけ薄い赤",
                "camera": "柱がゆっくり下がる。黒へ〇・五秒",
                "telop_note": "三・四",
                "en": "The tall column of light slowly sinking as the two figures share a lighter moment, while a small red pulse remains at one chest",
            },
            {
                "sec": "回収",
                "metaphor": "もう一度、玄関の靴とドア。胸に手を当てた人",
                "accent": "胸の一点だけ薄い赤",
                "camera": "最初のドアへゆっくり戻る。黒へ〇・五秒",
                "telop_note": "玄関・靴を再利用",
                "en": "Return to the same door and two pairs of shoes, one faceless figure with a hand on the chest, a faint red point of light at the chest",
            },
            {
                "sec": "締め",
                "metaphor": "空席の向かい。座った人がこちらを向く",
                "accent": "胸の光がゆっくり消える",
                "camera": "寄って止まり、黒へ〇・五秒",
                "telop_note": "敵でも味方でもない／問い",
                "en": "One faceless figure seated before an empty chair, hand still on the chest, the red point fading, the empty chair left unoccupied",
            },
        ],
    },
    {
        "id": "02-kawaranai",
        "file": "02_なぜ変わらないは楽なのか.mp4",
        "question": "なぜ、変わらない人の前で、こちらまで苦しくなるのか？",
        "title": "なぜ『変わらない』は／楽なのか",
        "title_plain": "なぜ『変わらない』は楽なのか",
        "hook_emotions": ["共感", "違和感", "自己投影"],
        "emotion_hooks": [
            ("共感", "相手の言い方を、今夜こそ直そうと待っていました。言葉を選び、間を置き、こちらの正解を渡します。それでも相手は、昨日と同じ顔で戻ってきます。なぜ、変わらない人の前で、こちらが苦しいのだろうか？"),
            ("違和感", "直したはずの約束が、翌朝には元の形に戻っていました。努力が足りないのだと思い、また手順を増やします。部屋の時計だけが、同じ時刻を指します。なぜ、直すほど相手が遠くなるのだろうか？"),
            ("自己投影", "相手を直しているあいだ、自分の夜がどんどん短くなっていました。正しいことを言っているはずなのに、胸だけが重いです。鏡の中の自分が、相手より疲れています。なぜ、直す役を降りられないのだろうか？"),
        ],
        "post_tags": "#心理学 #Shorts #哲学 #人間関係 #受け入れ #夫婦 #手放す",
        "lines": [
            ("相手の言い方を、今夜こそ直そうと待っていました。", 1, False),
            ("言葉を選び、間を置き、こちらの正解を渡します。", 1, False),
            ("それでも相手は、昨日と同じ顔で戻ってきます。", 1, True),
            ("なぜ、変わらない人の前で、こちらが苦しいのだろうか？", 2, True),
            ("実は、直す手を止めて今のままを《受け取る》と、楽が続きやすいからです。", 3, True),
            ("二千四年、クリステンセンたちが夫婦を比べました。", 4, False),
            ("長く悩む《百三十四》組が、参加しています。", 4, False),
            ("載ったのは、臨床心理の学術誌です。", 4, True),
            ("二人とも、深刻な悩みが長く続いていました。", 5, False),
            ("今の相手を受け取る関わりでは、《七十一》％が良くなりました。", 5, False),
            ("相手を直す関わりでは、《五十九》％が良くなりました。", 5, True),
            ("すると、受け取る側は満足が終わりまで上がり続けました。", 6, False),
            ("直す側は、最初のほうだけ早く上がりました。", 6, False),
            ("ところが、直す側は途中で伸びが止まっていました。", 6, True),
            ("ただし、終わりの差は偶然でも説明がつき、専門家がそばにいました。", 7, True),
            ("今夜こそ直そうと待った時間が、また胸に戻ってきます。", 8, False),
            ("同じ顔の人が、台の上に戻ってきます。", 8, True),
            ("同じ顔で戻ってきても楽なのは、直す役を降りたからだったんです。", 9, False),
            ("あなたが直し続けている人は、誰でしょうか？", 9, True),
        ],
        "scenes": [
            {
                "sec": "情景",
                "metaphor": "台座の上の人を、もう一人が両手で回そうとしている",
                "accent": "なし",
                "camera": "台座の人はほとんど回らない。ゆっくり寄る。黒へ〇・五秒",
                "telop_note": "情景三文",
                "en": "A faceless figure standing still on a low plinth while a second faceless figure pushes with both hands, trying to turn them, the figure on the plinth barely moving",
            },
            {
                "sec": "問い",
                "metaphor": "時計の下で、台座の人が同じ角度に戻る",
                "accent": "なし",
                "camera": "秒針だけが進み、人の向きが元に戻る。黒へ〇・五秒",
                "telop_note": "なぜ、の一文",
                "en": "The same plinth and figure under a large clock, the pushed figure slowly rotating back to the original angle as the second hand moves",
            },
            {
                "sec": "結論",
                "metaphor": "押していた両手を下ろす。肩の力が抜ける",
                "accent": "なし",
                "camera": "手がゆっくり下り、光が少し広がる。黒へ〇・五秒",
                "telop_note": "受け取る",
                "en": "The pushing figure slowly lowers both arms, shoulders dropping, the figure on the plinth left standing as they are, the spotlight widening a little",
            },
            {
                "sec": "研究",
                "metaphor": "たくさんの小さな二人組が、二つの列に並ぶ",
                "accent": "なし",
                "camera": "列が奥からゆっくり現れる。黒へ〇・五秒",
                "telop_note": "百三十四、七十一",
                "en": "Many tiny faceless couples arranged in two quiet rows under the spotlight, appearing slowly from the dark, no numbers written anywhere",
            },
            {
                "sec": "結果",
                "metaphor": "左の階段は上まで続き、右の階段は途中で平らになる",
                "accent": "左の階段の先に薄い琥珀の光",
                "camera": "左は登り続け、右は途中で止まる。黒へ〇・五秒",
                "telop_note": "五十九",
                "en": "Two staircases side by side, the left stairs continuing upward into a faint amber glow, the right stairs rising and then flattening into a landing",
            },
            {
                "sec": "限界",
                "metaphor": "二つの椅子のあいだに、空いた第三の椅子。扉",
                "accent": "なし",
                "camera": "第三の椅子だけが光の中に残る。黒へ〇・五秒",
                "telop_note": "限界の一文",
                "en": "A closed door and three chairs, two occupied by faceless figures and the middle chair empty, suggesting a quiet professional room",
            },
            {
                "sec": "対比",
                "metaphor": "右の階段は最初だけ急に上がり、そのあと平ら。左は最後まで続く",
                "accent": "左の先だけ薄い琥珀",
                "camera": "右が先に止まって、左が登り続ける。黒へ〇・五秒",
                "telop_note": "最初のほう、ところが",
                "en": "Two staircases, the right one climbing quickly then flattening, the left one rising slowly and steadily into a faint amber glow",
            },
            {
                "sec": "回収",
                "metaphor": "台座の人は同じ向きのまま。押す手はもうない",
                "accent": "なし",
                "camera": "最初の台座へ戻る。黒へ〇・五秒",
                "telop_note": "今夜こそ、を回収",
                "en": "Return to the plinth, the figure still facing the same way, the second figure standing beside them with hands down, no longer pushing",
            },
            {
                "sec": "締め",
                "metaphor": "二人並んで立つ。あいだに空いた余白",
                "accent": "なし",
                "camera": "余白へゆっくり寄る。黒へ〇・五秒",
                "telop_note": "問い",
                "en": "Two faceless figures standing side by side with an open gap between them, both still, the camera easing into that quiet gap",
            },
        ],
    },
    {
        "id": "03-warumono",
        "file": "03_なぜ離れた後は悪く見えるのか.mp4",
        "question": "なぜ、離れた人を悪く見ないと、落ち着かないのか？",
        "title": "なぜ『離れた後』は／悪く見えるのか",
        "title_plain": "なぜ『離れた後』は悪く見えるのか",
        "hook_emotions": ["共感", "違和感", "自己投影"],
        "emotion_hooks": [
            ("共感", "距離を置いた夜、相手を悪く言いかけて、口を閉じました。嫌いになれば決断は楽だと、分かっています。それでも、悪者の席を用意するのが嫌でした。なぜ、離れた人を悪く見ないと、落ち着かないのだろうか？"),
            ("違和感", "離れると決めたあと、急に相手の悪い記憶だけが並びました。昨日まで見えていた良い部分が、霧の向こうです。思い出を片付ける作業が、裁く作業に変わっています。なぜ、別れた人は急に悪く見えるのだろうか？"),
            ("自己投影", "相手を悪く言ったあと、少しだけ息ができました。その楽さのあとで、言い過ぎたと胸が痛みます。悪者にしないと、自分の決断が揺れて見えます。なぜ、悪く言わないと不安が残るのだろうか？"),
        ],
        "post_tags": "#心理学 #Shorts #哲学 #人間関係 #距離 #別れ #認知",
        "lines": [
            ("距離を置いた夜、相手を悪く言いかけて、口を閉じました。", 1, False),
            ("嫌いになれば決断は楽だと、分かっています。", 1, False),
            ("それでも、《悪者》の席を用意するのが嫌でした。", 1, True),
            ("なぜ、離れた人を悪く見ないと、落ち着かないのだろうか？", 2, True),
            ("実は、決めた直後は、選んだ道を良く見たくなるからです。", 3, True),
            ("一九六八年、ノックスとインクスターが競馬場で調べました。", 4, False),
            ("載ったのは、人格と社会心理の誌です。", 4, True),
            ("二ドルの馬券を買う前、六十九人の真ん中は《三・四八》でした。", 5, False),
            ("買った直後、七十二人の真ん中は《四・八一》でした。", 5, False),
            ("七段階のうち、良いほうへ寄っていました。", 5, True),
            ("すると、決め終えた人の方が、自分の選択を高く見ていました。", 6, False),
            ("この差は、偶然とは考えにくいものでした。", 6, True),
            ("ただし、馬券の場で、別々の人を比べた結果です。", 7, True),
            ("距離を置いた夜が、もう一度戻ってきます。", 8, False),
            ("口を閉じたあとでも、胸のざわつきは残っていました。", 8, True),
            ("灰色の人は、悪く塗られないまま立っています。", 9, False),
            ("《悪者》の席が空なのは、悪く見なくてよかったからだったんです。", 9, False),
            ("離れた人を、今日は灰色のまま置いておけますか？", 9, True),
        ],
        "scenes": [
            {
                "sec": "情景",
                "metaphor": "ドアの手前で口を閉じる人。奥の人は灰色のまま。赤い空席",
                "accent": "空席の縁だけ薄い赤、人は塗らない",
                "camera": "口元へ寄らず、空席が空のまま残る。黒へ〇・五秒",
                "telop_note": "悪者",
                "en": "A faceless figure at a doorway with a hand raised then lowered, as if closing the mouth, another figure remaining soft grey inside, and an empty chair with only a faint red rim",
            },
            {
                "sec": "問い",
                "metaphor": "鏡。映る人の輪郭が少し濃くなるが、赤くはならない",
                "accent": "鏡の枠だけ薄い赤",
                "camera": "鏡の中の輪郭がわずかに濃くなり、止まる。黒へ〇・五秒",
                "telop_note": "なぜ、の一文",
                "en": "A tall narrow mirror, a faceless figure outside it and a softer reflection inside, the reflection's outline slowly darkening but never turning red, the mirror frame faintly red",
            },
            {
                "sec": "結論",
                "metaphor": "二本の道。選んだ道だけ光が差す",
                "accent": "選んだ道の先に薄い琥珀",
                "camera": "選んだ道の光がゆっくり伸びる。黒へ〇・五秒",
                "telop_note": "結論",
                "en": "Two paths on a black floor, a faceless figure standing on the left path as a cone of light slowly brightens only along that path, a faint amber glow at its far end",
            },
            {
                "sec": "研究",
                "metaphor": "柵と窓口。小さな券を持つ人と、まだ持つ前の人",
                "accent": "券だけ薄い琥珀",
                "camera": "窓口の光が小さく揺れる。黒へ〇・五秒",
                "telop_note": "三・四八、四・八一",
                "en": "A simple railing and a small ticket window, one faceless figure still approaching and another holding a small ticket, the ticket catching a faint amber glow",
            },
            {
                "sec": "結果",
                "metaphor": "二本の縦の光。券を持った側が高い",
                "accent": "高い光の先端だけ薄い琥珀",
                "camera": "右の光だけがゆっくり伸びる。黒へ〇・五秒",
                "telop_note": "結果",
                "en": "Two faceless figures side by side, a short column of light beside the one without a ticket and a taller column beside the one holding a ticket",
            },
            {
                "sec": "限界",
                "metaphor": "柵と券と時計。人の別れは描かない",
                "accent": "券だけ薄い琥珀",
                "camera": "時計の秒針だけ。黒へ〇・五秒",
                "telop_note": "限界",
                "en": "Only the railing, one ticket, and a clock under the spotlight, no second person, the second hand moving slowly to mark the limit of the study",
            },
            {
                "sec": "結果",
                "metaphor": "選んだ道の光が、もう一段だけ伸びる",
                "accent": "道の先だけ薄い琥珀",
                "camera": "光がゆっくり伸びて止まる。黒へ〇・五秒",
                "telop_note": "偶然とは考えにくい",
                "en": "The chosen path's cone of light extending one step farther and then holding, a faint amber point at the end, the other path left dark",
            },
            {
                "sec": "回収",
                "metaphor": "もう一度、距離を置いた夜のドア。奥の人は灰色",
                "accent": "なし",
                "camera": "最初のドアへ戻る。黒へ〇・五秒",
                "telop_note": "距離を置いた夜",
                "en": "Return to the same doorway at night, the leaving figure paused, the remaining figure still soft grey and whole, not recast as a villain",
            },
            {
                "sec": "締め",
                "metaphor": "赤い空席は空のまま。灰色の人が立っている",
                "accent": "空席の縁だけ薄い赤",
                "camera": "空席から人へゆっくり移る。黒へ〇・五秒",
                "telop_note": "悪者、問い",
                "en": "The empty chair with a faint red rim stays empty, a faceless figure in soft grey standing beside it, untouched by red",
            },
        ],
    },
    {
        "id": "04-iihito",
        "file": "04_なぜ尽くす人は疲れるのか.mp4",
        "question": "なぜ、優しいままでいると、自分だけが空になるのか？",
        "title": "なぜ『尽くす人』は／疲れるのか",
        "title_plain": "なぜ『尽くす人』は疲れるのか",
        "hook_emotions": ["共感", "自己投影", "違和感"],
        "emotion_hooks": [
            ("共感", "頼まれると、自分の予定より先に手を挙げていました。断れば楽だと、薄々は気づいています。それでも、いい人の席を自分から降りられません。なぜ、優しいままでいると、自分だけが空になるのだろうか？"),
            ("自己投影", "みんなのコップが満たされるたび、自分のコップだけが空でした。感謝は届くのに、夜になると理由のわからない疲れが残ります。いい人でいる自分を、やめ方が分かりません。なぜ、優しさが自分を空にするのだろうか？"),
            ("違和感", "断らなかった夜のほうが、断った朝より心が重いです。役に立ったはずなのに、胸の奥が静かにくすんでいます。優しさの行き先が、相手ではなく自分の不安だと気づきます。なぜ、いい人でいるほど自分が薄くなるのだろうか？"),
        ],
        "post_tags": "#心理学 #Shorts #哲学 #いい人 #優しさ #境界線 #自己犠牲",
        "lines": [
            ("頼まれると、自分の予定より先に手を挙げていました。", 1, False),
            ("断れば楽だと、薄々は気づいています。", 1, False),
            ("それでも、いい人の席を自分から降りられません。", 1, True),
            ("なぜ、優しいままでいると、自分だけが空になるのだろうか？", 2, True),
            ("実は、嫌われまいとする優しさは、心を下げやすいからです。", 3, True),
            ("二千五年、インペットたちが恋人同士を追いました。", 4, False),
            ("《百五十三》人が、十四日間、毎日を記録しています。", 4, False),
            ("載ったのは、人格と社会心理の誌です。", 4, True),
            ("何かを譲った日は、全体の《四十八》％でした。", 5, False),
            ("二週間での平均は、《八・七》回です。", 5, False),
            ("一度でも学校や仕事を譲った人は、《七十三》％でした。", 5, True),
            ("譲ること自体が、悪いわけではありませんでした。", 6, False),
            ("喜ばせたい譲り方の日は、気分が上向きでした。", 6, False),
            ("ところが、衝突を避けたい日は、気分と関係が低めでした。", 6, True),
            ("ただし、対象は短い交際中の大学生だけです。", 7, True),
            ("頼まれて先に手を挙げる夜が、戻ってきます。", 8, False),
            ("空のコップが、また足元に戻ってきます。", 8, True),
            ("自分だけが空になるのは、《嫌われないため》だったんです。", 9, False),
            ("あなたの優しさは、誰のためでしたか？", 9, True),
        ],
        "scenes": [
            {
                "sec": "情景",
                "metaphor": "何本もの手が伸びる中、一人だけ手を挙げ、自分のコップは空",
                "accent": "空のコップの縁だけ薄い赤",
                "camera": "挙げた手へ寄る。黒へ〇・五秒",
                "telop_note": "情景三文",
                "en": "Several faceless hands reaching in from the dark, one faceless figure raising a hand first, an empty cup at their feet with a faint red rim",
            },
            {
                "sec": "問い",
                "metaphor": "挙げた手から糸が伸び、胸から離れていく",
                "accent": "糸だけ薄い赤",
                "camera": "糸がゆっくり張る。黒へ〇・五秒",
                "telop_note": "なぜ、の一文",
                "en": "A faceless figure with one hand raised, a thin red thread pulling that hand away from the chest, the chest left empty of light",
            },
            {
                "sec": "結論",
                "metaphor": "糸に引かれる手と、胸に戻した手。胸の光が落ちる",
                "accent": "糸が赤、胸の光は薄い琥珀から消える",
                "camera": "胸の光がゆっくり落ちる。黒へ〇・五秒",
                "telop_note": "結論",
                "en": "The same figure, the raised hand pulled by the red thread, a faint amber light at the chest sinking lower",
            },
            {
                "sec": "研究",
                "metaphor": "十四の小さな窓。約半分に点",
                "accent": "点だけ薄い琥珀",
                "camera": "窓が一段ずつ灯る。黒へ〇・五秒",
                "telop_note": "百五十三、四十八",
                "en": "A grid of fourteen small square windows, about half of them holding a tiny amber dot, lighting one by one, no numerals written",
            },
            {
                "sec": "結果",
                "metaphor": "左は胸から差し出す人、右は糸に引かれる人",
                "accent": "右の糸だけ赤。左の胸は薄い琥珀",
                "camera": "左の光が残り、右の光が落ちる。黒へ〇・五秒",
                "telop_note": "八・七",
                "en": "Two faceless figures, the left offering a hand from the chest with a faint amber glow, the right pulled sideways by a red thread as their light dims",
            },
            {
                "sec": "限界",
                "metaphor": "短い階段と時計。二人の若い背丈",
                "accent": "なし",
                "camera": "時計だけが進む。黒へ〇・五秒",
                "telop_note": "限界",
                "en": "A short flight of steps and a clock, two faceless figures of modest height standing together, the second hand marking a brief span of days",
            },
            {
                "sec": "対比",
                "metaphor": "左は胸から差し出す人、右は糸に引かれる人",
                "accent": "右の糸だけ赤。左の胸は薄い琥珀",
                "camera": "左の光が残り、右の光が落ちる。黒へ〇・五秒",
                "telop_note": "上向きと下向き",
                "en": "Two faceless figures side by side, the left offering from the chest with a steady amber glow, the right pulled by a red thread as their light sinks",
            },
            {
                "sec": "回収",
                "metaphor": "挙げた手が、胸のほうへ戻る",
                "accent": "胸に戻る一点だけ薄い赤",
                "camera": "手がゆっくり下りる。黒へ〇・五秒",
                "telop_note": "手を挙げる、を回収",
                "en": "The raised hand slowly returning toward the chest, the red thread going slack, a faint red point settling at the chest",
            },
            {
                "sec": "締め",
                "metaphor": "自分の胸に小さな光を持つ人。周りの手は暗い",
                "accent": "胸の光だけ薄い琥珀",
                "camera": "胸の光へ寄って止まる。黒へ〇・五秒",
                "telop_note": "嫌われないため、問い",
                "en": "One faceless figure holding a small amber light at their own chest, the surrounding reaching hands faded into black",
            },
        ],
    },
    {
        "id": "05-mikaeri",
        "file": "05_なぜ期待はわがままなのか.mp4",
        "question": "なぜ、与えた分を返してほしいと思ってしまうのか？",
        "title": "なぜ『期待』は／わがままなのか",
        "title_plain": "なぜ『期待』はわがままなのか",
        "hook_emotions": ["自己投影", "共感", "違和感"],
        "emotion_hooks": [
            ("自己投影", "贈り物を渡したあと、相手の反応を待ってしまいました。見返りを数える自分を、小さく責めています。それでも、待っている手を引っ込められません。なぜ、与えた分を返してほしいと思ってしまうのだろうか？"),
            ("共感", "あげたあとで、返事の速さばかり見てしまいました。そんな自分は小さいと、その夜に決めつけます。手はまだ、開いたままです。なぜ、お返しを待つ自分を許せないのだろうか？"),
            ("違和感", "与えることは美しく、待つことは汚いと、どこかで覚えてきました。なのに待たないと、胸の奥が静かにざわつきます。きれいな人でいるルールが、自分を裁いています。なぜ、貸し借りに気づくことが悪いことになったのだろうか？"),
        ],
        "post_tags": "#心理学 #Shorts #哲学 #見返り #人間関係 #自己受容 #互恵",
        "lines": [
            ("贈り物を渡したあと、相手の反応を待ってしまいました。", 1, False),
            ("見返りを数える自分を、小さく責めています。", 1, False),
            ("それでも、待っている手を引っ込められません。", 1, True),
            ("なぜ、与えた分を返してほしいと思ってしまうのだろうか？", 2, True),
            ("実は、人はもらったものを返したくなるように、できているからです。", 3, True),
            ("一九七一年、リーガンが七十七人で実験しました。", 4, False),
            ("載ったのは、実験社会心理の誌です。", 4, True),
            ("知らない人に一杯おごられると、くじの平均は《一・七三》枚でした。", 5, False),
            ("何ももらわないと、《零点九二》枚でした。", 5, True),
            ("実験者からの一杯だと、《一・〇八》枚でした。", 6, False),
            ("すると、相手本人からの一杯が、お返しを一番大きくしました。", 6, False),
            ("杯を受け取った人ほど、券を多く買っていました。", 6, True),
            ("ただし、これは実験室の、見知らぬ人同士の話です。", 7, True),
            ("贈り物を渡したあとが、もう一度戻ってきます。", 8, False),
            ("開いた掌は、まだ閉じないままでした。", 8, True),
            ("反応を待ってしまうのは、心の《帳面》が開くからだったんです。", 9, False),
            ("その期待を、あなたの汚さだと思っていませんか？", 9, True),
        ],
        "scenes": [
            {
                "sec": "情景",
                "metaphor": "小さな箱を渡したあと、開いた掌が残る",
                "accent": "掌の上に薄い赤が一度灯って消える",
                "camera": "開いた掌へゆっくり寄る。黒へ〇・五秒",
                "telop_note": "情景三文",
                "en": "A faceless figure offering a small wrapped box, then an open palm left waiting, a faint red pulse appearing once on the palm and fading",
            },
            {
                "sec": "問い",
                "metaphor": "開いた掌と、胸の小さな赤",
                "accent": "胸だけ薄い赤",
                "camera": "胸の赤が小さく瞬く。黒へ〇・五秒",
                "telop_note": "なぜ、の一文",
                "en": "The open palm still extended, the figure's head tilted slightly down, a faint red point flickering at the chest",
            },
            {
                "sec": "結論",
                "metaphor": "天秤。片方に杯、片方に小さな箱。汚くは描かない",
                "accent": "支点だけ薄い琥珀",
                "camera": "天秤がゆっくり水平に近づく。黒へ〇・五秒",
                "telop_note": "結論",
                "en": "A clean balance scale, a simple cup on one pan and a small gift box on the other, the beam easing toward level, a faint amber glow at the fulcrum",
            },
            {
                "sec": "研究",
                "metaphor": "二人のあいだを、一杯の杯が渡る",
                "accent": "杯だけ薄い琥珀",
                "camera": "杯が片方から片方へゆっくり移動。黒へ〇・五秒",
                "telop_note": "一・七三、〇・九二",
                "en": "Two faceless strangers, a simple cup passing slowly from one hand to the other, the cup holding a faint amber glow",
            },
            {
                "sec": "結果",
                "metaphor": "三つの券の束。高さが違う。真ん中が一番高い",
                "accent": "一番高い束だけ薄い琥珀",
                "camera": "高い束が最後に揃う。黒へ〇・五秒",
                "telop_note": "一・〇八",
                "en": "Three stacks of small blank tickets at different heights, the middle stack tallest with a faint amber edge, no numerals written",
            },
            {
                "sec": "限界",
                "metaphor": "小さな部屋、机、時計、見知らぬ二人",
                "accent": "なし",
                "camera": "部屋の全体が少し引く。黒へ〇・五秒",
                "telop_note": "限界",
                "en": "A small bare room, a table, a clock, and two faceless strangers who do not know each other, the camera easing slightly back",
            },
            {
                "sec": "結果",
                "metaphor": "杯を受け取った側の券の束だけが、もう一枚増える",
                "accent": "増えた束だけ薄い琥珀",
                "camera": "束が一段高くなって止まる。黒へ〇・五秒",
                "telop_note": "お返し",
                "en": "The tallest stack of blank tickets gaining one more sheet and then holding, a faint amber edge, the shorter stacks staying still",
            },
            {
                "sec": "回収",
                "metaphor": "もう一度、贈り物のあとの開いた掌",
                "accent": "赤はもう点かない",
                "camera": "最初の掌へ戻る。黒へ〇・五秒",
                "telop_note": "贈り物、を回収",
                "en": "Return to the open palm after the gift, no red pulse this time, the hand simply open under the spotlight",
            },
            {
                "sec": "締め",
                "metaphor": "開いた帳面のような二ページ。天秤はほぼ水平",
                "accent": "帳面の中央の線だけ薄い赤",
                "camera": "帳面へ寄って止まる。黒へ〇・五秒",
                "telop_note": "帳面、問い",
                "en": "An open blank ledger of two pages with a faint red center line, the balance scale behind it nearly level, no writing on the pages",
            },
        ],
    },
]


def plain(marked: str) -> str:
    return marked.replace("《", "").replace("》", "")


def wrap_text(text: str, limit: int = 13):
    lines = []
    i = 0
    n = len(text)
    while i < n:
        window = text[i : min(n, i + limit)]
        if i + limit >= n:
            lines.append(window)
            break
        br = None
        for k in range(len(window) - 1, 2, -1):
            if window[k] in "、。":
                br = k + 1
                break
        if br is None:
            for k in range(len(window) - 1, 3, -1):
                if window[k] in "はがをにのとでもへ":
                    br = k + 1
                    break
        if br is None:
            br = len(window)
        lines.append(text[i : i + br])
        i += br
    return lines


# 自動折り返しが十三字を超える、または読みが悪い文だけ手で割る。
WRAPS = {
    "それでも、嫌いの一言が出てきません。": ["それでも、", "嫌いの一言が", "出てきません。"],
    "なぜ、傷つけられても嫌いになれないのだろうか？": ["なぜ、傷つけられても", "嫌いになれない", "のだろうか？"],
    "実は、嫌いと好きが一人の中で並ぶと、心が休まらないからです。": ["実は、嫌いと好きが", "一人の中で並ぶと、", "心が休まらないからです。"],
    "二千七年、ホルト＝ランスダッドたちが調べました。": ["二千七年、", "ホルト＝ランスダッド", "たちが調べました。"],
    "好きと嫌いが混ざる友人に話すと、血圧は九・六上がりました。": ["好きと嫌いが混ざる", "友人に話すと、血圧は", "九・六上がりました。"],
    "支え合う友人では、上がり幅は五・四でした。": ["支え合う友人では、", "上がり幅は五・四でした。"],
    "すると、味方のつもりでいる人の前で、体が一番緊張したのです。": ["すると、味方のつもりで", "いる人の前で、体が", "一番緊張したのです。"],
    "ただし、測ったのは短い会話のあいだだけです。": ["ただし、測ったのは", "短い会話の", "あいだだけです。"],
    "玄関で靴を脱いだ夜が、また胸に戻ってきます。": ["玄関で靴を脱いだ夜が、", "また胸に戻ってきます。"],
    "嫌いが出ないまま痛いのは、敵でも味方でもない人だからだったんです。": ["嫌いが出ないまま", "痛いのは、敵でも", "味方でもない人", "だからだったんです。"],
    "相手の言い方を、今夜こそ直そうと待っていました。": ["相手の言い方を、", "今夜こそ直そうと", "待っていました。"],
    "言葉を選び、間を置き、こちらの正解を渡します。": ["言葉を選び、間を置き、", "こちらの正解を", "渡します。"],
    "それでも相手は、昨日と同じ顔で戻ってきます。": ["それでも相手は、", "昨日と同じ顔で", "戻ってきます。"],
    "なぜ、変わらない人の前で、こちらが苦しいのだろうか？": ["なぜ、変わらない人の", "前で、こちらが苦しい", "のだろうか？"],
    "実は、直す手を止めて今のままを受け取ると、楽が続きやすいからです。": ["実は、直す手を止めて", "今のままを受け取ると、", "楽が続きやすいからです。"],
    "二千四年、クリステンセンたちが夫婦を比べました。": ["二千四年、", "クリステンセンたちが", "夫婦を比べました。"],
    "今の相手を受け取る関わりでは、七十一％が良くなりました。": ["今の相手を受け取る", "関わりでは、", "七十一％が良くなりました。"],
    "相手を直す関わりでは、五十九％が良くなりました。": ["相手を直す関わりでは、", "五十九％が良くなりました。"],
    "すると、受け取る側は満足が終わりまで上がり続けました。": ["すると、受け取る側は", "満足が終わりまで", "上がり続けました。"],
    "ところが、直す側は途中で伸びが止まっていました。": ["ところが、直す側は", "途中で伸びが", "止まっていました。"],
    "ただし、終わりの差は偶然でも説明がつき、専門家がそばにいました。": ["ただし、終わりの差は", "偶然でも説明がつき、", "専門家がそばにいました。"],
    "今夜こそ直そうと待った時間が、また胸に戻ってきます。": ["今夜こそ直そうと", "待った時間が、", "また胸に戻ってきます。"],
    "同じ顔で戻ってきても楽なのは、直す役を降りたからだったんです。": ["同じ顔で戻ってきても", "楽なのは、直す役を", "降りたからだったんです。"],
    "あなたが直し続けている人は、誰でしょうか？": ["あなたが直し続けている", "人は、誰でしょうか？"],
    "距離を置いた夜、相手を悪く言いかけて、口を閉じました。": ["距離を置いた夜、", "相手を悪く言いかけて、", "口を閉じました。"],
    "それでも、悪者の席を用意するのが嫌でした。": ["それでも、悪者の席を", "用意するのが嫌でした。"],
    "なぜ、離れた人を悪く見ないと、落ち着かないのだろうか？": ["なぜ、離れた人を", "悪く見ないと、", "落ち着かないのだろうか？"],
    "実は、決めた直後は、選んだ道を良く見たくなるからです。": ["実は、決めた直後は、", "選んだ道を良く", "見たくなるからです。"],
    "一九六八年、ノックスとインクスターが競馬場で調べました。": ["一九六八年、ノックスと", "インクスターが", "競馬場で調べました。"],
    "二ドルの馬券を買う前、六十九人の真ん中は三・四八でした。": ["二ドルの馬券を買う前、", "六十九人の真ん中は", "三・四八でした。"],
    "買った直後、七十二人の真ん中は四・八一でした。": ["買った直後、", "七十二人の真ん中は", "四・八一でした。"],
    "すると、決め終えた人の方が、自分の選択を高く見ていました。": ["すると、決め終えた", "人の方が、自分の選択を", "高く見ていました。"],
    "ただし、馬券の場で、別々の人を比べた結果です。": ["ただし、馬券の場で、", "別々の人を比べた", "結果です。"],
    "悪者の席が空なのは、悪く見なくてよかったからだったんです。": ["悪者の席が空なのは、", "悪く見なくてよかった", "からだったんです。"],
    "離れた人を、今日は灰色のまま置いておけますか？": ["離れた人を、今日は", "灰色のまま", "置いておけますか？"],
    "頼まれると、自分の予定より先に手を挙げていました。": ["頼まれると、", "自分の予定より先に", "手を挙げていました。"],
    "それでも、いい人の席を自分から降りられません。": ["それでも、いい人の席を", "自分から降りられません。"],
    "なぜ、優しいままでいると、自分だけが空になるのだろうか？": ["なぜ、優しいままで", "いると、自分だけが", "空になるのだろうか？"],
    "実は、嫌われまいとする優しさは、心を下げやすいからです。": ["実は、嫌われまいと", "する優しさは、", "心を下げやすいからです。"],
    "二千五年、インペットたちが恋人同士を追いました。": ["二千五年、", "インペットたちが", "恋人同士を追いました。"],
    "百五十三人が、十四日間、毎日を記録しています。": ["百五十三人が、", "十四日間、毎日を", "記録しています。"],
    "何かを譲った日は、全体の四十八％でした。": ["何かを譲った日は、", "全体の四十八％でした。"],
    "喜ばせたい譲り方の日は、気分が上向きでした。": ["喜ばせたい譲り方の", "日は、気分が", "上向きでした。"],
    "ところが、衝突を避けたい日は、気分と関係が低めでした。": ["ところが、衝突を", "避けたい日は、", "気分と関係が低めでした。"],
    "ただし、対象は短い交際中の大学生だけです。": ["ただし、対象は", "短い交際中の", "大学生だけです。"],
    "自分だけが空になるのは、嫌われないためだったんです。": ["自分だけが空になるのは、", "嫌われないため", "だったんです。"],
    "あなたの優しさは、誰のためでしたか？": ["あなたの優しさは、", "誰のためでしたか？"],
    "贈り物を渡したあと、相手の反応を待ってしまいました。": ["贈り物を渡したあと、", "相手の反応を", "待ってしまいました。"],
    "なぜ、与えた分を返してほしいと思ってしまうのだろうか？": ["なぜ、与えた分を", "返してほしいと", "思ってしまうのだろうか？"],
    "実は、人はもらったものを返したくなるように、できているからです。": ["実は、人はもらった", "ものを返したくなる", "ように、できている", "からです。"],
    "一九七一年、リーガンが七十七人で実験しました。": ["一九七一年、リーガンが", "七十七人で実験しました。"],
    "知らない人に一杯おごられると、くじの平均は一・七三枚でした。": ["知らない人に一杯", "おごられると、くじの", "平均は一・七三枚でした。"],
    "実験者からの一杯だと、一・〇八枚でした。": ["実験者からの一杯だと、", "一・〇八枚でした。"],
    "すると、相手本人からの一杯が、お返しを一番大きくしました。": ["すると、相手本人からの", "一杯が、お返しを", "一番大きくしました。"],
    "ただし、これは実験室の、見知らぬ人同士の話です。": ["ただし、これは", "実験室の、見知らぬ", "人同士の話です。"],
    "贈り物を渡したあとが、もう一度戻ってきます。": ["贈り物を渡したあとが、", "もう一度戻ってきます。"],
    "反応を待ってしまうのは、心の帳面が開くからだったんです。": ["反応を待ってしまうのは、", "心の帳面が開くから", "だったんです。"],
    "その期待を、あなたの汚さだと思っていませんか？": ["その期待を、", "あなたの汚さだと", "思っていませんか？"],
}


def wraps_for(marked: str):
    text = plain(marked)
    if text in WRAPS:
        lines = WRAPS[text]
    else:
        lines = wrap_text(text)
    # 赤字範囲を行へ分配する
    reds = []
    i = 0
    bare = []
    while i < len(marked):
        if marked[i] == "《":
            j = marked.index("》", i)
            word = marked[i + 1 : j]
            reds.append((len(bare), len(bare) + len(word)))
            bare.extend(word)
            i = j + 1
        else:
            bare.append(marked[i])
            i += 1
    out = []
    cursor = 0
    for line in lines:
        start = cursor
        end = cursor + len(line)
        parts = []
        buf = ""
        red = None
        for k, ch in enumerate(line):
            is_red = any(a <= start + k < b for a, b in reds)
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
        shown = "".join(("《" + s + "》" if r else s) for s, r in parts)
        out.append(shown)
        cursor = end
    return out


def validate():
    ok = True
    for film in FILMS:
        texts = [plain(m) for m, _s, _b in film["lines"]]
        total = sum(len(t) for t in texts)
        print(f"\n== {film['id']} {total}字  scenes={max(s for _, s, _ in film['lines'])} ==")
        if not (400 <= total <= 600):
            print(f"  !! 字数 {total}")
            ok = False
        title = film["title_plain"]
        if not (14 <= len(title) <= 20):
            print(f"  !! タイトル字数 {len(title)} {title}")
            ok = False
        for marked, scene, _b in film["lines"]:
            text = plain(marked)
            if len(text) > 40:
                print(f"  !! {len(text)}字 {text}")
                ok = False
            if "！" in text or "!" in text:
                print("  !! 感嘆符", text)
                ok = False
            lines = wraps_for(marked)
            joined = "".join(plain(x) for x in lines)
            if joined != text:
                print("  !! 折り返し不一致")
                print("   ", text)
                print("   ", joined)
                ok = False
            for line in lines:
                if len(plain(line)) > 13:
                    print(f"  !! {len(plain(line))}字行 {plain(line)}")
                    ok = False
        if film["lines"][-1][0][-1] not in "？?":
            print("  !! 問いかけで終わっていない")
            ok = False
        n_scenes = len(film["scenes"])
        used = {s for _, s, _ in film["lines"]}
        if used != set(range(1, n_scenes + 1)):
            print("  !! 場面番号", used, n_scenes)
            ok = False
    return ok


def _reorder():
    """挿入した場面を、ナレーションの場面番号に合わせる。"""
    for film in FILMS:
        a, b = film["scenes"][5], film["scenes"][6]
        if a["sec"] == "限界" and b["sec"] in ("対比", "結果"):
            film["scenes"][5], film["scenes"][6] = b, a
    couples = FILMS[1]["scenes"][4]
    couples["sec"] = "結果"
    couples["metaphor"] = "二つの群れ。左だけが薄く光る"
    couples["accent"] = "左の群れだけ薄い琥珀"
    couples["camera"] = "左の光が残って、右が少し沈む。黒へ〇・五秒"
    couples["telop_note"] = "七十一と五十九"
    couples["en"] = (
        "Two clusters of tiny faceless couples, the left cluster holding a faint amber glow, "
        "the right cluster dimmer, both still under one spotlight"
    )
    study, result = FILMS[3]["scenes"][3], FILMS[3]["scenes"][4]
    FILMS[3]["scenes"][3], FILMS[3]["scenes"][4] = result, study
    FILMS[3]["scenes"][3]["sec"] = "研究"
    FILMS[3]["scenes"][3]["metaphor"] = "向かい合って記録する二人と、小さな手帳"
    FILMS[3]["scenes"][3]["accent"] = "手帳だけ薄い琥珀"
    FILMS[3]["scenes"][3]["camera"] = "手帳がゆっくり開く。黒へ〇・五秒"
    FILMS[3]["scenes"][3]["telop_note"] = "百五十三、十四日"
    FILMS[3]["scenes"][3]["en"] = (
        "Two faceless figures facing each other with a small open notebook between them, "
        "the notebook catching a faint amber glow"
    )
    FILMS[3]["scenes"][4]["sec"] = "結果"


_reorder()


if __name__ == "__main__":
    raise SystemExit(0 if validate() else 1)
