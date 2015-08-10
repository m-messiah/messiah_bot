# coding=utf-8
__author__ = 'm_messiah'
__url__ = "https://messiah-bot.appspot.com"
from base64 import b64decode, b64encode
from random import choice
from fuzzywuzzy import process
import time
from os import environ
from urllib import unquote, quote, urlencode
from flask import Flask, request, jsonify
from google.appengine.api import urlfetch

app = Flask(__name__)
app.config['DEBUG'] = False

try:
    from bot_token import BOT_TOKEN
except ImportError:
    BOT_TOKEN = environ["TOKEN"]


USERS = {}


def error():
    return jsonify(result="Info", text="Messiah_bot")


class Handler(object):
    def __init__(self, chatid):
        self.chatid = chatid
        self.last = None
        self.url = "https://api.telegram.org/bot%s/" % BOT_TOKEN

    def send(self, text=None, sticker=None):
        response = {
            'chat_id': self.chatid,
            'text': text,
            'sticker': sticker
        }
        payload = urlencode(response)
        if sticker:
            o = urlfetch.fetch(self.url + "sendSticker",
                               payload=payload,
                               method=urlfetch.POST).content
        elif text:
            o = urlfetch.fetch(self.url + "sendMessage",
                               payload=payload,
                               method=urlfetch.POST).content
        else:
            o = "Bad call"
        app.logger.debug(str(o))

    def not_found(self):
        self.send(text="Command not found. Try /help")

    def start(self, _, message):
        self.send(text="Hello, %s! I am listening you."
                       % message['from']['nickname'])

    def help(self, args, message):
        commands = {
            "about": "About my author",
            "base64": "Base64 encode/decode",
            "help": "This help message",
            "uri": "URI encode/decode",
            "morse": "Morse decode",
            "start": "Start messaging",
        }
        if args and args.strip() in commands:
            self.send(text="%s - %s" % (args.strip(), commands[args.strip()]))
        else:
            result = [
                "Hey, %s!" % message["from"].get("first_name"),
                "\rI can accept these commands:",
            ] + sorted(commands.keys()) + [
                "\nFor more info send me: /help command"
            ]
            self.send(text="\n\t".join(result))

    def about(self, _, message):
        self.send(text="Hey, %s!\n"
                       "My author is @m_messiah.\n"
                       "You can find this nickname at:\n"
                       "\t+ Telegram\n"
                       "\t+ Twitter\n"
                       "\t+ Instagram\n"
                       "\t+ VK\n"
                       "\t+ GitHub (m-messiah)\n"
                       % message['from']["first_name"])

    def handle(self, message):
        if 'text' in message:
            text = message['text']
            if text[0] == '/':
                command, _, arguments = text.partition(" ")

                self.last = getattr(self, command[1:],
                                    self.not_found)(arguments, message)
            elif self.last:
                self.last = getattr(self, self.last)(None, message)
            else:
                self.speech(message)
        elif 'sticker' in message:
            self.send(text="Sticker = %s" % message["sticker"].get("file_id"))

    def base64(self, args, message):
        if args == "":
            self.send(text="Enter Base64 encoded/plain text")
            return "base64"
        elif args is None:
            args = message["text"]

        try:
            response = b64decode(args.encode("utf8"))
            assert len(response)
        except:
            response = b64encode(args.encode("utf8"))
        finally:
            self.send(text=response)

    def uri(self, args, message):
        if args == "":
            self.send(text="Enter URI encoded/needed to be encode text")
            return "uri"
        elif args is None:
            args = message["text"]
        try:
            response = unquote(args)
            if response == args:
                response = quote(args.encode("utf8"))
        except Exception as e:
            response = "Error: %s" % e
        finally:
            self.send(text=response)

    def morse(self, args, message):
        if args == "":
            self.send(text="Enter your morse code")
            return "morse"
        elif args is None:
            args = message["text"]

        morse_en = {
            '.....': '5', '-.--.-': '(', '..--..': '?', '.----': '1',
            '---...': ':', '......': '.', '----.': '9', '---..': '8',
            '..---': '2', '--..--': '!', '....-': '4', '-....': '6',
            '-.-.-.': ';', '-----': '0', '...--': '3',
            '.-..-.': '"', '--...': '7', '/': ' ', '.-.-.-': ',',
            '---': 'O', '--.': 'G', '-...': 'B', '-..-': 'X',
            '.-.': 'R', '--.-': 'Q', '--..': 'Z', '.--': 'W',
            '.-': 'A', '..': 'I', '-.-.': 'C', '..-.': 'F',
            '-.--': 'Y', '-': 'T', '.': 'E', '.-..': 'L', '...': 'S',
            '..-': 'U', '-.-': 'K', '-..': 'D', '.---': 'J',
            '.--.': 'P', '--': 'M', '-.': 'N', '....': 'H', '...-': 'V',
            '.----.': "'", '-....-': "–", '-..-.': "/", '.--.-.': "@"}

        morse_ru = {
            '.....': '5', '-.--.-': '(', '..--..': '?', '.----': '1',
            '---...': ':', '......': '.', '----.': '9', '---..': '8',
            '..---': '2', '--..--': '!', '....-': '4', '-....': '6',
            '-.-.-.': ';', '-----': '0', '.-.-.-': ',', '...--': '3',
            '.-..-.': '"', '--...': '7', '/': ' ', '.----.': "'",
            "..-..": 'Э', "---": 'О', "--.": 'Г', "-...": 'Б',
            "-..-": 'Ь', ".-.": 'Р', "--.-": 'Щ', "--..": 'З',
            ".--": 'В', ".-": 'А', "..": 'И', "-.-.": 'Ц',
            "..-.": 'Ф', "..--": 'Ю', "-": 'Т', ".": 'Е',
            ".-.-": 'Я', ".-..": 'Л', "--.--": 'Ъ', "...": 'С',
            "..-": 'У', "----": 'Ш', "---.": 'Ч', "-.-": 'К',
            "-..": 'Д', ".---": 'Й', ".--.": 'П', "--": 'М',
            "-.": 'Н', "....": 'Х', "...-": 'Ж', "-.--": "Ы", '-....-': '–',
            '-..-.': '/', '.--.-.': '@'}

        def decode(text):
            return "".join(letters.get(c, "_") for c in text)

        def invert(word):
            # ord('-') = 45, ord('.') = 46
            return word.translate({46: 45, 45: 46})

        letters = morse_en
        args = args.split()
        plain_text = decode(args)
        decrypted_text = ["Answer:"]
        if any(c is not "_" for c in plain_text):
            decrypted_text.append("eng:\t%s" % plain_text)

        plain_text = decode(map(invert, args))
        if any(c is not "_" for c in plain_text):
            decrypted_text.append("eng_rev:\t%s" % plain_text)

        letters = morse_ru
        plain_text = decode(args)
        if any(c is not "_" for c in plain_text):
            decrypted_text.append("ru:\t%s" % plain_text)

        plain_text = decode(map(invert, args))
        if any(c is not "_" for c in plain_text):
            decrypted_text.append("ru rev:\t%s" % plain_text)

        self.send(text="\n".join(decrypted_text))

    def speech(self, message):
        responses = {
            "Hello": ["Hi there!", "Hi!", "Welcome!", "Hello, {name}!"],
            "Hi there": ["Hello!", "Hello, {name}!", "Hi!", "Welcome!"],
            "Hi!": ["Hi there!", "Hello, {name}!", "Welcome!", "Hello!"],
            "Welcome": ["Hi there!", "Hi!", "Hello!", "Hello, {name}!", ],
            "How are you?": ["I'm fine!", "Status: Working...",
                             "I'm doing great."],
            "Good bye": ["Bye, {name}!"],
            "What time is it?": ["Adventure Time!", "{date} UTC"],
        }

        stickers = {
            "adventure_time": "BQADAgADeAcAAlOx9wOjY2jpAAHq9DUC",
        }
        leven = process.extract(message.get("text", ""),
                                responses.keys(), limit=1)[0]

        if leven[1] < 75:
            self.send(text="I can not understand you")
        else:
            response = choice(responses[leven[0]]).format(
                name=message['chat'].get("first_name", ""),
                date=time.ctime(int(message.get("date")))
            )

            if response == "Adventure Time!":
                self.send(sticker=stickers['adventure_time'])
            else:
                self.send(text=response)



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
            sender = message['chat']['id']
            if sender not in USERS:
                USERS[sender] = Handler(sender)

            USERS[sender].handle(message)
            return jsonify(result="OK", text="Accepted")
        except Exception as e:
            app.logger.warning(str(e))
            return jsonify(result="Fail", text=str(e))


@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

