#-*- coding: utf-8 -*-

import argparse
import requests

BOT_TOKEN = "내봇 토큰값"
CHAT_ID = "내봇ID"


def send_message(message):
    response = requests.post(
        'https://api.telegram.org/bot%s/%s' % (BOT_TOKEN, 'sendMessage'),
        data={
            "chat_id": CHAT_ID,
            "text": message,
        }
    )
    #if response.status_code > 200:
        #print "Error:", response

def main():
        parser = argparse.ArgumentParser("Send messages to my phone")
        parser.add_argument("messages", nargs="+")
        args = parser.parse_args()

        for message in args.messages:
                send_message(message)

if __name__ == "__main__":
    main()
