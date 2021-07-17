from unittest import mock

import freezegun
import pytest


@pytest.fixture
def target():
    from maidchan.schedules import スケジュールされたお仕事をする

    return スケジュールされたお仕事をする


OHAYO_MESSAGE = "ご主人様、お嬢様、おはようございます！{}今日もご主人様、お嬢様のご活躍を心より応援致します。＼(^o^)／"
OHIRU_MESSAGE = "ご主人様、お嬢様！只今 {} 時をお知らせします！お昼ご飯を召し上がってください。(^o^)"
OKAERI_MESSAGE = "ご主人様、お嬢様！只今 {} 時をお知らせします！今日もお疲れ様です！メイド一同ご主人様、お嬢様のお帰りをお待ちしています！（*´▽｀*）"
OYASUMI_MESSAGE = "ご主人様、お嬢様！只今 {} 時をお知らせします！そろそろお休みになられることをおすすめします。(つ∀-)"


@pytest.mark.parametrize(
    "hour, expected",
    [
        (0, None),
        (7, None),
        (8, "ご主人様、お嬢様、おはようございます！今日の天気は分かりません(;_;)今日もご主人様、お嬢様のご活躍を心より応援致します。＼(^o^)／"),
        (9, None),
        (11, None),
        (12, "ご主人様、お嬢様！只今 12 時をお知らせします！お昼ご飯を召し上がってください。(^o^)"),
        (13, None),
        (17, None),
        (18, "ご主人様、お嬢様！只今 18 時をお知らせします！今日もお疲れ様です！メイド一同ご主人様、お嬢様のお帰りをお待ちしています！（*´▽｀*）"),
        (19, None),
        (21, None),
        (22, "ご主人様、お嬢様！只今 22 時をお知らせします！そろそろお休みになられることをおすすめします。(つ∀-)"),
        (23, None),
    ],
)
def test_schedule(target, hour, expected):
    """時刻に対するメイドちゃんのメッセージが仕様通りの内容であること

    天気予報については、APIがエラーを返す場合のケースでテストをする
    """
    with mock.patch("maidchan.tasks.天気予報._call_weather_api") as mock_call_weather_api:
        mock_call_weather_api.side_effect = Exception
        actual = target(hour)

    assert actual == expected
