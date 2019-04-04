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

    def _respond(self, text: str, tokens: [str], conv_id, sender):

        def has(txt, keys):
            for key in keys:
                if key in txt:
                    return True
            return False

        if has(tokens, ['hi', 'hello']):
            return self._send(conv_id, f'Greetings {sender.first_name}')
        if 'greetings' in tokens:
            return self._send(conv_id, f'Hi {sender.first_name}')

        choices = ['Yes', 'Affirmative', 'No', 'Negatory', 'Maybe', 'Perhaps']
        qs = ['should', 'will', 'can', 'do', 'are', 'is', 'did']
        # Greater than three so 'alien tami will' is invalid
        if len(tokens) > 3 and has(tokens, qs):
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
        sender = self._bot._user_list.get_user(event.user_id)
        if 'alien tami' in text and self._check_sender(sender):
            text = text.replace('alien tami', '')
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = text.strip()
            tokens = text.split(' ')
            logging.debug(f'processed: {tokens}')
            self._respond(tokens, text, event.conversation_id, sender)
