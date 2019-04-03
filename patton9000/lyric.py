

class PeriodicLyric:
    def __init__(self, bot, loop):
        self.bot = bot
        self.loop = loop
        with open('patton9000/dmx.txt') as f:
            self.lyrics = f.readlines()
        self.it = iter(self.lyrics)

    async def __call__(self):
        lyric = next(self.it)
        for conv in self.bot._conv_list.get_all():
            if len(conv.users) == 2:
                self.bot.send_message(conv.id_, lyric)
            print(f'sent {lyric} to {conv.name}')
