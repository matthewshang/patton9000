import argparse
import asyncio
import logging
import os
import random

import hangups
import appdirs
import emoji


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

        self._client = None  # hangups.Client
        self._conv_list = None  # hangups.ConversationList
        self._user_list = None  # hangups.UserList

        self._sticker = None  # hangups.UploadedImage

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
            await self._on_message(conv_event)

    async def _on_message(self, conv_event):
        conv_id = conv_event.conversation_id
        user = self._user_list.get_user(conv_event.user_id)
        print('{}: {!r}'.format(user.full_name, conv_event.text))

        if 'daniel' in conv_event.text.lower():
            await self._clone(conv_id)
        # if key in conv_event.text.lower():
        #     await self._purge(conv_event.conversation_id)

        if 'emogi' in conv_event.text.lower():
            self.send_message(conv_id, hangups.ChatMessageSegment(
                emoji.random_emoji()[0]))
        # if 'oppress' in conv_event.text.lower():
        #     for i in range(50):
        #         await self._set_otr_status(conv_event.conversation_id, (i % 2) + 1)

        #     self.send_message(conv_event.conversation_id,
        #                       hangups.ChatMessageSegment('okay'))
        # if conv_event.text == '!!dab':
            # print(self._get_group_ids(conv_id))
            # print(self._conv_list._conv_dict)
            # await self._create_empty_conv(user.id_.gaia_id)

        # key = '!squadup'
        # if key in conv_event.text.lower():
        #     await self._purge(conv_id)

        # if 'daniel' in conv_event.text.lower():
        #     await self._kick_random(conv_id)

        # if len(conv_event.attachments) > 0:
        #     print('{}'.format(conv_event.attachments))
        # await self._send_sticker(conv_event.conversation_id)
        # if conv_event.text == 'Hi Leo':
        #     for i in range(100):
        #         await self._conv_list.get(conv_event.conversation_id).rename("Hi gigolo " + str(i))
        # if conv_event.text == '!music':
        #     self.send_message(conv_id,
        #                       hangups.ChatMessageSegment('no'))
        # if conv_event.text == '!arvind':
        #     self.send_message(conv_event.conversation_id,
        #                       hangups.ChatMessageSegment('black -Varun'))

    async def _on_connect(self):
        print('connected')

        # self._sticker = await self._upload_image('image.png')

        self._user_list, self._conv_list = (
            await hangups.build_user_conversation_list(self._client)
        )
        self._conv_list.on_event.add_observer(self._on_event)
        self._print_convs()
        self._print_users()

    async def _send_sticker(self, conv_id):
        conv = self._conv_list.get(conv_id)
        request = hangups.hangouts_pb2.SendChatMessageRequest(
            request_header=self._client.get_request_header(),
            event_request_header=hangups.hangouts_pb2.EventRequestHeader(
                conversation_id=hangups.hangouts_pb2.ConversationId(
                    id=conv_id
                ),
                client_generated_id=self._client.get_client_generated_id(),
            ),
            existing_media=hangups.hangouts_pb2.ExistingMedia(
                photo=hangups.hangouts_pb2.Photo(
                    photo_id=self._sticker.image_id
                )
            )
        )

        await self._client.send_chat_message(request)

    async def _upload_image(self, file):
        image_file = open(file, 'rb')
        uploaded_image = await self._client.upload_image(
            image_file, return_uploaded_image=True
        )
        return uploaded_image

    async def _add_user(self, conv_id, user_gaia_id):
        conv = self._conv_list.get(conv_id)
        request = hangups.hangouts_pb2.AddUserRequest(
            request_header=self._client.get_request_header(),
            event_request_header=conv._get_event_request_header(),
            invitee_id=hangups.hangouts_pb2.InviteeID(
                gaia_id=user_gaia_id,
            )
        )
        await self._client.add_user(request)

    async def _remove_user(self, conv_id, user_gaia_id):
        conv = self._conv_list.get(conv_id)
        request = hangups.hangouts_pb2.RemoveUserRequest(
            request_header=self._client.get_request_header(),
            event_request_header=conv._get_event_request_header(),
            participant_id=hangups.hangouts_pb2.ParticipantId(
                gaia_id=user_gaia_id
            ),
        )
        await self._client.remove_user(request)

    async def _set_otr_status(self, conv_id, status):
        conv = self._conv_list.get(conv_id)
        request = hangups.hangouts_pb2.ModifyOTRStatusRequest(
            request_header=self._client.get_request_header(),
            event_request_header=conv._get_event_request_header(),
            otr_status=status
        )
        await self._client.modify_otr_status(request)

    async def _purge(self, conv_id):
        conv = self._conv_list.get(conv_id)
        for user in conv.users:
            if not user.is_self:
                await self._remove_user(conv_id, user.id_.gaia_id)
        await self._conv_list.leave_conversation(conv_id)

    async def _clone(self, conv_id):
        conv = self._conv_list.get(conv_id)
        ids = [hangups.hangouts_pb2.InviteeID(
            gaia_id=u.id_.gaia_id,
            fallback_name=u.full_name
        ) for u in conv.users]

        req = hangups.hangouts_pb2.CreateConversationRequest(
            request_header=self._client.get_request_header(),
            type=hangups.hangouts_pb2.CONVERSATION_TYPE_GROUP,
            client_generated_id=self._client.get_client_generated_id(),
            name=conv.name,
            invitee_id=ids
        )
        res = await self._client.create_conversation(req)
        self._conv_list._add_conversation(res.conversation)

        conv_id = res.conversation.conversation_id.id
        conv = self._conv_list.get(conv_id)
        self.send_message(conv_id, hangups.ChatMessageSegment("Hi"))

    async def _kick_random(self, conv_id):
        conv = self._conv_list.get(conv_id)
        user = random.choice(conv.users)
        while user.is_self:
            user = random.choice(conv.users)
        await self._remove_user(conv_id, user.id_.gaia_id)

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

    def _get_group_ids(self, conv_id):
        conv = self._conv_list.get(conv_id)
        ids = []
        for user in conv.users:
            if not user.is_self:
                ids.append(user.id_.gaia_id)
        return ids

    async def _create_empty_conv(self, user_gaia_id):
        request = hangups.hangouts_pb2.CreateConversationRequest(
            request_header=self._client.get_request_header(),
            type=hangups.hangouts_pb2.CONVERSATION_TYPE_GROUP,
            client_generated_id=self._client.get_client_generated_id(),
            invitee_id=[
                hangups.hangouts_pb2.InviteeID(
                    gaia_id=user_gaia_id
                )
            ],
            name='hi'
        )
        res = await self._client.create_conversation(request)
        print(res.conversation)

        _, conv_list = await hangups.build_user_conversation_list(self._client)
        print(conv_list._conv_dict)
        print(res.conversation.conversation_id.id)

        request = hangups.hangouts_pb2.GetConversationRequest(
            request_header=self._client.get_request_header(),
            conversation_spec=hangups.hangouts_pb2.ConversationSpec(
                conversation_id=res.conversation.conversation_id
            ),
        )
        res = await self._client.get_conversation(request)
        print(res.conversation_state)

        # await self.send_message(res.conversation.conversation_id,
        # hangups.ChatMessageSegment('asdf'))

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    bot = HangoutsBot(args.token_path)
    bot.run()


if __name__ == '__main__':
    run_bot()
