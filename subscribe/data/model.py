from telegram import Bot

from g3b1_data.elements import EntEleTy, ELE_TY_bkey, EleTy
from g3b1_data.entities import G3_M_SUBSCRIBE, EntTy

ENT_TY_bot: EntTy[Bot] = EntTy[Bot](G3_M_SUBSCRIBE, 'accnt', 'Account')
ENT_TY_bot.ele_ty_dct = dict(bkey=EntEleTy(ENT_TY_bot, ELE_TY_bkey, 'bkey'))

ENT_TY_setng_it_key_val = EntTy(G3_M_SUBSCRIBE, 'setng_it_key_val', 'SetngItKey Val')
ENT_TY_setng_it_key = EntTy(G3_M_SUBSCRIBE, 'setng_it_key', 'Setng It Key')
ENT_TY_setng_it = EntTy(G3_M_SUBSCRIBE, 'setng_it', 'Setng It', it_ent_ty_dct={'it_li': ENT_TY_setng_it_key})
ENT_TY_setng = EntTy(G3_M_SUBSCRIBE, 'setng', 'Setting', it_ent_ty_dct={'it_li': ENT_TY_setng_it})
ENT_TY_bcu = EntTy(G3_M_SUBSCRIBE, 'bcu', 'BCU')
ENT_TY_g3_bot = EntTy(G3_M_SUBSCRIBE, 'g3_bot', 'G3 Bot')
ENT_TY_subscribe_li = [
    ENT_TY_bcu, ENT_TY_g3_bot,
    ENT_TY_setng, ENT_TY_setng_it, ENT_TY_setng_it_key, ENT_TY_setng_it_key_val]

ELE_TY_setng_id = EleTy(id_='setng_id', descr='Setting', ent_ty=ENT_TY_setng)
ELE_TY_setng_it_id = EleTy(id_='setng_it_id', descr='Setng Item', ent_ty=ENT_TY_setng_it)
ELE_TY_setng_it_key_id = EleTy(id_='setng_it_key_id', descr='Setng It Key', ent_ty=ENT_TY_setng_it_key)
ELE_TY_setng_it_key_val_id = EleTy(id_='setng_it_key_val_id', descr='Setng It Key Val', ent_ty=ENT_TY_setng_it_key)
ELE_TY_bcu_id = EleTy(id_='bcu_id', descr='Bot Chat User', ent_ty=ENT_TY_bcu)
ELE_TY_g3_bot_id = EleTy(id_='g3_bot_id', descr='G3 Bot', ent_ty=ENT_TY_g3_bot)
ELE_TY_subscribe_li = [ELE_TY_setng_id, ELE_TY_setng_it_id, ELE_TY_setng_it_key_id, ELE_TY_setng_it_key_val_id,
                       ELE_TY_bcu_id,
                       ELE_TY_g3_bot_id]


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

    def __init__(self, g3_bot: G3Bot, bkey: str, id_: int = 0) -> None:
        super().__init__()
        self.g3_bot = g3_bot
        self.bkey = bkey
        self.id = id_
        self.it_li: list[SetngIt] = []

    def it_key_li(self, bkey:str) -> list['SetngItKey']:
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


