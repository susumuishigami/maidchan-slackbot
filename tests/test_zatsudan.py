import random
from unittest import mock

import freezegun
import pytest


@pytest.fixture
def target():
    from maidchan.tasks import 雑談カフェのお仕事をする

    return 雑談カフェのお仕事をする


@pytest.mark.parametrize(
    "text, expected",
    [
        ("おはよう", "＼（⌒∇⌒）／ おはようごさいます！ <@00000000> 様"),
        ("おやすみ", "(｡･ω･｡)ﾉ おやすみなさいませ。 <@00000000> 様"),
        ("寝ちゃった", "(｡･ω･｡)ﾉ おやすみなさいませ。 <@00000000> 様"),
        ("ただいま", "おかえりなさいませ！ <@00000000> 様 （*´▽｀*）"),
        ("いってきます", "(★･∀･)ﾉ〃行ってらっしゃいませ！ <@00000000> 様"),
        ("疲れた", "お疲れ様です。 <@00000000> 様 ＼(^o^)／"),
        ("終わった", "お疲れ様です。 <@00000000> 様 ＼(^o^)／"),
        ("円周率おしえて", "3.1415926535897932384626433832795028841971693993"),
        ("ぱい", "3.1415926535897932384626433832795028841971693993"),
        ("あはははあｈｖうぇｊｐｒｇｓｄｖ", None),  # 無関係なメッセージ
    ],
)
def test_text_response(target, text, expected):
    """テキストに対するレスポンスが仕様通りであること
    """
    actual = target({"user_id": "00000000", "text": text})
    assert actual == expected


def test_choice(target):
    """選ぶ機能が仕様通りの結果を返すこと

    内部で乱数を使っているのでseedを0に固定して結果を付き合わせる
    """
    random.seed(0)
    actual = target({"user_id": "00000000", "text": "いか、たこどっちがいいかな？"})
    assert actual == "どうしようかなあ。。。じゃあ たこ が良いと思う！"


@pytest.mark.parametrize(
    "random_seed, expected",
    [
        (0, "そんなことないよ！（*´▽｀*）"),
        (1, "ありがとう！ (〃'∇'〃)ゝｴﾍﾍ"),
    ],
)
def test_kawaii(target, random_seed, expected):
    """メイドちゃん可愛い機能が仕様通りの結果を返すこと

    内部で乱数を使っているのでseedを0に固定して結果を付き合わせる。
    また「お屋敷の秘密」部分についてはテスト対象とせず、前方一致で確認する。
    """
    random.seed(random_seed)
    actual = target({"user_id": "00000000", "text": "メイドちゃん！可愛い！"})
    assert actual.startswith(expected)


@freezegun.freeze_time("2021-07-18")
def test_uranai(target):
    """占い機能が仕様通りの結果を返すこと

    外部APIを使っているので結果はモックのレスポンスを使用して付き合わせる
    """
    with mock.patch("maidchan.tasks.占って._call_uranai_api") as mock_call_uranai_api:
        mock_call_uranai_api.return_value = {
            "horoscope": {
                "2021/07/18": {
                    7: {
                        "rank": 1,
                        "sign": "蠍座",
                        "total": 1,
                        "love": 2,
                        "money": 3,
                        "job": 4,
                        "color": "透明",
                        "item": "メイド服",
                        "content": "今日はいいことがあるでしょう！",
                    }
                }
            }
        }
        actual = target({"user_id": "00000000", "text": "占って！1116"})
    assert (
        actual
        == """\
<@00000000> 様の今日の運勢はこちらです！
1位 蠍座
総合: ★☆☆☆☆
恋愛運: ★★☆☆☆
金運: ★★★☆☆
仕事運: ★★★★☆
ラッキーカラー: 透明
ラッキーアイテム: メイド服
今日はいいことがあるでしょう！"""
    )
