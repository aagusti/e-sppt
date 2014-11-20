import sys
from model_base import *
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class spptModel(Base):
    __tablename__  = 'sppt'
    __table_args__ = {'extend_existing':True,'schema' : 'pbb', 
                      'autoload':True}
    """kd_propinsi              = Column(String(2) , nullable=False, primary_key=True)
    kd_dati2                 = Column(String(2) , nullable=False, primary_key=True)                      
    kd_kecamatan             = Column(String(3) , nullable=False, primary_key=True)                      
    kd_kelurahan             = Column(String(3) , nullable=False, primary_key=True)                      
    kd_blok                  = Column(String(3) , nullable=False, primary_key=True)                      
    no_urut                  = Column(String(4) , nullable=False, primary_key=True)                      
    kd_jns_op                = Column(String(1) , nullable=False, primary_key=True)                      
    thn_pajak_sppt           = Column(String(4) , nullable=False, primary_key=True)                      
    siklus_sppt              = Column(Integer , nullable=False)                      
    kd_kanwil_bank           = Column(String(2),)                      
    kd_kppbb_bank            = Column(String(2),)                      
    kd_bank_tunggal          = Column(String(2),)                      
    kd_bank_persepsi         = Column(String(2),)                      
    kd_tp                    = Column(String(2) , nullable=False)                      
    nm_wp_sppt               = Column(String(30) , nullable=False)                      
    jln_wp_sppt              = Column(String(30) , nullable=False)                      
    blok_kav_no_wp_sppt      = Column(String(15),)                      
    rw_wp_sppt               = Column(String(2),)                      
    rt_wp_sppt               = Column(String(3),)                      
    kelurahan_wp_sppt        = Column(String(30),)                      
    kota_wp_sppt             = Column(String(30),)                      
    kd_pos_wp_sppt           = Column(String(5),)                      
    npwp_sppt                = Column(String(15),)                      
    no_persil_sppt           = Column(String(5),)                      
    kd_kls_tanah             = Column(String(3), nullable=False , default='XXX' )                      
    thn_awal_kls_tanah       = Column(String(4), nullable=False , default='1986' )                      
    kd_kls_bng               = Column(String(3), nullable=False , default='XXX' )                      
    thn_awal_kls_bng         = Column(String(4), nullable=False , default='1986' )                      
    tgl_jatuh_tempo_sppt     = Column(Date , nullable=False)                      
    luas_bumi_sppt           = Column(BigInteger, nullable=False)                      
    luas_bng_sppt            = Column(BigInteger, nullable=False)                      
    njop_bumi_sppt           = Column(BigInteger, nullable=False)                      
    njop_bng_sppt            = Column(BigInteger, nullable=False)                      
    njop_sppt                = Column(BigInteger, nullable=False)                      
    njoptkp_sppt             = Column(Integer , nullable=False)                      
    njkp_sppt                = Column(Integer,)                      
    pbb_terhutang_sppt       = Column(BigInteger , nullable=False)                      
    faktor_pengurang_sppt    = Column(BigInteger,)                      
    pbb_yg_harus_dibayar_sppt= Column(BigInteger , nullable=False)                      
    status_pembayaran_sppt   = Column(String(1) ,nullable=False, default='0' )                      
    status_tagihan_sppt      = Column(String(1) ,nullable=False, default='0' )                      
    status_cetak_sppt        = Column(String(1) ,nullable=False, default='0' )                      
    tgl_terbit_sppt          = Column(Date, nullable=False)                      
    tgl_cetak_sppt           = Column(DateTime, nullable=False)                      
    nip_pencetak_sppt        = Column(String(18), nullable=False)                      
    kd_kanwil                = Column(String(2))                      
    kd_kantor                = Column(String(2))                      
    """                  
    @classmethod
    def get_by_nop_thn(cls, nop, thn):
        return DBSession.query(cls).filter(
                    cls.kd_propinsi    == nop[:2],
                    cls.kd_dati2       == nop[2:4],
                    cls.kd_kecamatan   == nop[4:7],
                    cls.kd_kelurahan   == nop[7:10],
                    cls.kd_blok        == nop[10:13],
                    cls.no_urut        == nop[13:17],
                    cls.kd_jns_op      == nop[17:18],
                    cls.thn_pajak_sppt == thn
               ).first()
               
    @classmethod           
    def get_by_nop(cls, nop):
        return DBSession.query(cls).filter(
                    cls.kd_propinsi    == nop[:2],
                    cls.kd_dati2       == nop[2:4],
                    cls.kd_kecamatan   == nop[4:7],
                    cls.kd_kelurahan   == nop[7:10],
                    cls.kd_blok        == nop[10:13],
                    cls.no_urut        == nop[13:17],
                    cls.kd_jns_op      == nop[17:18]
               )       
               
    @classmethod           
    def get_sisa_by_nop(cls, nop="13213123"):
        return DBSession.query(cls.thn_pajak_sppt, cls.nm_wp_sppt, 
                                  cls.pbb_yg_harus_dibayar_sppt,
                                  func.sum(pspptModel.denda_sppt).label('denda'),
                                  func.sum(pspptModel.jml_sppt_yg_dibayar).label('bayar'),
                                  (cls.pbb_yg_harus_dibayar_sppt+
                                  func.sum(pspptModel.denda_sppt)-
                                  func.sum(pspptModel.jml_sppt_yg_dibayar)).label('sisa')
                    ).filter(
                    cls.kd_propinsi    == nop[:2],
                    cls.kd_dati2       == nop[2:4],
                    cls.kd_kecamatan   == nop[4:7],
                    cls.kd_kelurahan   == nop[7:10],
                    cls.kd_blok        == nop[10:13],
                    cls.no_urut        == nop[13:17],
                    cls.kd_jns_op      == nop[17:18],
                    cls.kd_propinsi    == pspptModel.kd_propinsi,
                    cls.kd_dati2       == pspptModel.kd_dati2, 
                    cls.kd_kecamatan   == pspptModel.kd_kecamatan,
                    cls.kd_kelurahan   == pspptModel.kd_kelurahan,
                    cls.kd_blok        == pspptModel.kd_blok,
                    cls.no_urut        == pspptModel.no_urut,
                    cls.kd_jns_op      == pspptModel.kd_jns_op,
                    cls.thn_pajak_sppt == pspptModel.thn_pajak_sppt
                    ).group_by(cls)                   
               

class pspptModel(Base):
    __tablename__  = 'pembayaran_sppt'
    __table_args__ = {'extend_existing':True,'schema' : 'public', 
                      'autoload':True}
    """kd_propinsi              = Column(String(2) , nullable=False, primary_key=True)
    kd_dati2                 = Column(String(2) , nullable=False, primary_key=True)                      
    kd_kecamatan             = Column(String(3) , nullable=False, primary_key=True)                      
    kd_kelurahan             = Column(String(3) , nullable=False, primary_key=True)                      
    kd_blok                  = Column(String(3) , nullable=False, primary_key=True)                      
    no_urut                  = Column(String(4) , nullable=False, primary_key=True)                      
    kd_jns_op                = Column(String(1) , nullable=False, primary_key=True)                      
    thn_pajak_sppt           = Column(String(4) , nullable=False, primary_key=True)                      
    pembayaran_sppt_ke       = Column(Integer, nullable=False, primary_key=True)
    kd_kanwil                = Column(String(2))                      
    kd_kantor                = Column(String(2))   
    kd_tp                    = Column(String(2))
    denda_sppt               = Column(BigInteger)
    jml_sppt_yg_dibayar      = Column(BigInteger)
    tgl_pembayaran_sppt      = Column(Date)
    tgl_rekam_byr_sppt       = Column(DateTime)
    nip_rekam_byr_sppt       = Column(String(18))
    #user_id integer,                      
    """                  
    @classmethod
    def get_by_nop_thn(cls, nop, thn):
        return DBSession.query(cls).filter(
                    cls.kd_propinsi    == nop[:2],
                    cls.kd_dati2       == nop[2:4],
                    cls.kd_kecamatan   == nop[4:7],
                    cls.kd_kelurahan   == nop[7:10],
                    cls.kd_blok        == nop[10:13],
                    cls.no_urut        == nop[13:17],
                    cls.kd_jns_op      == nop[17:18],
                    cls.thn_pajak_sppt == thn
               )

class userModel(BaseDB, Base):
    __tablename__  = 'users'
    __table_args__ = {'extend_existing':True,'schema' : 'public'}
    userid   = Column(String(25), nullable=False)
    nama     = Column(String(50), nullable=False)
    passwd   = Column(String(50), nullable=False)
    nip      = Column(String(18), nullable=False)
    jabatan  = Column(String(50), nullable=False)
    disabled = Column(SmallInteger, nullable=False)
    def __init__(self,data):
        BaseDB.__init__(self,data)
        self.userid  = data['userid'] or None
        self.nama    = data['nama'] or None
        self.passwd  = data['passwd'] or None
        self.nip     = 'nip' in data and data['nip'] or '-'
        self.jabatan = 'jabatan' in data and data['jabatan'] or '-'
        self.disabled = 'disabled' in data and data['disabled'] or 0

    @classmethod
    def get_by_user(cls, uid):
        return DBSession.query(cls).filter(
                  cls.userid == uid
                ).first()
        
class esRegModel(BaseModelDB, Base):
    __tablename__  = 'es_register'
    __table_args__ = {'extend_existing':True,'schema' : 'esppt'}
    alamat1         = Column(String(64), nullable=False)
    alamat2         = Column(String(64), nullable=False)
    kelurahan       = Column(String(64), nullable=False)
    kecamatan       = Column(String(64), nullable=False)
    kabupaten       = Column(String(64), nullable=False)
    propinsi        = Column(String(64), nullable=False)
    no_hp           = Column(String(16), nullable=False)
    email           = Column(String(64), nullable=False)
    password        = Column(String(16), nullable=False)    

    def __init__(self, data):
        BaseModelDB.__init__(self,data)
        self.alamat1      = data['alamat1'] 
        self.alamat2      = data['alamat2']
        self.kelurahan    = data['kelurahan']
        self.kecamatan    = data['kecamatan']
        self.kabupaten    = data['kabupaten']
        self.propinsi     = data['propinsi']
        self.no_hp        = data['no_hp']
        self.email        = data['email']
        self.password     = data['password']
        
    @classmethod
    def get_by_nik(cls, nik):
        return DBSession.query(cls).filter(
                  cls.kode == nik
                ).first()
            
    @classmethod            
    def get_by_nik_email(cls, nik, email):
        return DBSession.query(cls).filter(
                  cls.kode == nik,
                  cls.email == email
                )
      
class esNopModel(BaseDB, Base):
    __tablename__  = 'es_nop'
    __table_args__ = {'extend_existing':True,'schema' : 'esppt'}
    kd_propinsi         = Column(String(2), nullable=False)
    kd_dati2            = Column(String(2), nullable=False)
    kd_kecamatan        = Column(String(3), nullable=False)     
    kd_kelurahan        = Column(String(3), nullable=False)
    kd_blok             = Column(String(3), nullable=False)
    no_urut             = Column(String(4), nullable=False)
    kd_jns_op           = Column(String(1), nullable=False)
    tahun               = Column(String(4), nullable=False)
    tgl_bayar           = Column(Date, nullable=False)        
    es_reg_id           = Column(BigInteger, ForeignKey("esppt.es_register.id"))
    es_register         = relationship("esRegModel", backref="es_nop")
    
    def __init__(self, data):
        BaseDB.__init__(self,data)
        self.nama           = data['nama']
        self.kd_propinsi    = data['nop'][:2]
        self.kd_dati2       = data['nop'][2:4]
        self.kd_kecamatan   = data['nop'][4:7]
        self.kd_kelurahan   = data['nop'][7:10]
        self.kd_blok        = data['nop'][10:13]
        self.no_urut        = data['nop'][13:17]
        self.kd_jns_op      = data['nop'][17:18]
        self.tahun          = data['tahun']
        self.tgl_bayar      = data['tgl_bayar']        
        self.es_reg_id      = data['es_reg_id']        

    def get_nop(cls):
        return "".join([self.kd_propinsi, self.kd_dati2, self.kd_kecamatan,
                        self.kd_kelurahan, self.kd_blok, self.kd_no_urut,
                        self.kd_jns_op])
                        
    def set_nop(cls,nop):
        self.kd_propinsi    = nop[:2]
        self.kd_dati2       = nop[2:4]
        self.kd_kecamatan   = nop[4:7]
        self.kd_kelurahan   = nop[7:10]
        self.kd_blok        = nop[10:13]
        self.no_urut        = nop[13:17]
        self.kd_jns_op      = nop[17:18]
        
    @classmethod
    def get_by_nop(cls,nop):
        print nop
        return DBSession.query(cls).filter(
                    cls.kd_propinsi    == nop[:2],
                    cls.kd_dati2       == nop[2:4],
                    cls.kd_kecamatan   == nop[4:7],
                    cls.kd_kelurahan   == nop[7:10],
                    cls.kd_blok        == nop[10:13],
                    cls.no_urut        == nop[13:17],
                    cls.kd_jns_op      == nop[17:18],
                  )
                                
          
