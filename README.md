このプロジェクトはメイドカフェでノマド会に管理を移管しました: https://github.com/maidnomad/maidchan-slackbot

# maidchan-slackbot
maidchan slack bot for maid cafe nomad workspace

# setup develop environment

```console
$ python3.9 -m venv venv
$ . venv/bin/activate
$ make pip_dev
```

# developing command

format
```console
$ make fmt
```

test
```console
$ make test
```

test last failed with detail message
```console
$ make test-lf
```

lint
```console
$ make lint
```

# archetecture

```
+ functions/                 .... lambda-function source code
  + maichan/                .... maidchan core
    - settings.py           .... settings variables by environment
    - schedules.py          .... maidchan scheduled functions 
    - tasks.py              .... maidchan functions hooked by slack message
  - lambda_function.py      .... AWS lambda main
  - maidchan_http.py        ....   + API Gateway main
  - maidchan_scheduled.py   ....   + Scheduled Event main
  - maidchan_debug.py
+ tests/                    .... unit test files
  - 
- Makefile
```

# How to make maidchan task

edit functions/maidchan/tasks.py

1. make class decorated by @zatsudan_work (for zatsudan cafe channel) or @oyashiki_work (for all channel)
    - has method: `is_target(self, text, body)`
    - has method: `perform(self, text, body)`

    ```
    @zatsudan_work
    class TaskName:
    def is_target(self, text, body):
        pass
    def perform(self, text, body):
        pass
    ```

2. implement `is_target` method:
    - return True: when text/body is target message
    - return False: when text/body is not target message

    ```
    def perform(self, text, body):
        # メッセージに「かわいい」と「メイドちゃん」が含まれていたら対象
        return ("かわいい" in text) and ("メイドちゃん" in text)
    ```

3. implement `perform` method:
    - return result message from maildchan
    ```
    def perform(self, text, body):
        return "うれしい♪(^^)"
    ```
4. write unit test
    - edit tests/test_zatsudan.py or tests/test_oyashiki.py

# setup production environment

- setup lambda
    - make lambda as python 3.6 on your preference region (AWS us-east-1 region is recommended)
    - make api gateway and connect the lambda
    - make cloud watch event `cron(0 * * * ? *)` and connect the lambda
    - make slack outgoint webhook and copy TOKEN to lthe lambda environment variable
    - make slack incomming webhook and copy WEBHOOK_URL to the lambda environment variable
    - set MAIDNAME to the lambda environment variable on your prefere
- setup GitHub Actions
    - see [deploy.yml](.github/workflows)
    - make AWS Iam User to Deploy lambda, and get ACCESS KEY ID, SECRET ACCESS KEY

# deploy

- push/merge master branch, and deploy

that's it!
