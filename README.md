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

lint
```console
$ make lint
```

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
