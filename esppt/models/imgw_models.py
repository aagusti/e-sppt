import sys
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from other_base import *

class antrianModel(OtherBase):
    __tablename__  = 'antrian'
    __table_args__ = {'extend_existing':True , 'schema' : 'im', 
                      'autoload':True}
