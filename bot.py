import argparse
import asyncio
import logging
import os

import hangups
import appdirs

def _get_parser(extra_args):
    """Return ArgumentParser with any extra arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    dirs = appdirs.AppDirs('hangups', 'hangups')
    default_token_path = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')
    parser.add_argument(
        '--token-path', default=default_token_path,
        help='path used to store OAuth refresh token'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='log detailed debugging messages'
    )
    for extra_arg in extra_args:
        parser.add_argument(extra_arg, required=True)
    return parser

class HangoutsBot:
    def __init__(self, token_path):
        self._token_path = token_path

        self._client = None # hangups.Client
        self._conv_list = None # hangups.ConversationList
        self._user_list = None # hangups.UserList

    def login(self, token_path):
        try:
            cookies = hangups.auth.get_auth_stdin(token_path)
            return cookies
        except hangups.GoogleAuthError:
            logging.exception('Error while attempting to login')
            return None

    def run(self):
        cookies = self.login(self._token_path)
        self._client = hangups.Client(cookies)
        self._client.on_connect.add_observer(self._on_connect)
        loop = asyncio.get_event_loop()
        task = asyncio.ensure_future(self._client.connect())

        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            task.cancel()
            loop.run_until_complete(task)
        finally:
            loop.close()

    def send_message(self, conv_id, message):
        self.send_message_segments(conv_id, [message])

    def send_message_segments(self, conv_id, segments):
        conv = self._conv_list.get(conv_id)
        asyncio.ensure_future(
            conv.send_message(segments)
        )

    async def _on_event(self, conv_event):
        sender = self._user_list.get_user(conv_event.user_id)
        if sender.is_self:
            return
        if isinstance(conv_event, hangups.ChatMessageEvent):
            print('received chat message: {!r}'.format(conv_event.text))
            if conv_event.text == '!purge':
                await self._remove_user(conv_event.conversation_id, sender.id_.gaia_id)

    async def _on_connect(self):
        print('connected')

        self._user_list, self._conv_list = (
            await hangups.build_user_conversation_list(self._client)
        )
        self._conv_list.on_event.add_observer(self._on_event)
        self._print_convs()
        self._print_users()

    async def _remove_user(self, conv_id, user_gaia_id):
        conv = self._conv_list.get(conv_id)
        event_request = conv._get_event_request_header()
        request = hangups.hangouts_pb2.RemoveUserRequest(
            request_header=self._client.get_request_header(),
            participant_id=hangups.hangouts_pb2.ParticipantId(
                gaia_id=user_gaia_id
            ),
            event_request_header=event_request,
        )
        await self._client.remove_user(request)

    def _print_convs(self):
        conversations = self._conv_list.get_all(include_archived=True)
        print('{} known conversations'.format(len(conversations)))
        for conversation in conversations:
            if conversation.name:
                name = conversation.name
            else:
                name = 'Unnamed conversation ({})'.format(conversation.id_)
            print('    {}'.format(name))

    def _print_users(self):
        users = self._user_list.get_all()
        print('{} known users'.format(len(users)))
        for user in users:
            print('    {}'.format(user.full_name))

def run_bot(*extra_args):
    args = _get_parser(extra_args).parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    bot = HangoutsBot(args.token_path)
    bot.run()

if __name__ == '__main__':
    run_bot()