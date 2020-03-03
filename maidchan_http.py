import datetime
import json
import random
import urllib.request
import traceback
import textwrap
import os
import re


ZATSUDAN_TOKEN = os.environ.get('ZATSUDAN_TOKEN')
ALL_TOKEN = os.environ.get('ALL_TOKEN')
MAIDNAME = os.environ.get('MAIDNAME')


ERROR_MESSAGE = '(ﾉД`)ご主人様助けて〜シクシク {} だよー'
OHAYO_MESSAGE = '＼（⌒∇⌒）／ おはようごさいます！ <@{}> 様'
OYASUMI_MESSAGE = '(｡･ω･｡)ﾉ おやすみなさいませ。 <@{}> 様'
OKAERI_MESSAGE = 'おかえりなさいませ！ <@{}> 様 （*´▽｀*）'
ITERA_MESSAGE = '(★･∀･)ﾉ〃行ってらっしゃいませ！ <@{}> 様'
OTSUKARE_MESSAGE = 'お疲れ様です。 <@{}> 様 ＼(^o^)／'


def http_handler(event, contect):
    try:
        body = parse_body(event)
        if body.get('user_id') == 'USLACKBOT':
            return None  # 無限ループ対策
        if body.get('text') is None:
            return None
        if body.get('token') in ZATSUDAN_TOKEN.split(','):
            print('zatsudan token recieved:', body)
            result = 雑談カフェのお仕事(body)
            if result:
                return message(result)
            else:
                respond(400, {'message': 'unsupported message'})
                
        if body.get('token') in ALL_TOKEN.split(','):
            print('all_message recieved:', body)
            result = 全体のお仕事(body)
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
    

def in_keyword(text, *keyword):
    for k in keyword:
        if k in text:
            return True
    return False

class どれがいいかな:
    """
    迷うことがあったら雑談カフェで私に行ってね！私が選んであげるよ！「いか、たこどっちがいいかな？」「赤　青　きいろどれがいいかな？」みたいに聞いてね！
    """
    def get_suffix(self, text):
        for suffix in ('どれがいいかな', 'どっちがいいかな', 'どれがいいかな？', 'どっちがいいかな？'):
            if text.endswith(suffix):
                return suffix
    def 呼び出し(self, text, body):
        if self.get_suffix(text):
            return True
        return False

    def やったよ(self, text, body):
        suffix = self.get_suffix(text)
        selection = text[:-len(suffix)].replace('、', ' ').split()
        choosed = random.choice(selection)
        return 'どうしようかなあ。。。じゃあ {} が良いと思う！'.format(choosed)

class 可愛い:
    """
    私、褒められると弱いんだ。嬉しくなっちゃう。お屋敷の秘密教えちゃうかも！
    """
    def 呼び出し(self, text, body):
        return ('かわいい' in text or '可愛い' in text) and MAIDNAME in text

    def やったよ(self, text, body):
        response = random.choice([
            "ありがとう！ (〃'∇'〃)ゝｴﾍﾍ",
            "そんなことないよ！（*´▽｀*）"
        ])
        if random.randint(1, 10) > 7:
            # 30%の確率でメイドちゃんが機能を教えてくれる
            response += '\n' + textwrap.dedent(random.choice(雑談お仕事リスト + 全体お仕事リスト).__doc__)
        return response

class 占って:
    """
    雑談カフェでご主人様、お嬢様の今日の運勢を占ってあげるよ！ `占って！` のあとに数字4桁で誕生日を書いてね！例えば `占って！0101` みたいに言ってね！
    """
    def uranai(self, user_id, birthday):
        # The uranai() function is:
        #
        #    Copyright (c) 2016 beproud
        #    https://github.com/beproud/beproudbot
        today = datetime.date.today().strftime('%Y/%m/%d')
        response = urllib.request.urlopen('http://api.jugemkey.jp/api/horoscope/free/{}'.format(today))
        data = json.loads(response.read().decode('utf8'))
        d = data['horoscope'][today][self._calc_index(birthday)]
        for s in ['total', 'love', 'money', 'job']:
            d[s] = self.star(d[s])
        return """\
<@{}> 様の今日の運勢はこちらです！
{rank}位 {sign}
総合: {total}
恋愛運: {love}
金運: {money}
仕事運: {job}
ラッキーカラー: {color}
ラッキーアイテム: {item}
{content}""".format(user_id, **d)

    @staticmethod
    def _calc_index(birthday):
        if not birthday.endswith("座"):
            month, day = int(birthday[:2]), int(birthday[2:])
            period = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 23]
            return (month + 8 + (day >= period[(month - 1) % 12])) % 12
        # おひつじ てんびん みずがめ are shorten because len(birthday) == 4
        n = {"ひつじ":0, "おうし":1, "ふたご":2, "おとめ":5,
             "んびん":6, "さそり":7, "ずがめ":10,
        }.get(birthday[-4:-1])
        if isinstance(n, int):
            return n
        n = {"牡羊":0, "牡牛":1, "双子":2, "かに":3, "しし":4, "獅子":4, "乙女":5,
             "天秤":6, "いて":8, "射手":8, "やぎ":9, "山羊":9, "水瓶":10, "うお":11,
        }.get(birthday[-3:-1])
        if isinstance(n, int):
            return n
        n = {"蟹":3, "蠍":7, "魚":11,
        }.get(birthday[-2:-1])
        if isinstance(n, int):
            return n
        # ValueError pretend
        month, day = int(birthday[:2]), int(birthday[2:])

    def star(self, n):
        # The star() function is:
        #
        #    Copyright (c) 2016 beproud
        #    https://github.com/beproud/beproudbot
        return '★' * n + '☆' * (5 - n)

    def 呼び出し(self, text, body):
        return text.startswith('占って！')

    def やったよ(self, text, body):
        birthday = text[-4:]
        return self.uranai(body.get('user_id'), birthday)

class おはよう:
    """
    朝起きたら雑談カフェで一言言ってね！おはようのご挨拶をするよ！
    """
    def 呼び出し(self, text, body):
        return in_keyword(text, 'おはよう', 'おはよー')

    def やったよ(self, text, body):
        return OHAYO_MESSAGE.format(body.get('user_id'))

class おやすみ:
    """
    ご就寝前に雑談カフェで一言言ってね！お休みのご挨拶をするよ！
    """
    def 呼び出し(self, text, body):
        return in_keyword(text, 'おやすみ', 'お休み', '寝')

    def やったよ(self, text, body):
        return OYASUMI_MESSAGE.format(body.get('user_id'))

class おかえり:
    """
    帰ったら雑談カフェで言ってね！ご帰宅のご主人様、お嬢様をお出迎えするよ。
    """
    def 呼び出し(self, text, body):
        return in_keyword(text, '帰', 'ただいま', 'きたく', 'かえる')

    def やったよ(self, text, body):
        return OKAERI_MESSAGE.format(body.get('user_id'))

class お疲れ様:
    """
    疲れたら雑談カフェで言ってね！おつかれのご主人様、お嬢様をねぎらってあげるよ。
    """
    def 呼び出し(self, text, body):
        return in_keyword(text, '疲', 'つかれ', '終', 'おわた', 'おわった')

    def やったよ(self, text, body):
        return OTSUKARE_MESSAGE.format(body.get('user_id'))

class 行ってらっしゃい:
    """
    お出かけするときは `行ってきます` `いってきます` `出発` って雑談カフェで言ってね！
    ご主人様、お嬢様をお見送りするよ！
    """
    def 呼び出し(self, text, body):
        return in_keyword(text, '行ってきます', 'いってきます', '出かけ', '行きます', 'いきます', '出発')

    def やったよ(self, text, body):
        return ITERA_MESSAGE.format(body.get('user_id'))
    

雑談お仕事リスト = (
    どれがいいかな(),
    可愛い(),
    占って(),
    おはよう(),
    おやすみ(),
    おかえり(),
    お疲れ様(),
    行ってらっしゃい()
)

def 雑談カフェのお仕事(body):
    """
    雑談カフェチャネルでのメイドちゃんのお仕事だよ！
    """
    text = body['text']

    for お仕事 in 雑談お仕事リスト:
        if お仕事.呼び出し(text, body):
            return お仕事.やったよ(text, body)

    if 'XXX' == text:
        # 例外テスト
        print(10/0)

class 褒めて:
    """
    `メイドちゃん！` で始まって `褒めて！` で終わるように話しかけると、メイドちゃんが褒めてあげるよ！
    間に @ メンションがあるとその人を褒めてあげるよ！
    誰もメンションがなければあなたを褒めるよ！でも `僕を` `私を` `俺を` 褒めてって言ってくれると嬉しいな。
    理由も書いてね☆
    私、どのチャネルにでも駆けつけるよ！
    """
    def 呼び出し(self, text, body):
        return text.startswith('メイドちゃん！') and text.endswith('褒めて！')

    def やったよ(self, text, body):
        return self.plusplus(
            text[len('メイドちゃん！'):-len('褒めて') - 1],
            body.get('user_id')
        )

    def plusplus(self, text, user_id):
        who = ''
        for m in re.finditer('<(.+?)>', text):
            who += f'<{m.group(1)}>さん、'
        if text.endswith('僕を') or text.endswith('私を') or text.endswith('俺を'):
            who = f'<@{user_id}>さん、'
            text = text[0:-2]
        if not who:
            who = f'<@{user_id}>さん、'
        riyu = text
        for m in reversed(list(re.finditer('<(.+?)>', text))):
            riyu = riyu[0:m.start()] + riyu[m.end():]
        
        if riyu.endswith('を'):
            riyu = riyu[0:-1]
        
        return who + riyu + 'すごーい！'

全体お仕事リスト = (
    褒めて(), 
)

def 全体のお仕事(body):
    """
    すべてのチャネルでのメイドちゃんのお仕事だよ！

    >>> body = {'user_id': '00000000'}

    >>> body['text'] = 'メイドちゃん！早く帰った僕を褒めて！'
    >>> 全体のお仕事(body)
    '<00000000>さん、早く帰ったすごーい！'

    >>> body['text'] = 'メイドちゃん！仕事頑張った<00000001> <00000002>を褒めて！'
    >>> 全体のお仕事(body)
    '<00000001>さん、<00000002>さん、仕事頑張った すごーい！'
    """
    text = body['text']
    
    for お仕事 in 全体お仕事リスト:
        if お仕事.呼び出し(text, body):
            return お仕事.やったよ(text, body)

if __name__ == '__main__':
    MAIDNAME = 'メイドちゃん'
    from sys import argv
    body = {
        'user_id': '00000000',
        'text': argv[1]
    }
    print(全体のお仕事(body) or 雑談カフェのお仕事(body))
        
