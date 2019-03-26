import hangups


class Handler():
    _bot: 'HangoutsBot'

    def __init__(self, bot: 'HangoutsBot'):
        self._bot = bot

    async def on_event(self, event: hangups.ConversationEvent) -> None:
        raise NotImplementedError
