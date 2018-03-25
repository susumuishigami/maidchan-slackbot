# maidchan-slackbot
maidchan slack bot for maid cafe nomad workspace

# setup

- make lambda as python 3.6 on your preference region (AWS us-east-1 region is recommended)
- export this code to the lambda function
- make api gateway and connect the lambda
- make cloud watch event `cron(0 * * * ? *)` and connect the lambda
- make slack outgoint webhook and copy TOKEN to lthe lambda environment variable
- make slack incomming webhook and copy WEBHOOK_URL to the lambda environment variable
- set MAIDNAME to the lambda environment variable on your prefere

that's it!
