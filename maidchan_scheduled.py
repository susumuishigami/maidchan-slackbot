import json
import urllib
import datetime
import os


WEBHOOK_URL = os.environ['WEBHOOK_URL']


OHAYO_MESSAGE = '<!here> ご主人様、お嬢様、おはようございます！只今 {} 時をお知らせします！今日もご主人様、お嬢様のご活躍メイド一同心より応援致します。＼(^o^)／'
OHIRU_MESSAGE = '<!here> ご主人様、お嬢様！只今 {} 時をお知らせします！お昼休みのお時間です。(^o^)'
OKAERI_MESSAGE = '<!here> ご主人様、お嬢様！只今 {} 時をお知らせします！今日もお疲れ様です！メイド一同ご主人様、お嬢様のお帰りをお待ちしています！（*´▽｀*）'
OYASUMI_MESSAGE = '<!here> ご主人様、お嬢様！只今 {} 時をお知らせします！明日も早いですのでそろそろお休みになられることをおすすめします。(つ∀-)'


def scheduled_handler(event, context):
    print("scheduled event: ", event)
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    now = datetime.datetime.now(JST)
    hour = now.hour
    
    if hour == 8:
        message(OHAYO_MESSAGE.format(hour))

    if hour == 12:
        message(OHIRU_MESSAGE.format(hour))
        
    if hour == 18:
        message(OKAERI_MESSAGE.format(hour))

    if hour == 22:
        message(OYASUMI_MESSAGE.format(hour))
    
    
def message(text):
    obj = {"text": text}
    print('send message', obj)
    headers = {"Content-Type" : "application/json"}
    json_data = json.dumps(obj).encode("utf-8")
    request = urllib.request.Request(WEBHOOK_URL, data=json_data, method='POST', headers=headers)
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
        print("response event: " + response_body)
    
   