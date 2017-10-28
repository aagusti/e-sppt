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
        
class eschange(BaseViews):
    @view_config(route_name = 'change',
                 renderer = 'templates/esppt/change.pt')
    def change(self):
        request = self.request
        session = self.session
        params = request.params
        ses = self.session
        if not 'logged' in session or  not session['logged']:
            url = self.request.resource_url(self.context, '')
            return HTTPFound(location=url, headers=None)
                    
        userid = session['userid']
        if request.POST:
            old_passwd = params['old_passwd']
            new_passwd = params['new_passwd']
            conf_passwd = params['conf_passwd']
            if new_passwd != conf_passwd:
                return render_to_response ('json',
                          dict(success=False,
                               msg="Password baru dan konfirmasi berbeda"))
                               
            if not new_passwd.strip() or not conf_passwd.strip():
                return render_to_response ('json',
                          dict(success=False,
                               msg="Password baru atau konfirmasi tidak boleh kosong"))
                               
            row = userModel.get_by_user(userid)
            if row.passwd != old_passwd:
                return render_to_response ('json',
                          dict(success=False,
                               msg="Password lama kurang tepat"))
            
            row.passwd = new_passwd
            DBSession.add(row)
            DBSession.flush()
            
            pesan = 'Password Login e-sppt Kota Tangerang Selatan Anda sudah diubah'
            row = DBSession.query(esRegModel).filter(
                      esRegModel.kode == userid).first()
            if row:
                if row and row.no_hp:
                    self.msg = pesan
                    antrian = antrianModel()
                    antrian.jalur = 1
                    antrian.penerima = row.no_hp
                    antrian.pesan = pesan
                    OtherDBSession.add(antrian)
                    OtherDBSession.flush()
                
                if row and row.email:
                    antrian_id = OtherDBSession.execute(antrian_seq)
                    a = antrianModel(id=antrian_id, kirim=True, jalur=6, 
                                     penerima=row.email, pesan=pesan)
                    
                    a.pengirim = "pbb@tangselkota.org"
                    subject = "Password untuk %s " % row.email 
                    mail = mailModel(id=antrian_id, subject=subject, name=row.nama)
                    OtherDBSession.add(mail)
                    OtherDBSession.add(a)
                    OtherDBSession.flush()
                row.passwd = new_passwd
                DBSession.add(row)
                DBSession.flush()
            
            return render_to_response ('json',
                      dict(success=True))
                      
        self.datas['title']="Silahkan Masukan password lama dan password baru anda"
        self.datas['judul']=''
        self.datas['userid']= userid

        self.datas['app']='app' in session and session['app'] or ''

        return dict(datas = self.datas,
                    rows = ())