import os
from typing import Union

from telegram import Bot, File

from g3b1_cfg.tg_cfg import G3Ctx
from g3b1_data.elements import EntEleTy, ELE_TY_bkey, EleTy
from g3b1_data.entities import G3_M_SUBSCRIBE, EntTy, EntId
from py_meta import by_row_initializer

ENT_TY_bot: EntTy[Bot] = EntTy[Bot](G3_M_SUBSCRIBE, 'accnt', 'Account')
ENT_TY_bot.ele_ty_dct = dict(bkey=EntEleTy(ENT_TY_bot, ELE_TY_bkey, 'bkey'))

ENT_TY_setng_it_key_val = EntTy(G3_M_SUBSCRIBE, 'setng_it_key_val', 'SetngItKey Val')
ENT_TY_setng_it_key = EntTy(G3_M_SUBSCRIBE, 'setng_it_key', 'Setng It Key')
ENT_TY_setng_it = EntTy(G3_M_SUBSCRIBE, 'setng_it', 'Setng It', it_ent_ty_dct={'it_li': ENT_TY_setng_it_key})
ENT_TY_setng = EntTy(G3_M_SUBSCRIBE, 'setng', 'Setting', it_ent_ty_dct={'it_li': ENT_TY_setng_it})
ENT_TY_bcu = EntTy(G3_M_SUBSCRIBE, 'bcu', 'BCU')
ENT_TY_g3_bot = EntTy(G3_M_SUBSCRIBE, 'g3_bot', 'G3 Bot')
ENT_TY_g3_file = EntTy(G3_M_SUBSCRIBE, 'file', 'File')
ENT_TY_ctx = EntTy(G3_M_SUBSCRIBE, 'ctx', 'Context')
ENT_TY_ctx_msg = EntTy(G3_M_SUBSCRIBE, 'ctx_msg', 'Ctx Msg')

ENT_TY_subscribe_li = [
    ENT_TY_bcu, ENT_TY_g3_bot, ENT_TY_g3_file, ENT_TY_ctx, ENT_TY_ctx_msg,
    ENT_TY_setng, ENT_TY_setng_it, ENT_TY_setng_it_key, ENT_TY_setng_it_key_val]

ELE_TY_setng_id = EleTy(id_='setng_id', descr='Setting', ent_ty=ENT_TY_setng)
ELE_TY_setng_it_id = EleTy(id_='setng_it_id', descr='Setng Item', ent_ty=ENT_TY_setng_it)
ELE_TY_setng_it_key_id = EleTy(id_='setng_it_key_id', descr='Setng It Key', ent_ty=ENT_TY_setng_it_key)
ELE_TY_setng_it_key_val_id = EleTy(id_='setng_it_key_val_id', descr='Setng It Key Val', ent_ty=ENT_TY_setng_it_key)
ELE_TY_bcu_id = EleTy(id_='bcu_id', descr='Bot Chat User', ent_ty=ENT_TY_bcu)
ELE_TY_g3_bot_id = EleTy(id_='g3_bot_id', descr='G3 Bot', ent_ty=ENT_TY_g3_bot)
ELE_TY_g3_file_id = EleTy(id_='file_id', descr='G3 File', ent_ty=ENT_TY_g3_file)
ELE_TY_ctx_id = EleTy(id_='ctx_id', descr='Context', ent_ty=ENT_TY_ctx)
ELE_TY_ctx_msg_id = EleTy(id_='ctx_msg_id', descr='Ctx Msg', ent_ty=ENT_TY_ctx_msg)

ELE_TY_subscribe_li = [ELE_TY_setng_id, ELE_TY_setng_it_id, ELE_TY_setng_it_key_id, ELE_TY_setng_it_key_val_id,
                       ELE_TY_bcu_id,
                       ELE_TY_g3_bot_id, ELE_TY_g3_file_id]


class Ctx:
    var_name = 'ctx'
    ent_ty = ENT_TY_ctx

    @by_row_initializer
    def __init__(self, chat_id: int, user_id: int, title: str, ins_tst: str = None, stop_tst: str = None,
                 id_=0) -> None:
        super().__init__()
        self.chat_id = chat_id
        self.user_id = user_id
        self.title = title
        self.ins_tst = ins_tst
        self.stop_tst = stop_tst
        self.id = id_


class CtxMsg:
    var_name = 'ctx_msg'
    ent_ty = ENT_TY_ctx_msg

    @by_row_initializer
    def __init__(self, ctx: Ctx, ext_msg_id: int, id_=0) -> None:
        super().__init__()
        self.ctx = ctx
        self.ext_msg_id = ext_msg_id
        self.id = id_


class G3File:
    var_name = 'g3_file'
    ent_ty = ENT_TY_g3_file

    @classmethod
    def from_g3_ctx(cls):
        file = G3Ctx.get_tg_aud_or_voi_file()
        msg = G3Ctx.upd.effective_message
        return G3File(G3Ctx.chat_id(), msg.message_id, G3Ctx.for_user_id(), file.file_id, file.file_unique_id,
                      mime_type='audio/ogg')

    @by_row_initializer
    def __init__(self, chat_id: int, ext_id: int, own__user_id: int, file_id: str, file_unique_id: str,
                 duration=-1, file_size=-1, mime_type='', id_: int = 0, g3b1_fl='') -> None:
        super().__init__()
        self.chat_id = chat_id
        self.ext_id = ext_id
        self.own__user_id = own__user_id
        self.file_id = file_id
        self.file_unique_id = file_unique_id
        self.duration = duration
        self.file_size = file_size
        self.mime_type = mime_type
        self.g3b1_fl = g3b1_fl
        self.id = id_
        delattr(self, 'id_')

    def get_path(self) -> str:
        return f'{G3Ctx.get_tg_files_dir()}{os.sep}{self.file_unique_id}'


class G3Bot:
    var_name = 'g3_bot'
    ent_ty = ENT_TY_g3_bot

    def __init__(self, bkey: str, id_: int = 0) -> None:
        super().__init__()
        self.bkey = bkey
        self.id = id_


class BCU:
    var_name = 'bcu'
    ent_ty = ENT_TY_bcu

    def __init__(self, g3_bot: G3Bot, chat_id: int, user_id: int, id_: int = 0) -> None:
        super().__init__()
        self.g3_bot = g3_bot
        self.chat_id = chat_id
        self.user_id = user_id
        self.id = id_


class Setng:
    """Example settings for bot TRANS, setting txt_menu"""

    var_name = 'setng'
    ent_ty = ENT_TY_setng

    @by_row_initializer
    def __init__(self, g3_bot_id: Union[G3Bot, int], bkey: str, id_: int = 0) -> None:
        super().__init__()
        # noinspection PyTypeChecker
        self.g3_bot: G3Bot = g3_bot_id
        self.bkey = bkey
        self.id = id_
        self.it_li: list[SetngIt] = []

    def it_key_li(self, bkey: str) -> list['SetngItKey']:
        it_key_li = [it_key for it in self.it_li if it.bkey == bkey for it_key in it.it_li]
        return it_key_li


class SetngIt:
    """Example settings for bot TRANS, setting txt_menu: on_it_click"""

    var_name = 'setng_it'
    ent_ty = ENT_TY_setng_it

    def __init__(self, setng: Setng, bkey: str, id_: int = 0) -> None:
        super().__init__()
        self.setng = setng
        self.bkey = bkey
        self.id = id_
        self.it_li: list[SetngItKey] = []


class SetngItKey:
    """Example settings for bot TRANS, setting txt_menu: on_it_click - [SELECT, MERGE, INFO]"""

    var_name = 'setng_it_key'
    ent_ty = ENT_TY_setng_it_key

    def __init__(self, setng_it: SetngIt, bkey: str, id_: int = 0) -> None:
        super().__init__()
        self.setng_it = setng_it
        self.bkey = bkey
        self.id = id_
        self.it_li = []


class SetngItKeyVal:
    """Example settings for bot TRANS, setting txt_menu: on_it_click -
    [
        SELECT = [1, 'X'],
        INFO = [2, ''],
        MERGE = [3, 'X"],
        INFO = [4, 'x']
    ]
    => Meaning: in txt_menu on_it_click execute the commands: SELECT, MERGE, INFO
    """

    var_name = 'setng_it_key_val'
    ent_ty = ENT_TY_setng_it_key_val

    def __init__(self, bcu: BCU, setng_it_key: SetngItKey, num: str, val: str, id_: int = 0) -> None:
        super().__init__()
        self.bcu = bcu
        self.setng_it_key = setng_it_key
        self.num = num
        self.val = val
        self.id = id_
