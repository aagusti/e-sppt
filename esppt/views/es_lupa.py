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
from esppt.models.model_base import DBSession
from esppt.models.other_base import OtherDBSession
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
        
class eslupa(BaseViews):
    @view_config(route_name = 'lupa',
                 renderer = 'templates/esppt/lupa.pt')
    def login(self):
        request = self.request
        session = self.session
        if request.POST:
            email = request.POST['email']
            row = DBSession.query(esRegModel).filter(
                      or_(esRegModel.email == email,
                          esRegModel.kode == email,
                          esRegModel.no_hp == email
                      )).first()
                      
            if not row:
                return render_to_response ('json',
                          dict(success=False))
                          
            datLogin = userModel.get_by_user(row.kode)
            if not datLogin:
                return render_to_response ('json',
                          dict(success=False))
                          
            if datLogin.passwd != row.password:
               row.passwd = datLogin.passwd
               DBSession.add(row)
               DBSession.flush()
            
            pesan = 'Password Login e-sppt Kota Tangerang Selatan Anda %s' % datLogin.passwd
            
            if row.no_hp:
                self.msg = pesan
                antrian = antrianModel()
                antrian.jalur = 1
                antrian.penerima = row.no_hp
                antrian.pesan = pesan
                OtherDBSession.add(antrian)
                OtherDBSession.flush()
            
            if row.email:
                antrian_id = OtherDBSession.execute(antrian_seq)
                a = antrianModel(id=antrian_id, kirim=True, jalur=6, 
                                 penerima=row.email, pesan=pesan)
                
                a.pengirim = "pbb@tangselkota.org"
                subject = "Password untuk %s " % email 
                mail = mailModel(id=antrian_id, subject=subject, name=row.nama)
                OtherDBSession.add(mail)
                OtherDBSession.add(a)
                OtherDBSession.flush()
            
            return render_to_response ('json',
                      dict(success=True))
           
             
            
        self.datas['title']="Silahkan Masukan userid/email/handphone"
        self.datas['judul']=''

        self.datas['app']='app' in session and session['app'] or ''

        #cek apakah session sedang login kalau ya langsung di redirect ke home
        if 'logged' in session and session['logged']:
            HTTPFound(request.route_url("es_home"))
            #return self.home()

        return dict(datas = self.datas,
                    rows = ())