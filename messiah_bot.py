#!/usr/bin/python3

__author__ = 'm_messiah'
import logging
import signal
from requests import Session
import tornado.ioloop
import tornado.web
import tornado.escape
from base64 import b64decode

from bot_token import BOT_TOKEN


logging.basicConfig(filename="conversation.log", level=logging.INFO)

# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):
        def post(self):
            try:
                logging.debug("Got request: %s" % self.request.body)
                update = tornado.escape.json_decode(self.request.body)
                message = update['message']
                text = message['text']

                logging.info("MESSAGE\t%s (%s)\t%s" % (
                    message['from']['username'],
                    message['from']['id'],
                    text))

                if text[0] == '/':
                    command, *arguments = text.split(" ", 1)
                    reply = CMD.get(command, not_found)(arguments, message)

                    logging.info("REPLY\t%s (%s)\t%s" % (
                        message['from']['username'],
                        message['from']['id'],
                        reply
                    ))

                    self.sendMessage(reply, command, message['from']['id'])
                else:
                    logging.info("COMMAND NOT FOUND\t%s (%s)" % (
                        message['from']['username'],
                        message['from']['id'],
                    ))
                    self.sendMessage(not_found("", message), "/not_found",
                                     message['from']['id'])
            except Exception as e:
                logging.warning(str(e))

        def sendMessage(self, text, command, id):
            payload = {
                'chat_id': id,
                'text': text,
                # 'reply_markup': keyboard
            }

            api.post(URL + "sendMessage", data=payload)

def about(arguments, message):
    return """Hey, %s!
My author is @m_messiah.
You can find this nickname at:
    + Telegram
    + Twitter
    + Instagram
    + VK
    + GitHub (m-messiah)
    """ % message["from"]["first_name"]

def not_found(arguments, message):
    return "Command not found"

def base64_decode(arguments, message):
    try:
        return b64decode(" ".join(arguments).encode("utf8"))
    except:
        return "Can't decode it"

def help_message(arguments, message):
    result = "Hey, %s!\nI can accept only these commands:\n" % message["from"]["first_name"]
    for command in CMD:
        result += "\t%s\n" % command

    return result

URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
CMD = {
    "/whoisyourdaddy": about,
    "/base64": base64_decode,
    "/help": help_message,
}
MyURL = "https://messiah.ddns.net/telegram/"
MyURL = ""
api = Session()
application = tornado.web.Application([
    (r"/", Handler),
])


def signal_term_handler(signal, frame):
    logging.error("Got SIGTERM. Quit.")
    api.get(URL + "setWebhook?url=")
    exit(0)


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
