# coding=utf-8
__author__ = 'm_messiah'
from base64 import b64decode
from random import choice
from fuzzywuzzy import process
import time

RESPONSES = {
    "Hello": ["Hi there!", "Hi!", "Welcome!", "Hello, {name}!"],
    "Hi there": ["Hello!", "Hello, {name}!", "Hi!", "Welcome!"],
    "Hi!": ["Hi there!", "Hello, {name}!", "Welcome!", "Hello!"],
    "Welcome": ["Hi there!", "Hi!", "Hello!", "Hello, {name}!",],
    "How are you?": ["I'm fine!", "Status: Working...", "I'm doing great."],
    "Good bye": ["Bye, {name}!"],
    "What time is it?": ["Adventure Time!", "{date} UTC"],
}

STICKERS = {
    "adventure_time": "BQADAgADeAcAAlOx9wOjY2jpAAHq9DUC",
}

def human_response(message):
    leven = process.extract(message.get("text", ""),
                            RESPONSES.keys(), limit=1)[0]
    if leven[1] < 75:
        return "I can not understand you"

    response = {'chat_id': message['from']['id'],
                'text': choice(RESPONSES.get(leven[0])).format_map(
                    {'name': message["from"].get("first_name", ""),
                     'date': time.ctime(int(message.get("date"))), }
                )}

    if response['text'] == "Adventure Time!":
        response['sticker'] = STICKERS['adventure_time']
        del response['text']

    return response


def about(arguments, message):
    response = {
        'chat_id': message['from']['id'],
        'text':  """Hey, %s!
My author is @m_messiah.
You can find this nickname at:
    + Telegram
    + Twitter
    + Instagram
    + VK
    + GitHub (m-messiah)
    """ % message["from"].get("first_name")
    }
    return response

def base64_decode(arguments, message):
    response = {'chat_id': message['from']['id']}
    try:
        response['text'] = b64decode(" ".join(arguments).encode("utf8"))
    except:
        response['text'] = "Can't decode it"
    finally:
        return response

def help_message(arguments, message):
    response = {'chat_id': message['from']['id']}
    result = ["Hey, %s!" % message["from"].get("first_name"),
              "\rI can accept only these commands:"]
    for command in CMD:
        result.append(command)
    response['text'] = "\n\t".join(result)
    return response


CMD = {
    "0": human_response,
    "/whoisyourdaddy": about,
    "/base64": base64_decode,
    "/help": help_message,
}
