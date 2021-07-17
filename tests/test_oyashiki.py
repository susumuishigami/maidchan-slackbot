from unittest import mock

import freezegun
import pytest


@pytest.fixture
def target():
    from maidchan.tasks import お屋敷のお仕事をする

    return お屋敷のお仕事をする


@pytest.mark.parametrize(
    "text, expected",
    [
        ("メイドちゃん！褒めて！", "<@00000000>さん！すごーい！"),
        ("メイドちゃん！私を褒めて！", "<@00000000>さん！すごーい！"),
        ("メイドちゃん！頑張った僕を褒めて！", "<@00000000>さん、頑張ったんだ！すごーい！"),
        ("メイドちゃん！テストで一位の僕を褒めて！", "<@00000000>さん、テストで一位なんだ！すごーい！"),
        ("メイドちゃん！早起きした<@00000001>を褒めて！", "<@00000001>さん、早起きしたんだ！すごーい！"),
        ("あはははあｈｖうぇｊｐｒｇｓｄｖ", None),  # 無関係なメッセージ
    ],
)
def test_text_response(target, text, expected):
    """テキストに対するレスポンスが仕様通りであること"""
    actual = target({"user_id": "00000000", "text": text})
    assert actual == expected


@pytest.mark.parametrize(
    "text, expected",
    [
        ("メイドちゃん！今日の天気を教えて！", "今日の秋葉原地方の天気は *晴れ* 、最高気温は 30度 です！"),
        ("メイドちゃん！明日の天気を教えて！", "明日の秋葉原地方の天気は *曇り* 、最高気温は 20度 です！"),
        ("メイドちゃん！明後日の天気を教えて！", "明後日の秋葉原地方の天気は *雨* 、最高気温は 10度 です！ *傘を忘れないで!!* "),
    ],
)
def test_weather_by_date_label(target, text, expected):
    """天気予報機能で今日、明日、明後日の指定が正しくできること"""
    with mock.patch("maidchan.tasks.天気予報._call_weather_api") as mock_call_weather_api:
        mock_call_weather_api.return_value = {
            "forecasts": {
                0: {
                    "dateLabel": "今日",
                    "telop": "晴れ",
                    "temperature": {"max": {"celsius": "30"}},
                },
                1: {
                    "dateLabel": "明日",
                    "telop": "曇り",
                    "temperature": {"max": {"celsius": "20"}},
                },
                2: {
                    "dateLabel": "明後日",
                    "telop": "雨",
                    "temperature": {"max": {"celsius": "10"}},
                },
            },
            "location": {"district": "秋葉原地方"},
        }
        actual = target({"user_id": "00000000", "text": text})
    assert actual == expected


@pytest.mark.parametrize(
    "time, expected",
    [
        ("08:00:00+09:00", "今日の秋葉原地方の天気は *晴れ* 、最高気温は 30度 です！"),
        ("17:59:59+09:00", "今日の秋葉原地方の天気は *晴れ* 、最高気温は 30度 です！"),
        ("18:00:00+09:00", "明日の秋葉原地方の天気は *曇り* 、最高気温は 20度 です！"),
        ("20:00:00+09:00", "明日の秋葉原地方の天気は *曇り* 、最高気温は 20度 です！"),
    ],
)
def test_weather_by_current_time(target, time, expected):
    """天気予報機能で現在時刻に応じて、今日か明日のとりわけが正しくできること"""
    with freezegun.freeze_time("2021-07-18 " + time) as _, mock.patch(
        "maidchan.tasks.天気予報._call_weather_api"
    ) as mock_call_weather_api:
        mock_call_weather_api.return_value = {
            "forecasts": {
                0: {
                    "dateLabel": "今日",
                    "telop": "晴れ",
                    "temperature": {"max": {"celsius": "30"}},
                },
                1: {
                    "dateLabel": "明日",
                    "telop": "曇り",
                    "temperature": {"max": {"celsius": "20"}},
                },
            },
            "location": {"district": "秋葉原地方"},
        }
        actual = target({"user_id": "00000000", "text": "メイドちゃん！天気を教えて！"})
    assert actual == expected


def test_weather_responded_error(target):
    """天気予報機能でAPIエラーの時の挙動が仕様通りであること"""
    with mock.patch("maidchan.tasks.天気予報._call_weather_api") as mock_call_weather_api:
        mock_call_weather_api.side_effect = Exception
        actual = target({"user_id": "00000000", "text": "メイドちゃん！天気を教えて！"})
    assert actual == "今日の天気は分かりません(;_;)"


def test_weather_by_unknown_response(target):
    """天気予報機能でAPIのレスポンスが想定外の形式の時のメッセージが仕様通りであること"""
    with mock.patch("maidchan.tasks.天気予報._call_weather_api") as mock_call_weather_api:
        mock_call_weather_api.return_value = {
            "forecasts": {
                0: {
                    "dateLabel": "今日",
                }
            },
            "location": {"district": "秋葉原地方"},
        }
        actual = target({"user_id": "00000000", "text": "メイドちゃん！今日の天気を教えて！"})
    assert actual == "今日の秋葉原地方の天気は *わかりません* 、最高気温は わかりません です！"


@pytest.mark.parametrize(
    "text, city_id",
    [
        ("メイドちゃん！今日の大阪の天気を教えて！", "270000"),
        ("メイドちゃん！今日の仙台の天気を教えて！", "040010"),
        ("メイドちゃん！今日の天気を教えて！", "130010"),
    ],
)
def test_weather_by_city(target, text, city_id):
    """天気予報機能で都市の指定が正しくできること"""
    with mock.patch("maidchan.tasks.天気予報._call_weather_api") as mock_call_weather_api:
        mock_call_weather_api.return_value = {
            "forecasts": {
                0: {
                    "dateLabel": "今日",
                    "telop": "晴れ",
                    "temperature": {"max": {"celsius": "30"}},
                },
            },
            "location": {"district": "秋葉原地方"},
        }
        target({"user_id": "00000000", "text": text})
        mock_call_weather_api.assert_called_with(city_id)
