from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.renderers import get_renderer
from pyramid.url import resource_url
from datetime import datetime 
from sqlalchemy.exc import DBAPIError
from esppt.models.model_base import (
    DBSession,
    )
from pyjasper.client import JasperGenerator
#from osipkd.models.admin_models import (
#    AppModel,GroupModuleModel,ModuleModel, GroupModel, UserGroupModel, UserModel
#    )
#from osipkd.models.apbd_admin_models import (
#    UnitModel,
#    )
    
def json_format(o):
    if type(o) is Date:
        return o.strftime("%d-%m-%Y")

status_apbds = {"0":"Pilih",
            "1":"RKA",
            "2":"DPA",
            "3":"RPKA",
            "4":"DPPA"}

jenis_belanjas = {"0":"Pilih",
                 "1":"UP",
                 "2":"TU",
                 "3":"GU",
                 "4":"LS",                 
                }            
jenis_indikators = {"0":"Pilih",
                 "1":"Capaian Program",
                 "2":"Masukan",
                 "3":"Keluaran",
                 "4":"Hasil",                 
                }            
triwulans        = {"0":"Pilih",
                 "1":"Triwulan I",
                 "2":"Triwulan II",
                 "3":"Triwulan III",
                 "4":"Triwulan IV",                 
                }  


                           
class JasperPDF(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(MovementGenerator, self).__init__()
        self.reportname = 'reports/Greeting.jrxml'
        self.xpath = '/greetings/greeting'
        self.root = ET.Element('gretings')

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""

        ET.SubElement(self.root, 'generator').text = __revision__
        for name in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'greeting')
            ET.SubElement(xml_greeting, "greeting_to").text = unicode(name)
            ET.SubElement(xml_greeting, "greeting_from").text = u"Max"
        return xmlroot
        
class BaseViews(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = request.session
        self.cut_nm   = "PEMERINTAH KABUPATEN/KOTA DEMO"
        ##Initialaize session
        if not 'app' in self.session:
            self.session['app'] = ""
        if not 'mod' in self.session:
            self.session['mod'] = ""
        if not 'user_id' in self.session:
            self.session['user_id'] = None
            
        if not 'sa' in self.session:
            self.session['sa'] = 0
        if not 'logged' in self.session:
            self.session['logged'] = 0
        if not 'tahun' in self.session:
            self.session['tahun'] =  datetime.strftime(datetime.now(),'%Y')
        if not 'status_apbd' in self.session:
            self.session['status_apbd'] = 0 # no status
        if not 'unit_id' in self.session:
            self.session['unit_id'] = 0 #No tahun datetime.strftime(datetime.now(),'%Y')
        if not 'all_unit' in self.session:
            self.session['all_unit'] = 0 # no status
        if not 'cust_nm' in self.session:
            self.session['cust_nm'] = self.cut_nm
        if not 'app_nm' in self.session:
            self.session['app_nm'] = "NONAME"
            
        # Inisiasi tahun anggaran
        if 'app' in request.params and request.params['app']:
            self.session['app'] = request.params['app']
            row = DBSession.query(AppModel).filter(AppModel.kode==self.session['app']).first()
            self.session['tahun'] = row and row.tahun or datetime.strftime(datetime.now(),'%Y')
            self.session['app_nm'] = row and row.nama or "Noname"
          
        if 'mod' in request.params and request.params['mod']:
            self.session['mod'] = request.params['mod']
            
        self.logged = self.session['logged']
        self.app = self.session['app']
        self.app_nm = self.session['app_nm']
        self.tahun = self.session['tahun']
        self.user_id = self.session['user_id']
        #default ajax result
        self.d = {}
        self.d['success'] = False        
        self.d['msg']='Hak akses dibatasi'

        #default datas 
        self.datas={}
        self.datas['title'] = "openSIPKD"
        self.datas['judul'] = ''
        self.datas['app'] = self.app
        self.datas['tahun'] = self.tahun
        self.datas['logged'] = self.logged
        self.datas['app_nm'] = self.app_nm 
        
        self.datas['user']={}
        self.datas['user']['id'] = 'userid' in self.session and self.session['userid'] or ''
        self.datas['user']['nm'] = 'usernm' in self.session and self.session['usernm'] or ''
        self.datas['cust_nm'] = 'cust_nm' in self.session and self.session['cust_nm'] or 'PEMERINTAH KABUPATEN/KOTA DEMO'
        self.datas['url'] = resource_url(context,request)

        if self.session["all_unit"]:
            unit_id = 'unit_id' in request.params and request.params["unit_id"] or self.session["unit_id"]
        else:
            unit_id = self.session["unit_id"]
            
        if unit_id:
            rows = UnitModel.get_by_id(unit_id) 
        elif self.session["all_unit"]:
            rows = UnitModel.get_by_kode_first()
        else:
            rows = None
        self.datas['units'] = rows
        
    def _DTstrftime(self, chain):
        ret = chain and datetime.strftime(chain, '%d-%m-%Y')
        if ret:
            return ret
        else:
            return chain
        
    def _DTnumberformat(self, chain):
        import locale
        locale.setlocale(locale.LC_ALL, 'id_ID.utf8')
        ret = locale.format("%d", chain, grouping=True)
        if ret:
          return ret
        else:
          return chain
          
    def _DTactive(self, chain):
        ret = chain==1 and 'Aktif' or 'Inaktif'
        if ret:
          return ret
        else:
          return chain

        
    def is_logged(self):
        if self.logged:
            return self.logged
        else:
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
    
    def is_sysadmin(self):
        return 'sa' in self.session and self.session['sa'] or False

    def is_akses_app(self):
        if self.is_sysadmin():
          return True
        else:
            row = DBSession.query(UserGroupModel).join(GroupModel).\
                  join(ModuleModel).join(AppModel).\
                  filter(AppModel.kode==self.app,
                         UserGroupMode.user_id==self.user_id)
                         
            #Jika gak punya akses aplikasi diredirect ke root
            if row:
                return True
            else: 
                return HTTPFound(location='/', headers=headers)
                #TODO: Message Application Forbidden 
    
    def is_akses_mod(self, act):
        if self.is_sysadmin():
            return True
        else:
            row = DBSession.query(GroupModuleModel).join(GroupModel).\
                  join(UserGroupModel).join(ModuleModel).\
                  filter(UserGroupModel.user_id == self.session['user_id'],
                         ModuleModel.kode  == self.session['mod']).first()
            if row:
              if act=='read':
                  return (row.reads==1)
              elif act=='add':
                  return (row.inserts==1)
              elif act=='edit':
                  return (row.edits==1)
              elif act=='delete':
                  return (row.deletes==1)
        return False

class TuBaseViews(BaseViews):
    def __init__(self, context, request):
        BaseViews.__init__(self, context, request)
          
        self.tahun = 'tahun' in self.session and self.session['tahun'] or\
                     datetime.strftime(datetime.now(),'%Y')
        
        self.all_unit =  'all_unit' in self.session and self.session['all_unit'] or 0        
        self.unit_id  = 'unit_id' in self.session and self.session['unit_id'] or 0
        self.unit_kd  = 'unit_kd' in self.session and self.session['unit_kd'] or "X.XX.XX"
        self.unit_nm  = 'unit_nm' in self.session and self.session['unit_nm'] or "Pilih Unit"
        self.sub_keg_id  = 'sub_keg_id' in self.session and self.session['sub_keg_id'] or 0
        
        self.datas['all_unit'] = self.all_unit
        self.datas['unit_id'] = self.unit_id
        self.datas['unit_kd'] = self.unit_kd
        self.datas['unit_nm'] = self.unit_nm
    
