__author__ = 'AA.GUSTI'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )
from zope.sqlalchemy import ZopeTransactionExtension


OtherDBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
OtherBase = declarative_base()
