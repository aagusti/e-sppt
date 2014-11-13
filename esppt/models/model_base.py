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



DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

SPD_KODE = [
    ['no_urut', 6, 'N','000001'],
    ['tag1', 1, 'A', "/"],
    ['tahun_id', 4, 'N', datetime.strftime(datetime.now(),'%Y')]
    ]
    
    
class BaseDB(object):
    __tablename__ = ''
    __table_args__ = {'extend_existing':True}
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created = Column(DateTime,  nullable=False, default=datetime.now)
    updated = Column(DateTime,  nullable=False, default=datetime.now)
    update_uid = Column(Integer)
    create_uid = Column(Integer)

    def __init__(self,data):
        tipe = str(type('id' in data and data['id']))
        if tipe=="<type 'int'>":
            if int(data['id'])>0:
                self.id = data['id']
        elif tipe=="<type 'unicode'>":
            if data['id'].isdigit() and int(data['id'])>0:
                self.id = data['id']
        #self.disabled  = 0
        self.created = data['created']
        self.updated = data['updated']
        self.create_uid = data['create_uid']
        self.update_uid = data['update_uid']

    @classmethod
    def tambah(cls, datas):
        datas['created'] = datetime.now()
        datas['updated'] = datetime.now()
        data=cls(datas)
        #try:
        DBSession.add(data)
        DBSession.flush()
        return data.id
        #except:
        #    print exc
        #    return 0
        #return False
        
    @classmethod
    def update(cls, datas):
        datas['updated'] = datetime.now()
        for f in datas:
            if not f in cls.__table__.columns.keys():
                del datas[f]
        row = DBSession.query(cls).filter(cls.id==datas['id']).update(datas)
        
        return datas['id']
        
    @classmethod
    def edit(cls, data):
        DBSession.merge(cls(data))

    @classmethod
    def hapus(cls, data):
        return DBSession.query(cls).filter(cls.id==data['id']).delete()

    @classmethod
    def hapus_detail(cls, params):
        DBSession.query(cls).filter(params).delete()

    @classmethod
    def row2dict(cls,row):
        d = {}
        for col in cls.__table__.columns: 
            tipe = str(col.type)
            if tipe == 'DATE' and getattr(row, col.name):
                d[col.name] = datetime.strftime(getattr(row, col.name),'%d-%m-%Y')
            else:
                d[col.name] = getattr(row, col.name) and str(getattr(row, col.name)) or ''
        return d
        
        #return dict((col, getattr(row, col)) for col in cls.__table__.columns.keys())

    @classmethod
    def rows2dict(cls,rows):
        rowdicted={}
        for row in rows:
            rowdicted[row['id']].append(cls.row2dict(row))
        return rowdicted

    @classmethod
    def get_count(cls):
        return DBSession.query(func.count(cls.id)).first()

    @classmethod
    def get_max_id(cls):
        return DBSession.query(func.max(cls.id))[0]


    @classmethod
    def get_rows(cls):
        return DBSession.query(cls).all()


    @classmethod
    def get_dict_all(cls):
        d={}
        d['success']=0 

        d['data']=[]
        for c in cls.get_rows(): 
            d['data'].append(cls.row2dict(c))
            d['success']=d['success']+1
        return d

    @classmethod
    def get_filtered_rows(cls,params):
        if params=='':
            return cls.get_rows()
        else:
            return DBSession.query(cls).filter(params).all()

    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).filter(
                  cls.id==id
                ).first()

class BaseKodeDB(BaseDB):
    kode = Column(String(50), unique=True, nullable=False)

    def __init__(self,data):
        BaseDB.__init__(self,data)
        self.kode = data['kode']

    @classmethod
    def get_by_kode(cls, kode):
        return DBSession.query(cls).filter(
                  cls.kode==kode
                ).first()
                
    @classmethod
    def get_by_kode_first(cls):
        return DBSession.query(cls).order_by(cls.kode).first()

        
class BaseModelDB(BaseKodeDB):
    nama = Column(String(250), nullable=False)
    disabled = Column(Integer, nullable=False, default=0)

    def __init__(self,data):
        BaseKodeDB.__init__(self,data)
        self.nama = data['nama']

    @classmethod
    def get_by_nama(cls, nama):
        return DBSession.query(cls).filter(
                       cls.nama.like( '%s%' % nama)
                       ).first()
 
    @classmethod
    def get_enabled(cls):
        #return cls.get_rows()
        return DBSession.query(cls).filter_by(disabled=0)

