#!/usr/bin/python3

__author__ = 'm_messiah'
import logging
import signal
from requests import Session
import tornado.ioloop
import tornado.web
import tornado.escape

from bot_token import BOT_TOKEN
from commands import CMD


logging.basicConfig(filename="conversation.log", level=logging.INFO)


URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
MyURL = ""  # TODO: add url here, when get valid HTTPS


def not_found(arguments, message):
    return "Command not found. Try /help"

def send_message(text, command, id):
    payload = {
        'chat_id': id,
        'text': text,
        # 'reply_markup': keyboard
    }

    api.post(URL + "sendMessage", data=payload)

# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
        def post(self):
            try:
                logging.debug("Got request: %s" % self.request.body)
                update = tornado.escape.json_decode(self.request.body)
                message = update['message']
                text = message['text']

                logging.info("MESSAGE\t%s\t%s" % (
                    message['from']['id'],
                    text))

                if text[0] == '/':
                    command, *arguments = text.split(" ", 1)
                    reply = CMD.get(command, not_found)(arguments, message)

                    logging.info("REPLY\t%s\t%s" % (
                        message['from']['id'],
                        reply
                    ))

                    send_message(reply, command, message['from']['id'])
                else:
                    reply = CMD["0"](message)
                    logging.info("REPLY\t%s\t%s" % (
                        message['from']['id'],
                        reply
                    ))
                    send_message(reply, "human", message['from']['id'])
            except Exception as e:
                logging.warning(str(e))


def signal_term_handler(signal, frame):
    logging.error("Got SIGTERM. Quit.")
    api.get(URL + "setWebhook?url=")
    exit(0)

api = Session()
application = tornado.web.Application([
    (r"/", Handler),
])



if __name__ == '__main__':
    signal.signal(signal.SIGTERM, signal_term_handler)
    try:
        set_hook = api.get(URL + "setWebhook?url=%s" % MyURL)
        if set_hook.status_code != 200:
            logging.error("Can't set hook: %s. Quit." % set_hook.text)
            exit(1)
        application.listen(8888)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(signal.SIGTERM, None)
