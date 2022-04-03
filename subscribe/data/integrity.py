from typing import Any

from sqlalchemy import Table
from sqlalchemy.engine import Row, Connection

import integrity
from subscribe.data.model import ENT_TY_setng, Setng, G3Bot, ENT_TY_g3_bot, ENT_TY_setng_it, SetngIt, \
    ENT_TY_setng_it_key, \
    SetngItKey, ENT_TY_setng_it_key_val, SetngItKeyVal, G3File, ENT_TY_g3_file, ENT_TY_ctx, Ctx
from g3b1_data.entities import EntTy, ET


def from_row_g3_bot(row: Row) -> G3Bot:
    return G3Bot(row['bkey'], row['id'])


def from_row_g3_file(row: Row) -> G3File:
    return G3File(row=row)


def from_row_setng(row: Row, repl_dct: dict) -> Setng:
    return Setng(row=row, repl_dct=repl_dct)


def from_row_setng_it(row: Row, repl_dct: dict) -> SetngIt:
    return SetngIt(repl_dct.get('setng_id', row['setng_id']), row['bkey'], row['id'])


def from_row_setng_it_key(row: Row, repl_dct: dict) -> SetngItKey:
    return SetngItKey(repl_dct.get('setng_it_id', row['setng_it_id']), row['bkey'], row['id'])


def from_row_setng_it_key_val(row: Row, repl_dct: dict) -> SetngItKeyVal:
    setng_it_key = repl_dct.get('setng_it_key_id', row['setng_it_key_id'])
    if isinstance(setng_it_key, list):
        setng_it_key = [it for it in setng_it_key if it.id == row['setng_it_key_id']][0]
    return SetngItKeyVal(repl_dct.get('bcu_id', row['bcu_id']), setng_it_key, row['num'], row['val'], row['id'])


# noinspection PyDefaultArgument
def orm(con: Connection, tbl: Table, row: Row, repl_dct={}) -> dict[str, Any]:
    return integrity.orm(con, tbl, row, from_row_any, repl_dct)


def from_row_any(ent_ty: EntTy[ET], row: Row, repl_dct: dict) -> ET:
    if ent_ty == ENT_TY_setng:
        return from_row_setng(row, repl_dct)
    elif ent_ty == ENT_TY_setng_it:
        return from_row_setng_it(row, repl_dct)
    elif ent_ty == ENT_TY_setng_it_key:
        return from_row_setng_it_key(row, repl_dct)
    elif ent_ty == ENT_TY_setng_it_key_val:
        return from_row_setng_it_key_val(row, repl_dct)
    elif ent_ty == ENT_TY_g3_bot:
        return from_row_g3_bot(row)
    elif ent_ty == ENT_TY_g3_file:
        return from_row_g3_file(row)
    elif ent_ty == ENT_TY_ctx:
        return Ctx(row, repl_dct)

    return row['id']
