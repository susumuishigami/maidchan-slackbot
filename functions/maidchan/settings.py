import logging
from os import environ
from typing import List


def env_list(name, default=[]) -> List[str]:
    if environ.get(name):
        return environ[name].split(",")
    return default


雑談カフェのトークン = env_list("ZATSUDAN_TOKEN")
お屋敷のトークン = env_list("ALL_TOKEN")
メイドちゃんの名前 = environ.get("MAIDNAME", "メイドちゃん")
メイドちゃん発言用URL = environ.get("WEBHOOK_URL")


logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    level=logging.INFO,
    force=True,
)
