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
from subscribe_token import BOT_TOKEN_SUBSCRIBE
from utilities import TgCommand

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)


def commands() -> dict:
    return dict(edit=
                TgCommand("edit", "subscribe_edit", hdl_cmd_subscribe_edit, hdl_cmd_subscribe_edit.__doc__, ['bkey']),
                default=
                TgCommand("default", "subscribe_default", hdl_cmd_subscribe_default, hdl_cmd_subscribe_default.__doc__,
                          ['bkey']),
                uname=
                TgCommand("uname", "subscribe_uname", hdl_cmd_subscribe_uname, hdl_cmd_subscribe_uname.__doc__,
                          ['bkey']),
                subscribe=
                TgCommand("subscribe", "subscribe_subscribe", hdl_cmd_subscribe_subscribe,
                          hdl_cmd_subscribe_subscribe.__doc__, ['bkey']))


def start(update: Update, context: CallbackContext) -> None:
    """Displays info on how to trigger an error."""
    tg_db.synchronize_from_message(update.message)

    commands_str = utilities.build_commands_str(commands())
    update.effective_message.reply_html(
        commands_str +
        utilities.build_debug_str(update)
    )


def hdl_message(update: Update, context: CallbackContext) -> None:
    """store message to DB"""
    message = update.message
    logger.debug(f"Handle message {message}")
    tg_db.synchronize_from_message(message)


def lookup_lod(lod, **kw):
    for row in lod:
        for k, v in kw.items():
            if row[k] != str(v): break
        else:
            return row
    return None


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


def hdl_cmd_subscribe_uname(update: Update, context: CallbackContext) -> None:
    """Set uname for user if key given. """
    logger.debug(f"Insert (/edit) bot")
    if context.args is not None and len(context.args) > 0:
        bkey_ = extract_bkey_arg(update, context, "uname")
        subscribe_db.set_uname(update.effective_user.id, bkey_)
    uname = subscribe_db.read_uname(update.effective_user.id)

    update.effective_message.reply_html(
        f'Your username is: {uname}.\n'
    )


def hdl_cmd_subscribe_edit(update: Update, context: CallbackContext) -> None:
    """Insert or save a bot."""
    logger.debug(f"Insert (/edit) bot")
    bkey_ = extract_bkey_arg(update, context, "edit")
    if bkey_:
        subscribe_db.bot_save(bkey_)
        tg_reply.command_successful(update)


def hdl_cmd_subscribe_default(update: Update, context: CallbackContext) -> None:
    """Set the default bot for the user."""
    logger.debug(f"Set default bot")
    bkey_ = extract_bkey_arg(update, context, "default")
    if bkey_:
        subscribe_db.bot_default(update.effective_chat.id, update.effective_user.id, bkey_)
        tg_reply.command_successful(update)


def hdl_cmd_subscribe_subscribe(update: Update, context: CallbackContext) -> None:
    """Subscribe to a bot %bkey% with current user and chat."""
    logger.debug(f"Subscribe to a bot")

    chat_id = update.effective_chat.id
    subscribe_db.for_chat(chat_id)
    user_id = update.effective_user.id
    subscribe_db.for_user(user_id)

    bkey_ = extract_bkey_arg(update, context, "subscribe")
    if bkey_:
        subscribe_db.bot_activate(user_id, chat_id, bkey_)
        tg_reply.command_successful(update)


def main() -> None:
    """Run the bot."""
    # str(bot_key): dict(db_row)

    tgdata_main.start_bot(__file__, commands(), start, hdl_message)


if __name__ == '__main__':
    main()
