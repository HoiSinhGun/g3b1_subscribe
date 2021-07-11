import logging
from typing import Tuple

from sqlalchemy import MetaData, create_engine
from sqlalchemy import Table
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine.mock import MockConnection
from telegram import Message, Chat, User  # noqa

from log.g3b1_log import cfg_logger
# create console handler and set level to debug
from tg_db import externalize_chat_id, externalize_user_id

BOT_BKEY_SUBSCRIBE = "subscribe"
BOT_BKEY_SUBSCRIBE_LC = BOT_BKEY_SUBSCRIBE.lower()

DB_FILE_SUBSCRIBE = rf'C:\Users\IFLRGU\Documents\dev\g3b1_{BOT_BKEY_SUBSCRIBE_LC}.db'
MetaData_SUBSCRIBE = MetaData()
Engine_SUBSCRIBE = create_engine(f"sqlite:///{DB_FILE_SUBSCRIBE}")
MetaData_SUBSCRIBE.reflect(bind=Engine_SUBSCRIBE)

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)


def bot_all() -> dict:
    bot_dict = {}
    with Engine_SUBSCRIBE.connect() as con:
        rs = con.execute(bot_table().select())
        for row in rs:
            d = dict(row)
            bot_dict.update({row['bkey']: d})
    return bot_dict


def bot_table() -> Table:
    return MetaData_SUBSCRIBE.tables["bot"]


def sql_bot_by_bkey(bkey: str) -> str:
    return f'SELECT ROWID FROM {bot_table().name} WHERE bkey = "{bkey}"'


def bot_id_by_key(bkey: str, con_input: MockConnection = None) -> int:
    def do_it(con: MockConnection) -> int:
        select = con.execute(sql_bot_by_bkey(bkey))
        row: Tuple = select.fetchone()
        if not row:
            return -1
        bot_id: int = int(row[0])
        return bot_id

    if con_input:
        return do_it(con_input)
    else:
        with Engine_SUBSCRIBE.connect() as con_new:
            return do_it(con_new)


def set_uname(tg_user_id: int, uname: str) -> int:
    with Engine_SUBSCRIBE.connect() as con:
        result = con.execute("UPDATE user_settings SET uname=:uname WHERE tg_user_id=:tg_user_id", uname=uname,
                             tg_user_id=tg_user_id)
        if result.rowcount:
            return 0

        table: Table = MetaData_SUBSCRIBE.tables["user_settings"]
        values = dict(tg_user_id=tg_user_id, uname=uname)
        insert_stmnt: insert = insert(table).values(values)
        logger.debug(f"Insert statement: {insert_stmnt}")
        con.execute(insert_stmnt)
        return 0


def read_uname(tg_user_id: int) -> str:
    with Engine_SUBSCRIBE.connect() as con:
        select = con.execute("SELECT uname FROM user_settings WHERE tg_user_id=:tg_user_id", tg_user_id=tg_user_id)
        row: Tuple = select.fetchone()
        if not row:
            return None
        uname: str = row[0]
        return uname


def id_by_uname(uname: str) -> int:
    with Engine_SUBSCRIBE.connect() as con:
        select = con.execute("SELECT tg_user_id FROM user_settings WHERE uname=:uname", uname=uname)
        row: Tuple = select.fetchone()
        if not row:
            return 0
        tg_user_id: int = row[0]
        return tg_user_id


def bot_default(tg_user_id: int, tg_chat_id: int, bkey: str):
    logger.debug(f"Save or update setting: user-chat bot default to {bkey}")

    def do_it() -> int:
        with Engine_SUBSCRIBE.connect() as con:
            table: Table = MetaData_SUBSCRIBE.tables["user_chat_settings"]
            bot_id: int = bot_id_by_key(bkey, con)
            if bot_id < 1:
                return -1

            # Try update
            result = con.execute(""
                                 "UPDATE user_chat_settings SET bot_id=:bot_id WHERE "
                                 "tg_user_id=:tg_user_id AND tg_chat_id=:tg_chat_id", bot_id=bot_id,
                                 tg_chat_id=tg_chat_id,
                                 tg_user_id=tg_user_id)
            if result.rowcount:
                return 0

            insert_stmnt = f'INSERT INTO {table.name} ' \
                           f'("tg_user_id", "tg_chat_id", "bot_id") VALUES ' \
                           f'({tg_user_id}, {tg_chat_id}, {bot_id})'
            logger.debug(f"Insert statement: {insert_stmnt}")
            con.execute(insert_stmnt)
            return 0

    return do_it()


def bot_save(bkey):
    """Save or update bot for %bkey%."""
    logger.debug(f"Saving bot {bkey}")
    with Engine_SUBSCRIBE.connect() as con:
        table: Table = MetaData_SUBSCRIBE.tables["bot"]
        logger.debug(f"Use Table: {table}")
        values = dict(bkey=bkey)
        insert_stmnt: insert = insert(table).values(values).on_conflict_do_update(
            index_elements=['bkey'],
            set_=values
        )
        logger.debug(f"Insert statement: {insert_stmnt}")
        con.execute(insert_stmnt)


def for_chat(chat_id: int):
    externalize_chat_id(BOT_BKEY_SUBSCRIBE_LC, chat_id)


def for_user(user_id: int):
    externalize_user_id(BOT_BKEY_SUBSCRIBE_LC, user_id)


def bot_activate(user_id: int, chat_id: int, bkey: str):
    """Activate bot for the user and the chat."""
    logger.debug(f"Subscribing user to bot {bkey}")
    with Engine_SUBSCRIBE.connect() as con:
        table: Table = MetaData_SUBSCRIBE.tables["user_chat_bot_subscription"]
        insert_stmnt = f'INSERT OR IGNORE INTO {table.name} VALUES ({user_id}, {chat_id},' \
                       f'(' + sql_bot_by_bkey(bkey) + ')' \
                                                      f' ) '
        logger.debug(f"Insert statement: {insert_stmnt}")
        con.execute(insert_stmnt)


def main():
    logger.debug("Running subscribe_db __main__")
    print("Add user")
    for_user(1)
    set_uname(1, "uname 1")
    for_user(2)
    set_uname(2, "uname 2")
    print("Add chat")
    for_chat(1)
    print("Save todo bot")
    bot_save('todo')
    print("Activate")
    bot_activate(1, 1, 'todo')
    bot_activate(2, 1, 'todo')
    print("Set default bot:")
    bot_default(1, 1, 'todo')
    default = bot_default(2, 1, 'todo')
    print(f"Default RC: {default}")


if __name__ == '__main__':
    main()
