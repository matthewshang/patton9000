import hangups
from handler import Handler


class LogHandler(Handler):
    def __init__(self, bot):
        Handler.__init__(self, bot)

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        if not isinstance(event, hangups.ChatMessageEvent):
            return
        sender = self._bot._user_list.get_user(event.user_id)
        conv = self._bot._conv_list.get(event.conversation_id)
        print(
            f'{event.timestamp} - {sender.full_name} in {conv.name}: {event.text}'
        )
