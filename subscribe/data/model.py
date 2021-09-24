from telegram import Bot

from g3b1_data.elements import EntEleTy, ELE_TY_bkey
from g3b1_data.entities import G3_M_SUBSCRIBE, EntTy

ENT_TY_bot: EntTy[Bot] = EntTy[Bot](G3_M_SUBSCRIBE, 'accnt', 'Account')
ENT_TY_bot.ele_ty_dct = dict(bkey=EntEleTy(ENT_TY_bot, ELE_TY_bkey, 'bkey'))
