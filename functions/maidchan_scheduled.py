import datetime
import json
import logging
import urllib
from typing import Any, Dict

from maidchan import settings
from maidchan.schedules import スケジュールされたお仕事をする

logger = logging.getLogger(__name__)


def scheduled_handler(event, context):
    print("scheduled event: ", event)
    JST = datetime.timezone(datetime.timedelta(hours=+9), "JST")
    now = datetime.datetime.now(JST)
    hour = now.hour
    message = スケジュールされたお仕事をする(hour)
    if message:
        send(message)


def request_webhook(obj: Dict[str, Any]):
    logger.info("send message", obj)
    headers = {"Content-Type": "application/json"}
    json_data = json.dumps(obj).encode("utf-8")
    request = urllib.request.Request(
        settings.メイドちゃん発言用URL,
        data=json_data,
        method="POST",
        headers=headers,
    )
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
        response_body


def send(text):
    request_webhook({"text": text})
