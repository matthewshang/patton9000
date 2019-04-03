import argparse
import os

import appdirs


def _parse_arguments():
    parser = argparse.ArgumentParser()

    dirs = appdirs.AppDirs('hangups', 'hangups')
    default_token_path = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')

    parser.add_argument(
        '--token-path',
        default=default_token_path,
        help='path used to store OAuth refresh token')

    parser.add_argument(
        '-d',
        '--dev-mode',
        action='store_true',
        help='run bot in development mode')
    return parser.parse_args()


CONSOLE_ARGS = _parse_arguments()

del _parse_arguments
