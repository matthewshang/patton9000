from emoji import random_emoji
import hangups
from handler import Handler


class CommandHandler(Handler):
    def __init__(self, bot):
        Handler.__init__(self, bot)

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        if not isinstance(event, hangups.ChatMessageEvent):
            return

        text: str = event.text.lower()
        if '👽' in text:
            res = ''
            for _ in range(text.count('👽')):
                res += random_emoji()
            return self._bot.send_message(event.conversation_id, res)
