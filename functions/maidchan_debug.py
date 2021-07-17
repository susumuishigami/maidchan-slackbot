from maidchan import settings
from maidchan.tasks import お屋敷のお仕事をする, 雑談カフェのお仕事をする

if __name__ == "__main__":
    settings.メイドちゃんの名前 = "メイドちゃん"

    while True:
        user_input = input("> ")
        if not user_input:
            break

        body = {"user_id": "00000000", "text": user_input}
        print(お屋敷のお仕事をする(body) or 雑談カフェのお仕事をする(body))
