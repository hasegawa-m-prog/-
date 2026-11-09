"""Five essay shorts. Spoken text (`say`) is what the voice reads.
`show` is the manuscript. `sub` is the on-screen line, with no punctuation.
"""

from __future__ import annotations

PUNCT = set("、。？！「」『』（）()・　 ")


def P(act, show, say, sub, figs, action, red="none", syms=()):
    if isinstance(sub, str):
        sub = (sub,)
    else:
        sub = tuple(sub)
    if isinstance(figs[0], str):
        figs = (tuple(figs),)
    else:
        figs = tuple(tuple(f) for f in figs)
    return {
        "act": act,
        "show": show,
        "say": say,
        "sub": sub,
        "figs": figs,
        "action": action,
        "red": red,
        "syms": tuple(syms),
    }


def solo(pose, pos="C", face=1):
    return ("a", pos, face, pose)


def pair(p1, p2, far=False):
    left, right = ("FL", "FR") if far else ("L", "R")
    return (("a", left, 1, p1), ("b", right, -1, p2))


# --- 1 ---------------------------------------------------------------

S1 = [
    P(1, "もしも、その人を", "もしも、そのひとを", "もしもその人を", solo("down"), ("a", "head", 8), "wound"),
    P(1, "嫌いになれたら、", "きらいになれたら、", "嫌いになれたら", solo("down"), ("a", "head", 6), "wound"),
    P(1, "それでもあなたは、", "それでもあなたは、", "それでもあなたは", solo("down"), ("a", "head", -12), "wound"),
    P(1, "楽になれますか。", "らくになれますか。", "楽になれますか", solo("down"), ("a", "head", -8), "wound"),
    P(2, "相手は、また笑っている。", "あいては、またわらっている。", "相手はまた笑っている", pair("down", "easy"), ("b", "arm"), "wound", ("note:b",)),
    P(2, "刺したことにも、", "さしたことにも、", "刺したことにも", pair("down", "easy"), ("a", "head", 8), "wound", ("note:b",)),
    P(2, "気づいていない。", "きづいていない。", "気づいていない", pair("down", "easy"), ("b", "arm"), "wound", ("note:b",)),
    P(2, "こちらだけが、夜まで", "こちらだけが、よるまで", "こちらだけが夜まで", pair("chest", "easy"), ("a", "head", 6), "wound", ("note:b",)),
    P(2, "その言葉を持っている。", "そのことばをもっている。", "その言葉を持っている", pair("chest", "easy"), ("a", "to", "chest"), "wound", ("note:b",)),
    P(2, "怒りたいのに、", "おこりたいのに、", "怒りたいのに", pair("down", "easy"), ("a", "head", 8), "wound", ("note:b",)),
    P(2, "その顔を見ると、", "そのかおをみると、", "その顔を見ると", pair("down", "easy"), ("a", "head", 4), "wound", ("note:b",)),
    P(2, "声が出ない。", "こえがでない。", "声が出ない", pair("down", "easy"), ("a", "to", "chest"), "wound", ("note:b",)),
    P(2, "私たちは、同じ言葉で、", "わたしたちは、おなじことばで、", "私たちは同じ言葉で", pair("chest", "easy"), ("a", "head", 6), "wound", ("note:b",)),
    P(2, "また胸を刺される。", "またむねをさされる。", "また胸を刺される", pair("chest", "easy"), ("a", "to", "chest"), "wound", ("note:b",)),
    P(2, "嫌いになれば、", "きらいになれば、", "嫌いになれば", pair("down", "easy", far=True), ("a", "head", -6), "wound", ("dots", "note:b")),
    P(2, "もう会わなくていい。", "もうあわなくていい。", "もう会わなくていい", pair("down", "easy", far=True), ("a", "walk", -36), "wound", ("dots", "note:b")),
    P(2, "でも、嫌い切れないから、", "でも、きらいきれないから、", "嫌い切れないから", pair("down", "stand"), ("a", "walk", 34), "wound", ("chain:a", "dots")),
    P(2, "足が勝手に戻ってしまう。", "あしがかってにもどってしまう。", ("足が勝手に", "戻ってしまう"), pair("down", "stand"), ("a", "walk", 24), "wound", ("chain:a", "dots")),
    P(2, "離れたいと願うほど、", "はなれたいとねがうほど、", "離れたいと願うほど", pair("down", "stand"), ("a", "head", 8), "wound", ("chain:a", "dots")),
    P(2, "名前が消せない。", "なまえがけせない。", "名前が消せない", pair("down", "stand"), ("a", "head", 6), "wound", ("chain:a", "dots")),
    P(3, "だから、つらいのは、", "だから、つらいのは、", "だからつらいのは", solo("down"), ("a", "head", 6), "wound", ("chain:a",)),
    P(3, "傷そのものじゃなくて、", "きずそのものじゃなくて、", ("傷そのもの", "じゃなくて"), solo("down"), ("a", "to", "chest"), "wound", ("chain:a",)),
    P(3, "嫌い切れない心、", "きらいきれないこころ、", "嫌い切れない心", solo("chest"), ("a", "head", 6), "wound", ("chain:a",)),
    P(3, "なんだと思う。", "なんだと思う。", "なんだと思う", solo("chest"), ("a", "head", -10), "wound", ("chain:a",)),
    P(3, "悪者にすれば、", "わるものにすれば、", "悪者にすれば", solo("stand"), ("a", "walk", 26), "wound", ("chain:a",)),
    P(3, "足は前に出る。", "あしはまえにでる。", "足は前に出る", solo("stand"), ("a", "walk", 16), "wound", ("chain:a",)),
    P(3, "でも、心がそれを、", "でも、こころがそれを、", "でも心がそれを", solo("stand"), ("a", "head", 10), "wound", ("chain:a",)),
    P(3, "静かに、受けつけなくなる。", "しずかに、受けつけなくなる。", ("静かに", "受けつけなくなる"), solo("stand"), ("a", "to", "down"), "wound", ("chain:a",)),
    P(4, "それは、やさしさというより、", "それは、やさしさというより、", ("それは", "やさしさというより"), solo("down"), ("a", "head", -8), "wound", ("arch:a", "chain:a")),
    P(4, "自分で出口を細くしている、", "じぶんででぐちをほそくしている、", ("自分で", "出口を細くしている"), solo("down"), ("a", "head", 4), "wound", ("arch:a", "chain:a")),
    P(4, "形なんだと思う。", "かたちなんだと思う。", "形なんだと思う", solo("down"), ("a", "head", 6), "wound", ("arch:a", "chain:a")),
    P(4, "そのつらさとは、", "そのつらさとは、", "そのつらさとは", solo("chest"), ("a", "head", 8), "wound", ("bubble:a", "chain:a")),
    P(4, "まだその人を心に、", "まだそのひとをこころに、", "まだその人を心に", solo("chest"), ("a", "head", 4), "wound", ("bubble:a", "chain:a")),
    P(4, "残している、", "のこしている、", "残している", solo("chest"), ("a", "to", "chest"), "wound", ("bubble:a", "chain:a")),
    P(4, "形なのかもしれない。", "かたちなのかもしれない。", "形なのかもしれない", solo("chest"), ("a", "head", -8), "wound", ("bubble:a", "chain:a")),
]

# --- 2 ---------------------------------------------------------------

S2 = [
    P(1, "もしも、その人が、", "もしも、そのひとが、", "もしもその人が", pair("reach", "stand"), ("a", "head", 6), "string"),
    P(1, "この先も変わらなかったら、", "このさきも変わらなかったら、", ("この先も", "変わらなかったら"), pair("reach", "stand"), ("a", "head", 4), "string"),
    P(1, "それでもあなたは、", "それでもあなたは、", "それでもあなたは", pair("reach", "stand"), ("a", "head", -10), "string"),
    P(1, "そばにいられますか。", "そばにいられますか。", "そばにいられますか", pair("reach", "stand"), ("a", "head", -6), "string"),
    P(2, "私たちは、相手の言葉に、", "わたしたちは、あいてのことばに、", ("私たちは", "相手の言葉に"), pair("reach", "stand"), ("a", "head", 8), "string", ("bubble:a", "radial:a")),
    P(2, "もう一言、足してしまう。", "もうひとこと、たしてしまう。", ("もう一言", "足してしまう"), pair("reach", "stand"), ("a", "arm"), "string", ("bubble:a", "radial:a")),
    P(2, "変わると信じて、", "変わるとしんじて、", "変わると信じて", pair("reach", "stand"), ("a", "head", 6), "string", ("radial:a",)),
    P(2, "待ってしまう。", "まってしまう。", "待ってしまう", pair("reach", "stand"), ("a", "head", 8), "string", ("radial:a",)),
    P(2, "昨日と同じ話を、", "きのうとおなじはなしを、", "昨日と同じ話を", pair("reach", "stand"), ("a", "arm"), "string", ("bubble:a",)),
    P(2, "今日も丁寧に繰り返す。", "きょうもていねいにくりかえす。", ("今日も丁寧に", "繰り返す"), pair("reach", "stand"), ("a", "head", 6), "string", ("bubble:a",)),
    P(2, "返事のない日も、", "へんじのないひも、", "返事のない日も", pair("reach", "stand"), ("a", "head", 8), "string", ("radial:a",)),
    P(2, "次の言葉を用意してしまう。", "つぎのことばをよういしてしまう。", ("次の言葉を", "用意してしまう"), pair("reach", "stand"), ("a", "to", "reach"), "string", ("radial:a",)),
    P(2, "相手は、自分のままで、", "あいては、じぶんのままで、", ("相手は", "自分のままで"), pair("reach", "easy"), ("b", "arm"), "string", ("note:b",)),
    P(2, "今日も笑っている。", "きょうもわらっている。", "今日も笑っている", pair("reach", "easy"), ("b", "arm"), "string", ("note:b",)),
    P(2, "変わらない人を、", "変わらないひとを、", "変わらない人を", pair("reach", "easy"), ("a", "head", 6), "string", ("note:b",)),
    P(2, "変えようとする夜が、", "かえようとするよるが、", "変えようとする夜が", pair("reach", "easy"), ("a", "head", 8), "string", ("radial:a",)),
    P(2, "続いていく。", "つづいていく。", "続いていく", pair("down", "easy"), ("a", "to", "down"), "string", ("note:b",)),
    P(2, "変えようとする手が、", "かえようとするてが、", ("変えようとする", "手が"), pair("reach", "easy"), ("a", "head", 12), "string", ("note:b",)),
    P(2, "先に疲れていく。", "さきにつかれていく。", "先に疲れていく", pair("reach", "easy"), ("a", "to", "down"), "string", ("note:b",)),
    P(3, "でも、変えるのをやめた日、", "でも、かえるのをやめたひ、", ("でも変えるのを", "やめた日"), pair("reach", "stand"), ("a", "to", "stand"), "string_fall"),
    P(3, "力が、ふっと抜けた。", "ちからが、ふっとぬけた。", ("力がふっと", "抜けた"), pair("stand", "stand"), ("a", "head", -12), "string_down"),
    P(3, "肩が、自分の位置に戻った。", "かたが、じぶんのいちにもどった。", ("肩が自分の", "位置に戻った"), pair("easy", "stand"), ("a", "to", "easy"), "string_down"),
    P(3, "相手が変わったんじゃなくて、", "あいてが変わったんじゃなくて、", ("相手が変わった", "んじゃなくて"), pair("stand", "stand"), ("a", "head", 4), "string_down"),
    P(3, "こちらが手を下ろした、", "こちらがてをおろした、", ("こちらが", "手を下ろした"), pair("stand", "stand"), ("a", "arm"), "string_down"),
    P(3, "だけなんだと思う。", "だけなんだと思う。", "だけなんだと思う", pair("stand", "stand"), ("a", "head", -6), "string_down"),
    P(4, "それは、あきらめというより、", "それは、あきらめというより、", ("それは", "あきらめというより"), pair("stand", "stand"), ("a", "head", -6), "string_down"),
    P(4, "ひとりの人に戻す、", "ひとりのひとに戻す、", ("ひとりの人に", "戻す"), pair("easy", "stand"), ("a", "to", "easy"), "string_down"),
    P(4, "ことなんだと思う。", "ことなんだと思う。", "ことなんだと思う", pair("easy", "stand"), ("a", "head", -4), "string_down"),
    P(4, "変えるのをやめるとは、", "かえるのをやめるとは、", ("変えるのを", "やめるとは"), pair("easy", "stand"), ("a", "head", -8), "string_down", ("sun",)),
    P(4, "自分の手へ戻す、", "じぶんのてへ戻す、", ("自分の手へ", "戻す"), pair("easy", "stand"), ("a", "arm"), "string_down", ("sun",)),
    P(4, "形なのかもしれない。", "かたちなのかもしれない。", "形なのかもしれない", pair("easy", "stand"), ("a", "head", -6), "string_down", ("sun",)),
]

# --- 3 ---------------------------------------------------------------

S3 = [
    P(1, "もしも、その人を、", "もしも、そのひとを、", "もしもその人を", pair("stand", "stand", far=True), ("a", "head", 4), "mark", ("dots",)),
    P(1, "悪者にしなくても、", "わるものにしなくても、", ("悪者に", "しなくても"), pair("stand", "stand", far=True), ("a", "head", 6), "mark", ("dots",)),
    P(1, "それでもあなたは、", "それでもあなたは、", "それでもあなたは", pair("stand", "stand", far=True), ("a", "head", -10), "mark", ("dots",)),
    P(1, "離れていられますか。", "はなれていられますか。", "離れていられますか", pair("stand", "stand", far=True), ("a", "head", -6), "mark", ("dots",)),
    P(2, "遠くの人を、私たちは、", "とおくのひとを、わたしたちは、", ("遠くの人を", "私たちは"), pair("reach", "stand", far=True), ("a", "to", "reach"), "mark", ("dots",)),
    P(2, "悪く言ってしまう。", "わるくいってしまう。", "悪く言ってしまう", pair("reach", "stand", far=True), ("a", "head", 6), "mark", ("dots",)),
    P(2, "悪く言ったあとで、", "わるくいったあとで、", "悪く言ったあとで", pair("down", "stand", far=True), ("a", "head", 8), "mark", ("dots",)),
    P(2, "胸のほうが痛くなる。", "むねのほうがいたくなる。", "胸のほうが痛くなる", pair("chest", "stand", far=True), ("a", "to", "chest"), "mark", ("dots",)),
    P(2, "ひどい人と思えれば、", "ひどいひととおもえれば、", ("ひどい人と", "思えれば"), pair("reach", "stand", far=True), ("a", "head", 8), "mark", ("dots", "radial:a")),
    P(2, "離れやすいから。", "はなれやすいから。", "離れやすいから", pair("reach", "stand", far=True), ("a", "head", -4), "mark", ("dots",)),
    P(2, "でも、思い出の顔は、", "でも、おもいでのかおは、", ("でも", "思い出の顔は"), pair("stand", "stand", far=True), ("a", "head", -8), "mark", ("dots",)),
    P(2, "悪くなりきらない。", "わるくなりきらない。", "悪くなりきらない", pair("stand", "stand", far=True), ("a", "head", 6), "mark", ("dots",)),
    P(2, "思い出の声のほうを、", "おもいでのこえのほうを、", "思い出の声のほうを", pair("stand", "stand", far=True), ("a", "head", -6), "mark", ("dots",)),
    P(2, "まだ信じてしまう。", "まだしんじてしまう。", "まだ信じてしまう", pair("stand", "stand", far=True), ("a", "head", 4), "mark", ("dots",)),
    P(2, "距離は、もう開いている。", "きょりは、もうひらいている。", ("距離はもう", "開いている"), pair("stand", "stand", far=True), ("a", "head", -4), "mark", ("dots",)),
    P(2, "距離は取ったのに、", "きょりはとったのに、", "距離は取ったのに", pair("stand", "stand", far=True), ("a", "head", 4), "mark", ("dots",)),
    P(2, "物語だけが終わらない。", "ものがたりだけがおわらない。", ("物語だけが", "終わらない"), pair("down", "stand", far=True), ("a", "head", 8), "mark", ("dots",)),
    P(2, "なのに心の中だけが、", "なのにこころのなかだけが、", ("なのに", "心の中だけが"), pair("down", "stand", far=True), ("a", "head", 8), "mark", ("dots",)),
    P(2, "悪者にしようとする。", "わるものにしようとする。", ("悪者に", "しようとする"), pair("reach", "stand", far=True), ("a", "to", "reach"), "mark", ("dots",)),
    P(3, "でも、悪者にしなくても、", "でも、わるものにしなくても、", ("でも悪者に", "しなくても"), pair("reach", "stand", far=True), ("a", "to", "stand"), "mark_fall", ("dots",)),
    P(3, "離れたままで、", "はなれたままで、", "離れたままで", pair("stand", "stand", far=True), ("a", "head", -8), "mark_down", ("arch:a", "dots")),
    P(3, "いいんだと思う。", "いいんだと思う。", "いいんだと思う", pair("stand", "stand", far=True), ("a", "head", -4), "mark_down", ("arch:a", "dots")),
    P(3, "距離は、罰じゃなくて、", "きょりは、ばつじゃなくて、", ("距離は", "罰じゃなくて"), pair("stand", "stand", far=True), ("a", "head", 4), "mark_down", ("arch:a", "dots")),
    P(3, "静かなあいだになる。", "しずかなあいだになる。", "静かなあいだになる", pair("up", "stand", far=True), ("a", "to", "up"), "mark_down", ("arch:a", "dots")),
    P(3, "相手を決めなくても、", "あいてをきめなくても、", ("相手を", "決めなくても"), pair("up", "stand", far=True), ("a", "head", -4), "mark_down", ("arch:a", "dots")),
    P(3, "戻らなくていい。", "もどらなくていい。", "戻らなくていい", pair("up", "stand", far=True), ("a", "head", -6), "mark_down", ("arch:a", "dots")),
    P(4, "それは、許したというより、", "それは、ゆるしたというより、", ("それは", "許したというより"), pair("stand", "stand", far=True), ("a", "head", -6), "mark_down", ("arch:a", "scatter:a")),
    P(4, "話を一つ閉じた、", "はなしをひとつとじた、", ("話を一つ", "閉じた"), pair("stand", "stand", far=True), ("a", "head", 4), "mark_down", ("arch:a", "scatter:a")),
    P(4, "形なんだと思う。", "かたちなんだと思う。", "形なんだと思う", pair("stand", "stand", far=True), ("a", "head", -4), "mark_down", ("arch:a", "scatter:a")),
    P(4, "嫌いじゃなくていいとは、", "きらいじゃなくていいとは、", ("嫌いじゃなくて", "いいとは"), pair("up", "stand", far=True), ("a", "head", -8), "none", ("arch:a", "scatter:a")),
    P(4, "距離のまま置く、", "きょりのままおく、", ("距離のまま", "置く"), pair("up", "stand", far=True), ("a", "head", 4), "none", ("dots", "scatter:a")),
    P(4, "形なのかもしれない。", "かたちなのかもしれない。", "形なのかもしれない", pair("up", "stand", far=True), ("a", "head", -6), "none", ("dots", "scatter:a")),
]

# --- 4 ---------------------------------------------------------------

S4 = [
    P(1, "もしも、いい人を、", "もしも、いいひとを、", "もしもいい人を", pair("open", "easy"), ("a", "arm"), "none", ("note:a",)),
    P(1, "やめたら、", "やめたら、", "やめたら", pair("open", "easy"), ("a", "head", 6), "none", ("note:a",)),
    P(1, "それでもあなたは、", "それでもあなたは、", "それでもあなたは", pair("open", "easy"), ("a", "head", -8), "none", ("note:a",)),
    P(1, "ここにいられますか。", "ここにいられますか。", "ここにいられますか", pair("open", "easy"), ("a", "head", -6), "none", ("note:a",)),
    P(2, "私たちは、断る前に、", "わたしたちは、ことわるまえに、", ("私たちは", "断る前に"), pair("open", "easy"), ("a", "head", 8), "none", ("note:a",)),
    P(2, "笑ってしまう。", "わらってしまう。", "笑ってしまう", pair("open", "easy"), ("a", "arm"), "none", ("note:a",)),
    P(2, "頼まれるたびに、いいえが、", "たのまれるたびに、いいえが、", ("頼まれるたびに", "いいえが"), pair("open", "easy"), ("a", "head", 6), "none", ("note:a",)),
    P(2, "喉の奥へ下がっていく。", "のどのおくへさがっていく。", ("喉の奥へ", "下がっていく"), pair("down", "easy"), ("a", "to", "down"), "none", ("note:a",)),
    P(2, "相手が困らないように、", "あいてがこまらないように、", ("相手が", "困らないように"), pair("open", "easy"), ("sym", "crumb"), "crumb_fall", ("note:a",)),
    P(2, "疲れを、うしろへ隠す。", "つかれを、うしろへかくす。", ("疲れを", "うしろへ隠す"), pair("open", "easy"), ("a", "head", 10), "crumb_ground", ("note:a",)),
    P(2, "いい人でいると、", "いいひとでいると、", "いい人でいると", pair("open", "easy"), ("b", "arm"), "crumb_ground", ("note:a",)),
    P(2, "頼みごとが、増えていく。", "たのみごとが、ふえていく。", ("頼みごとが", "増えていく"), pair("open", "easy"), ("b", "arm"), "crumb_ground", ("note:a",)),
    P(2, "ありがとうと言われるほど、", "ありがとうといわれるほど、", ("ありがとうと", "言われるほど"), pair("open", "easy"), ("a", "head", 6), "crumb_ground", ("note:a",)),
    P(2, "自分の疲れは、", "じぶんのつかれは、", "自分の疲れは", pair("open", "easy"), ("a", "head", 8), "crumb_ground", ("note:a",)),
    P(2, "見えなくなる。", "みえなくなる。", "見えなくなる", pair("down", "easy"), ("a", "to", "down"), "crumb_ground"),
    P(2, "でも、自分の声は、", "でも、じぶんのこえは、", "でも自分の声は", pair("down", "easy"), ("a", "head", 6), "crumb_ground"),
    P(2, "だんだん小さくなる。", "だんだんちいさくなる。", ("だんだん", "小さくなる"), pair("down", "easy"), ("a", "head", 8), "crumb_ground"),
    P(2, "誰かの安心と引きかえに、", "だれかのあんしんと引きかえに、", ("誰かの安心と", "引きかえに"), pair("down", "easy"), ("a", "head", 6), "crumb_fall"),
    P(2, "自分の今日が削れていく。", "じぶんのきょうがけずれていく。", ("自分の今日が", "削れていく"), pair("down", "easy"), ("sym", "crumb"), "crumb_fall"),
    P(3, "だから、失っていたのは、", "だから、うしなっていたのは、", ("だから", "失っていたのは"), solo("chest"), ("a", "head", 6), "crumb_hand"),
    P(3, "好かれることじゃなくて、", "すかれることじゃなくて、", ("好かれること", "じゃなくて"), solo("chest"), ("a", "head", 4), "crumb_hand"),
    P(3, "自分の声なんだと思う。", "じぶんのこえなんだと思う。", ("自分の声", "なんだと思う"), solo("chest"), ("a", "to", "chest"), "crumb_hand"),
    P(3, "優しさが外ばかりだと、", "やさしさがそとばかりだと、", ("優しさが", "外ばかりだと"), solo("down"), ("a", "head", 8), "crumb_hand"),
    P(3, "中のほうが、すいていく。", "なかのほうが、すいていく。", ("中のほうが", "すいていく"), solo("down"), ("a", "to", "down"), "crumb_hand"),
    P(4, "それは、いい人というより、", "それは、いいひとというより、", ("それは", "いい人というより"), solo("chest"), ("a", "head", -8), "crumb_hand"),
    P(4, "自分を後回しにした、", "じぶんをあとまわしにした、", ("自分を", "後回しにした"), solo("chest"), ("a", "head", 6), "crumb_hand"),
    P(4, "形なんだと思う。", "かたちなんだと思う。", "形なんだと思う", solo("chest"), ("a", "head", -4), "crumb_hand"),
    P(4, "いい人でいた時間とは、", "いいひとでいたじかんとは、", ("いい人でいた", "時間とは"), solo("chest"), ("a", "head", 6), "crumb_hand"),
    P(4, "自分のかけらを、", "じぶんのかけらを、", "自分のかけらを", solo("chest"), ("a", "to", "chest"), "crumb_hand"),
    P(4, "静かに渡してきた、", "しずかにわたしてきた、", ("静かに", "渡してきた"), solo("down"), ("a", "head", 6), "crumb_hand"),
    P(4, "形なのかもしれない。", "かたちなのかもしれない。", "形なのかもしれない", solo("down"), ("a", "head", -8), "crumb_hand"),
]

# --- 5 ---------------------------------------------------------------

S5 = [
    P(1, "もしも、お返しを、", "もしも、おかえしを、", "もしもお返しを", pair("reach", "stand"), ("a", "head", 4), "expect", ("gift:a",)),
    P(1, "待たなかったら、", "またなかったら、", "待たなかったら", pair("reach", "stand"), ("a", "head", 6), "expect", ("gift:a",)),
    P(1, "それでもあなたは、", "それでもあなたは、", "それでもあなたは", pair("reach", "stand"), ("a", "head", -8), "expect", ("gift:a",)),
    P(1, "渡し続けられますか。", "わたしつづけられますか。", "渡し続けられますか", pair("reach", "stand"), ("a", "head", -6), "expect", ("gift:a",)),
    P(2, "私たちは、渡したあとに、", "わたしたちは、わたしたあとに、", ("私たちは", "渡したあとに"), pair("reach", "stand"), ("a", "head", 8), "expect", ("gift:a",)),
    P(2, "相手の手を見てしまう。", "あいてのてをみてしまう。", ("相手の手を", "見てしまう"), pair("reach", "stand"), ("a", "head", 6), "expect", ("gift:a",)),
    P(2, "返ってくるまで、", "かえってくるまで、", "返ってくるまで", pair("reach", "stand"), ("a", "head", 4), "expect", ("gift:a", "q:a")),
    P(2, "胸のどこかが、", "むねのどこかが、", "胸のどこかが", pair("reach", "stand"), ("a", "to", "chest"), "expect", ("q:a",)),
    P(2, "開いたままになる。", "ひらいたままになる。", "開いたままになる", pair("chest", "stand"), ("a", "head", 6), "expect_chest", ("q:a",)),
    P(2, "それを、よくばりだと、", "それを、よくばりだと、", ("それを", "よくばりだと"), pair("down", "stand"), ("a", "head", 8), "expect", ("chain:a",)),
    P(2, "自分で責めてしまう。", "じぶんでせめてしまう。", ("自分で", "責めてしまう"), pair("down", "stand"), ("a", "to", "down"), "expect", ("chain:a",)),
    P(2, "何も返ってこない夜に、", "なにもかえってこないよるに、", ("何も返ってこない", "夜に"), pair("down", "stand"), ("a", "head", 8), "expect", ("chain:a", "q:a")),
    P(2, "自分を嫌いになりかける。", "じぶんをきらいになりかける。", ("自分を嫌いに", "なりかける"), pair("down", "stand"), ("a", "to", "squat"), "expect", ("chain:a",)),
    P(2, "嬉しさの記憶だけが、", "うれしさのきおくだけが、", "嬉しさの記憶だけが", pair("chest", "stand"), ("a", "head", -6), "expect_chest"),
    P(2, "残ってしまう。", "のこってしまう。", "残ってしまう", pair("chest", "stand"), ("a", "to", "chest"), "expect_chest"),
    P(2, "それでも次の日も、", "それでもつぎのひも、", "それでも次の日も", pair("reach", "stand"), ("a", "to", "reach"), "expect", ("gift:a",)),
    P(2, "また何かを渡してしまう。", "またなにかをわたしてしまう。", ("また何かを", "渡してしまう"), pair("reach", "stand"), ("a", "head", 4), "expect", ("gift:a",)),
    P(2, "でも、その気持ちは、", "でも、そのきもちは、", "でもその気持ちは", pair("down", "stand"), ("a", "head", -8), "expect", ("chain:a",)),
    P(2, "渡したあかしなんだと思う。", "わたしたあかしなんだと思う。", ("渡したあかし", "なんだと思う"), pair("chest", "stand"), ("a", "to", "chest"), "expect_chest"),
    P(3, "だから、待つ心は、", "だから、まつこころは、", "だから待つ心は", pair("down", "stand"), ("a", "head", -6), "expect", ("chain_fall:a",)),
    P(3, "ずるいんじゃなくて、", "ずるいんじゃなくて、", ("ずるいん", "じゃなくて"), pair("stand", "stand"), ("a", "to", "stand"), "expect"),
    P(3, "まっすぐなんだと思う。", "まっすぐなんだと思う。", "まっすぐなんだと思う", pair("stand", "stand"), ("a", "head", -8), "expect"),
    P(3, "渡したものが、", "わたしたものが、", "渡したものが", pair("chest", "stand"), ("a", "head", 4), "expect_chest"),
    P(3, "自分には大きかった。", "じぶんにはおおきかった。", "自分には大きかった", pair("chest", "stand"), ("a", "to", "chest"), "expect_chest"),
    P(3, "ただ、それだけ、", "ただ、それだけ、", "ただそれだけ", pair("chest", "stand"), ("a", "head", -4), "expect_chest"),
    P(3, "なんだと思う。", "なんだと思う。", "なんだと思う", pair("chest", "stand"), ("a", "head", -6), "expect_chest"),
    P(4, "それは、よくばりというより、", "それは、よくばりというより、", ("それは", "よくばりというより"), pair("chest", "stand"), ("a", "head", -6), "expect_chest"),
    P(4, "本気で渡していた、", "ほんきでわたしていた、", ("本気で", "渡していた"), pair("chest", "stand"), ("a", "head", 4), "expect_chest"),
    P(4, "形なんだと思う。", "かたちなんだと思う。", "形なんだと思う", pair("chest", "stand"), ("a", "head", -4), "expect_chest"),
    P(4, "見返りを待つとは、", "みかえりをまつとは、", ("見返りを", "待つとは"), pair("up", "stand"), ("a", "to", "up"), "expect_chest", ("scatter:a",)),
    P(4, "自分のやさしさを、", "じぶんのやさしさを、", "自分のやさしさを", pair("up", "stand"), ("a", "head", -4), "expect_chest", ("scatter:a",)),
    P(4, "まだ信じている、", "まだしんじている、", "まだ信じている", pair("up", "stand"), ("a", "head", 4), "expect_chest", ("scatter:a",)),
    P(4, "形なのかもしれない。", "かたちなのかもしれない。", "形なのかもしれない", pair("up", "stand"), ("a", "head", -8), "expect_chest", ("scatter:a",)),
]


STORIES = [
    {
        "id": "01",
        "slug": "01_嫌いになれないまま傷つく",
        "title": "嫌いになれないまま、傷つく",
        "red_label": "胸の赤い傷",
        "red_meaning": "嫌い切れないまま、何度でも触れてしまう心の傷",
        "symbols": [
            ("♪", "相手が、傷つけたことに気づいていないこと"),
            ("二人のあいだの点線", "離れたいのに、離れ切れない距離"),
            ("足元の鎖", "嫌い切れない気持ちが、足を縛っていること"),
            ("人を覆うアーチ", "自分で細くしている出口"),
            ("吹き出しの中の小さな人", "心の奥に、まだ置いている相手"),
        ],
        "closing": "嫌いになれないまま傷つくとは、まだその人を心に残している形なのかもしれない",
        "hashtag": "#人間関係",
        "phrases": S1,
    },
    {
        "id": "02",
        "slug": "02_変えるのをやめた日",
        "title": "変えるのを、やめた日",
        "red_label": "相手へ伸ばした赤い糸",
        "red_meaning": "変えたいという執着。やめた日、その糸は地面に置かれる",
        "symbols": [
            ("吹き出しの中の小さな人", "こうなってほしい、という理想の相手"),
            ("頭のまわりの短い線", "変わってほしい焦り"),
            ("♪", "相手は、自分のまま笑っていること"),
            ("小さな太陽", "手を下ろしたあとに残る、静かな軽さ"),
        ],
        "closing": "人を変えるのをやめるとは、自分の手を自分へ戻す形なのかもしれない",
        "hashtag": "#手放す",
        "phrases": S2,
    },
    {
        "id": "03",
        "slug": "03_離れた人を嫌わなくていい",
        "title": "離れた人を、嫌わなくていい",
        "red_label": "手にした赤いばつ印",
        "red_meaning": "離れた相手を悪者にするための印。貼らなくていい",
        "symbols": [
            ("二人のあいだの点線", "もう開いている距離"),
            ("頭のまわりの短い線", "悪者にしたくなる焦り"),
            ("人を覆うアーチ", "距離が、自分を守る静かな幅であること"),
            ("小さな点の散り", "印を下ろしたあとの、ほっとした解放"),
        ],
        "closing": "離れた人を嫌わなくていいとは、距離のまま置いておく形なのかもしれない",
        "hashtag": "#距離",
        "phrases": S3,
    },
    {
        "id": "04",
        "slug": "04_いい人のうしろ",
        "title": "いい人の、うしろで消えたもの",
        "red_label": "落ちていく赤いかけら",
        "red_meaning": "いい人でいるあいだに、自分からこぼれ落ちたもの",
        "symbols": [
            ("♪", "断る前に笑ってしまう、自分でも気づきにくい顔"),
        ],
        "closing": "いい人でいた時間とは、自分のかけらを静かに渡してきた形なのかもしれない",
        "hashtag": "#優しさ",
        "phrases": S4,
    },
    {
        "id": "05",
        "slug": "05_見返りを待つ心",
        "title": "見返りを、求めてしまう心",
        "red_label": "届かない赤い点線",
        "red_meaning": "返ってくるのを、そっと待ってしまう気持ち",
        "symbols": [
            ("手の中の白い丸", "相手に渡したもの"),
            ("？", "返ってこないことへの、小さな戸惑い"),
            ("手もとの鎖", "よくばりだと、自分を責めてしまうこと"),
            ("小さな点の散り", "責めるのをやめたあとに残る余白"),
        ],
        "closing": "見返りを待ってしまうとは、自分のやさしさをまだ信じている形なのかもしれない",
        "hashtag": "#気持ち",
        "phrases": S5,
    },
]


def sentences_of(phrases):
    groups = []
    cur = []
    for phrase in phrases:
        cur.append(phrase)
        if phrase["show"].endswith(("。", "？")):
            groups.append(cur)
            cur = []
    if cur:
        raise ValueError("文が句点で終わっていません: " + cur[-1]["show"])
    return groups


def manuscript(phrases) -> str:
    return "".join(p["show"] for p in phrases)


def validate(stories=None) -> list[str]:
    stories = STORIES if stories is None else stories
    errors = []
    allowed_red = {
        "none", "wound", "string", "string_fall", "string_down", "mark", "mark_fall",
        "mark_down", "crumb_fall", "crumb_ground", "crumb_hand", "expect", "expect_chest",
    }
    for story in stories:
        phrases = story["phrases"]
        try:
            groups = sentences_of(phrases)
        except ValueError as exc:
            errors.append(f"{story['id']}: {exc}")
            continue
        text = manuscript(phrases)
        n = len(text)
        if not 280 <= n <= 360:
            errors.append(f"{story['id']}: 原稿が{n}文字（目安300〜340）")
        if phrases[0]["act"] != 1 or phrases[-1]["act"] != 4:
            errors.append(f"{story['id']}: 幕が1から4まで通っていません")
        for i, phrase in enumerate(phrases, 1):
            if phrase["red"] not in allowed_red:
                errors.append(f"{story['id']}#{i}: 未知の赤 {phrase['red']}")
            if len(phrase["sub"]) > 2:
                errors.append(f"{story['id']}#{i}: 字幕が3行以上")
            for line in phrase["sub"]:
                if len(line) > 10:
                    errors.append(f"{story['id']}#{i}: 字幕「{line}」が{len(line)}文字")
                bad = [ch for ch in line if ch in PUNCT]
                if bad:
                    errors.append(f"{story['id']}#{i}: 字幕に句読点 {bad}")
            if len("".join(phrase["sub"])) > 20:
                errors.append(f"{story['id']}#{i}: 字幕が長すぎます")
            ids = {f[0] for f in phrase["figs"]}
            if phrase["action"] and phrase["action"][0] not in ids and phrase["action"][0] != "sym":
                errors.append(f"{story['id']}#{i}: 動きの相手が画面にいません")
            needs_b = phrase["red"] in {"string", "string_fall", "string_down", "expect", "expect_chest"} or "dots" in phrase["syms"]
            if needs_b and "b" not in ids:
                errors.append(f"{story['id']}#{i}: 二人必要な画面なのに一人です")
        # The hook should contain もしも and あなた.
        head = "".join(p["show"] for p in phrases if p["act"] == 1)
        if "もしも" not in head or "あなた" not in head:
            errors.append(f"{story['id']}: フックに「もしも」「あなた」がありません")
        story["_sentences"] = len(groups)
        story["_chars"] = n
    return errors


if __name__ == "__main__":
    errs = validate()
    for story in STORIES:
        print(f"\n===== {story['id']} {story['title']}  {story.get('_chars')}字 / {story.get('_sentences')}文 =====")
        print(manuscript(story["phrases"]))
    if errs:
        print("\nERRORS")
        for e in errs:
            print(" -", e)
        raise SystemExit(1)
    print("\nOK")
