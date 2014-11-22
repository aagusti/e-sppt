__author__ = 'AA.GUSTI'

from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    String,
    Index,
    ForeignKey,
    func,
    Table,
    Float,
    BigInteger,
    SmallInteger,
    Numeric,
    Date, 
    and_, 
    or_, 
    func
    )
from sqlalchemy.ext.declarative import declarative_base, declared_attr

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    exc
    )
    
from zope.sqlalchemy import ZopeTransactionExtension
from datetime import datetime
from datatables import ColumnDT, DataTables



OtherDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
OtherBase = declarative_base()
  