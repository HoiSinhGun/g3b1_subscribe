import logging

import subscribe
from g3b1_log.g3b1_log import cfg_logger
from g3b1_serv import tgdata_main
from subscribe import tg_hdl

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)


def start_bot():
    """Run the bot."""
    # str(bot_key): dict(db_row)
    tgdata_main.start_bot(tg_hdl.__file__, subscribe.COLUMNS_SUBSCRIBE)


def main() -> None:
    start_bot()


if __name__ == '__main__':
    main()
