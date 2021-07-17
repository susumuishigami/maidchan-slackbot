import datetime
import json
import logging
import random
import re
import textwrap
import urllib
import urllib.request
from typing import Dict, List, Optional, Type

from . import settings

logger = logging.getLogger(__name__)

RequestBody = Dict[str, str]

朝のご挨拶 = "＼（⌒∇⌒）／ おはようごさいます！ <@{}> 様"
おやすみのご挨拶 = "(｡･ω･｡)ﾉ おやすみなさいませ。 <@{}> 様"
おかえりのご挨拶 = "おかえりなさいませ！ <@{}> 様 （*´▽｀*）"
いってらっしゃいのご挨拶 = "(★･∀･)ﾉ〃行ってらっしゃいませ！ <@{}> 様"
お疲れ様のセリフ = "お疲れ様です。 <@{}> 様 ＼(^o^)／"
本日の運勢 = """\
<@{}> 様の今日の運勢はこちらです！
{rank}位 {sign}
総合: {total}
恋愛運: {love}
金運: {money}
仕事運: {job}
ラッキーカラー: {color}
ラッキーアイテム: {item}
{content}"""
選んだよのセリフ = "どうしようかなあ。。。じゃあ {} が良いと思う！"
照れたときのメッセージリスト = ["ありがとう！ (〃'∇'〃)ゝｴﾍﾍ", "そんなことないよ！（*´▽｀*）"]
褒めるときのセリフ = "{誰}、{理由}んだ！すごーい！"
褒めるときのセリフ理由なし版 = "{誰}！すごーい！"

雑談お仕事リスト: List[Type] = []
お屋敷お仕事リスト: List[Type] = []


def 雑談カフェのお仕事をする(body: RequestBody) -> Optional[str]:
    """雑談カフェチャネルでのメイドちゃんのお仕事だよ！
    """

    text = body["text"]

    for お仕事 in 雑談お仕事リスト:
        if お仕事.呼び出し(text, body):
            return お仕事.やったよ(text, body)

    if "XXX" == text:  # pragma:nocover
        # 例外テスト
        print(10 / 0)

    return None


def お屋敷のお仕事をする(body: RequestBody) -> Optional[str]:
    """すべてのチャネルでのメイドちゃんのお仕事だよ！
    """

    text = body["text"]

    for お仕事 in お屋敷お仕事リスト:
        if お仕事.呼び出し(text, body):
            return お仕事.やったよ(text, body)

    return None


def 雑談カフェのお仕事(cls):
    雑談お仕事リスト.append(cls())
    return cls


def お屋敷のお仕事(cls):
    お屋敷お仕事リスト.append(cls())
    return cls


def 合言葉を探す(text: str, *keyword) -> bool:
    for k in keyword:
        if k in text:
            return True
    return False


@雑談カフェのお仕事
class どれがいいかな:
    """メイドちゃんが選んであげるよ！

    迷うことがあったら雑談カフェで私に行ってね！私が選んであげるよ！「いか、たこどっちがいいかな？」「赤　青　きいろどれがいいかな？」みたいに聞いてね！
    """

    def おしりを取る(self, text):
        for 読点 in ("", "？", "！", "。"):
            for いいかな in ("いいかな", "良いかな", "良いと思う", "いいと思う"):
                for どれ in ("どれ", "どっち", "どの子"):
                    おしり = f"{どれ}が{いいかな}{読点}"
                    if text.endswith(おしり):
                        return おしり

    def 呼び出し(self, text, body):
        return self.おしりを取る(text) is not None

    def やったよ(self, text, body):
        言葉のおしり = self.おしりを取る(text)
        選択肢 = text[: -len(言葉のおしり)].replace("、", " ").split()
        選んだもの = random.choice(選択肢)
        return 選んだよのセリフ.format(選んだもの)


@雑談カフェのお仕事
class 可愛い:
    """褒められると嬉しくなっちゃって、お屋敷の秘密教えちゃうかも！
    """

    def 呼び出し(self, text, body):
        return ("かわいい" in text or "可愛い" in text) and settings.メイドちゃんの名前 in text

    def やったよ(self, text, body):
        返事 = random.choice(照れたときのメッセージリスト)
        if random.randint(1, 10) > 3:
            # 70%の確率でメイドちゃんが機能を教えてくれる
            返事 += "\n" + textwrap.dedent(random.choice(雑談お仕事リスト + お屋敷お仕事リスト).__doc__)
        return 返事


@雑談カフェのお仕事
class 占って:
    """雑談カフェでご主人様、お嬢様の今日の運勢を占ってあげるよ！
    
    `占って！` のあとに数字4桁で誕生日を書いてね！例えば `占って！0101` みたいに言ってね！
    """

    def _call_uranai_api(self, today):  # pragma: nocover
        response = urllib.request.urlopen(
            "http://api.jugemkey.jp/api/horoscope/free/{}".format(today)
        )
        return json.loads(response.read().decode("utf8"))

    def 占い(self, user_id, birthday):
        # The 占い() function is:
        #
        #    Copyright (c) 2016 beproud
        #    https://github.com/beproud/beproudbot
        JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
        今日 = datetime.datetime.now(tz=JST).strftime("%Y/%m/%d")
        data = self._call_uranai_api(今日)
        d = data["horoscope"][今日][self._calc_index(birthday)]
        for s in ["total", "love", "money", "job"]:
            d[s] = self.お星様きらり(d[s])
        return 本日の運勢.format(user_id, **d)

    @staticmethod
    def _calc_index(birthday):
        if birthday.endswith("座"):
            # 星座入力の場合
            # おひつじ てんびん みずがめ are shorten because len(birthday) == 4
            星座 = {
                "ひつじ": 0,
                "おうし": 1,
                "ふたご": 2,
                "おとめ": 5,
                "んびん": 6,
                "さそり": 7,
                "ずがめ": 10,
            }.get(birthday[-4:-1])
            if isinstance(星座, int):
                return 星座
            星座 = {
                "牡羊": 0,
                "牡牛": 1,
                "双子": 2,
                "かに": 3,
                "しし": 4,
                "獅子": 4,
                "乙女": 5,
                "天秤": 6,
                "いて": 8,
                "射手": 8,
                "やぎ": 9,
                "山羊": 9,
                "水瓶": 10,
                "うお": 11,
            }.get(birthday[-3:-1])
            if isinstance(星座, int):
                return 星座
            星座 = {
                "蟹": 3,
                "蠍": 7,
                "魚": 11,
            }.get(birthday[-2:-1])
            if isinstance(星座, int):
                return 星座
        # 誕生日入力の場合
        月, 日 = int(birthday[:2]), int(birthday[2:])
        区切り = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 23]
        星座 = (月 + 8 + (日 >= 区切り[(月 - 1) % 12])) % 12
        return 星座

    def お星様きらり(self, n):
        # The お星様きらり:star() function is:
        #
        #    Copyright (c) 2016 beproud
        #    https://github.com/beproud/beproudbot
        return "★" * n + "☆" * (5 - n)

    def 呼び出し(self, text, body):
        return text.startswith("占って！")

    def やったよ(self, text, body):
        birthday = text[-4:]
        return self.占い(body.get("user_id"), birthday)


@雑談カフェのお仕事
class おはよう:
    """おはようのご挨拶をするよ！

    朝起きたら雑談カフェで一言言ってね！
    """

    def 呼び出し(self, text, body):
        return 合言葉を探す(text, "おはよう", "おはよー")

    def やったよ(self, text, body):
        return 朝のご挨拶.format(body.get("user_id"))


@雑談カフェのお仕事
class おやすみ:
    """おやすみのご挨拶をするよ！

    ご就寝前に雑談カフェで一言言ってね！
    """

    def 呼び出し(self, text, body):
        return 合言葉を探す(text, "おやすみ", "お休み", "寝")

    def やったよ(self, text, body):
        return おやすみのご挨拶.format(body.get("user_id"))


@雑談カフェのお仕事
class おかえり:
    """ご帰宅のご主人様、お嬢様をお出迎えするよ。

    帰ったら雑談カフェで言ってね！
    """

    def 呼び出し(self, text, body):
        return 合言葉を探す(text, "帰", "ただいま", "きたく", "かえる")

    def やったよ(self, text, body):
        return おかえりのご挨拶.format(body.get("user_id"))


@雑談カフェのお仕事
class 円周率言って:
    """メイドちゃんは円周率を言うのが得意だよ！

    「ぱい」は円周率のことだよね！
    """

    def 呼び出し(self, text, body):
        if "円周率" in text and "おしえて" in text:
            return True
        if "ぱい" in text or "パイ" in text or "π" in text:
            return True
        return False

    def やったよ(self, text, body):
        return "3.1415926535897932384626433832795028841971693993"


@雑談カフェのお仕事
class お疲れ様:
    """おつかれのご主人様、お嬢様をねぎらってあげるよ。

    疲れたら雑談カフェで言ってね！
    """

    def 呼び出し(self, text, body):
        return 合言葉を探す(text, "疲", "つかれ", "終", "おわた", "おわった")

    def やったよ(self, text, body):
        return お疲れ様のセリフ.format(body.get("user_id"))


@雑談カフェのお仕事
class 行ってらっしゃい:
    """ご主人様、お嬢様をお見送りするよ！

    お出かけするときは `行ってきます` `いってきます` `出発` って雑談カフェで言ってね！
    """

    def 呼び出し(self, text, body):
        return 合言葉を探す(text, "行ってきます", "いってきます", "出かけ", "行きます", "いきます", "出発")

    def やったよ(self, text, body):
        return いってらっしゃいのご挨拶.format(body.get("user_id"))


@お屋敷のお仕事
class 褒めて:
    """頑張ってる人をメイドちゃんが褒めてあげるよ！

    `メイドちゃん！` で始まって `褒めて！` で終わるように話しかけてね！
    間に @ メンションがあるとその人を褒めてあげるよ！
    誰もメンションがなければあなたを褒めるよ！でも `僕を` `私を` `俺を` 褒めてって言ってくれると嬉しいな。
    理由も書いてね☆
    私、どのチャネルにでも駆けつけるよ！
    """

    def 呼び出し(self, text, body):
        return text.startswith("メイドちゃん！") and text.endswith("褒めて！")

    def やったよ(self, text, body):
        return self.褒める(text[len("メイドちゃん！") : -len("褒めて") - 1], body.get("user_id"))

    def 褒める(self, text, user_id):
        誰 = ""
        for m in re.finditer("<(.+?)>", text):
            誰 += f"<{m.group(1)}>さん"
        if text.endswith("僕を") or text.endswith("私を") or text.endswith("俺を"):
            誰 = f"<@{user_id}>さん"
            text = text[0:-2]
        if not 誰:
            誰 = f"<@{user_id}>さん"
        理由 = text
        for m in reversed(list(re.finditer("<(.+?)>", text))):
            理由 = 理由[0 : m.start()] + 理由[m.end() :]

        if 理由.endswith("を"):
            理由 = 理由[0:-1]

        if 理由.endswith("の"):
            理由 = 理由[0:-1] + "な"

        誰 = 誰.strip()
        理由 = 理由.strip()

        if 理由:
            return 褒めるときのセリフ.format(誰=誰, 理由=理由)
        else:
            return 褒めるときのセリフ理由なし版.format(誰=誰)


@お屋敷のお仕事
class 天気予報:
    """メイドちゃんが天気予報をするよ！

    `メイドちゃん！` で始まって `天気を教えて！` で終わるように話しかけると、メイドちゃんが天気を教えてあげるよ！
    「大阪の天気を教えて！」みたいに、メイドちゃんの知ってる都市の名前を言ってくれると、その地域の天気を教えるよ！
    メイドちゃんの知らない都市だったら、東京の天気を教えるね (^^;

    `今日` 、 `明日` 、 `明後日` の天気が教えられるよ！
    いつの天気か言わなかったら、時間帯に応じて今日か明日の天気を教えるね！

    """

    def _call_weather_api(self, city):  # pragma: nocover
        response = urllib.request.urlopen(
            # APIキーが必要ないlivedoor互換のAPIを使用する
            # thanks weather.tsukumijima.net
            f"https://weather.tsukumijima.net/api/forecast?city={city}"
        )
        data = json.loads(response.read().decode("utf8"))
        return data

    def get_weather(self, city, forecasts_index):
        """天気予報APIを呼び出して結果を読み込む
        """

        try:
            data = self._call_weather_api(city)
            dateLabel = "いつか分からない日"
            location = "どこか分からない場所"
            telop = "わかりません"
            temperature = "わかりません"
            try:
                dateLabel = data["forecasts"][forecasts_index]["dateLabel"]
                location = data["location"]["district"]
                telop = data["forecasts"][forecasts_index]["telop"]
                temperature = (
                    data["forecasts"][forecasts_index]["temperature"]["max"]["celsius"]
                    + "度"
                )
            except Exception:
                logger.exception("Exception when getting weather")
                pass
            message = "{}の{}の天気は *{}* 、最高気温は {} です！".format(
                dateLabel, location, telop, temperature
            )

            # 降水確率が取れなかったのでとりあえず、天気に「雨」や「雪」が入ってたら傘を持てという
            if "雨" in telop or "雪" in telop:
                message += " *傘を忘れないで!!* "
            return message
        except Exception:
            logger.exception("Exception when getting weather")
            return "今日の天気は分かりません(;_;)"

    def 呼び出し(self, text, body):
        return text.startswith("メイドちゃん！") and text.endswith("天気を教えて！")

    def やったよ(self, text, body):
        # 今何時かを調べる
        JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
        now = datetime.datetime.now(JST)
        hour = now.hour

        forecasts_index = 0
        # 18時以降は明日の天気
        if hour >= 18:
            forecasts_index = 1

        # 指定したら今日・明日・明後日の天気
        for date_label, date_forecasts_index in [
            ("今日", 0),
            ("明日", 1),
            ("明後日", 2),
        ]:
            if date_label in text:
                forecasts_index = date_forecasts_index

        # メイドちゃんの知ってる都市
        city = "130010"  # 東京
        for city_name, city_id in [
            ("大阪", "270000"),
            ("名古屋", "230010"),
            ("福岡", "400010"),
            ("仙台", "040010"),
            ("札幌", "016010"),
        ]:
            if city_name in text:
                city = city_id

        return self.get_weather(city, forecasts_index)
