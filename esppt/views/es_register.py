from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from sqlalchemy import *
from sqlalchemy import distinct
from sqlalchemy.exc import DBAPIError
from views import *
from esppt.models.model_base import *
#from esppt.models.admin_models import *
#from esppt.models.apbd_admin_models import UserApbdModel, UrusanModel
import os
from pyramid.renderers import render_to_response
from esppt.models.esppt_models import *
import re
   
def get_logged(request):
    session = request.session
    if 'logged' in session:
        r = '<div class="btn-group pull-right">'
        r += '  <a class="btn dropdown-toggle" data-toggle="dropdown" href="#"></a>'
        r += '  <ul class="dropdown-menu pull-right">'
        r += '  <li><a href="#">Ubah Password</a></li>'
        r += '  <li><a href="/logout">Logout</a></li>'
        r += '  </ul>'
        r += '</div>'
            
    return r or ''
    
class espptRegister(BaseViews):
    
    @view_config(route_name='es_reg', renderer='../templates/esppt/register.pt')
    def esregister(self):
        self.datas['title']="Selamat Datang"
        self.datas['judul']='Modules'
        return dict(datas=self.datas,
                    rows = '', 
                    sess=self.session)   
    
    @view_config(route_name='es_reg_act', renderer='json')
    def es_register_act(self):
        ses = self.session
        req = self.request
        params = req.params
        url_dict = req.matchdict
        
        if url_dict['act']=='all':
            p = params.copy()
            p['nop'] = re.sub("[^0-9]", "", p['nop'])
            if not p['password1'] or not p['password2'] or p['password1']!=p['password2'] :
                self.d['msg']='Password tidak sama atau kosong'
                return self.d
                
            p['password']=p['password1']
            if 'disabled' not in p:
                p['disabled']='0'
            else:
                p['disabled']='1'
            p['tgl_bayar']  = p and p['tgl_bayar'] and \
                     datetime.strptime(p['tgl_bayar'], '%d-%m-%Y') or None
            p['created']    = datetime.now
            p['create_uid'] = self.session['user_id']
            p['update_uid'] = self.session['user_id']
            
            #check nik, email
            q = esRegModel.get_by_nik_email(p['kode'], p['email'])
            q = q.first()
            if q:
                self.d['msg']='NIK atau e-mail sudah digunakan'
                return self.d
                
            #CEK APAKAH DATA SPPT ADA???
            q = spptModel.get_by_nop_thn(p['nop'], p['tahun'])
            #q = q.first()
            if not q or q.nm_wp_sppt.strip() != p['nm_wp'].strip():
                self.d['msg']='NAMA tidak sesuai'
                return self.d
            #CEK PEMBAYARAN
            q = pspptModel.get_by_nop_thn(p['nop'], p['tahun'])
            q = q.first()
            
            if not q or q.tgl_pembayaran_sppt != p['tgl_bayar'].date():
                self.d['msg']='Tanggal pembayaran tidak sesuai'
                return self.d
                
            #Simpan data Registrasi
            rows = esRegModel.tambah(p)
            if rows:
                p['es_reg_id']=rows
                rows = esNopModel.tambah(p)
                #tambahkan user login
                us = {}
                us['userid'] = p['kode']
                us['nama']   = p['nama']
                us['passwd'] = p['password']
                us['created']    = datetime.now
                us['create_uid'] = self.session['user_id']
                us['update_uid'] = self.session['user_id']                
 
                rows = userModel.tambah(us)
                ses['userid'] = p['kode']
                ses['user_nm'] = p['nama']
                ses[user_id] = rows
                
                self.d['msg']='Sukses Simpan Data'
                self.d['success']=True
            return self.d
        elif url_dict['act']=='nop_save':
            p = params.copy()
            p['nop'] = re.sub("[^0-9]", "", p['nop'])
            if 'disabled' not in p:
                p['disabled']='0'
            else:
                p['disabled']='1'
            p['tgl_bayar']  = p and p['tgl_bayar'] and \
                     datetime.strptime(p['tgl_bayar'], '%d-%m-%Y') or None
            p['update_uid'] = self.session['user_id']
            p['created']    = datetime.now
            p['create_uid'] = self.session['user_id']
            
            #CEK APAKAH DATA SPPT ADA???
            q = spptModel.get_by_nop_thn(p['nop'], p['tahun'])
            #q = q.first()
            if not q or q.nm_wp_sppt.strip() != p['nm_wp'].strip():
                self.d['msg']='NAMA tidak sesuai'
                return self.d
            #CEK PEMBAYARAN
            q = pspptModel.get_by_nop_thn(p['nop'], p['tahun'])
            q = q.first()
            
            if not q or q.tgl_pembayaran_sppt != p['tgl_bayar'].date():
                self.d['msg']='Tanggal pembayaran tidak sesuai'
                return self.d
                
            #Simpan data Registrasi
            q = esRegModel.get_by_nik(ses['userid'])
            if not q:
                return self.d
            p['es_reg_id'] = q.id
            p['nama']=q.nama
            if 'id' in p: 
                del p['id']
            
            rows = esNopModel.tambah(p)
            if rows:
                self.d['msg']='Sukses Simpan Data'
                self.d['success']=True                    
            return self.d
            
        elif url_dict['act']=='prof_save':
            p = params.copy()
            if  p['password1']!=p['password2'] :
                self.d['msg']='Password tidak sama'
                return self.d
            if  p['password1']:   
                p['password']=p['password1']
            if 'disabled' not in p:
                p['disabled']='0'
            else:
                p['disabled']='1'
            p['updated']    = datetime.now
            p['update_uid'] = self.session['user_id']
            if 'password1' in p:
                del p['password1']
            if 'password2' in p:
                del p['password2']
                
            #Simpan data Registrasi
            if esRegModel.update(p):
                self.d['msg']='Sukses Simpan Data'
                self.d['success']=True
            return self.d
            
        else:
            HTTPNotFound()            
    
class eslogin(BaseViews):
    @view_config(route_name = 'login',
                 renderer = '../templates/esppt/login.pt')
    def login(self):
        request = self.request
        session = self.session
        self.datas['title']="Silahkan melakukan otentifikasi"
        self.datas['judul']=''

        self.datas['app']='app' in session and session['app'] or ''

        #cek apakah session sedang login kalau ya langsung di redirect ke home
        if 'logged' in session and session['logged']:
            return self.home()
        return dict(datas = self.datas,
                    rows = ())

    @view_config(route_name='login_it', renderer='json')
    def login_it(self):
        request = self.request
        session = request.session
        url = self.request.resource_url(self.context, '/login')
        referrer = request.url
        if referrer == url:
            referrer = '/login' # never use the login form itself as came_from
        #Cek dulu apakah sumbernya dari form login
        #Json Define
        a={}
        a['msg'] = 'Salah id atau password'
        a['success'] = False
        if 'login' in request.params:
            headers = forget(self.request)
            userid = request.params['userid']
            headers = remember(request, userid)
            xpasswd = request.params['passwd']
            row = userModel.get_by_user(userid)
            if row and row.passwd==xpasswd and not row.disabled: #Bisa Login
                session['user_id'] = row.id
                session['userid']  = row.userid
                session['usernm']  = row.nama
                session['logged']=1
                if userid=='sa':
                    session['sa'] = 1
                else: 
                    session['sa'] = 0
                    
                # Get Informasi APBD
                """row = UserApbdModel.get_by_id(self.session['user_id'])
                self.session['unit_id'] = row and row.unit_id or 0
                self.session['all_unit'] = row and row.all_unit or self.session['sa'] 
                if self.session['unit_id'] > 0:
                    row = DBSession.query(UnitModel).join(UrusanModel)\
                          .filter(UnitModel.urusan_id==UrusanModel.id, \
                                  UnitModel.id==self.session['unit_id']).first()
                    self.session['unit_nm'] = row and row.nama or ""
                    self.session['unit_kd'] = row and ''.join([row.urusans.kode,'.',row.kode]) or ""
                #end off apbd
                """
                a['msg'] = 'Berhasil Login'
                a['success'] = True
        return a

    @view_config(route_name="logout", renderer="../templates/home.pt")
    def logout(self):
        session          = self.session
        session.invalidate()
        self.session['sa'] =  None
        #['logged']=0
        #session['app']   =None
        session['userid']=None
        headers          = forget(self.request)
        self.datas['logged']=0;
        url = self.request.resource_url(self.context, '')
        return HTTPFound(location=url, headers=headers)

class esHome(BaseViews):
    @view_config(route_name='es_home', renderer='../templates/esppt/home.pt')
    def es_home(self):
        ses = self.session
        if not 'logged' in ses or   not ses['logged']:
            url = self.request.resource_url(self.context, '')
            return HTTPFound(location=url, headers=None)

        return dict(datas=self.datas,
                    rows = '', 
                    sess=self.session) 
                    
    @view_config(route_name='es_home_nop', renderer='../templates/esppt/home_nop.pt')
    def es_home_frm(self):
        req = self.request
        ses = self.session
        params = req.params
        url_dict = req.matchdict 
        return dict(datas=self.datas,
                    rows = '', 
                    sess=self.session)

    @view_config(route_name='es_home_prof', renderer='../templates/esppt/home_prof.pt')
    def es_home_prof(self):
        req = self.request
        ses = self.session
        params = req.params
        url_dict = req.matchdict 
        if url_dict['id'] and url_dict['id'].isdigit():
            rows = DBSession.query(esRegModel).filter(
                    esRegModel.kode==ses['userid']
                ).first()
            return dict(datas=self.datas,
                    rows = rows, 
                    sess=self.session)
        else:
            HTTPNotFound()            

    
    @view_config(route_name='es_home_act', renderer='json')
    def es_home_act(self):
        req = self.request
        ses = self.session
        params = req.params
        url_dict = req.matchdict 
        if url_dict['act'] == 'grid1':
            columns = []
            columns.append(ColumnDT('kd_propinsi'))
            columns.append(ColumnDT('kd_dati2'))
            columns.append(ColumnDT('kd_kecamatan'))
            columns.append(ColumnDT('kd_kelurahan'))
            columns.append(ColumnDT('kd_blok'))
            columns.append(ColumnDT('no_urut'))
            columns.append(ColumnDT('kd_jns_op'))
            query = DBSession.query(esNopModel).filter(
                esNopModel.es_reg_id == esRegModel.get_by_nik(ses['userid']).id
              )
            rowTable = DataTables(req, esNopModel, query, columns)
            return rowTable.output_result()

        elif url_dict['act'] == 'grid2':
            id = 'id' in params and params['id'] or ""
            if id:
                q = esNopModel.get_by_nop(id)
                r = q.first()
                if not r or r.es_register.kode !=ses['userid']:
                   id = ""
                
            columns = []
            columns.append(ColumnDT('thn_pajak_sppt'))
            columns.append(ColumnDT('nm_wp_sppt'))
            columns.append(ColumnDT('pbb_yg_harus_dibayar_sppt'))
            columns.append(ColumnDT('denda'))
            columns.append(ColumnDT('bayar'))
            columns.append(ColumnDT('sisa'))
            
            query = spptModel.get_sisa_by_nop(id)
            
            rowTable = DataTables(req, spptModel, query, columns)
            return rowTable.output_result()
                 
        elif url_dict['act'] == 'delete':
            id = 'id' in params and params['id'] or ""
            if id:
                q = esNopModel.get_by_nop(id)
                r = q.first()
                if r and r.es_register.kode ==ses['userid']:
                   q.delete()
                   self.d['msg']='Sukses Hapus Data'
                   self.d['success']=True
            return self.d