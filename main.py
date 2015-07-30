__author__ = 'm_messiah'
from os import environ
import urllib
from flask import Flask, request, jsonify
from google.appengine.api import urlfetch

app = Flask(__name__)
app.config['DEBUG'] = False

from commands import CMD

try:
    from bot_token import BOT_TOKEN
except ImportError:
    BOT_TOKEN = environ["TOKEN"]

URL = "https://api.telegram.org/bot%s/" % BOT_TOKEN
MyURL = "https://messiah-bot.appspot.com"
LAST_COMMAND = {}


def error():
    return jsonify(result="Info", text="Messiah_bot")


def not_found(_, message):
    return {
        'chat_id': message['chat']['id'],
        'text': "Command not found. Try /help"
    }


def send_reply(response):
    app.logger.debug("SENT\t%s", response)
    payload = urllib.urlencode(response)
    if 'sticker' in response:
        urlfetch.fetch(url=URL + "sendSticker",
                       payload=payload,
                       method=urlfetch.POST)
    elif 'text' in response:
        o = urlfetch.fetch(URL + "sendMessage",
                           payload=payload,
                           method=urlfetch.POST)
        app.logger.debug(str(o.content))


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return error()
    else:
        if 'Content-Type' not in request.headers:
            return error()
        if request.headers['Content-Type'] != 'application/json':
            return error()
        app.logger.debug("Request: %s", request)
        try:
            update = request.json
            message = update['message']
            sender = message['chat']
            text = message.get('text')
            if text:
                app.logger.debug("MESSAGE FROM\t%s",
                                 sender['username'] if 'username' in sender
                                 else sender['id'])

                if text[0] == '/':
                    command, _, arguments = text.partition(" ")
                    app.logger.debug("REQUEST\t%s\t%s\t'%s'",
                                     sender['id'],
                                     command.encode("utf8"),
                                     arguments.encode("utf8"))
                    response = CMD.get(command, not_found)(arguments, message)
                    send_reply(response)
                    LAST_COMMAND[sender["id"]] = command
                else:
                    if sender["id"] in LAST_COMMAND:
                        response_func = CMD.get(LAST_COMMAND[sender["id"]],
                                                CMD["<speech>"])
                        del LAST_COMMAND[sender["id"]]
                    else:
                        response_func = CMD["<speech>"]
                    response = response_func(None, message)
                    send_reply(response)

            elif message.get("sticker"):
                send_reply({
                    'chat_id': sender['id'],
                    'text': "Sticker id = %s"
                            % message["sticker"].get("file_id")
                })

            return jsonify(result="OK", text="Accepted")
        except Exception as e:
            app.logger.warning(str(e))
            return jsonify(result="Fail", text=str(e))


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

