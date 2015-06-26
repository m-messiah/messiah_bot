#!/usr/bin/python3

import requests
from bot_token import BOT_TOKEN
import json
import time
import logging
import signal

logging.basicConfig(filename="puller.log", level=logging.INFO)
last = 681692814
URL = "https://api.telegram.org/bot%s/getUpdates" % BOT_TOKEN


def signal_term_handler(signal, frame):
    logging.error("Got SIGTERM. Quit.LAST=%s" % last)
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_term_handler)
    try:
        while True:
            r = requests.get(URL + "?offset=%s" % (last + 1))
            if r.status_code == 200:
                for message in r.json()["result"]:
                    last = int(message["update_id"])
                    requests.post("https://messiah.ddns.net:44380/telegram/",
                                  data=json.dumps(message),
                                  headers={'Content-type': 'application/json',
                                           'Accept': 'text/plain'},
                                  verify=False)
            else:
                logging.warning("FAIL " + r.text)
            time.sleep(3)
    except KeyboardInterrupt:
        signal_term_handler(signal.SIGTERM, None)
