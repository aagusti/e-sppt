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
from sqlalchemy import distinct
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

def get_logo():
    a = AssetResolver('esppt') 
    resolver = a.resolve(''.join(['static/images/','logo_rpt.png']))
    return resolver.abspath()
#logo = '/home/tangselkota/domains/e-sppt.tangselkota.org/env/e-sppt/esppt/static/images/logo_tangsel.png'

def get_rpath(filename):
    a = AssetResolver('esppt')
    resolver = a.resolve(''.join(['reports/',filename]))
    return resolver.abspath()
    
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
            ET.SubElement(xml_greeting, "alamat_op").text = row.jalan_op
            ET.SubElement(xml_greeting, "rt_rw_op").text = "%s %s/%s" % (row.blok_kav_no_op and row.blok_kav_no_op or '-', 
                                                             row.rw_op and row.rw_op or '000',
                                                             row.rt_op and row.rt_op or '00')
            ET.SubElement(xml_greeting, "desa_op").text = row.nm_kelurahan and row.nm_kelurahan or '-'
            ET.SubElement(xml_greeting, "kec_op").text = row.nm_kecamatan and row.nm_kecamatan  or '-'
            ET.SubElement(xml_greeting, "kota_op").text = row.nm_dati2 and  row.nm_dati2 or '-'
            ET.SubElement(xml_greeting, "nama_wp").text = row.nm_wp_sppt
            ET.SubElement(xml_greeting, "alamat_wp").text = row.jln_wp_sppt
            ET.SubElement(xml_greeting, "rt_rw_wp").text = '%s %s/%s' % (row.blok_kav_no_wp_sppt and row.blok_kav_no_wp_sppt or '-',
                                                                      row.rt_wp_sppt and row.rt_wp_sppt or '000', 
                                                                      row.rw_wp_sppt and row.rw_wp_sppt or '00')
            ET.SubElement(xml_greeting, "desa_wp").text = row.kelurahan_wp_sppt
            ET.SubElement(xml_greeting, "kec_wp").text = '' #row.kec_wp
            ET.SubElement(xml_greeting, "kota_wp").text = row.kota_wp_sppt
            ET.SubElement(xml_greeting, "npwp").text = row.npwp_sppt
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
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logo
        print ET.tostring(self.root, encoding='utf8', method='xml')
        return self.root
        
class ViewSPPTLap(BaseViews):
    @view_config(route_name="es_report_act")
    def es_report_act(self):
        if not self.logged :
            headers=forget(self.request)
            return HTTPFound(location='/login?app=%s' % self.app, headers=headers)
            
        #global logo
        #logo   = ''
        #logo   = 'https://e-sppt.tangselkota.org/static/images/logo_tangsel.png'
        #logo = self.request.static_url('esppt:static/images/logo_tangsel.png')
        #logo = self.request.static_url('esppt:static/images/logo_tangsel.png')
        #print ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>", logo
        req    = self.request
        params = req.params
        url_dict = req.matchdict
        url_dict = req.matchdict 

        if url_dict['act'] == 'sppt':
            pk_id = 'id' in params and params['id']  or None
            if pk_id:
                nop = pk_id
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
                            spptModel.thn_pajak_sppt == params['thn'])
                generator = r001Generator()
                pdf = generator.generate(query)
                response=req.response
                response.content_type="application/pdf"
                response.content_disposition='filename=sppt.pdf' 
                response.write(pdf)
                return response
        else:
            return HTTPNotFound() #TODO: Warning Hak Akses 
