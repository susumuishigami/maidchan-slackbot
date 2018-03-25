import json
import random
import urllib
import traceback
import os


TOKEN = os.environ['TOKEN']
MAIDNAME = os.environ['MAIDNAME']


ERROR_MESSAGE = '(ﾉД`)ご主人様助けて〜シクシク {} だよー'
OHAYO_MESSAGE = '＼（⌒∇⌒）／ おはようごさいます！ <@{}> 様'
OYASUMI_MESSAGE = '(｡･ω･｡)ﾉ おやすみなさいませ。 <@{}> 様'
OKAERI_MESSAGE = 'おかえりなさいませ！ <@{}> 様 （*´▽｀*）'
ITERA_MESSAGE = '(★･∀･)ﾉ〃行ってらっしゃいませ！ <@{}> 様'
OTSUKARE_MESSAGE = 'お疲れ様です。 <@{}> 様 ＼(^o^)／'
TERE_MESSAGES = ["ありがとう！ (〃'∇'〃)ゝｴﾍﾍ",
                 "そんなことないよ！（*´▽｀*）"]


def http_handler(event, contect):
    try:
        body = parse_body(event)
        if body.get('user_id') == 'USLACKBOT':
            return None  # 無限ループ対策
        if body.get('text') is None:
            return None
        if body.get('token') != TOKEN:
            return None

        print('http recieved:', body)
        result = main(body)
        if result:
            return message(result)
        else:
            respond(400, {'message': 'unsupported message'})

    except Exception as e:
        print(traceback.format_exc())
        return message(ERROR_MESSAGE.format(str(e)))


def parse_body(event):
   return {k: v for k, v in urllib.parse.parse_qsl(event['body'])}


def respond(status, res):
    print('respond:', res)
    return {
        'statusCode': status,
        'body': json.dumps(res),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def message(text):
    return respond(200, {
        "text": text,
        "username": MAIDNAME,
        "icon_emoji": ":maidchan:"
    })


def main(body):
    text = body['text']
    if in_keyword(text, 'おはよう', 'おはよー'):
        return OHAYO_MESSAGE.format(body.get('user_id'))
        
    if in_keyword(text, 'おやすみ'):
        return OYASUMI_MESSAGE.format(body.get('user_id'))

    if in_keyword(text, '帰', 'ただいま', 'きたく', 'かえる'):
        return OKAERI_MESSAGE.format(body.get('user_id'))

    if in_keyword(text, '疲', 'つかれ', '終', 'おわた', 'おわった'):
        return OTSUKARE_MESSAGE.format(body.get('user_id'))
        
    if in_keyword(text, '行ってきます', 'いってきます', '出かけ', '行きます', 'いきます', '出発'):
        return ITERA_MESSAGE.format(body.get('user_id'))
    
    for suffix in ('どれがいいかな？', 'どっちがいいかな？'):
        selection = text[:len(suffix)].replace('、', ' ').split()
        choosed = random.choice(selection)
        choosed = choosed_format(choosed)
        return 'どうしようかなあ。。。じゃあ {} が良いと思う！'.format(choosed)

    if ('かわいい' in text or '可愛い' in text) and MAIDNAME in text:
        return random.choice(TERE_MESSAGES)

    if 'XXX' == text:
        # 例外テスト
        print(10/0)

def in_keyword(text, *keyword):
    for k in keyword:
        if k in text:
            return True
    return False