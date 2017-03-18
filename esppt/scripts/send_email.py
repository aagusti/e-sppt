import sys
import os
#os.environ['PYJASPER_SERVLET_URL'] = 'http://localhost:5555/pyJasper/jasper.py'
import base64
import locale
locale.setlocale(locale.LC_ALL, 'id_ID.UTF-8')
import transaction
from sqlalchemy import engine_from_config
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    bootstrap,
    )
from ..models.model_base import (
    DBSession,
    Base,
    )
from ..models.other_base import (
    OtherDBSession,
    OtherBase,
    )

USER_ID = 'sa'
EMAIL_SUBJECT = 'SPPT {nop} {tahun}'
EMAIL_BODY = """Bapak / Ibu {nama_wp} yth,

Terlampir SPPT dengan Nomor Objek Pajak {nop} untuk tahun {tahun} senilai
Rp {nilai}.
"""

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def get_nop(row):
    return row.kd_propinsi + row.kd_dati2 + row.kd_kecamatan + \
           row.kd_kelurahan + row.kd_blok + row.no_urut + \
           row.kd_jns_op

def thousand(value):
    return locale.format('%.0f', value, True)

def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    os.environ['PYJASPER_SERVLET_URL'] = settings['jasper_url'] 
    bootstrap(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    other_engine = engine_from_config(settings, 'othersql.')
    Base.metadata.bind = engine
    OtherBase.metadata.bind = other_engine
    from ..models.esppt_models import (
        esNopModel,
        esRegModel,
        spptModel,
        )
    from ..views.es_reports import GenerateSppt
    DBSession.configure(bind=engine)
    q = DBSession.query(esNopModel, esRegModel).filter(
            esNopModel.es_reg_id == esRegModel.id)
    q = q.filter(esNopModel.email_sent == 0)
    for r_nop, r_reg in q:
        nop = get_nop(r_nop)
        q = spptModel.get_by_nop_thn(nop, r_nop.tahun)
        sppt = q.first()
        if not sppt:
            continue
        nilai = thousand(sppt.pbb_yg_harus_dibayar_sppt)
        g = GenerateSppt(nop, r_nop.tahun, r_reg.kode) 
        #USER_ID) updated menggunakan password dari user yang ada di reg.kode aagusti
        sppt_file = g.sppt_file
        e_filename = os.path.split(sppt_file)[-1]
        f = open(sppt_file)
        content = f.read()
        f.close()
        e_content = base64.encodestring(content)
        e_subject = EMAIL_SUBJECT.format(nop=nop, tahun=r_nop.tahun)
        e_body = EMAIL_BODY.format(nama_wp=sppt.nm_wp_sppt, nop=nop,
                    tahun=r_nop.tahun, nilai=nilai)
        files = [(e_filename, e_content)]
        print('To: {name} <{email}>'.format(name=sppt.nm_wp_sppt,
                email=r_reg.email))
        print('Subject: {s}'.format(s=e_subject))
        print('Body: {s}'.format(s=e_body))
        print('File: {s}'.format(s=e_filename))
        r_nop.email_sent = 1
        flush(r_nop)
        send(r_reg.email, sppt.nm_wp_sppt, e_subject, e_body, files,
                settings['email_pengirim'])
    transaction.commit()

def send(penerima, name, subject, pesan, files=[], pengirim=None): 
    from ..models.imgw_models import (
        antrian_seq,
        antrianModel,
        mailModel,
        mailFileModel,
        )
    other_engine = OtherBase.metadata.bind
    antrian_id = antrian_seq.execute(bind=other_engine)
    mail = mailModel(id=antrian_id, subject=subject, name=name)
    other_flush(mail)
    urutan = 0
    for filename, content in files:
        urutan += 1
        mail_file = mailFileModel(id=antrian_id, urutan=urutan,
                        filename=filename, content=content)
        other_flush(mail_file)
    a = antrianModel(id=antrian_id, kirim=True, jalur=6, penerima=penerima,
            pesan=pesan)
    a.pengirim = pengirim 
    other_flush(a)

def flush(row):
    DBSession.add(row)
    DBSession.flush()

def other_flush(row):
    OtherDBSession.add(row)
    OtherDBSession.flush()
