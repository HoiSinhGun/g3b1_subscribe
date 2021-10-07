from typing import Tuple

from sqlalchemy.engine import Engine
from telegram import Message, Chat, User  # noqa

# create console handler and set level to debug
from subscribe.data import eng_SUB, md_SUB
from subscribe.data.integrity import from_row_any
from subscribe.data.model import Setng, BCU, SetngItKeyVal, ENT_TY_setng, ENT_TY_setng_it_key_val, SetngItKey, \
    ELE_TY_setng_it_key_id, ELE_TY_bcu_id
from g3b1_data.entities import G3_M_SUBSCRIBE
from g3b1_data import settings
from g3b1_data.tg_db import *
from g3b1_log.log import cfg_logger

logger = cfg_logger(logging.getLogger(__name__), logging.WARN)


def bot_all() -> dict[str, dict]:
    bot_dict = {}
    with eng_SUB.connect() as con:
        rs = con.execute(bot_table().select())
        for row in rs:
            d = dict(row)
            bot_dict.update({row['bkey']: d})
    return bot_dict


def bot_table() -> Table:
    return md_SUB.tables["g3_bot"]


def sel_g3_bot_id_by_bkey(bkey: str, con: Connection = None) -> Optional[int]:
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
        cr: CursorResult = con.execute("SELECT uname FROM user_settings WHERE tg_user_id=:tg_user_id",
                                       tg_user_id=tg_user_id)
        row: Tuple = cr.first()
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
            bot_id: int = sel_g3_bot_id_by_bkey(bkey, con)
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
    externalize_chat_id(G3_M_SUBSCRIBE, chat_id)


def for_user(user_id: int):
    externalize_user_id(G3_M_SUBSCRIBE, user_id)


def sel_user_by_chat(chat_id: int, eng: Engine, md: MetaData) -> list[int]:
    with eng.connect() as con:
        tbl: Table = md.tables['user_chat_settings']
        col_sel: Select = select(tbl.c.tg_user_id)
        col_sel = col_sel.where(tbl.c.tg_chat_id == chat_id)
        rs: Result = con.execute(col_sel)
        rows = rs.fetchall()
        return [row['tg_user_id'] for row in rows]


def sel_setng_by_bkey(bkey: str, bcu: BCU = None) -> Setng:
    if not bcu:
        g3_bot_id = sel_g3_bot_id_by_bkey(G3Ctx.g3_m_str)
        bcu: BCU = sel_bcu(g3_bot_id, user_id=0)
    setng = sel_ent_ty(EntId(ENT_TY_setng, bkey, bcu.g3_bot.id))
    return setng.result


def fi_setng_it_key_val(setng: Setng, bkey: str, bcu: BCU = None) -> list[SetngItKeyVal]:
    if not bcu:
        g3_bot_id = sel_g3_bot_id_by_bkey(G3Ctx.g3_m_str)
        bcu: BCU = sel_bcu(g3_bot_id, user_id=0)
    tbl: Table = md_SUB.tables['bcu_setng_it_key_val']
    setng_it_key_li: list[SetngItKey] = setng.it_key_li(bkey)
    stmnt = (select(tbl).where(
        tbl.c.bcu_id == bcu.id, tbl.c.setng_it_key_id.in_([it.id for it in setng_it_key_li])
    ).order_by(tbl.c.num))
    cr: CursorResult = eng_SUB.execute(stmnt)
    row_li: list[Row] = cr.fetchall()
    res_li: list[SetngItKeyVal] = []
    for row in row_li:
        res_li.append(
            from_row_any(ENT_TY_setng_it_key_val, row,
                         {ELE_TY_setng_it_key_id.id_: setng_it_key_li,
                          ELE_TY_bcu_id.id_: bcu})
        )
    return res_li


def sel_bcu(g3_bot_id: int, chat_id: int = None, user_id: int = None) -> BCU:
    if chat_id is None:
        chat_id = G3Ctx.chat_id()
    if user_id is None:
        user_id = G3Ctx.for_user_id()
    tbl: Table = md_SUB.tables["bcu"]
    cr: CursorResult = eng_SUB.execute(
        select(tbl).where(tbl.c.g3_bot_id == g3_bot_id, tbl.c.chat_id == chat_id, tbl.c.user_id == user_id)
    )
    row: Row = cr.first()
    return BCU(row['g3_bot_id'], row['chat_id'], row['user_id'], row['id'])


def ins_bcu(chat_id: int, user_id: int, bkey: str):
    """Activate bot for the user and the chat."""
    logger.debug(f"Subscribing user to bot {bkey}")
    if bkey not in bot_all().keys():
        logger.error(f'Bot with bkey "{bkey}" not found!')
        return
    externalize_chat_id('subscribe', chat_id)
    externalize_user_id('subscribe', user_id)
    externalize_user_id('subscribe', 0)
    with eng_SUB.connect() as con:
        table: Table = md_SUB.tables["bcu"]
        g3_bot_id = sel_g3_bot_id_by_bkey(bkey, con)
        insert_stmnt = f'INSERT OR IGNORE INTO {table.name} (user_id, chat_id, g3_bot_id) ' \
                       f'VALUES ({user_id}, {chat_id}, {g3_bot_id})'
        logger.debug(f"Insert statement: {insert_stmnt}")
        con.execute(insert_stmnt)
        # Adding the default entry
        con.execute(f'INSERT OR IGNORE INTO {table.name} (g3_bot_id, chat_id, user_id) '
                    f'VALUES ({g3_bot_id}, {chat_id}, 0)')


def sel_setng(setng_id: int) -> Setng:
    pass


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
        ele_val = settings.read_setting(con, md_SUB, setng_dct)
        return G3Result.from_ele_val(ele_val)


def main():
    pass


if __name__ == '__main__':
    main()
