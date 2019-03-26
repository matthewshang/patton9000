import hangups
from handler import Handler


class CommandHandler(Handler):
    def __init__(self, bot):
        Handler.__init__(self, bot)

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        if not isinstance(event, hangups.ChatMessageEvent):
            return
        self._bot.send_message(event.conversation_id, 'This is a test')
