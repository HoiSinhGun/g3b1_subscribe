from telegram.ext import Dispatcher

import subscribe
from g3b1_test import test_utils
from g3b1_serv import utilities
from subscribe import tg_hdl


def main():
    dispatcher: Dispatcher = test_utils.setup(tg_hdl.__file__, subscribe.COLUMNS_SUBSCRIBE)

    ts: test_utils.TestSuite = test_utils.TestSuite(
        dispatcher, []
    )

    ts.tc_li.extend(
        [
            test_utils.TestCaseHdl(utilities.g3_cmd_by_func(
                tg_hdl.cmd_default),
                {'bkey': 'todo'}
            ),
            test_utils.TestCaseHdl(utilities.g3_cmd_by_func(
                tg_hdl.cmd_edit),
                {'bkey': 'money'}
            ),
            test_utils.TestCaseHdl(utilities.g3_cmd_by_func(
                tg_hdl.cmd_uname),
                {'uname': 'money'}
            ),
            test_utils.TestCaseHdl(utilities.g3_cmd_by_func(
                tg_hdl.cmd_subscribe),
                {'bkey': 'money'}
            ),
            test_utils.TestCaseHdl(utilities.g3_cmd_by_func(
                tg_hdl.cmd_default),
                {'user_id': '3', 'bkey': 'todo'}
            )
        ]
    )
    for tc in ts.tc_li:
        ts.tc_exec(tc)


if __name__ == '__main__':
    main()
