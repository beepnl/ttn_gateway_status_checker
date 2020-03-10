#!/usr/bin/python
import requests
import time
import os.path

KEEPALIVE_TIMEOUT_S = 60
API_ENDPOINT = '/home/bitnami/gateway/slack_channel.json'
GATEWAY_LIST = '/home/bitnami/gateway/gateways.json'

SECONDS_PER_MINUTE  = 60
SECONDS_PER_HOUR    = 3600
SECONDS_PER_DAY     = 86400


file_exists = os.path.isfile(API_ENDPOINT)

if file_exists:
    slack_app = open(API_ENDPOINT,'r')
    SLACK_ENDPOINT = slack_app.read()
    slack_app.close()

else:
        print("slack_file not created")


#change the state of the gateway in the gateway_id.json
def change_last_state(bool):
    # print("Write action test:" + str(bool))
    last_state_write = open(LAST_STATE_PATH,'w')
    last_state_write.write(str(bool))
    last_state_write.close()

def send_message_to_slack(text):
    from urllib import request, parse
    import json

    post = {"text": "{0}".format(text)}

    try:
        json_data = json.dumps(post)
        req = request.Request(SLACK_ENDPOINT,
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'})
        resp = request.urlopen(req)
    except Exception as em:
        print("EXCEPTION: " + str(em))

def convert(seconds):

    days = seconds / SECONDS_PER_DAY
    seconds = seconds % SECONDS_PER_DAY

    hours = seconds / SECONDS_PER_HOUR
    seconds = seconds % SECONDS_PER_HOUR

    minutes = seconds / SECONDS_PER_MINUTE
    seconds = seconds % SECONDS_PER_MINUTE

    return "%d d, %02d hrs, %02d min"%(days,hours,minutes)


def check_gateway(state):
#check is the gateway.json exist, if not create it.
    file_exists = os.path.isfile(LAST_STATE_PATH)

    if file_exists:
        last_state_read = open(LAST_STATE_PATH,'r')
        ttnup = last_state_read.read()
        last_state_read.close()

    else:
        change_last_state(False)
        last_state_read = open(LAST_STATE_PATH,'r')
        ttnup = last_state_read.read()
        last_state_read.close()
        print("created new gateway file: " + GATEWAY_ID)


#check the gateway Id in TTN
    resp = requests.get('http://noc.thethingsnetwork.org:8085/api/v2/gateways/'+GATEWAY_ID)
    if resp.status_code != 200:
        # This means something went wrong.
        print('GET gateways code {}'.format(resp.status_code))
        send_message_to_slack("TTN is not responding for " + GATEWAY_ID + ". Either one of the TTN services is down or the gateway ID is incorrect")
    else:
        last_seen = int(resp.json()['time'][:-9])
        last_seen_human = time.strftime('%d %b %Y %H:%M',time.gmtime(last_seen))
        delta=int(time.time()) - last_seen
        print("Time not seen: " + str(delta))

        if ( delta > KEEPALIVE_TIMEOUT_S ):

            if (ttnup == "False"):
                change_last_state(ttnup)
                print("Gateway already down since" + last_seen_human )
            else:
                send_message_to_slack("Gateway " + GATEWAY_ID + " is DOWN since " + last_seen_human)
                # print(last_seen)
                print("Gateway " + GATEWAY_ID + " is DOWN since " + last_seen_human)

                # print("Gateway " + GATEWAY_ID + " is DOWN since " + time.strftime('%a, %d %b %Y %H:%M:%S GMT',last_seen))
                ttnup = False
                change_last_state(ttnup)
                # print(ttnup + "was al")


        else:

            if (ttnup == "True"):
                # print("ttnup must be true here:")
                # print(ttnup)
                print(GATEWAY_ID + " already up")
                change_last_state(ttnup)


            else:
                send_message_to_slack("Gateway " + GATEWAY_ID + " is UP")
                ttnup = True
                print("Status of Json " + str(ttnup))
                change_last_state(ttnup)


#Loop the gateways listed in the gateway file. On gateway per line.

with open(GATEWAY_LIST) as fp:
   for cnt, line in enumerate(fp):
       line = line.strip('\n')
       print ("")
       print ("-------------------------------------------------------------")
       print(time.strftime('%d/%m/%Y-%H:%M:%S'))
       print ("")
       print ("Gateway ID: " + line)
       GATEWAY_ID = line
       LAST_STATE_PATH = GATEWAY_ID+'.json'

       check_gateway(GATEWAY_ID)
