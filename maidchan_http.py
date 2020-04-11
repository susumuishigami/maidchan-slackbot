import datetime
import json
import random
import urllib.request
import traceback
import textwrap
import os
import re


雑談カフェのトークン = os.environ.get('ZATSUDAN_TOKEN')
お屋敷のトークン = os.environ.get('ALL_TOKEN')
メイドちゃんの名前 = os.environ.get('MAIDNAME')


エラーが出たときのセリフ = '(ﾉД`)ご主人様助けて〜シクシク {} だよー'
朝のご挨拶 = '＼（⌒∇⌒）／ おはようごさいます！ <@{}> 様'
おやすみのご挨拶 = '(｡･ω･｡)ﾉ おやすみなさいませ。 <@{}> 様'
おかえりのご挨拶 = 'おかえりなさいませ！ <@{}> 様 （*´▽｀*）'
いってらっしゃいのご挨拶 = '(★･∀･)ﾉ〃行ってらっしゃいませ！ <@{}> 様'
お疲れ様のセリフ = 'お疲れ様です。 <@{}> 様 ＼(^o^)／'
本日の運勢 = """\
<@{}> 様の今日の運勢はこちらです！
{rank}位 {sign}
総合: {total}
恋愛運: {love}
金運: {money}
仕事運: {job}
ラッキーカラー: {color}
ラッキーアイテム: {item}
{content}"""
選んだよのセリフ = 'どうしようかなあ。。。じゃあ {} が良いと思う！'
照れたときのメッセージリスト = [
    "ありがとう！ (〃'∇'〃)ゝｴﾍﾍ",
    "そんなことないよ！（*´▽｀*）"
]
褒めるときのセリフ = '{誰}{理由}んだ！すごーい！'


def http_handler(event, contect):
    try:
        body = parse_body(event)
        if body.get('user_id') == 'USLACKBOT':
            return None  # 無限ループ対策
        if body.get('text') is None:
            return None
        if body.get('token') in 雑談カフェのトークン.split(','):
            print('zatsudan token recieved:', body)
            セリフ = 雑談カフェのお仕事(body)
            if セリフ:
                return セリフを言う(セリフ)
            else:
                respond(400, {'message': 'unsupported message'})
                
        if body.get('token') in お屋敷のトークン.split(','):
            print('all_message recieved:', body)
            セリフ = お屋敷のお仕事(body)
            if セリフ:
                return セリフを言う(セリフ)
            else:
                respond(400, {'message': 'unsupported message'})

        

    except Exception as e:
        print(traceback.format_exc())
        return セリフを言う(エラーが出たときのセリフ.format(str(e)))


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


def セリフを言う(text):
    return respond(200, {
        "text": text,
        "username": メイドちゃんの名前,
        "icon_emoji": ":maidchan:"
    })
    

def 合言葉を探す(text, *keyword):
    for k in keyword:
        if k in text:
            return True
    return False

class どれがいいかな:
    """
    迷うことがあったら雑談カフェで私に行ってね！私が選んであげるよ！「いか、たこどっちがいいかな？」「赤　青　きいろどれがいいかな？」みたいに聞いてね！
    """
    def おしりを取る(self, text):
        for 句読点 in ('', '？', '！', '。'):
            for いいかな in ('いいかな', '良いかな', '良いと思う', 'いいと思う'):
                for どれ in ('どれ', 'どっち', 'どの子'):
                    おしり = f'{どれ}が{いいかな}{句読点}'
                    if text.endswith(おしり):
                        return おしり
    def 呼び出し(self, text, body):
        return self.おしりを取る(text) is not None

    def やったよ(self, text, body):
        言葉のおしり = self.おしりを取る(text)
        選択肢 = text[:-len(言葉のおしり)].replace('、', ' ').split()
        選んだもの = random.choice(選択肢)
        return 選んだよのセリフ.format(選んだもの)

class 可愛い:
    """
    私、褒められると弱いんだ。嬉しくなっちゃう。お屋敷の秘密教えちゃうかも！
    """
    def 呼び出し(self, text, body):
        return ('かわいい' in text or '可愛い' in text) and メイドちゃんの名前 in text

    def やったよ(self, text, body):
        返事 = random.choice(照れたときのメッセージリスト)
        if random.randint(1, 10) > 3:
            # 70%の確率でメイドちゃんが機能を教えてくれる
            返事 += '\n' + textwrap.dedent(random.choice(雑談お仕事リスト + お屋敷お仕事リスト).__doc__)
        return 返事

class 占って:
    """
    雑談カフェでご主人様、お嬢様の今日の運勢を占ってあげるよ！ `占って！` のあとに数字4桁で誕生日を書いてね！例えば `占って！0101` みたいに言ってね！
    """
    def 占い(self, user_id, birthday):
        # The 占い() function is:
        #
        #    Copyright (c) 2016 beproud
        #    https://github.com/beproud/beproudbot
        今日 = datetime.date.today().strftime('%Y/%m/%d')
        response = urllib.request.urlopen('http://api.jugemkey.jp/api/horoscope/free/{}'.format(今日))
        data = json.loads(response.read().decode('utf8'))
        月, 日 = int(birthday[:2]), int(birthday[2:])
        区切り = [20, 19, 21, 20, 21, 22, 23, 23, 23, 24, 22, 23]
        星座 = (月 + 8 + (日 >= 区切り[(月 - 1) % 12])) % 12
        d = data['horoscope'][今日][星座]
        for s in ['total', 'love', 'money', 'job']:
            d[s] = self.お星様きらり(d[s])
        return 本日の運勢.format(user_id, **d)

    def お星様きらり(self, n):
        # The お星様きらり:star() function is:
        #
        #    Copyright (c) 2016 beproud
        #    https://github.com/beproud/beproudbot
        return '★' * n + '☆' * (5 - n)

    def 呼び出し(self, text, body):
        return text.startswith('占って！')

    def やったよ(self, text, body):
        birthday = text[-4:]
        return self.占い(body.get('user_id'), birthday)

class おはよう:
    """
    朝起きたら雑談カフェで一言言ってね！おはようのご挨拶をするよ！
    """
    def 呼び出し(self, text, body):
        return 合言葉を探す(text, 'おはよう', 'おはよー')

    def やったよ(self, text, body):
        return 朝のご挨拶.format(body.get('user_id'))

class おやすみ:
    """
    ご就寝前に雑談カフェで一言言ってね！お休みのご挨拶をするよ！
    """
    def 呼び出し(self, text, body):
        return 合言葉を探す(text, 'おやすみ', 'お休み', '寝')

    def やったよ(self, text, body):
        return おやすみのご挨拶.format(body.get('user_id'))

class おかえり:
    """
    帰ったら雑談カフェで言ってね！ご帰宅のご主人様、お嬢様をお出迎えするよ。
    """
    def 呼び出し(self, text, body):
        return 合言葉を探す(text, '帰', 'ただいま', 'きたく', 'かえる')

    def やったよ(self, text, body):
        return おかえりのご挨拶.format(body.get('user_id'))
        
class 円周率言って:
    """
    円周率を言うよ
    """
    def 呼び出し(self, text, body):
        if '円周率' in text and 'おしえて' in text:
            return True
        if 'ぱい' in text or 'パイ' in text or 'π' in text:
            return True
        return False
        
    def やったよ(self, text, body):
        return "3.1415926535897932384626433832795018841971693993"

class お疲れ様:
    """
    疲れたら雑談カフェで言ってね！おつかれのご主人様、お嬢様をねぎらってあげるよ。
    """
    def 呼び出し(self, text, body):
        return 合言葉を探す(text, '疲', 'つかれ', '終', 'おわた', 'おわった')

    def やったよ(self, text, body):
        return お疲れ様のセリフ.format(body.get('user_id'))

class 行ってらっしゃい:
    """
    お出かけするときは `行ってきます` `いってきます` `出発` って雑談カフェで言ってね！
    ご主人様、お嬢様をお見送りするよ！
    """
    def 呼び出し(self, text, body):
        return 合言葉を探す(text, '行ってきます', 'いってきます', '出かけ', '行きます', 'いきます', '出発')

    def やったよ(self, text, body):
        return いってらっしゃいのご挨拶.format(body.get('user_id'))
    

雑談お仕事リスト = (
    どれがいいかな(),
    可愛い(),
    占って(),
    おはよう(),
    おやすみ(),
    おかえり(),
    お疲れ様(),
    行ってらっしゃい(),
    円周率言って()
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
        return self.褒める(
            text[len('メイドちゃん！'):-len('褒めて') - 1],
            body.get('user_id')
        )

    def 褒める(self, text, user_id):
        誰 = ''
        for m in re.finditer('<(.+?)>', text):
            誰 += f'<{m.group(1)}>さん、'
        if text.endswith('僕を') or text.endswith('私を') or text.endswith('俺を'):
            誰 = f'<@{user_id}>さん、'
            text = text[0:-2]
        if not 誰:
            誰 = f'<@{user_id}>さん、'
        理由 = text
        for m in reversed(list(re.finditer('<(.+?)>', text))):
            理由 = 理由[0:m.start()] + 理由[m.end():]
        
        if 理由.endswith('を'):
            理由 = 理由[0:-1]
            
        if 理由.endswith('の'):
            理由 = 理由[0:-1]
        
        誰 = 誰.strip()
        理由 = 理由.strip()
        
        return 褒めるときのセリフ.format(誰=誰,理由=理由)

お屋敷お仕事リスト = (
    褒めて(), 
)

def お屋敷のお仕事(body):
    """
    すべてのチャネルでのメイドちゃんのお仕事だよ！

    >>> body = {'user_id': '00000000'}

    >>> body['text'] = 'メイドちゃん！早く帰った僕を褒めて！'
    >>> お屋敷のお仕事(body)
    '<00000000>さん、早く帰ったんだ！すごーい！'

    >>> body['text'] = 'メイドちゃん！仕事頑張った<00000001> <00000002>を褒めて！'
    >>> お屋敷のお仕事(body)
    '<00000001>さん、<00000002>さん、仕事頑張ったんだ！すごーい！'
    """
    text = body['text']
    
    for お仕事 in お屋敷お仕事リスト:
        if お仕事.呼び出し(text, body):
            return お仕事.やったよ(text, body)

if __name__ == '__main__':
    メイドちゃんの名前 = 'メイドちゃん'
    from sys import argv
    body = {
        'user_id': '00000000',
        'text': argv[1]
    }
    print(お屋敷のお仕事(body) or 雑談カフェのお仕事(body))
        
