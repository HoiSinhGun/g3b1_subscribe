import logging
from datetime import datetime
from queue import Queue
from typing import Union, List, Tuple

from telegram import Update, Bot, Message, User, Chat, ReplyMarkup, constants
from telegram.ext import CallbackContext, Dispatcher
from telegram.utils.helpers import DEFAULT_NONE
from telegram.utils.types import ODVInput, DVInput, JSONDict

import subscribe_db
import subscribe_main
import subscribe_token
import test_utils
import utilities
from log.g3b1_log import cfg_logger
from utilities import print_header_line, module_by_file_str

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)


def test_subscribe(update: Update, ctx: CallbackContext):
    print_header_line("cmd bot_all")
    bot_all = subscribe_db.bot_all()
    print(bot_all)
    print(f'todo bot: {bot_all["todo"]}')

    print_header_line("cmd subscribe %todo%")
    subscribe_main.hdl_cmd_subscribe(update, ctx, bkey='todo')

    print_header_line("cmd uname %user_1%")
    subscribe_main.hdl_cmd_uname(update, ctx, uname='uname_1')

    print_header_line("cmd uname %user_2%")
    update, ctx = test_utils.setup(subscribe_main.__file__, 2, 1, 2, 'user-2')
    subscribe_main.hdl_cmd_uname(update, ctx, uname='uname_2')


def main():
    update, ctx = test_utils.setup(subscribe_main.__file__)
    test_subscribe(update, ctx)


if __name__ == '__main__':
    main()
