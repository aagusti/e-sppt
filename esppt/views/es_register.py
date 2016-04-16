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
    values['sms_sent']      = 1
    values['email_sent']    = 1
    
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
 
def route_reg_list(request):
    return HTTPFound(location=request.route_url('es_reg'))
 
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