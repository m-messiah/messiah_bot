# coding=utf-8
from urllib.parse import unquote, quote

__author__ = 'm_messiah'
from base64 import b64decode, b64encode
from random import choice
from fuzzywuzzy import process
import time
from json import dumps

RESPONSES = {
    "Hello": ["Hi there!", "Hi!", "Welcome!", "Hello, {name}!"],
    "Hi there": ["Hello!", "Hello, {name}!", "Hi!", "Welcome!"],
    "Hi!": ["Hi there!", "Hello, {name}!", "Welcome!", "Hello!"],
    "Welcome": ["Hi there!", "Hi!", "Hello!", "Hello, {name}!", ],
    "How are you?": ["I'm fine!", "Status: Working...", "I'm doing great."],
    "Good bye": ["Bye, {name}!"],
    "What time is it?": ["Adventure Time!", "{date} UTC"],
}

STICKERS = {
    "adventure_time": "BQADAgADeAcAAlOx9wOjY2jpAAHq9DUC",
}


def human_response(_, message):
    leven = process.extract(message.get("text", ""), RESPONSES, limit=1)[0]

    response = {'chat_id': message['from']['id']}
    if leven[1] < 75:
        response['text'] = "I can not understand you"
    else:
        response['text'] = choice(RESPONSES[leven[0]]).format_map(
            {'name': message["from"].get("first_name", ""),
             'date': time.ctime(int(message.get("date"))), }
        )

    if response['text'] == "Adventure Time!":
        response['sticker'] = STICKERS['adventure_time']
        del response['text']

    return response


def start(_, message):
    return {'chat_id': message['from']['id'], 'text': "I am awake!"}


def about(_, message):
    return {'chat_id': message['from']['id'],
            'text': "Hey, %s!\n"
                    "My author is @m_messiah."
                    "You can find this nickname at:"
                    "\t+ Telegram"
                    "\t+ Twitter"
                    "\t+ Instagram"
                    "\t+ VK"
                    "\t+ GitHub (m-messiah)"
                    % message["from"]["first_name"]
            }


def base64_code(arguments, message):
    if arguments == "":
        response = {'chat_id': message['from']['id'],
                    'text': "Enter Base64 encoded/plain text"}
        return response
    elif arguments is None:
        arguments = message["text"]

    response = {'chat_id': message['from']['id']}
    try:
        response['text'] = b64decode(arguments.encode("utf8"))
        assert len(response['text'])
    except:
        response['text'] = b64encode(arguments.encode("utf8"))
    finally:
        return response


def help_message(_, message):
    response = {'chat_id': message['from']['id']}
    result = ["Hey, %s!" % message["from"].get("first_name"),
              "\rI can accept these commands:"]
    for command in CMD:
        result.append(command)
    response['text'] = "\n\t".join(result)
    return response


def uri(arguments, message):
    if arguments == "":
        response = {'chat_id': message['from']['id'],
                    'text': "Enter URI encoded/needed to be encode text"}
        return response
    elif arguments is None:
        arguments = message["text"]
    response = {'chat_id': message['from']['id']}
    try:
        response['text'] = unquote(arguments)
        if response['text'] == arguments:
            response['text'] = quote(arguments.encode("utf8"))
    except Exception as e:
        response['text'] = "Error: %s" % e
    finally:
        return response


def morse(arguments, message):
    if arguments == "":
        response = {
            'chat_id': message['from']['id'],
            'text': "Enter your morse code",
        }
        return response
    elif arguments is None:
        arguments = message["text"]

    MORSE_EN = {
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
        '.--.': 'P', '--': 'M', '-.': 'N', '....': 'H',
        '...-': 'V', '.----.': "'", '-....-': "–", '-..-.': "/", '.--.-.': "@"}

    MORSE_RU = {
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

    letters = MORSE_EN
    response = {'chat_id': message['from']['id']}
    arguments = arguments.split()
    plain_text = decode(arguments)
    decrypted_text = ["Answer:"]
    if any(c is not "_" for c in plain_text):
        decrypted_text.append("eng:\t%s" % plain_text)

    plain_text = decode(map(invert, arguments))
    if any(c is not "_" for c in plain_text):
        decrypted_text.append("eng_rev:\t%s" % plain_text)

    letters = MORSE_RU
    plain_text = decode(arguments)
    if any(c is not "_" for c in plain_text):
        decrypted_text.append("ru:\t%s" % plain_text)

    plain_text = decode(map(invert, arguments))
    if any(c is not "_" for c in plain_text):
        decrypted_text.append("ru rev:\t%s" % plain_text)

    response["text"] = "\n".join(decrypted_text)
    return response


CMD = {
    "<speech>": human_response,
    "/whoisyourdaddy": about,
    "/base64": base64_code,
    "/help": help_message,
    "/uri": uri,
    "/morse": morse,
    "/start": start,
}
