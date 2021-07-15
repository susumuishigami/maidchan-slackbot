import json
import urllib
import datetime
import os


testing = False


WEBHOOK_URL = os.environ['WEBHOOK_URL']


OHAYO_MESSAGE = 'ご主人様、お嬢様、おはようございます！{}今日もご主人様、お嬢様のご活躍を心より応援致します。＼(^o^)／'
OHIRU_MESSAGE = 'ご主人様、お嬢様！只今 {} 時をお知らせします！お昼ご飯を召し上がってください。(^o^)'
OKAERI_MESSAGE = 'ご主人様、お嬢様！只今 {} 時をお知らせします！今日もお疲れ様です！メイド一同ご主人様、お嬢様のお帰りをお待ちしています！（*´▽｀*）'
OYASUMI_MESSAGE = 'ご主人様、お嬢様！只今 {} 時をお知らせします！そろそろお休みになられることをおすすめします。(つ∀-)'


def scheduled_handler(event, context):
    print("scheduled event: ", event)
    JST = datetime.timezone(datetime.timedelta(hours=+9), 'JST')
    now = datetime.datetime.now(JST)
    hour = now.hour
    
    if hour == 8:
        message(OHAYO_MESSAGE.format(get_weather()))

    if hour == 12:
        message(OHIRU_MESSAGE.format(hour))
        
    if hour == 18:
        message(OKAERI_MESSAGE.format(hour))

    if hour == 22:
        message(OYASUMI_MESSAGE.format(hour))
    
    if testing:    
        message(get_weather())
    
    
def message(text):
    if not testing:
        text = '<!here> ' + text
    obj = {"text": text}
    print('send message', obj)
    headers = {"Content-Type" : "application/json"}
    json_data = json.dumps(obj).encode("utf-8")
    request = urllib.request.Request(WEBHOOK_URL, data=json_data, method='POST', headers=headers)
    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
        print("response event: " + response_body)
    
def get_weather():
    try:
        # APIキーが必要ないlivedoorのAPIを使用する
        response = urllib.request.urlopen("https://weather.tsukumijima.net/api/forecast?city=130010")  # 東京の天気を取得する
        data = json.loads(response.read().decode('utf8'))
        telop = 'わかりません'
        temperature = 'わかりません'
        try:
            telop = data['forecasts'][0]['telop']
            temperature = data['forecasts'][0]['temperature']['max']['celsius'] + '度'
        except:
            pass
        message = '今日の東京地方の天気は *{}* 、最高気温は {} です！'.format(telop, temperature)
        
        # 降水確率が取れなかったのでとりあえず、天気に「雨」や「雪」が入ってたら傘を持てという
        if '雨' in telop or '雪' in telop:
            message += ' *傘を忘れないで!!* '
        return message
    except Exception as e:
        print(e) 
        return '今日の天気は分かりません(;_;)'