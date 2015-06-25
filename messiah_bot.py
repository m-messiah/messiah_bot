__author__ = 'm_messiah'
from requests import Session
import tornado.ioloop
import tornado.web
import tornado.escape
from base64 import b64decode

from bot_token import BOT_TOKEN

# noinspection PyAbstractClass
class Handler(tornado.web.RequestHandler):

        def get(self):
            try:
                updates = api.get(URL + "getUpdates")
                updates = updates.json()
                if updates["ok"]:
                    self.write("%s" % updates["result"])
                else:
                    print("FAIL: %s" % updates)
            except Exception as e:
                print("FAILURE: %s" % e)

        def post(self):
            try:
                update = tornado.escape.json_decode(self.request.body)
                message = update['message']
                text = message['text']
                if text[0] == '/':
                    command, *arguments = text.split(" ", 1)
                    reply = COMMANDS.get(command, not_found)(arguments, message)
                    self.sendMessage(reply, command, message['from']['id'])
                else:
                    self.sendMessage(not_found("", message), "/not_found",
                                     message['from']['id'])
            except Exception as e:
                print("FAILURE: %s" % e)

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

URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
COMMANDS = {
    "/whoisyourdaddy": about,
    "/base64": base64_decode,
}
MyURL = "https://messiah.ddns.net/telegram/"
api = Session()
application = tornado.web.Application([
    (r"/", Handler),
])



if __name__ == '__main__':
    set_hook = api.get(URL + "setWebhook?url=%s" % MyURL)
    if set_hook.status_code != 200:
        print("FAIL: %s" % set_hook.text)
        exit(1)
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
