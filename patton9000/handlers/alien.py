import hangups
from handler import Handler
import random


class AlienHandler(Handler):
    def __init__(self, bot):
        Handler.__init__(self, bot)

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        if not isinstance(event, hangups.ChatMessageEvent):
            return
        key = 'alien tami'
        conv_id = event.conversation_id
        text: str = event.text.lower()
        choices = ['Yes', 'No', 'Maybe']
        if key in text:
            if 'should' in text:
                self._bot.send_message(conv_id, random.choice(choices))
