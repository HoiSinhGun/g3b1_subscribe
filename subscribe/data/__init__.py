from sqlalchemy import MetaData, create_engine

from entities import G3_M_SUBSCRIBE

DB_FILE_SUBSCRIBE = rf'C:\Users\IFLRGU\Documents\dev\g3b1_{G3_M_SUBSCRIBE}.db'
md_SUB = MetaData()
eng_SUB = create_engine(f"sqlite:///{DB_FILE_SUBSCRIBE}")
md_SUB.reflect(bind=eng_SUB)
eng_SUBSCRIBE = eng_SUB
md_SUBSCRIBE = md_SUB
