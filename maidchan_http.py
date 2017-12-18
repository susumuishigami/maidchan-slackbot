import json
import random
import urllib
import traceback
import os
import re


TOKEN = os.environ['TOKEN']
MAIDNAME = os.environ['MAIDNAME']


ERROR_MESSAGE = '(ﾉД`)ご主人様助けて〜シクシク {} だよー'
OHAYO_MESSAGE = '＼（⌒∇⌒）／ おはようごさいます！ <@{}> 様'
OYASUMI_MESSAGE = '(｡･ω･｡)ﾉ おやすみなさいませ。 <@{}> 様'
OKAERI_MESSAGE = 'おかえりなさいませ！ <@{}> 様 （*´▽｀*）'
ITERA_MESSAGE = '(★･∀･)ﾉ〃行ってらっしゃいませ！ <@{}> 様'
OTSUKARE_MESSAGE = 'お疲れ様です。 <@{}> 様 ＼(^o^)／'
TERE_MESSAGE = "ありがとう！ (〃'∇'〃)ゝｴﾍﾍ"


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
    if re.search('おはよう', text):
        return OHAYO_MESSAGE.format(body.get('user_id'))

    if re.search('おやすみ', text):
        return OYASUMI_MESSAGE.format(body.get('user_id'))

    if re.search('(帰|きたく|かえる)', text):
        return OKAERI_MESSAGE.format(body.get('user_id'))

    if re.search('(疲|つかれ|おわた|おわった|終)', text):
        return OTSUKARE_MESSAGE.format(body.get('user_id'))

    if re.search('(行ってきます|出かけます|行きます|いきます|いってきます)', text):
        return ITERA_MESSAGE.format(body.get('user_id'))

    if re.search('^えらんで！', text):
        selection = text[len('えらんで！'):].replace('、', ' ').split()
        return 'どれにしようかなあ。。。じゃあ {} ちゃんに決めた！'.format(random.choice(selection))

    if re.search('(かわいい|可愛い)', text) and re.search('@maidchan', text):
        return TERE_MESSAGE

    if re.search('XXX', text):
        # 例外テスト
        print(10/0)
