import logging

from g3b1_serv import utilities
from g3b1_log.g3b1_log import cfg_logger

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)
g3_m_str_subscribe: str = utilities.module_by_file_str(__file__)
COLUMNS_SUBSCRIBE = dict[str: utilities.TgColumn]
