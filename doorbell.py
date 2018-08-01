#!/usr/bin/env python3

import logging
import os.path
import random
import requests
import signal
import subprocess
import sys
import threading

import toml

from telegram.bot import Bot as TelegramBot

from doorbell import DoorbellBot

_doorbell_bot = None

def main():
    if not os.path.isfile("secrets.toml"):
        print("secrets.toml does not exist. Please create a copy from secrets.example.toml")
        exit(1)

    with open("secrets.toml") as f:
        config = toml.load(f)

    if "proxy" in config:
        logging.error("Proxy config is not supported yet")
        exit(1)

        # request_session = requests.Session()
        # request_session.proxies.update(config["proxy"])
        # # Replace the requests import in mmpy_bot to use our proxied Session instance.
        # mmpy_bot.mattermost_v4.requests = request_session
        # mmpy_bot.mattermost.requests = request_session

    client = TelegramBot(config['telegram']['bot_token'], base_url=config['telegram']['server'])

    _doorbell_bot = DoorbellBot(client, config["doorbell"])
    _doorbell_bot.start()


def signal_handler(sig, frame):
    if _doorbell_bot is not None:
        _doorbell_bot.stop()


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    signal.signal(signal.SIGINT, signal_handler)
    main()