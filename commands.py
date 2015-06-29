# coding=utf-8
__author__ = 'm_messiah'
from base64 import b64decode
from random import choice
from fuzzywuzzy import process

responses = {
    "Hello": ["Hi there!", "Hi!", "Welcome!", "Hello, {name}!"],
    "Hi there": ["Hello!", "Hello, {name}!", "Hi!", "Welcome!"],
    "Hi!": ["Hi there!", "Hello, {name}!", "Welcome!", "Hello!"],
    "Welcome": ["Hi there!", "Hi!", "Hello!", "Hello, {name}!",],
    "How are you?": ["I'm fine!", "Status: Working...", "I'm doing great."],
    "Good bye": ["Bye, {name}!"]
}

def human_response(message):
    leven = process.extract(message.get("text", ""),
                            responses.keys(), limit=1)[0]
    if leven[1] < 75:
        return "I can not understand you"

    return choice(responses.get(leven[0])
                  ).format_map({'name': message["from"].get("first_name", ""),
                                'date': message.get("date", ""),
                                })


def about(arguments, message):
    return """Hey, %s!
My author is @m_messiah.
You can find this nickname at:
    + Telegram
    + Twitter
    + Instagram
    + VK
    + GitHub (m-messiah)
    """ % message["from"].get("first_name")

def base64_decode(arguments, message):
    try:
        return b64decode(" ".join(arguments).encode("utf8"))
    except:
        return "Can't decode it"

def help_message(arguments, message):
    result = ["Hey, %s!" % message["from"].get("first_name"),
              "\rI can accept only these commands:"]
    for command in CMD:
        result.append(command)
    return "\n\t".join(result)


CMD = {
    "0": human_response,
    "/whoisyourdaddy": about,
    "/base64": base64_decode,
    "/help": help_message,
}
