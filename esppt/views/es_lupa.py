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
        
class eslupa(BaseViews):
    @view_config(route_name = 'lupa',
                 renderer = 'templates/esppt/lupa.pt')
    def login(self):
        request = self.request
        session = self.session
        self.datas['title']="Silahkan Masukan userid/email/handphone"
        self.datas['judul']=''

        self.datas['app']='app' in session and session['app'] or ''

        #cek apakah session sedang login kalau ya langsung di redirect ke home
        if 'logged' in session and session['logged']:
            HTTPFound(request.route_url("es_home"))
            #return self.home()

        return dict(datas = self.datas,
                    rows = ())