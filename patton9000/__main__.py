import argparse
import logging
import logging.config
import os

import appdirs
import lyricsgenius
from bot import HangoutsBot


def main():
    parser = argparse.ArgumentParser()

    dirs = appdirs.AppDirs('hangups', 'hangups')
    default_token_path = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')

    parser.add_argument(
        '--token-path',
        default=default_token_path,
        help='path used to store OAuth refresh token')

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='log detailed debugging messages')
    args = parser.parse_args()

    logging.config.fileConfig(fname='log.conf', disable_existing_loggers=False)

    bot = HangoutsBot(args.token_path)
    bot.run()


if __name__ == '__main__':
    main()
