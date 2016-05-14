from sqlalchemy import Sequence
from other_base import OtherBase


antrian_seq = Sequence('antrian_id_seq', schema='im')

class antrianModel(OtherBase):
    __tablename__  = 'antrian'
    __table_args__ = dict(schema='im', autoload=True)

class mailModel(OtherBase):
    __tablename__ = 'mail'
    __table_args__ = dict(schema='im', autoload=True)

class mailFileModel(OtherBase):
    __tablename__ = 'mail_files'
    __table_args__ = dict(schema='im', autoload=True)
