import binascii
import logging
import random
import signal
import subprocess
import sys
import threading

from datetime import datetime, timedelta

import requests

from telegram.ext import Updater as TelegramUpdater
from telegram.chat import Chat as TelegramChat
from telegram.bot import Bot as TelegramBot


class DoorbellBot(object):
    def __init__(self, client: TelegramBot, config):
        self.client = client  # type: TelegramBot
        self.config = config

        self.chats = [TelegramChat(id=chat['chat_id'], type=chat['chat_type']) for chat in config['chats']]

        self.doorbell_proc = None

    def start(self):
        self.doorbell_proc = subprocess.Popen(
            [
                'rtl_433',
                '-X', self.config["spec"],  # spec for decoding OOK modulated data from the doorbell button
                '-R', '0'  # disable decoding of all other devices
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        things = binascii.hexlify(bytes(self.config["payload"]))
        needle = b"{%d}%s" % (len(things) * 4, things)

        doorbell_next = datetime.now()

        for line in iter(self.doorbell_proc.stdout.readline, b''):
            if needle in line and doorbell_next < datetime.now():
                doorbell_next = datetime.now() + timedelta(seconds=3)

                joke = random.choice(self.config["jokes"])

                logging.info("Sending joke: {}".format(joke))
                for chat in self.chats:
                    self.client.send_message(chat.id, text=joke)


    def stop(self):
        if self.doorbell_proc is None:
            return

        self.doorbell_proc.wait()
