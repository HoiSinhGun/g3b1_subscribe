import logging

from g3b1_log.log import cfg_logger
from g3b1_serv.generic_mdl import TgColumn

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)
COLUMNS_SUBSCRIBE = dict[str: TgColumn]
