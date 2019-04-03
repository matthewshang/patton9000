import hangups
import logging
from handler import Handler


class LogHandler(Handler):
    def __init__(self, bot):
        Handler.__init__(self, bot)

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        if not isinstance(event, hangups.ChatMessageEvent):
            return
        sender = self._bot._user_list.get_user(event.user_id)
        conv = self._bot._conv_list.get(event.conversation_id)
        name = sender.full_name if not conv.name else conv.name
        logging.info(f'{sender.full_name} to "{name}": {event.text}')
