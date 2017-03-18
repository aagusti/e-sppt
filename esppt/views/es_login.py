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
        
class eslogin(BaseViews):
    @view_config(route_name = 'login',
                 renderer = 'templates/esppt/login.pt')
    def login(self):
        request = self.request
        session = self.session
        self.datas['title']="Silahkan melakukan otentifikasi"
        self.datas['judul']=''

        self.datas['app']='app' in session and session['app'] or ''

        #cek apakah session sedang login kalau ya langsung di redirect ke home
        if 'logged' in session and session['logged']:
            HTTPFound(request.route_url("es_home"))
            #return self.home()

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

    @view_config(route_name="logout", renderer="templates/home.pt")
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

