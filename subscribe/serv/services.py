from collections import Callable

from sqlalchemy.engine import Engine
from telegram import Update
from telegram.ext import CallbackContext

from g3b1_serv import utilities
from g3b1_serv.utilities import TgColumn, TableDef
from subscribe.data import db


def map_id_uname(data_dict: dict, field_mapping: dict) -> dict:
    """ @:param data_dict {int: dict, int: dict, ...}"""
    map_dict = {}
    for row, row_data in data_dict.items():
        for k, v in field_mapping.items():
            tg_user_id = row_data[k]  # e.g. row[creat__tg_user_id] = 1
            if tg_user_id not in map_dict:
                read_uname = db.read_uname(tg_user_id)
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


def list_chat_user(chat_id: int, engine) -> dict[int, dict[..., ...]]:
    # mdata = MetaData()
    # mdata.reflect(bind=engine)
    # con: MockConnection
    user_dct = {}
    # with engine.connect() as con:
    #     id_li = g3_db.all_tg_user(con, mdata)
    id_li = db.sel_user_by_chat(chat_id, engine)
    for id_ in id_li:
        user_dct.update({id_: {'id': id_, 'uname': db.read_uname(id_)}})
    return user_dct


def tbl_chat_user_send(upd: Update, chat_id: int, engine: Engine, enrich_dct: Callable = None):
    user_dct = list_chat_user(chat_id, engine)
    col_li = [TgColumn('id', -1, 'id', 15), TgColumn('uname', -1, 'uname', 25)]
    if enrich_dct:
        user_dct = enrich_dct(upd, user_dct)
        for k in [x for x in list(user_dct.values())[0].keys() if x != 'id' and x != 'uname']:
            col_li.append(TgColumn(k.id_, -1, k.descr, 10))
    table_def = TableDef(col_li)
    tg_tbl = utilities.dc_dic_2_tbl(user_dct, table_def)
    reply_str = utilities.tbl_2_str(tg_tbl)
    upd.effective_message.reply_html(
        f'<code>{reply_str}</code>'
    )


def for_user(for_uname, user_id):
    if for_uname:
        for_user_id = db.id_by_uname(for_uname)
    else:
        for_user_id = user_id
    return for_user_id
