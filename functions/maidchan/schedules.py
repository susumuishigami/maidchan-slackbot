from typing import Optional

from .tasks import 天気予報

OHAYO_MESSAGE = "ご主人様、お嬢様、おはようございます！{}今日もご主人様、お嬢様のご活躍を心より応援致します。＼(^o^)／"
OHIRU_MESSAGE = "ご主人様、お嬢様！只今 {} 時をお知らせします！お昼ご飯を召し上がってください。(^o^)"
OKAERI_MESSAGE = "ご主人様、お嬢様！只今 {} 時をお知らせします！今日もお疲れ様です！メイド一同ご主人様、お嬢様のお帰りをお待ちしています！（*´▽｀*）"
OYASUMI_MESSAGE = "ご主人様、お嬢様！只今 {} 時をお知らせします！そろそろお休みになられることをおすすめします。(つ∀-)"


def スケジュールされたお仕事をする(hour: int) -> Optional[str]:
    if hour == 8:
        return OHAYO_MESSAGE.format(天気予報().get_weather(130010, 0))

    if hour == 12:
        return OHIRU_MESSAGE.format(hour)

    if hour == 18:
        return OKAERI_MESSAGE.format(hour)

    if hour == 22:
        return OYASUMI_MESSAGE.format(hour)

    return None
