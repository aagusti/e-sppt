import unittest
import os.path
import urlparse

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.security import forget
from pyramid.security import has_permission
from sqlalchemy import *
from sqlalchemy import distinct, literal_column
from sqlalchemy.sql.functions import concat
from sqlalchemy.exc import DBAPIError
from views import *
#from models.model_base import *
from esppt.models.esppt_models import *
from datetime import datetime
import os
from pyramid.renderers import render_to_response

from pyjasper import (JasperGenerator)
from pyjasper import (JasperGeneratorWithSubreport)
import xml.etree.ElementTree as ET
from pyramid.path import AssetResolver
import PyPDF2

from ..models.model_base import DBSession

from ..models.esppt_models import userModel, esNopModel
from ..models.imgw_models import *

def get_logo():
    a = AssetResolver('esppt') 
    resolver = a.resolve(''.join(['static/images/','logo_rpt.png']))
    return resolver.abspath()
#logo = '/home/tangselkota/domains/e-sppt.tangselkota.org/env/e-sppt/esppt/static/images/logo_tangsel.png'

def get_rpath(filename):
    a = AssetResolver('esppt')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
    
def send_message():
      q = DBSession.query(esNopModel).\
              filter(or_(sms_sent==0, email_sent==0))
      rows = q.all()
      for row in rows:
          id  = "".join([row.kd_propinsi, row.kd_dati2, row.kd_kecamatan, row.kd_kelurahan,
                         row.kd_blok, row.no_urut, row.kd_jns_op])
          thn = row.tahun
          
          if row.sms_sent==0:
              penerima = row.es_register.no_hp
              GenerateSms(id,thn,penerima)
          
          if row.email_sent==0:
              userid = row.es_register.kode
              penerima = row.es_register.email
              
              sppt_file = GenerateSppt(id,thn,userid)
              antrian = antrianModel()
              antrian.jalur = 1
              antrian.penerima=penerima
              antrian.pesan='SPPT '+id+' '+thn #dan seterusnya
              OtherDBSession.add(antrian)
              OtherDBSession.flush()
              
class GenerateSms():
    def __init__(self,id,thn,penerima):
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
           self.d['msg']=pesan
           self.d['success']=True
                   
class r001Generator(JasperGenerator):
    """Jasper-Generator for Greetingcards"""
    def __init__(self):
        super(r001Generator, self).__init__()
        self.reportname = get_rpath('sppt.jrxml')
        self.xpath = '/pad/sppt'
        self.root = ET.Element('pad') 

    def generate_xml(self, tobegreeted):
        """Generates the XML File used by Jasperreports"""
        #xml_a  =  ET.SubElement(self.root, 'master')
        for row in tobegreeted:
            xml_greeting  =  ET.SubElement(self.root, 'sppt')
            ET.SubElement(xml_greeting, "tahun").text = unicode(row.thn_pajak_sppt)
            ET.SubElement(xml_greeting, "nop").text = "%s.%s-%s.%s-%s.%s-%s" % (row.kd_propinsi, 
                       row.kd_dati2, row.kd_kecamatan, row.kd_kelurahan, row.kd_blok, row.no_urut, 
                       row.kd_jns_op)
            ET.SubElement(xml_greeting, "alamat_op").text = row.jalan_op and row.jalan_op or '-'
            ET.SubElement(xml_greeting, "rt_rw_op").text = "%s %s/%s" % (row.blok_kav_no_op and row.blok_kav_no_op or '-', 
                                                             row.rw_op and row.rw_op or '000',
                                                             row.rt_op and row.rt_op or '00')
            ET.SubElement(xml_greeting, "desa_op").text = row.nm_kelurahan and row.nm_kelurahan or '-'
            ET.SubElement(xml_greeting, "kec_op").text = row.nm_kecamatan and row.nm_kecamatan  or '-'
            ET.SubElement(xml_greeting, "kota_op").text = row.nm_dati2 and  row.nm_dati2 or '-'
            ET.SubElement(xml_greeting, "nama_wp").text = row.nm_wp_sppt
            ET.SubElement(xml_greeting, "alamat_wp").text = row.jln_wp_sppt and row.jln_wp_sppt or '-'
            ET.SubElement(xml_greeting, "rt_rw_wp").text = '%s %s/%s' % (row.blok_kav_no_wp_sppt and row.blok_kav_no_wp_sppt or '-',
                                                                      row.rt_wp_sppt and row.rt_wp_sppt or '000', 
                                                                      row.rw_wp_sppt and row.rw_wp_sppt or '00')
            ET.SubElement(xml_greeting, "desa_wp").text = row.kelurahan_wp_sppt
            ET.SubElement(xml_greeting, "kec_wp").text = '' #row.kec_wp
            ET.SubElement(xml_greeting, "kota_wp").text = row.kota_wp_sppt
            ET.SubElement(xml_greeting, "npwp").text = row.npwp_sppt and row.npwp_sppt or '-'
            ET.SubElement(xml_greeting, "bumi_luas").text = unicode(row.luas_bumi_sppt)
            ET.SubElement(xml_greeting, "bumi_kelas").text = '001' #unicode(row.bumi_kelas)
            ET.SubElement(xml_greeting, "bumi_njop").text = unicode(row.luas_bumi_sppt and row.njop_bumi_sppt/row.luas_bumi_sppt or 0)
            ET.SubElement(xml_greeting, "bumi_total").text = unicode(row.njop_bumi_sppt) 
            ET.SubElement(xml_greeting, "bng_luas").text = unicode(row.luas_bng_sppt)
            ET.SubElement(xml_greeting, "bng_kelas").text = '001' #unicode(row.bng_kelas)
            ET.SubElement(xml_greeting, "bng_njop").text = unicode(row.luas_bng_sppt and row.njop_bng_sppt/row.luas_bng_sppt or 0)
            ET.SubElement(xml_greeting, "bng_total").text = unicode(row.njop_bng_sppt)
            ET.SubElement(xml_greeting, "njop_dasar").text = unicode(row.njop_sppt)
            ET.SubElement(xml_greeting, "njoptkp").text = unicode(row.njoptkp_sppt)
            ET.SubElement(xml_greeting, "njop_pbb").text = unicode(row.njop_sppt-row.njoptkp_sppt)
            ET.SubElement(xml_greeting, "tarif").text = '0.1%'
            ET.SubElement(xml_greeting, "pbb").text = unicode(row.pbb_yg_harus_dibayar_sppt)
            ET.SubElement(xml_greeting, "tgl_jatuhtempo").text = row.tgl_jatuh_tempo_sppt.strftime('%d-%m-%Y')
            ET.SubElement(xml_greeting, "tgl_terbit_sppt").text = row.tgl_terbit_sppt.strftime('%d-%m-%Y')
            ET.SubElement(xml_greeting, "jabatan").text = 'jabatan'
            ET.SubElement(xml_greeting, "kepala").text = 'kepala'
            ET.SubElement(xml_greeting, "nip").text = '123456789'
            ET.SubElement(xml_greeting, "logo").text = get_logo()
            ET.SubElement(xml_greeting, "tgl_proses").text = row.tgl_proses.strftime('%d-%m-%Y')
            ET.SubElement(xml_greeting, "sequence").text = row.sequence
            ET.SubElement(xml_greeting, "pbb_terhutang").text = unicode(row.pbb_terhutang_sppt)
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logo
        print ET.tostring(self.root, encoding='utf8', method='xml')
        return self.root
        
class GenerateSppt():
    def __init__(self,nop,thn,user_id):
        _here = os.path.dirname(__file__)
        sppt_path  = os.path.join(os.path.dirname(_here), 'sppt')
        sppt_file  = '%s/%s%s.pdf' %(sppt_path,nop,thn) 
        self.sppt_file = sppt_file
        owner_pass='t4ngs3l'
        user_pass='t4ngs3l'
        users = userModel.get_by_user(user_id)
        if users:
            user_pass=users.passwd.encode('utf8') 
            
        if not os.path.exists(sppt_file):
            q = DBSession.query(spptModel.kd_propinsi, spptModel.kd_dati2, spptModel.kd_kecamatan, 
                        spptModel.kd_kelurahan, spptModel.kd_blok, spptModel.no_urut, spptModel.kd_jns_op, 
                        spptModel.thn_pajak_sppt, spptModel.nm_wp_sppt, spptModel.jln_wp_sppt, 
                        spptModel.blok_kav_no_wp_sppt, spptModel.rw_wp_sppt, spptModel.rt_wp_sppt, 
                        spptModel.kelurahan_wp_sppt, spptModel.kota_wp_sppt, spptModel.kd_pos_wp_sppt, 
                        spptModel.npwp_sppt, spptModel.kd_kls_tanah, spptModel.kd_kls_bng, 
                        spptModel.tgl_jatuh_tempo_sppt, spptModel.luas_bumi_sppt, spptModel.luas_bng_sppt, 
                        spptModel.njop_bumi_sppt, spptModel.njop_bng_sppt, spptModel.njop_sppt, 
                        spptModel.njoptkp_sppt, spptModel.pbb_terhutang_sppt, 
                        spptModel.pbb_yg_harus_dibayar_sppt, spptModel.tgl_terbit_sppt, 
                        dopModel.jalan_op, dopModel.blok_kav_no_op, dopModel.rw_op,dopModel.rt_op, 
                        kelurahanModel.nm_kelurahan, kecamatanModel.nm_kecamatan, dati2Model.nm_dati2).\
                    outerjoin(dopModel).\
                    outerjoin(kelurahanModel).\
                    outerjoin(kecamatanModel).\
                    outerjoin(dati2Model).\
                    filter(
                        spptModel.kd_propinsi    == nop[:2],
                        spptModel.kd_dati2       == nop[2:4],
                        spptModel.kd_kecamatan   == nop[4:7],
                        spptModel.kd_kelurahan   == nop[7:10],
                        spptModel.kd_blok        == nop[10:13],
                        spptModel.no_urut        == nop[13:17],
                        spptModel.kd_jns_op      == nop[17:18],
                        spptModel.thn_pajak_sppt == thn)
            row = q.first()
            
            v_pbb_hrsbyr = str(row.pbb_yg_harus_dibayar_sppt)
            v_c1 = datetime.now().strftime('%d%m%Y%H%M%S')
            v_c2 = v_pbb_hrsbyr[:1];
            v_c3 = row.nm_wp_sppt[:1];
            v_c4 = user_id[:1]
            v_c5 = row.nm_wp_sppt[-1:]
            v_c6 = str(len(v_pbb_hrsbyr) - 3)[:1]
            v_c7 = row.nm_wp_sppt[2:1]
            v_c8 = str(len(v_pbb_hrsbyr))
            v_c9 = 'ES'
            kode = "".join([v_c1,v_c2,v_c3,v_c4,v_c5,v_c6,v_c7,v_c8,v_c9])
            query = DBSession.query(spptModel.kd_propinsi, spptModel.kd_dati2, spptModel.kd_kecamatan, 
                        spptModel.kd_kelurahan, spptModel.kd_blok, spptModel.no_urut, spptModel.kd_jns_op, 
                        spptModel.thn_pajak_sppt, spptModel.nm_wp_sppt, spptModel.jln_wp_sppt, 
                        spptModel.blok_kav_no_wp_sppt, spptModel.rw_wp_sppt, spptModel.rt_wp_sppt, 
                        spptModel.kelurahan_wp_sppt, spptModel.kota_wp_sppt, spptModel.kd_pos_wp_sppt, 
                        spptModel.npwp_sppt, spptModel.kd_kls_tanah, spptModel.kd_kls_bng, 
                        spptModel.tgl_jatuh_tempo_sppt, spptModel.luas_bumi_sppt, spptModel.luas_bng_sppt, 
                        spptModel.njop_bumi_sppt, spptModel.njop_bng_sppt, spptModel.njop_sppt, 
                        spptModel.njoptkp_sppt, spptModel.pbb_terhutang_sppt, 
                        spptModel.pbb_yg_harus_dibayar_sppt, spptModel.tgl_terbit_sppt, 
                        dopModel.jalan_op, dopModel.blok_kav_no_op, dopModel.rw_op,dopModel.rt_op,
                        kelurahanModel.nm_kelurahan, kecamatanModel.nm_kecamatan, dati2Model.nm_dati2,
                        literal_column("'%s'" %kode).label("sequence"),
                        func.current_timestamp().label("tgl_proses")).\
                    outerjoin(dopModel).\
                    outerjoin(kelurahanModel).\
                    outerjoin(kecamatanModel).\
                    outerjoin(dati2Model).\
                    filter(
                        spptModel.kd_propinsi    == nop[:2],
                        spptModel.kd_dati2       == nop[2:4],
                        spptModel.kd_kecamatan   == nop[4:7],
                        spptModel.kd_kelurahan   == nop[7:10],
                        spptModel.kd_blok        == nop[10:13],
                        spptModel.no_urut        == nop[13:17],
                        spptModel.kd_jns_op      == nop[17:18],
                        spptModel.thn_pajak_sppt == thn)
                        
            generator = r001Generator()
            pdf = generator.generate(query) 
            output_file ='%s.tmp' %sppt_file
            open(sppt_file, 'w').write(pdf)
            output = PyPDF2.PdfFileWriter()
            input_stream = PyPDF2.PdfFileReader(open(sppt_file, "rb"))
            for i in range(0, input_stream.getNumPages()):
                output.addPage(input_stream.getPage(i))
                
            outputStream = open(output_file, "wb")
         
            # Set user and owner password to pdf file
            output.encrypt(user_pass, owner_pass, use_128bit=True)
            output.write(outputStream)
            outputStream.close()
         
            # Rename temporary output file with original filename, this
            # will automatically delete temporary file
            os.rename(output_file, sppt_file)
            self.sppt_file = sppt_file
     
class ViewSPPTLap(BaseViews):
    @view_config(route_name="es_report_act")
    def es_report_act(self):
        if not self.logged :
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
        req    = self.request
        params = req.params
        url_dict = req.matchdict

        if url_dict['act'] == 'sppt':
            pk_id = 'id' in params and params['id']  or None
            if pk_id:
                nop = pk_id
                thn = params['thn']
                sppt_file = GenerateSppt(nop,thn,req.session['userid']).sppt_file
                if sppt_file:
                    pdf = open(sppt_file, 'r').read()
                    response=req.response
                    response.content_type="application/pdf"
                    response.content_disposition='filename=%s.pdf' %nop
                    response.write(pdf)
                    return response
                else:
                    return HTTPNotFound() 
        else:
            return HTTPNotFound() #TODO: Warning Hak Akses 
            
    @view_config(route_name="es_gen_sppt", renderer='json')
    def es_sppt_gen(self):
        req =  self.request
        url_dict = req.matchdict
        thn = url_dict['thn']
        if not thn:
            thn = datetime.now().year
   
        if not thn or req.session['userid']!='sa':
            json_data ={"status":0,
                  "msg":"Not Allowed"}
            return json_data
        
        q = DBSession.query(esNopModel).join(esRegModel).\
                      order_by(esNopModel.kd_propinsi,esNopModel.kd_dati2,esNopModel.kd_kecamatan,
                               esNopModel.kd_kelurahan,esNopModel.kd_blok,esNopModel.no_urut,
                               esNopModel.kd_jns_op)
        rows = q.all()
        nop=[]
        for row in rows:
            nop.append("".join([row.kd_propinsi,row.kd_dati2,row.kd_kecamatan,
                              row.kd_kelurahan,row.kd_blok,row.no_urut,row.kd_jns_op])) 
            # sppt_file = self.genarate_sppt(nop,thn,row.es_register.kode)
            row.tahun = thn
            row.sms_sent = 0
            row.email_sent = 0
            DBSession.add(row)

        DBSession.flush()
            
        return dict(status=1,
             msg="Sukses masuk kedalam antrian",
             nop=nop)
        