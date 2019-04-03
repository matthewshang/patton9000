import argparse
import logging
import logging.config
import os

import appdirs
from console_args import CONSOLE_ARGS
import lyricsgenius
from bot import HangoutsBot


def main():
    logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)

    if CONSOLE_ARGS.dev_mode:
        logging.info('Bot running in development mode')
    bot = HangoutsBot(CONSOLE_ARGS.token_path)
    bot.run()


if __name__ == '__main__':
    main()
