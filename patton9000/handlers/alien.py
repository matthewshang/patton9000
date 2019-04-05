import logging
import random
import string

import hangups
from handler import Handler
import utils


class AlienHandler(Handler):
    TIMEOUT = 2000

    def __init__(self, bot):
        Handler.__init__(self, bot)
        self._users = {}

    def _send(self, conv_id, msg) -> None:
        self._bot.send_message(conv_id, msg)

    def _respond(self, text: str, tokens: [str], conv_id: str, sender):

        if utils.match_one(tokens[0], ['hi', 'hello']):
            return self._send(conv_id, f'Greetings {sender.first_name}')
        if utils.match_one(tokens[0], ['greetings']):
            return self._send(conv_id, f'Hi {sender.first_name}')

        if utils.match(tokens[0], ['who']):
            user = self._bot.get_random_user(conv_id)
            return self._send(conv_id, user.full_name)

        choices = ['Yes', 'Affirmative', 'No', 'Negatory', 'Maybe', 'Perhaps']
        qs = ['should', 'will', 'can', 'do', 'are', 'is', 'did']
        if utils.match(tokens, qs):
            if len(tokens) == 1:
                return self._send(conv_id, 'Please ask a full question bitch')
            return self._send(conv_id, random.choice(choices))

    def _check_sender(self, sender) -> bool:
        id = sender.id_.gaia_id
        t = utils.millis()
        if id not in self._users:
            self._users[id] = t
            return True
        elif t - self._users[id] > AlienHandler.TIMEOUT:
            self._users[id] = t
            return True
        else:
            return False

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        if not isinstance(event, hangups.ChatMessageEvent):
            return
        text: str = event.text.lower()
        sender = self._bot.get_user(event.user_id)
        if 'alien tami' in text and self._check_sender(sender):
            text = text.replace('alien tami', '')
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = text.strip()
            tokens = text.split(' ')
            logging.debug(f'processed: {tokens}')
            if len(tokens) > 0:
                self._respond(text, tokens, event.conversation_id, sender)
