import logging

from g3b1_log.log import cfg_logger
from generic_mdl import TgColumn
from model import g3m_str_by_file_str

logger = cfg_logger(logging.getLogger(__name__), logging.DEBUG)
g3_m_str_subscribe: str = g3m_str_by_file_str(__file__)
COLUMNS_SUBSCRIBE = dict[str: TgColumn]
