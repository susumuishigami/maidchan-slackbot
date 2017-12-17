# maidchan-slackbot
maidchan slack bot for maid cafe nomad workspace

# setup

- make lambda as python 3.6 on your preference region (AWS us-west-1 region is recommended)
- export this code to lambda function
- make api gateway and connect lambda
- make cloud watch event `cron(0 * * * ? *)` and connect lambda
- make slack outgoint webhook and copy TOKEN to lambda environment
- make slack incomming webhook and copy WEBHOOK_URL to lambda environment
- set MAIDNAME to lambda environment on your prefere
- that's it!
