from os import environ
from typing import List


def env_list(name, default=[]) -> List[str]:
    if environ.get(name):
        return environ[name].split(",")
    return default


雑談カフェのトークン = env_list("ZATSUDAN_TOKEN")
お屋敷のトークン = env_list("ALL_TOKEN")
メイドちゃんの名前 = environ.get("MAIDNAME", "メイドちゃん")