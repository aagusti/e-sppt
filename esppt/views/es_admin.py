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

class esAdmin(BaseViews):
    @view_config(route_name='es_admin', renderer='templates/esppt/admin.pt')
    def home(self):
        ses = self.session
        if not 'logged' in ses or   not ses['logged'] or ses['userid']!='sa':
            url = self.request.resource_url(self.context, '')
            return HTTPFound(location=url, headers=None)

        return dict(datas=self.datas,
                    rows = '', 
                    sess=self.session,
                    tahun=datetime.now().year) 
                    
    @view_config(route_name='es_admin_act', renderer='json')
    def es_admin_act(self):
        req = self.request
        ses = self.session
        params = req.params
        url_dict = req.matchdict 
        ses = self.session
        if not 'logged' in ses or   not ses['logged'] or ses['userid']!='sa':
            url = self.request.resource_url(self.context, '')
            self.d['msg'] = ""
            return self.d

        if url_dict['act'] == 'grid':
            columns = []
            columns.append(ColumnDT('id'))
            columns.append(ColumnDT('kode'))
            columns.append(ColumnDT('nama'))
            columns.append(ColumnDT('kelurahan'))
            columns.append(ColumnDT('kecamatan'))
            columns.append(ColumnDT('kabupaten'))
            columns.append(ColumnDT('no_hp'))

            query = DBSession.query(esRegModel)
            rowTable = DataTables(req, esRegModel, query, columns)
            return rowTable.output_result()
            
        elif url_dict['act'] == 'delete':
            id = 'id' in params and params['id'] or ""
            if id:
                try:
                  q = esRegModel.query_id(id).delete()
                  DBSession.flush()
                  self.d['msg']='Sukses Hapus Data'
                  self.d['success']=True
                except:
                  self.d['msg']='Gagal Hapus Data'
                  self.d['success']=False
            return self.d
