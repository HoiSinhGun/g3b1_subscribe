import unittest

from data import eng_SUB, md_SUB
from data.db import sel_g3_bot_id_by_bkey, sel_bcu, fi_setng_it_key_val
from data.model import ENT_TY_setng, Setng, SetngItKeyVal
from entities import G3_M_SUBSCRIBE, EntId
from test_utils import g3_context_mock
from tg_db import sel_ent_ty


class MyTestCase(unittest.TestCase):
    def test_setng_by_id(self):
        # {ENT_TY_setng_it : {ENT_TY_setng_it_key:{}}}
        g3_context_mock(eng_SUB, md_SUB, G3_M_SUBSCRIBE)
        setng: Setng = sel_ent_ty(EntId(ENT_TY_setng, 1)).result
        self.assertEqual(setng.g3_bot.bkey, 'trans')

    def test_setng_by_bkey(self):
        # {ENT_TY_setng_it : {ENT_TY_setng_it_key:{}}}
        g3_context_mock(eng_SUB, md_SUB, G3_M_SUBSCRIBE)
        g3_bot_id = sel_g3_bot_id_by_bkey('trans')
        setng: Setng = sel_ent_ty(EntId(ENT_TY_setng, 'txt_menu', g3_bot_id)).result
        self.assertEqual(setng.g3_bot.bkey, 'trans')

    def test_fi_setng_key_val(self):
        # {ENT_TY_setng_it : {ENT_TY_setng_it_key:{}}}
        g3_context_mock(eng_SUB, md_SUB, G3_M_SUBSCRIBE)
        g3_bot_id = sel_g3_bot_id_by_bkey('trans')
        bcu = sel_bcu(g3_bot_id, 0, 0)
        setng: Setng = sel_ent_ty(EntId(ENT_TY_setng, 'txt_menu', g3_bot_id)).result
        setng_it_key_val_li:list[SetngItKeyVal] = fi_setng_it_key_val(setng, 'on_click_txt_it', bcu)
        self.assertEqual(len(setng_it_key_val_li), 3)


if __name__ == '__main__':
    unittest.main()
