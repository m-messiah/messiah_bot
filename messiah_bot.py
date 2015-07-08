#!/usr/bin/env python3

__author__ = 'm_messiah'
import logging
from signal import signal, SIGTERM
from os import environ

from requests import Session
from tornado.ioloop import IOLoop
from tornado.web import Application, RequestHandler
from tornado.escape import json_decode

from commands import CMD

try:
    from bot_token import BOT_TOKEN
except ImportError:
    BOT_TOKEN = environ["TOKEN"]

logging.basicConfig(level=logging.INFO)
logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)

URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
MyURL = "https://messiah-bot.herokuapp.com"
LAST_COMMAND = {}


def not_found(_, message):
    return {
        'chat_id': message['from']['id'],
        'text': "Command not found. Try /help"
    }


def send_reply(response):
    logging.debug("SENT\t%s", response)
    if 'sticker' in response:
        api.post(URL + "sendSticker", data=response)
    elif 'text' in response:
        api.post(URL + "sendMessage", data=response)


# noinspection PyAbstractClass
class Handler(RequestHandler):
    def get(self):
        self.write({"result": "Ok", "text": "I am awake!"})

    def post(self):
        try:
            logging.debug("Request: %s", self.request.body)
            update = json_decode(self.request.body)
            message = update['message']
            sender = message['from']
            text = message.get('text')
            if text:
                logging.info("MESSAGE FROM\t%s",
                             sender['username'] if 'username' in sender
                             else sender['id'])

                if text[0] == '/':
                    command, _, arguments = text.partition(" ")
                    logging.debug("REQUEST\t%s\t%s\t'%s'",
                                  sender['id'],
                                  command.encode("utf8"),
                                  arguments.encode("utf8")
                    )
                    response = CMD.get(command, not_found)(arguments, message)

                    send_reply(response)
                    LAST_COMMAND[sender["id"]] = command
                else:
                    if sender["id"] in LAST_COMMAND:
                        response_func = CMD.get(LAST_COMMAND[sender["id"]],
                                                CMD["<speech>"])
                    else:
                        response_func = CMD["<speech>"]
                    response = response_func(None, message)
                    send_reply(response)
                    del LAST_COMMAND[sender["id"]]

            elif message.get("sticker"):
                send_reply({
                    'chat_id': sender['id'],
                    'text': "Sticker id = %s"
                            % message["sticker"].get("file_id")
                })

            self.write({"result": "Ok", "text": "Accepted"})

        except Exception as e:
            logging.warning(str(e))
            self.write({"result": "Fail", "text": "Error"})


def signal_term_handler(sig, _):
    logging.error("Got %s. Quit.", sig)
    exit(0)

api = Session()
application = Application([(r"/", Handler), ])

if __name__ == '__main__':
    signal(SIGTERM, signal_term_handler)
    try:
        set_hook = api.get(URL + "setWebhook?url=%s" % MyURL)
        if set_hook.status_code != 200:
            logging.error("Can't set hook: %s. Quit." % set_hook.text)
            exit(1)
        application.listen(environ["PORT"])
        IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(SIGTERM, None)
