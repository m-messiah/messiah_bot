#!/usr/bin/python3

__author__ = 'm_messiah'
import logging
import signal
from requests import Session
import tornado.ioloop
import tornado.web
import tornado.escape
from os import environ as ENV

try:
    from bot_token import BOT_TOKEN
except:
    BOT_TOKEN = ENV["TOKEN"]
from commands import CMD


logging.basicConfig(filename="conversation.log", level=logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.WARNING)


URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
MyURL = ""  # TODO: add url here, when get valid HTTPS

LAST_COMMAND = {}


def not_found(arguments, message):
    return {'chat_id': message['from']['id'],
            'text': "Command not found. Try /help"
            }

def send_reply(response):
    logging.debug("SENT\t%s" % response)
    if 'sticker' in response:
        api.post(URL + "sendSticker", data=response)
    elif 'text' in response:
        api.post(URL + "sendMessage", data=response)

# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
        def post(self):
            try:
                logging.debug("Got request: %s" % self.request.body)
                update = tornado.escape.json_decode(self.request.body)
                message = update['message']
                text = message.get('text')
                if text:
                    logging.info("MESSAGE\t%s\t%s" % (
                        message['from']['id'],
                        text))

                    if text[0] == '/':
                        command, *arguments = text.split(" ", 1)
                        if len(arguments):
                            arguments = arguments[0]
                        else:
                            arguments = ""
                        logging.debug("REQUEST\t%s\t%s\t'%s'" % (
                            message['from']['id'],
                            command,
                            arguments
                        ))
                        response = CMD.get(command, not_found)(arguments,
                                                               message)

                        logging.info("REPLY\t%s\t%s" % (
                            message['from']['id'],
                            response
                        ))
                        send_reply(response)
                        LAST_COMMAND[message["from"]["id"]] = command
                    else:
                        if message["from"]["id"] in LAST_COMMAND:
                            response_func = CMD.get(
                                LAST_COMMAND[message["from"]["id"]],
                                CMD["<speech>"]
                            )
                        else:
                            response_func = CMD["<speech>"]
                        response = response_func(None, message)
                        logging.info("REPLY\t%s\t%s" % (
                            message['from']['id'],
                            response
                        ))
                        send_reply(response)
                        del LAST_COMMAND[message["from"]["id"]]

                elif message.get("sticker"):
                    send_reply(
                        {'chat_id': message['from']['id'],
                         'text': "Sticker id = %s" % message[
                             "sticker"].get("file_id")
                        })

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
        application.listen(ENV["PORT"])
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        signal_term_handler(signal.SIGTERM, None)
