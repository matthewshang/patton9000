import hangups
from handler import Handler
import random


class AlienHandler(Handler):
    first_event = True

    def __init__(self, bot):
        Handler.__init__(self, bot)

    def _send(self, conv_id, msg) -> None:
        self._bot.send_message(conv_id, msg)

    def _respond(self, tokens: [str], conv_id, sender):

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
        if has(tokens, ['should', 'will', 'can', 'do', 'are']):
            return self._send(conv_id, random.choice(choices))

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        if not isinstance(event, hangups.ChatMessageEvent):
            return
        text: str = event.text.lower()
        if 'alien tami' in text:
            conv_id = event.conversation_id
            sender = self._bot._user_list.get_user(event.user_id)
            tokens = text.split(' ')
            self._respond(tokens, conv_id, sender)
