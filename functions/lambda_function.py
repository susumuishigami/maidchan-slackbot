import json
import traceback

print("Loading function")


def lambda_handler(event, context):
    if "POST" == event.get("httpMethod"):
        from maidchan_http import http_handler

        return http_handler(event, context)

    if "aws.events" == event.get("source"):
        from maidchan_scheduled import scheduled_handler

        return scheduled_handler(event, context)

    print("Unknown Event")
