"""Subscription to learn the user pool."""
import logging

from telegram import Update
from telegram.ext import CallbackContext

import subscribe_db
import tg_db
import tg_reply
import tgdata_main
import utilities
from log.g3b1_log import cfg_logger

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)
g3_m_str_subscribe: str = utilities.module_by_file_str(__file__)
COLUMNS_SUBSCRIBE = []


def map_id_uname(data_dict: dict, field_mapping: dict) -> dict:
    """ @:param data_dict {int: dict, int: dict, ...}"""
    map_dict = {}
    for row, row_data in data_dict.items():
        for k, v in field_mapping.items():
            tg_user_id = row_data[k]  # e.g. row[creat__tg_user_id] = 1
            if tg_user_id not in map_dict:
                read_uname = subscribe_db.read_uname(tg_user_id)
                map_dict.update({tg_user_id: read_uname})
            uname: str = map_dict[tg_user_id]
            row_data[v] = uname
    return data_dict


def extract_bkey_arg(update: Update, context: CallbackContext, cmd: str) -> str:
    if len(context.args) > 0:
        return context.args[0]

    update.effective_message.reply_html(
        'Provide a key in lower case.\n'
        'Examples:\n'
        f'/{cmd} <code>todo</code>\n'
        f'/{cmd} <code>meet</code>\n'
        f'/{cmd} <code>translate</code>\n'
    )


@tgdata_main.handler()
def hdl_cmd_uname(update: Update, ctx: CallbackContext, uname: str = None) -> None:
    """Set uname for user if key given.
    :type ctx: object
    :type uname: str
    :param update:
    :param ctx: !!!args: %uname%!!!
    """
    if uname:
        logger.debug(f"Setting uname {uname}")
        subscribe_db.set_uname(update.effective_user.id, uname)
    logger.debug(f"Reading uname")
    uname = subscribe_db.read_uname(update.effective_user.id)

    update.effective_message.reply_html(
        f'Your username is: {uname}.\n'
    )


@tgdata_main.handler()
def hdl_cmd_edit(update: Update, ctx: CallbackContext, bkey: str = None) -> None:
    """Insert or save a bot.
    :param bkey: key of the bot = g3_m_str
    :param ctx:
    :param update:
    :param ctx: !!!args: %bkey%!!!
    """
    logger.debug(f"Insert (/edit) bot")
    if bkey:
        subscribe_db.bot_save(bkey)
        tg_reply.command_successful(update)


@tgdata_main.handler()
def hdl_cmd_default(update: Update, ctx: CallbackContext, bkey: str = None) -> None:
    """Set the default bot for the user.
    :param bkey: key of the bot / g3_m_str
    :param update:
    :param ctx: !!!args: %bkey%!!!
    """
    logger.debug(f"Set default bot to {bkey}")
    if bkey:
        subscribe_db.bot_default(update.effective_chat.id, update.effective_user.id, bkey)
        tg_reply.command_successful(update)


@tgdata_main.handler()
def hdl_cmd_subscribe(update: Update, ctx: CallbackContext, bkey: str = None) -> None:
    """Subscribe to a bot %bkey% with current user and chat."""
    logger.debug(f"Subscribe to a bot")

    chat_id = update.effective_chat.id
    subscribe_db.for_chat(chat_id)
    user_id = update.effective_user.id
    subscribe_db.for_user(user_id)

    if bkey:
        subscribe_db.bot_activate(user_id, chat_id, bkey)
        tg_reply.command_successful(update)


def main() -> None:
    """Run the bot."""
    # str(bot_key): dict(db_row)
    tgdata_main.start_bot(__file_)


if __name__ == '__main__':
    main()
