from typing import Tuple

from sqlalchemy.engine import Engine, CursorResult
from telegram import Message, Chat, User  # noqa

# create console handler and set level to debug
from g3b1_data import settings
from g3b1_data.tg_db import *
from g3b1_log.log import cfg_logger

BOT_BKEY_SUBSCRIBE = "subscribe"
BOT_BKEY_SUBSCRIBE_LC = BOT_BKEY_SUBSCRIBE.lower()

DB_FILE_SUBSCRIBE = rf'C:\Users\IFLRGU\Documents\dev\g3b1_{BOT_BKEY_SUBSCRIBE_LC}.db'
md_SUB = MetaData()
eng_SUB = create_engine(f"sqlite:///{DB_FILE_SUBSCRIBE}")
md_SUB.reflect(bind=eng_SUB)

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)


def bot_all() -> dict[str, dict]:
    bot_dict = {}
    with eng_SUB.connect() as con:
        rs = con.execute(bot_table().select())
        for row in rs:
            d = dict(row)
            bot_dict.update({row['bkey']: d})
    return bot_dict


def bot_table() -> Table:
    return md_SUB.tables["bot"]


def sel_bot_bkey(bkey: str, con: Connection = None) -> Optional[int]:
    def wrapped(con_: Connection) -> Optional[int]:
        stmnt = select(bot_table()).where(bot_table().c.bkey == bkey)
        rs = con_.execute(stmnt)
        row: Tuple = rs.first()
        if not row:
            return
        bot_id: int = int(row[0])
        return bot_id

    if con:
        return wrapped(con)
    else:
        with eng_SUB.connect() as con_new:
            return wrapped(con_new)


def set_uname(tg_user_id: int, uname: str) -> int:
    with eng_SUB.connect() as con:
        result = con.execute("UPDATE user_settings SET uname=:uname WHERE tg_user_id=:tg_user_id", uname=uname,
                             tg_user_id=tg_user_id)
        if result.rowcount:
            return 0

        table: Table = md_SUB.tables["user_settings"]
        values = dict(tg_user_id=tg_user_id, uname=uname)
        insert_stmnt: insert = insert(table).values(values)
        logger.debug(f"Insert statement: {insert_stmnt}")
        con.execute(insert_stmnt)
        return 0


def read_uname(tg_user_id: int) -> str:
    with eng_SUB.connect() as con:
        select = con.execute("SELECT uname FROM user_settings WHERE tg_user_id=:tg_user_id", tg_user_id=tg_user_id)
        row: Tuple = select.first()
        if not row:
            # noinspection PyTypeChecker
            return None
        uname: str = row[0]
        return uname


def id_by_uname(uname: str) -> int:
    if len(uname) < 6:
        uname = f'g3b1_{uname}'
    with eng_SUB.connect() as con:
        stmnt = con.execute("SELECT tg_user_id FROM user_settings WHERE uname=:uname", uname=uname)
        row: Tuple = stmnt.first()
        if not row:
            return 0
        tg_user_id: int = row[0]
        return tg_user_id


def bot_default(tg_chat_id: int, tg_user_id: int, bkey: str):
    logger.debug(f"Save or update setting: user-chat bot default to {bkey}")

    def do_it() -> int:
        with eng_SUB.connect() as con:
            table: Table = md_SUB.tables["user_chat_settings"]
            bot_id: int = sel_bot_bkey(bkey, con)
            if not bot_id:
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
    with eng_SUB.connect() as con:
        table: Table = md_SUB.tables["bot"]
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


def sel_user_by_chat(chat_id: int, engine: Engine, meta: MetaData) -> list[int]:
    with engine.connect() as con:
        tbl: Table = meta.tables['user_chat_settings']
        col_sel: Select = select(tbl.c.tg_user_id)
        col_sel = col_sel.where(tbl.c.tg_chat_id == chat_id)
        rs: Result = con.execute(col_sel)
        rows = rs.fetchall()
        return [row['tg_user_id'] for row in rows]


def ins_bot_uc_subscription(chat_id: int, user_id: int, bkey: str):
    """Activate bot for the user and the chat."""
    logger.debug(f"Subscribing user to bot {bkey}")
    if bkey not in bot_all().keys():
        logger.error(f'Bot with bkey "{bkey}" not found!')
        return
    externalize_chat_id('subscribe', chat_id)
    externalize_user_id('subscribe', user_id)
    with eng_SUB.connect() as con:
        table: Table = md_SUB.tables["user_chat_bot_subscription"]
        insert_stmnt = f'INSERT OR IGNORE INTO {table.name} VALUES ({user_id}, {chat_id},' \
                       f'{sel_bot_bkey(bkey, con)}' \
                       f' ) '
        logger.debug(f"Insert statement: {insert_stmnt}")
        con.execute(insert_stmnt)


def iup_uc_setngs(chat_id: int, user_id: int, values: dict):
    with eng_SUB.begin() as con:
        tbl: Table = md_SUB.tables['user_chat_settings']
        values['tg_user_id'] = user_id
        values['tg_chat_id'] = chat_id
        stmnt: insert = insert(tbl).values(values).on_conflict_do_update(
            index_elements=['tg_user_id', 'tg_chat_id'],
            set_=values
        )
        logger.debug(f"Insert statement: {stmnt}")
        con.execute(stmnt)


def sel_uc_setngs(chat_id: int, user_id: int) -> Row:
    with eng_SUB.begin() as con:
        tbl: Table = md_SUB.tables['user_chat_settings']
        stmnt = (select(tbl).where(tbl.c.tg_user_id == user_id, tbl.c.tg_chat_id == chat_id))
        rs: CursorResult = con.execute(stmnt)
        return rs.first()


def iup_setting(setng_dct: dict[str, ...]) -> G3Result:
    with eng_SUB.connect() as con:
        settings.iup_setting(con, md_SUB, setng_dct)
        return G3Result()


def read_setting(setng_dct: dict[str, ...]) -> G3Result:
    with eng_SUB.connect() as con:
        g3r = settings.read_setting(con, md_SUB, setng_dct)
        return g3r


def main():
    pass


if __name__ == '__main__':
    main()
