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
from datetime import (datetime, date)
#from esppt.models.admin_models import *
#from esppt.models.apbd_admin_models import UserApbdModel, UrusanModel
import os
from pyramid.renderers import render_to_response
from esppt.models.esppt_models import *
from esppt.models.imgw_models import *
  
import re
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from email.Utils import parseaddr, formataddr   
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
    
    
def nik_found(nik):
      return userModel.get_by_user(nik) or esRegModel.get_by_nik(nik) 

def nik_reg_found(nik):
      return esRegModel.get_by_nik(nik)
      
def email_found(email):
      return esRegModel.get_by_email(email)

def email_validator(node, value):
    name, email = parseaddr(value)
    if not email or email.find('@') < 0:
        raise colander.Invalid(node, 'Invalid email format')
        
def form_reg_validator(form, value):
    def err_nik():
        raise colander.Invalid(form,
                'NIK %s sudah ada yang menggunakan' % value['regschema']['kode'])
        
    def err_email():
        raise colander.Invalid(form,
                'e-mail %s sudah ada yang menggunakan' % value['regschema']['email'])
                
    def err_sppt():
        raise colander.Invalid(form,
                'SPPT %s %s nama %s tidak ditemukan' % (value['nopschema']['nop'], 
                       value['nopschema']['tahun'], value['nopschema']['nm_wp']))
                
    def err_psppt():
        raise colander.Invalid(form,
                'PEMBAYARAN SPPT %s %s tidak valid' % (value['nopschema']['nop'], 
                       value['nopschema']['tahun']))
    
    if nik_found(value['regschema']['kode']):
        return err_nik()
        
    if email_found(value['regschema']['email']):
        return err_email()
    nop = re.sub("[^0-9]", "", value['nopschema']['nop'])
    tahun = str(value['nopschema']['tahun'])
    #CEK APAKAH DATA SPPT ADA???
    q = spptModel.get_by_nop_thn(nop, tahun)
    q = q.first()
    if not q or q.nm_wp_sppt.strip() != value['nopschema']['nm_wp'].strip():
        return err_sppt()
        
    #CEK PEMBAYARAN
    q = pspptModel.get_by_nop_thn(nop, tahun)
    q = q.first()
    if not q or q.tgl_pembayaran_sppt != value['nopschema']['tgl_bayar']:
        return err_psppt()

def form_nop_validator(form, value):
    def err_sppt():
        raise colander.Invalid(form,
                'SPPT %s %s nama %s tidak ditemukan' % (value['nop'], 
                       value['tahun'], value['nm_wp']))
                
    def err_psppt():
        raise colander.Invalid(form,
                'PEMBAYARAN SPPT %s %s tidak valid' % (value['nop'], 
                       value['tahun']))
    
    nop = re.sub("[^0-9]", "", value['nop'])
    tahun = str(value['tahun'])
    #CEK APAKAH DATA SPPT ADA???
    q = spptModel.get_by_nop_thn(nop, tahun)
    q = q.first()
    if not q or q.nm_wp_sppt.strip() != value['nm_wp'].strip():
        return err_sppt()
        
    #CEK PEMBAYARAN
    q = pspptModel.get_by_nop_thn(nop, tahun)
    q = q.first()
    if not q or q.tgl_pembayaran_sppt != value['tgl_bayar']:
        return err_psppt()

def form_prof_validator(form, value):
    def err_nik():
        raise colander.Invalid(form,
                'NIK %s sudah ada yang menggunakan' % value['kode'])
        
    def err_email():
        raise colander.Invalid(form,
                'e-mail %s sudah ada yang menggunakan' % value['email'])
    r = email_found(value['email'])      
    if r :
        if r.id!= ('id' in value and value['id'] or 0):
            return err_email()
class RegAddSchema(colander.Schema):
  kode        = colander.SchemaNode(
                    colander.String(),
                    title="NIK",
                    oid="kode")
  nama        = colander.SchemaNode(
                    colander.String(),)
  alamat1     = colander.SchemaNode(
                    colander.String(),
                    title="Alamat")
  alamat2     = colander.SchemaNode(
                    colander.String(),
                    missing=colander.drop,
                    title="")
  kelurahan   = colander.SchemaNode(
                    colander.String(),)
  kecamatan   = colander.SchemaNode(
                    colander.String(),)
  kabupaten   = colander.SchemaNode(
                    colander.String(),
                    title="Kabupaten/Kota")
  propinsi    = colander.SchemaNode(
                    colander.String(),)
  no_hp       = colander.SchemaNode(
                    colander.String(),
                    title="No Handphone")
  email       = colander.SchemaNode(
                    colander.String(),
                    title="e-mail",
                    validator=email_validator)
  password    = colander.SchemaNode(
                    colander.String(),
                    widget=widget.CheckedPasswordWidget(size=20),
                    validator=colander.Length(min=6))
                    
class NopAddSchema(colander.Schema):
  nop  = colander.SchemaNode(
                    colander.String(),
                    #validator = colander.Length(min=18, max=18),
                    widget = widget.TextInputWidget(
                                mask = '99.99.999.999-999.9999.9',
                                mask_placeholder = '#'), 
                    title="NOP")
  tahun        = colander.SchemaNode(
                    colander.Integer(),
                    validator=colander.Range(min=1999, max=datetime.now().year),
                    title="Tahun SPPT",
                    )
  tgl_bayar    = colander.SchemaNode(
                    colander.Date())
  nm_wp         = colander.SchemaNode(
                    colander.String(),
                    title="Nama WP SPPT")
                    

class RegSchema(colander.Schema):
  regschema = RegAddSchema()
  nopschema = NopAddSchema()
  
class RegEditSchema(RegAddSchema):
    id = colander.SchemaNode(colander.Integer(),
            missing=colander.drop,
            widget=widget.HiddenWidget(readonly=True),
            title="")

def get_form(request, class_form):
    schema = class_form(validator=form_reg_validator)
    schema = schema.bind()
    schema.request = request
    return Form(schema, buttons=('register','batal'))
    
def get_nop_form(request, class_form):
    schema = class_form(validator=form_nop_validator)
    schema = schema.bind()
    schema.request = request
    return Form(schema, buttons=('register','batal'))
    
def get_prof_form(request, class_form):
    schema = class_form(validator=form_prof_validator)
    schema = schema.bind()
    schema.request = request
    return Form(schema, buttons=('register','batal'))    
    
def save_reg(values, row=None):
    if not row:
        row =esRegModel()
    row.from_dict(values)
    if values['password']:
        row.password = values['password']
    DBSession.add(row)
    DBSession.flush()
    return row
    
def save_nop(values, row=None):
    if not row:
        row =esNopModel()
    nop = re.sub("[^0-9]", "", values['nop'])
    values['kd_propinsi']   = nop[:2]
    values['kd_dati2']      = nop[2:4]
    values['kd_kecamatan']  = nop[4:7]
    values['kd_kelurahan']  = nop[7:10]
    values['kd_blok']       = nop[10:13]
    values['no_urut']       = nop[13:17]
    values['kd_jns_op']     = nop[17:18]
    row.from_dict(values)
    DBSession.add(row)
    DBSession.flush()
    return row
    
def save_user(values, row=None):
    if not row:
        row =userModel()
        values['created'] = datetime.now()
        values['create_uid']=1
    else:
      values['updated'] = datetime.now()
      values['update_uid']=1
    values['userid'] = values['kode']
    if values['password']:
        values['passwd'] = values['password']
    if not 'nip' in values:
        values['nip'] = values['kode']
    if not 'jabatan' in values:
        values['jabatan'] = 'Guest'
    row.from_dict(values)
    row.disabled = 'disabled' in values and 1 or 0  
    DBSession.add(row)
    DBSession.flush()
    return row
    
def save_reg_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save_reg(values, row)
    request.session.flash('Registrasi %s sudah disimpan.' % row.nama)
    values['es_reg_id'] = row.id
    row=[]
    row = save_nop(values,row)
    row=[]
    row = save_user(values,row)

def save_nop_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    if  not 'es_reg_id' in values:
        values['es_reg_id'] = esRegModel.get_by_nik(request.session['userid']).id    
    row=[]
    row = save_nop(values,row)
    
def save_prof_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save_reg(values,row)
    
def route_reg_list(request):
    return HTTPFound(location=request.route_url('es_reg'))
    
def route_nop_list(request):
    return HTTPFound(location=request.route_url('es_home'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
                    
class espptRegister(BaseViews):
    @view_config(route_name='es_reg', renderer='templates/esppt/register.pt')
    def view_add(self):
        request = self.request
        form = get_form(request, RegSchema)
        if request.POST:
            if 'register' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form, datas=self.datas)
                save_reg_request(dict(controls), request)
            return route_reg_list(request)
        return dict(form=form, datas=self.datas)
                    
    @view_config(route_name='es_help', renderer='templates/esppt/help.pt')
    def esregister(self):
        self.datas['title']="Pertolongan"
        self.datas['judul']='Modules'
        return dict(datas=self.datas,
                    rows = '', 
                    sess=self.session)  
        
class esHome(BaseViews):
    @view_config(route_name='es_home', renderer='templates/esppt/home.pt')
    def es_home(self):
        ses = self.session
        if not 'logged' in ses or   not ses['logged']:
            url = self.request.resource_url(self.context, '')
            return HTTPFound(location=url, headers=None)

        return dict(datas=self.datas,
                    rows = '', 
                    sess=self.session) 
                    
    @view_config(route_name='es_home_nop', renderer='templates/esppt/home_nop.pt')
    def es_home_nop_frm(self):
        request = self.request
        form = get_nop_form(request, NopAddSchema)
        if request.POST:
            if 'register' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form, datas=self.datas)
                save_nop_request(dict(controls), request)
            return route_nop_list(request)
        return dict(form=form, datas=self.datas)

    @view_config(route_name='es_home_prof', renderer='templates/esppt/home_prof.pt')
    def es_home_prof(self):
        request = self.request
        ses = request.session
        row = esRegModel.get_by_nik(ses['userid'])
        if not row:
            return HTTPFound(location=request.route_url("es_home_prof_add"))
        
        form = get_prof_form(request, RegEditSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form, datas=self.datas)
                save_prof_request(dict(controls), request, row)
            return route_nop_list(request)
        values = row.to_dict()
        form.set_appstruct(values)
        return dict(form=form, datas=self.datas)
        
    @view_config(route_name='es_home_prof_add', renderer='templates/esppt/home_prof.pt')
    def es_home_prof_add(self):
        request = self.request
        form = get_prof_form(request, RegAddSchema)
        if request.POST:
            if 'simpan' in request.POST:
                controls = request.POST.items()
                try:
                    c = form.validate(controls)
                except ValidationFailure, e:
                    return dict(form=form, datas=self.datas)
                save_prof_request(dict(controls), request)
            return route_nop_list(request)
        values = {}
        values['kode']=request.session['userid']
        form.set_appstruct(values)
        return dict(form=form, datas=self.datas)
        
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

        elif url_dict['act'] == 'sms':
            id = 'id' in params and params['id'] or ""
            thn = 'thn' in params and params['thn'] or ""
            if id:
                q = esNopModel.get_by_nop(id).first()
                if not q or q.es_register.kode != ses['userid']:
                    self.d['msg']='NOP bukan milik anda'
                    return self.d
                penerima = q.es_register.no_hp    
                q = spptModel.get_by_nop_thn(id,thn).first()
                if q:
                   pesan = ''.join(['NOP:', id,' ',thn, ' NAMA:', q.nm_wp_sppt or '', \
                                ' ALAMAT:',q.jln_wp_sppt or '', q.blok_kav_no_wp_sppt or '', \
                                ' RT/RW:', q.rt_wp_sppt or '', '/',q.rw_wp_sppt or '', \
                                ' KELURAHAN:', q.kelurahan_wp_sppt or '', \
                                ' KOTA:', q.kota_wp_sppt or '', \
                                ' NJOP:', '{0:,}'.format(q.njop_sppt) or '', \
                                ' TERUTANG:', '{0:,}'.format(q.pbb_yg_harus_dibayar_sppt)  or ''])
                   antrian = antrianModel()
                   antrian.jalur = 1
                   antrian.penerima=penerima
                   antrian.pesan=pesan
                   OtherDBSession.add(antrian)
                   OtherDBSession.flush()
                   #OtherDBSession.commit()
                   self.d['msg']='Sukses Kirim Data '+pesan
                   self.d['msg']=pesan
                   self.d['success']=True
            return self.d            