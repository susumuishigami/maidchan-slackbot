import json
import logging
import urllib.request
from typing import Any, Dict, Optional

from maidchan import settings
from maidchan.tasks import お屋敷のお仕事をする, 雑談カフェのお仕事をする

logger = logging.getLogger(__name__)

ParsedBody = Dict[str, str]
ResponseBody = Dict[str, Any]


def http_handler(event, context) -> Optional[ResponseBody]:
    body = parse_body(event)
    return maidchan_handle_message(body)


def maidchan_handle_message(body: ParsedBody) -> Optional[ResponseBody]:
    """メッセージ本文を元にメイドちゃんを制御する"""
    try:
        if is_bot_message(body):
            return None  # 無限ループ対策
        if is_empty_message(body):
            return None

        if is_zatsudan_cafe_message(body):
            logger.debug("zatsudan token recieved: %s", body)
            message = 雑談カフェのお仕事をする(body)
            if message:
                return say(message)

        if is_oyashiki_message(body):
            logger.debug("all_message recieved: %s", body)
            message = お屋敷のお仕事をする(body)
            if message:
                return say(message)

        return None

    except Exception as e:
        logger.exception("Error occurred in http_handler")
        return say(f"(ﾉД`)ご主人様助けて〜シクシク {e} だよー")


def parse_body(event) -> ParsedBody:
    """メッセージ本文を解釈する"""
    return {k: v for k, v in urllib.parse.parse_qsl(event["body"])}


def is_bot_message(body: ParsedBody) -> bool:
    """botからのメッセージか？"""
    return body.get("user_id") == "USLACKBOT"


def is_empty_message(body: ParsedBody) -> bool:
    """空のメッセージか？"""
    return body.get("text") is None


def is_zatsudan_cafe_message(body: ParsedBody) -> bool:
    """雑談カフェに送信されたメッセージか？"""
    return body.get("token") in settings.雑談カフェのトークン


def is_oyashiki_message(body: ParsedBody) -> bool:
    """お屋敷に送信されたメッセージか？"""
    return body.get("token") in settings.お屋敷のトークン


def respond(status: int, res: ResponseBody) -> ResponseBody:
    """Slackに返却するオブジェクトに変換する"""
    print("respond:", res)
    return {
        "statusCode": status,
        "body": json.dumps(res),
        "headers": {
            "Content-Type": "application/json",
        },
    }


def say(text) -> ResponseBody:
    """Slackにメッセージを返却するオブジェクトを生成する

    :param text: メイドちゃんが応答するメッセージ
    """
    return respond(
        200,
        {"text": text, "username": settings.メイドちゃんの名前, "icon_emoji": ":maidchan:"},
    )
