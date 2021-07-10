from datetime import datetime
from queue import Queue
from typing import Union, List, Tuple

from telegram import Update, Bot, Message, User, Chat, ReplyMarkup, constants
from telegram.ext import CallbackContext, Dispatcher
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import ODVInput, DVInput, JSONDict

import subscribe_main
import test_utils


class MyMessage(Message):

    def reply_html(self, text: str, disable_web_page_preview: ODVInput[bool] = DEFAULT_NONE,
                   disable_notification: DVInput[bool] = DEFAULT_NONE, reply_to_message_id: int = None,
                   reply_markup: ReplyMarkup = None, timeout: ODVInput[float] = DEFAULT_NONE,
                   api_kwargs: JSONDict = None, allow_sending_without_reply: ODVInput[bool] = DEFAULT_NONE,
                   entities: Union[List['MessageEntity'], Tuple['MessageEntity', ...]] = None,
                   quote: bool = None) -> 'Message':
        print(text)
        return self
        # return super().reply_html(text, disable_web_page_preview, disable_notification, reply_to_message_id,
        #                          reply_markup, timeout, api_kwargs, allow_sending_without_reply, entities, quote)


def test_subscribe(update: Update, ctx: CallbackContext):
    ctx.args = ['todo']
    subscribe_main.hdl_cmd_subscribe_subscribe(update, ctx)

    print("cmd uname:")
    ctx.args = ['uname_1']
    subscribe_main.hdl_cmd_subscribe_uname(update, ctx)

    print("cmd uname:")
    update, ctx = test_utils.setup(subscribe_main.BOT_TOKEN_SUBSCRIBE, 2, 1, 2, 'user-2')
    ctx.args = ['uname_2']
    subscribe_main.hdl_cmd_subscribe_uname(update, ctx)


def main():
    message = MyMessage(message_id=1, date=datetime.now(),
                        chat=Chat(id=1, type=constants.CHAT_GROUP),
                        from_user=User(id=1, first_name='GUNNAR', is_bot=False)
                        )
    update = Update(1, message)
    dispatcher = Dispatcher(Bot(subscribe_main.BOT_TOKEN_SUBSCRIBE), Queue())
    context = CallbackContext(dispatcher)
    test_subscribe(update, context)


if __name__ == '__main__':
    main()
