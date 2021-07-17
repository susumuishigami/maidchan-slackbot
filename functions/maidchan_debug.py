from maidchan import settings
from maidchan.schedules import スケジュールされたお仕事をする
from maidchan.tasks import お屋敷のお仕事をする, 雑談カフェのお仕事をする


def scheduled_task(user_input):
    """数字だけ入力された時はスケジュールされたイベントを実行する
    """
    try:
        hour = int(user_input)
    except TypeError:
        return None
    return スケジュールされたお仕事をする(hour)


if __name__ == "__main__":
    settings.メイドちゃんの名前 = "メイドちゃん"

    while True:
        user_input = input("> ")
        if not user_input:
            break

        body = {"user_id": "00000000", "text": user_input}
        print(お屋敷のお仕事をする(body) or 雑談カフェのお仕事をする(body) or scheduled_task(user_input))
