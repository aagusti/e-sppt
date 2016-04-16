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
import os
from pyramid.renderers import render_to_response
from esppt.models.esppt_models import *

  
import re
import colander
from deform import (
    Form,
    widget,
    ValidationFailure,
    )
from email.Utils import parseaddr, formataddr   
                    
from es_register import RegEditSchema, NopAddSchema, save_nop     
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

def save_prof_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
    row = save_reg(values,row)


def save_nop_request(values, request, row=None):
    if 'id' in request.matchdict:
        values['id'] = request.matchdict['id']
        
    if  not 'es_reg_id' in values:
        sid = esRegModel.get_by_nik(request.session['userid'])
        if not sid:
            return
        values['es_reg_id'] = sid.id
    row=[]
    row = save_nop(values,row)
    
def route_nop_list(request):
    return HTTPFound(location=request.route_url('es_home'))
    
def session_failed(request, session_name):
    r = dict(form=request.session[session_name])
    del request.session[session_name]
    return r
def get_prof_form(request, class_form):
    schema = class_form(validator=form_prof_validator)
    schema = schema.bind()
    schema.request = request
    return Form(schema, buttons=('register','batal'))    
    
def get_nop_form(request, class_form):
    schema = class_form(validator=form_nop_validator)
    schema = schema.bind()
    schema.request = request
    return Form(schema, buttons=('register','batal'))

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
            columns.append(ColumnDT('sms_sent'))
            columns.append(ColumnDT('email_sent'))
            sid = esRegModel.get_by_nik(ses['userid'])
            if not sid:
                aadata= {"aaData": [], 
                          "iTotalRecords": "0", 
                          "sEcho": "1", 
                          "iTotalDisplayRecords": "0"}
                return aadata
            query = DBSession.query(esNopModel).\
                          filter(esNopModel.es_reg_id == sid.id)
                          
            rowTable = DataTables(req, esNopModel, query, columns)
            return rowTable.output_result()

        elif url_dict['act'] == 'grid2':
            id = 'id' in params and params['id'] or ""
            #print '*******', id,  params['id'], params
            if id:
                q = esNopModel.get_by_nop(id)
                r = q.first()
                if not r or r.es_register.kode !=ses['userid']:
                   id = ""
                
            columns = []
            columns.append(ColumnDT('thn_pajak_sppt'))
            columns.append(ColumnDT('nm_wp_sppt'))
            columns.append(ColumnDT('pbb_yg_harus_dibayar_sppt', filter=self._DTnumberformat))
            columns.append(ColumnDT('denda', filter=self._DTnumberformat))
            columns.append(ColumnDT('bayar', filter=self._DTnumberformat))
            columns.append(ColumnDT('sisa', filter=self._DTnumberformat))
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

                penerima = q.es_register.no_hp    
                sms = GenerateSMS(penerima,id,thn)
                if sms.msg:
                    self.d = sms.msg
                    
            return self.d            
                   
        elif url_dict['act'] == 'email':
            id = 'id' in params and params['id'] or ""
            thn = 'thn' in params and params['thn'] or ""
            if id and thn:
                q = esNopModel.get_by_nop(id).first()
                if not q or q.es_register.kode != ses['userid']:
                    return dict(msg='NOP bukan milik anda')
                q.email_sent = 0
                q.tahun=thn
                DBSession.add(q)
                DBSession.flush()
                self.d = dict(msg = 'Sukses Masuk Kedalam Antrian ',
                        success = True)
            return self.d
            
        else:
            return dict(msg = 'Command Not Found',
                        success = False)