# ttn_gateway_status_checker
This script will check the status of the listed TTN gateways and will inform you on Slack if a gateway is down.

#how to use

1. create a gateway.json file and add all gateways you want to check_gateway
2. create a slack_channel.json file and enter the Slack webhook: see https://api.slack.com/messaging/webhooks
3. add the script to a chrontab to run it af often as you like:
"python3 check_TTN_gateway_status.py" 
