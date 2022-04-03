import codecs
import os
from collections import Callable
from os.path import join

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine, Row
from sqlalchemy.sql.functions import now
from telegram import Update, File
from telegram.ext import CallbackContext

from elements import ELE_TY_stop_tst
from g3b1_ui.model import TgUIC
from settings import cu_setng, iup_setng, read_setng
from subscribe.data.db import sel_g3_bot_id_by_bkey, sel_bcu, fi_setng_it_key_val, externalize_message, upd_ctx_add_msg, \
    fin_ctx_active
from subscribe.data.model import SetngItKeyVal, Setng, ENT_TY_setng, G3File, Ctx, ELE_TY_ctx_id, ENT_TY_g3_file
from entities import EntId
from g3b1_cfg.tg_cfg import G3Ctx
from g3b1_data.model import G3Command
from g3b1_serv import utilities
from g3b1_serv.utilities import upd_extract_chat_user_id, now_for_fl
from generic_mdl import TgColumn, TableDef
from sql_utils import dc_dic_2_tbl, tbl_2_str
from subscribe.data import db, eng_SUB, md_SUB
from tg_db import sel_ent_ty, ins_ent_ty, synchronize_from_message, externalize_file_id, upd_ent_ty


def ctx_start(title: str) -> Ctx:
    ctx = Ctx(G3Ctx.chat_id(), G3Ctx.for_user_id(), title)
    ctx = ins_ent_ty(ctx).result
    iup_setng(cu_setng(ELE_TY_ctx_id, ctx.id))
    return ctx


def ctx_stop(ctx: Ctx) -> Ctx:
    ctx.stop_tst = utilities.tst_for_sql()
    ctx = upd_ent_ty(ctx, [ELE_TY_stop_tst.col_name])
    iup_setng(cu_setng(ELE_TY_ctx_id))
    return ctx


def iup_g3_file_message() -> G3File:
    g3_file: G3File = G3File.from_g3_ctx()
    tg_file: File = G3Ctx.get_tg_aud_or_voi_file()
    ctx_as_dict = G3Ctx.as_dict()
    G3Ctx.eng = eng_SUB
    G3Ctx.md = md_SUB
    g3_file = ins_ent_ty(g3_file).result
    # TODO Select g3_file by file_unique_id
    G3Ctx.from_dict(ctx_as_dict)
    tg_file.download(g3_file.get_path())
    externalize_file_id(G3Ctx.g3_m_str, g3_file.id)
    synch_message(g3_file)
    return g3_file


def synch_message(g3_file: G3File):
    msg = G3Ctx.upd.effective_message
    synchronize_from_message(msg, g3_file=g3_file, is_command_explicit=False)
    # not working: msg_id = externalize_message(msg.chat_id, msg.message_id)
    # for ctx in fin_ctx_active(msg.chat_id):
    #     upd_ctx_add_msg(ctx.id, msg_id)


def sel_g3_file(g3_file_id: int) -> G3File:
    g3_file: G3File = sel_ent_ty(EntId(ENT_TY_g3_file, g3_file_id)).result
    return g3_file


def send_aud_g3_file(g3_file_id: int, fl_name: str = '') -> G3File:
    g3_file = sel_g3_file(g3_file_id)
    if not fl_name:
        fl_name = os.path.splitext(g3_file.file_unique_id)[0]
    fl_name_mp3 = fl_name + f'__{g3_file.file_unique_id}.mp3'
    fl_name_wav = fl_name + f'__{g3_file.file_unique_id}.wav'

    send_cmd_audio(f'to_mp3 {fl_name_mp3} {g3_file.get_path()}')
    send_cmd_audio(f'to_wav {fl_name_wav} {g3_file.get_path()}')

    return g3_file


def send_cmd_audio(cmd_line: str):
    cmd_split = cmd_line.split(' ', 1)
    g3_fl = join(os.environ.get('g3b1_dir'), 'g3b1_comm', f'trans_audio_{now_for_fl()}_{cmd_split[0]}.g3')
    with codecs.open(g3_fl, encoding='utf-8', mode='x') as file:
        if len(cmd_split) > 1:
            file.writelines([f'{cmd_split[1]}'])

    TgUIC.uic.send(g3_fl)


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


def list_chat_user(chat_id: int, engine, meta: MetaData) -> dict[int, dict[..., ...]]:
    # mdata = MetaData()
    # mdata.reflect(bind=engine)
    # con: Connection
    user_dct = {}
    # with engine.connect() as con:
    #     id_li = g3_db.all_tg_user(con, mdata)
    id_li = db.sel_user_by_chat(chat_id, engine, meta)
    for id_ in id_li:
        user_dct.update({id_: {'id': id_, 'uname': db.read_uname(id_)}})
    return user_dct


def tbl_chat_user_send(upd: Update, chat_id: int, engine: Engine, meta: MetaData, enrich_dct: Callable = None):
    user_dct = list_chat_user(chat_id, engine, meta)
    col_li = [TgColumn('id', -1, 'id', 15), TgColumn('uname', -1, 'uname', 25)]
    if enrich_dct:
        user_dct = enrich_dct(upd, user_dct)
        for k in [x for x in list(user_dct.values())[0].keys() if x != 'id' and x != 'uname']:
            col_li.append(TgColumn(k.id_, -1, k.descr, 10))
    table_def = TableDef(col_li)
    tg_tbl = dc_dic_2_tbl(user_dct, table_def)
    reply_str = tbl_2_str(tg_tbl)
    upd.effective_message.reply_html(
        f'<code>{reply_str}</code>'
    )


def setng_it_key_val(bkey: str, it_bkey: str) -> list[SetngItKeyVal]:
    g3_bot_id = sel_g3_bot_id_by_bkey(G3Ctx.g3_m_str)
    bcu = sel_bcu(g3_bot_id, 0, 0)
    setng: Setng = sel_ent_ty(EntId(ENT_TY_setng, bkey, g3_bot_id)).result
    setng_it_key_val_li: list[SetngItKeyVal] = fi_setng_it_key_val(setng, it_bkey, bcu)
    return setng_it_key_val_li


def id_by_uname(uname: str) -> int:
    return db.id_by_uname(uname)


def for_user(for_uname, user_id):
    if for_uname:
        for_user_id = db.id_by_uname(for_uname)
    else:
        for_user_id = user_id
    return for_user_id


def sel_setng_cmd_default(uname: str = '', f_shorten=False) -> str:
    """Select cmd_prefix. Consistency check related to bot_id"""
    chat_id, user_id = utilities.upd_extract_chat_user_id()
    for_user_id = for_user(uname, user_id)
    row: Row = db.sel_uc_setngs(chat_id, for_user_id)
    cmd_default = str(row['cmd_default'])
    if f_shorten and cmd_default.startswith(f'{G3Ctx.g3_m_str}'):
        cmd_default = cmd_default.replace(f'{G3Ctx.g3_m_str}_', '')
    return cmd_default


def sel_setng_cmd_prefix(uname: str = '') -> str:
    """Select cmd_prefix. Consistency check related to bot_id"""
    chat_id, user_id = utilities.upd_extract_chat_user_id()
    for_user_id = for_user(uname, user_id)
    row: Row = db.sel_uc_setngs(chat_id, for_user_id)
    cmd_prefix = str(row['cmd_prefix'])
    pfx = f'.{G3Ctx.g3_cmd.g3_m.name}.'
    if not cmd_prefix or not cmd_prefix.startswith(pfx):
        cmd_prefix = pfx
    return cmd_prefix


def iup_setng_cmd_prefix(cmd_prefix: str = '', uname: str = '', g3_m_str=''):
    """Set the cmd_prefix which replaces triple dot."""
    chat_id, user_id = utilities.upd_extract_chat_user_id()
    for_user_id = for_user(uname, user_id)

    if not g3_m_str:
        g3_m_str = G3Ctx.g3_cmd.g3_m.name
    pfx = f'.{g3_m_str}.'
    bot_cmd_prefix = f'{pfx}{cmd_prefix}'
    bot_id: int = db.sel_g3_bot_id_by_bkey(g3_m_str)
    values = {'bot_id': bot_id, 'cmd_prefix': bot_cmd_prefix}
    db.iup_uc_setngs(chat_id, for_user_id, values)


def iup_setng_cmd_default(g3_cmd: G3Command = None, uname: str = ''):
    """Set the cmd_default"""
    chat_id, user_id = utilities.upd_extract_chat_user_id()
    for_user_id = for_user(uname, user_id)

    chat_id, user_id = upd_extract_chat_user_id()
    if g3_cmd:
        g3m_str = g3_cmd.g3_m.name
        cmd_default = g3_cmd.long_name
        bot_id: int = db.sel_g3_bot_id_by_bkey(g3m_str)
        values = {'bot_id': bot_id, 'cmd_default': cmd_default}
    else:
        values = {'cmd_default': ''}
    db.iup_uc_setngs(chat_id, for_user_id, values)


def bot_activate(g3_m_str: str, uname: str = '', user_id=0):
    chat_id = G3Ctx.chat_id()
    if not user_id:
        user_id = G3Ctx.for_user_id()
    for_user_id = for_user(uname, user_id)
    db.ins_bcu(chat_id, for_user_id, g3_m_str)
