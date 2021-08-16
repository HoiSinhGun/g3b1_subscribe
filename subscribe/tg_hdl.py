"""Subscription to learn the user pool."""

from telegram import Update, Message

from g3b1_serv import tg_reply, tgdata_main
from subscribe import logger
from subscribe.data import db


@tgdata_main.tg_handler()
def cmd_uname(upd: Update, replyToMsg: Message, user_id, uname: str = None) -> None:
    """Set uname with a length of 5 or greater for the user if the key given.
    Reply with the uname of the user
    """
    if replyToMsg:
        for_user_id = replyToMsg.from_user.id
    else:
        for_user_id = user_id
    if uname:
        if len(uname) < 5:
            upd.effective_message.reply_html(
                'The minimum length of the G3B1 username is 5 characters!'
            )
            return
        logger.debug(f"Setting uname {uname}")
        db.set_uname(for_user_id, uname)
    logger.debug(f"Reading uname")
    uname = db.read_uname(for_user_id)

    upd.effective_message.reply_html(
        f'The username is: {uname}.\n'
    )


@tgdata_main.tg_handler()
def cmd_edit(upd: Update, bkey: str = None) -> None:
    """Insert or save a bot.
    """
    logger.debug(f"Insert (/edit) bot")
    if bkey:
        db.bot_save(bkey)
        tg_reply.cmd_success(upd)


@tgdata_main.tg_handler()
def cmd_default(upd: Update, bkey: str = None) -> None:
    """Set the default bot for the user.
    """
    logger.debug(f"Set default bot to {bkey}")
    if bkey:
        db.bot_default(upd.effective_chat.id, upd.effective_user.id, bkey)
        tg_reply.cmd_success(upd)


@tgdata_main.tg_handler()
def cmd_subscribe(upd: Update, chat_id: int, user_id: int, bkey: str = None) -> None:
    """Subscribe to a bot %bkey% with current user and chat."""
    logger.debug(f"Subscribe to a bot")

    chat_id = upd.effective_chat.id
    db.for_chat(chat_id)
    user_id = upd.effective_user.id
    db.for_user(user_id)

    if bkey:
        db.bot_activate(chat_id, user_id, bkey)
        tg_reply.cmd_success(upd)
