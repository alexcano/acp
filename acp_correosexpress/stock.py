# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields,osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import sys
reload(sys)
sys.setdefaultencoding('iso-8859-1')
from urllib import unquote_plus
import os
import tempfile
from datetime import datetime, date
from xml.dom.minidom import parseString
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time
import pytz
from dateutil import tz
import base64
import os.path
from zpl_label.service import ZPLlabel

from correosexpress.service import CORREOSEXPRESService
from correosexpress.resources.response import CORREOSEXPRESShipmentResponse
from correosexpress.resources.plantilla_impresora import acp_correxpress_label

from PyPDF2 import PdfFileMerger, PdfFileReader


# Overloaded stock_picking to manage carriers :
class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_correxpress(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context=context):
            carrier_id = pick.carrier_id.id
            correxpress_company_id = pick.company_id.correxpress_carrier_id.id
            picking_type = pick.picking_type_id.code
            if carrier_id == correxpress_company_id and pick.state in ['done','waiting','confirmed','assigned','partially_available'] and picking_type == 'outgoing':
                res[pick.id] = True
            else:
                res[pick.id] = False

        return res
        
    def _get_mrw(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context=context):
            if pick.correxpress or pick.dhl:
                res[pick.id] = False
            else:
                res[pick.id] = True
        return res        

    def onchange_carrier_correos_id(self, cr, uid, ids,  carrier_id, company_id, state, context=None):
        values = self.onchange_carrier_id(cr,uid,ids,carrier_id,company_id,state, context=context)
        vals = {}        
        vals = values['value']
        if not carrier_id:
            vals['correxpress'] = False
        else:
            picking = self.browse(cr,uid,ids[0])
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            picking_type = picking.picking_type_id.code
            if carrier_id == company.correxpress_carrier_id.id and picking.state in ['done','waiting','confirmed','assigned','partially_available'] and picking_type == 'outgoing':
                if 'mrw' not in vals:
                    vals['mrw'] = False
                vals['correxpress'] = True
            else:
                vals['correxpress'] = False
        print vals
        return {'value': vals}


    _columns = {
        'mrw': fields.function(_get_mrw, type='boolean', string='Campos visibles MRW'),
        'correxpress': fields.function(_get_correxpress, type='boolean', string='Campos visibles correos express'),
        'correxpress_fecha': fields.datetime('Fecha Envio'),
        'correxpress_ref': fields.char('Referencia Envio', size=30),
        'correxpress_refcli': fields.char('Referencia Cliente Envio', size=30),
        'correxpress_numbultos': fields.integer('Numero Bultos'),
        'correxpress_kilos': fields.float('Kilos', digits=(16, 2)),
        'correxpress_volumen': fields.float('Volumen', digits=(16, 2)),
        'correxpress_alto': fields.float('Alto', digits=(16, 2)),
        'correxpress_largo': fields.float('Largo', digits=(16, 2)),
        'correxpress_ancho': fields.float('Ancho', digits=(16, 2)),
        'correxpress_producto': fields.many2one('acp_correxpress.product','Producto'),
        'correxpress_portes': fields.selection([('P', 'Pagado'),
                                ('D', 'Debido'),
                                   ], 'Portes'),
        'correxpress_reembolso': fields.float('Reembolso', digits=(16, 2)),
        'correxpress_entrsabado': fields.selection([('S', 'Si'),
                                ('N', 'No'),
                                   ], 'Entrega Sábado'),
        'correxpress_seguro': fields.float('Seguro', digits=(16, 2)),
        'correxpress_numenviovuelta': fields.integer('Numero Envio Vuelta'),
        'correxpress_observaciones': fields.text('Observaciones'),
        'correxpress_numenvio': fields.char('Numero de Envio', size=20),
        'correxpress_error': fields.char('Codigo Error', size=20),
        'correxpress_mensaje': fields.text('Mensaje'),
        'correxpress_codunico': fields.char('Codunico', size=240),
        'correxpress_codunico': fields.char('Codunico', size=240),
        'correxpress_bultos_ids' : fields.one2many('acp_correxpress.picking_bultos', 'picking_id', 'Detalle Bultos'),
    }

    _defaults ={
        'correxpress_entrsabado': 'N',
        'correxpress_portes': 'P',
    }

    def send_correxpress_mail (self, cr, uid, ids, context=None):
        email_template_obj = self.pool.get('email.template')
        template_ids = email_template_obj.search(cr, uid,[('name','=','Enviar Aviso Tracking (Correo Express)')],context=context)
        if template_ids:
            template_id = email_template_obj.browse(cr, uid, template_ids, context=context)
            for picking in self.browse(cr, uid, ids, context=context):
                if picking.carrier_tracking_ref:
                    values = email_template_obj.generate_email(cr, uid, template_id.id, picking.sale_id.id, context=context)
                    values['res_id'] = picking.sale_id.id
                    values['partner_ids'] = [picking.sale_id.partner_invoice_id.id]
                    values['notified_partner_ids'] = [picking.sale_id.partner_invoice_id.id]
                    values['email_to'] = picking.sale_id.partner_invoice_id.email
                    values['notification'] = True
                    mail_mail_obj = self.pool.get('mail.mail')
                    msg_id = mail_mail_obj.create(cr, uid, values, context=context)
                    if msg_id:
                        mail_mail_obj.send(cr, uid, [msg_id], context=context)
        return True

    def get_data (self, cr, uid, ids, bulto_id, context=None):
        picking = self.browse(cr,uid,ids[0], context=context)
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr,uid,picking.company_id.id)
        username = company.correxpress_username or False
        password = company.correxpress_password or False
        code = company.correxpress_code or False
        debug = company.correxpress_debug

        if picking.correxpress_fecha:
            correxpress_fecha_d = datetime.strptime(picking.correxpress_fecha, '%Y-%m-%d %H:%M:%S')
            correxpress_fecha_c = correxpress_fecha_d.strftime('%d%m%Y')
            etiq_fecha = correxpress_fecha_d.strftime('%d/%m/%Y')
        else:
            correxpress_fecha_d = datetime.strptime(fields.datetime.now(), '%Y-%m-%d %H:%M:%S')
            correxpress_fecha_c = correxpress_fecha_d.strftime('%d%m%Y')
            etiq_fecha = correxpress_fecha_d.strftime('%d/%m/%Y')

        if picking.correxpress_ref:
            ref = picking.correxpress_ref
        else:
            #ref = picking.name
            if picking.opencart_id:
               ref = 'PEDIDO ' + picking.opencart_id
            else:
               ref = 'PEDIDO ' + picking.origin            

        if picking.correxpress_refcli:
               refcli = picking.correxpress_refcli
        else:
            if picking.opencart_id:
               refcli = 'PEDIDO ' + picking.opencart_id
            else:
               refcli = 'PEDIDO ' + picking.origin


        if company.country_id.code == 'ES':
            codpostnacrte = company.zip
            codposintrte = ''
        else:
            codpostnacrte = ''
            codposintrte = company.zip

        if picking.partner_id.country_id.code == 'ES':
            codpostnacdest = picking.partner_id.zip
            codposintdest = ''
        else:
            codpostnacdest = ''
            codposintdest = picking.partner_id.zip

        if not picking.number_of_packages or picking.number_of_packages == 0:
            numbultos = 1
        else:
            numbultos = picking.number_of_packages

        if not picking.weight or picking.weight == 0:
            if not picking.correxpress_kilos or picking.correxpress_kilos == 0:
                kilos = 1
            else:
                kilos = 1 #picking.correxpress.kilos
        else:
            kilos = 1 #picking.weight

        data = {}
        data['solicitante'] = username
        data['password'] = password
        data['codRte'] = code
        data['ref'] = ref
        data['refCli'] = refcli
        data['fecha'] = correxpress_fecha_c
        data['nomRte'] = company.name and unquote_plus(company.name.encode('utf-8','xmlcharrefreplace')) or ''
        data['dirRte'] = company.street and unquote_plus(company.street.encode('utf-8','xmlcharrefreplace')) or ''
        data['pobRte'] = company.city and unquote_plus(company.city.encode('utf-8','xmlcharrefreplace')) or ''
        data['codPosNacRte'] = codpostnacrte and unquote_plus(codpostnacrte.encode('utf-8','xmlcharrefreplace')) or ''
        data['paisISORte'] = company.country_id.code and unquote_plus(company.country_id.code.encode('utf-8','xmlcharrefreplace')) or ''
        data['codPosIntRte'] = codposintrte and unquote_plus(codposintrte.encode('utf-8','xmlcharrefreplace')) or ''
        data['contacRte'] = company.name and unquote_plus(company.name.encode('utf-8','xmlcharrefreplace')) or ''
        data['telefRte'] = company.phone and unquote_plus(company.phone.encode('utf-8','xmlcharrefreplace')) or ''
        data['emailRte'] = company.email and unquote_plus(company.email.encode('utf-8','xmlcharrefreplace')) or ''
        data['nomDest'] = picking.partner_id.name and unquote_plus(picking.partner_id.name.encode('utf-8','xmlcharrefreplace')) or ''
        data['dirDest'] = picking.partner_id.street and unquote_plus(picking.partner_id.street.encode('utf-8','xmlcharrefreplace')) or ''
        data['pobDest'] = picking.partner_id.city and unquote_plus(picking.partner_id.city.encode('utf-8','xmlcharrefreplace')) or ''
        data['codPosNacDest'] = codpostnacdest and unquote_plus(codpostnacdest.encode('utf-8','xmlcharrefreplace')) or ''
        data['paisISODest'] = picking.partner_id.country_id.code and unquote_plus(picking.partner_id.country_id.code.encode('utf-8','xmlcharrefreplace')) or ''
        data['codPosIntDest'] = codposintdest and unquote_plus(codposintdest.encode('utf-8','xmlcharrefreplace')) or ''
        data['contacDest'] = picking.partner_id.name and unquote_plus(picking.partner_id.name.encode('utf-8','xmlcharrefreplace')) or ''
        data['telefDest'] = picking.partner_id.phone and unquote_plus(picking.partner_id.phone.encode('utf-8','xmlcharrefreplace')) or ''
        data['emailDest'] = picking.partner_id.email and unquote_plus(picking.partner_id.email.encode('utf-8','xmlcharrefreplace')) or ''
        data['contacOtrs'] = ''
        data['telefOtrs'] = ''
        data['emailOtrs'] = ''
        data['observac'] = picking.correxpress_observaciones and unquote_plus(picking.correxpress_observaciones.encode('utf-8','xmlcharrefreplace')) or ''
        data['numBultos'] = numbultos
        data['kilos'] = kilos
        data['volumen'] = picking.correxpress_volumen
        data['alto'] = picking.correxpress_alto
        data['largo'] = picking.correxpress_largo
        data['ancho'] = picking.correxpress_ancho
        data['producto'] = picking.correxpress_producto.codigo
        data['portes'] = picking.correxpress_portes
        data['reembolso'] = str(picking.correxpress_reembolso)
        data['entrSabado'] = picking.correxpress_entrsabado
        data['seguro'] = picking.correxpress_seguro
        data['numEnvioVuelta'] = picking.correxpress_numenviovuelta or ''


        if bulto_id:
            acp_correxpress_bultos_obj = self.pool.get('acp_correxpress.picking_bultos')
            bulto = acp_correxpress_bultos_obj.browse(cr,uid,bulto_id, context=context)
            data['codbarras'] = bulto.codbarras
            data['etiq_nomRte'] = company.name and company.correxpress_code + ' ' + unquote_plus(company.name.encode('utf-8','xmlcharrefreplace')) or ''
            data['etiq_bulto'] = bulto.numbulto
            data['etiq_fecha'] = etiq_fecha
            data['etiq_tsv_abrevia'] = picking.correxpress_producto.sigla
            if picking.partner_id.country_id.code == 'ES':
                destino = self.destino(cr, uid, ids,context=context)
                cod_destino = destino.get(codpostnacdest[:3].zfill(3),'')
                if not cod_destino:
                    cod_destino = destino.get(codpostnacdest[:2]+'0','')                    
                data['etiq_destino'] = cod_destino
                data['etiq_pais'] = ''
            else:
                data['etiq_destino'] = ''
                data['etiq_pais'] = picking.partner_id.country_id.name
            if picking.correxpress_entrsabado == 'S':
                data['etiq_entrSabado'] = 'SABADO'
            else:
                data['etiq_entrSabado'] = ''
            if picking.correxpress_portes == 'P':
                data['etiq_portes'] = 'PAGADOS'
            else:
                data['etiq_portes'] = 'DEBIDOS'

            if picking.correxpress_reembolso > 0:
                data['etiq_reembolso'] = str(picking.correxpress_reembolso) + ' Eur'
            else:
                data['etiq_reembolso'] = ''                               

            data['observac_bulto'] = bulto.observaciones and unquote_plus(bulto.observaciones.encode('utf-8','xmlcharrefreplace')) or ''
            data['numenvio'] = picking.carrier_tracking_ref or ''
        return data


    def button_correxpress_envio(self, cr, uid, ids, context=None):
        picking = self.browse(cr,uid,ids[0], context=context)
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr,uid,picking.company_id.id)
        username = company.correxpress_username or False
        password = company.correxpress_password or False
        code = company.correxpress_code or False
        debug = company.correxpress_debug
        acp_correxpress_bultos_obj = self.pool.get('acp_correxpress.picking_bultos')

        #Comprobación de datos
        if picking.carrier_tracking_ref:
            raise osv.except_osv(
                        _('Error Envio Correo Express'),
                        _('Ya tiene numero de envio'))


        correos_api = CORREOSEXPRESService(username, password, code, debug)

        data = self.get_data(cr, uid, ids,bulto_id=None,context=context)

        response = correos_api.grabarenvio(
            canalEntrada=None,
            numEnvio=None,
            ref=data.get('ref', ''),
            refCli=data.get('refCli', ''),
            fecha=data.get('fecha', ''),
            codRte=data.get('codRte', ''),
            nomRte=data.get('nomRte', ''),
            nifRte=data.get('nifRte', ''),
            dirRte=data.get('dirRte', ''),
            pobRte=data.get('pobRte', ''),
            codPosNacRte=data.get('codPosNacRte', ''),
            paisISORte=data.get('paisISORte', ''),
            codPosIntRte=data.get('codPosIntRte', ''),
            contacRte=data.get('contacRte', ''),
            telefRte=data.get('telefRte', ''),
            emailRte=data.get('emailRte', ''),
            codDest=data.get('codDest', ''),
            nomDest=data.get('nomDest', ''),
            nifDest=data.get('nifDest', ''),
            dirDest=data.get('dirDest', ''),
            pobDest=data.get('pobDest', ''),
            codPosNacDest=data.get('codPosNacDest', ''),
            paisISODest=data.get('paisISODest', ''),
            codPosIntDest=data.get('codPosIntDest', ''),
            contacDest=data.get('contacDest', ''),
            telefDest=data.get('telefDest', ''),
            emailDest=data.get('emailDest', ''),
            contacOtrs=data.get('contacOtrs', ''),
            telefOtrs=data.get('telefOtrs', ''),
            emailOtrs=data.get('emailOtrs', ''),
            observac=data.get('observac', ''),
            numBultos=data.get('numBultos', ''),
            kilos=data.get('kilos', ''),
            volumen=data.get('volumen', ''),
            alto=data.get('alto', ''),
            largo=data.get('largo', ''),
            ancho=data.get('ancho', ''),
            producto=data.get('producto', ''),
            portes=data.get('portes', ''),
            reembolso=data.get('reembolso', ''),
            entrSabado=data.get('entrSabado', ''),
            seguro=data.get('seguro', ''),
            numEnvioVuelta=data.get('numEnvioVuelta', '')
        )

        if response.success:

            numbultos = data.get('numBultos', 0)
            kilos = data.get('kilos', 0)


            correxpress_numenvio = response.datos_resultado
            correxpress_listbultos = response.lista_bultos
            count_bulto = 0


            bultos_ids = acp_correxpress_bultos_obj.search(cr, uid,[('picking_id','=',picking.id)],context=context)

            if bultos_ids:
                # Borramos los bultos si hay para su envio de nuevo
                acp_correxpress_bultos_obj.unlink(cr,uid,bultos_ids, context=context)


            for bulto in correxpress_listbultos:
                count_bulto += 1
                acp_correxpress_bultos_obj.create(cr, uid,{'picking_id':picking.id,
                                                           'numbulto':bulto.orden,
                                                           'kilos':1, #RC
                                                           'codbarras':bulto.codUnico,
                                                           }, context=context)

            if correxpress_numenvio:
                correxpress_fecha_d = datetime.strptime(data.get('fecha', ''), '%d%m%Y')
                correxpress_fecha_c = correxpress_fecha_d.strftime('%Y-%m-%d')
                tracking_ref = correxpress_numenvio[:16]
                super(stock_picking, self).write(cr, uid,picking.id,{'carrier_tracking_ref':tracking_ref,
                                                                     'correxpress_numenvio':correxpress_numenvio,
                                                                     'correxpress_fecha':correxpress_fecha_c,
                                                                     'correxpress_numbultos':data.get('numBultos', ''),
                                                                     'number_of_packages':data.get('numBultos', ''),
                                                                     'correxpress_ref':data.get('ref', ''),
                                                                     'correxpress_refcli':data.get('refCli', ''),
                                                                     'correxpress_kilos':kilos,
                                                                    }, context=context)
                # Envio de Correo al cliente
                self.pool.get('sale.order').write(cr, uid, picking.sale_id.id,{'tracking':'COREXPRESS ' + tracking_ref})
                self.send_correxpress_mail(cr, uid, ids[0],context=None)
                
                # Generacion de Etiqueta
                return self.button_correxpress_etiqueta(cr, uid, ids,context=None)
                
                     
                                                                                
        else:
            mess_id = self.pool.get('acp_wizard.message').create(cr, uid, {'text':response.errors})
            return {'name':_("Information"),
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
                    'res_model': 'acp_wizard.message',
                    'res_id': mess_id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                    }



    def button_correxpress_etiqueta(self, cr, uid, ids, context=None):
        picking = self.browse(cr,uid,ids[0], context=context)
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr,uid,picking.company_id.id)
        attach_obj = self.pool.get('ir.attachment')        
        acp_correxpress_bultos_obj = self.pool.get('acp_correxpress.picking_bultos')
        bultos_ids = acp_correxpress_bultos_obj.search(cr, uid,[('picking_id','=',picking.id)],context=context)
        data = ''
        label = ''
        correxpress_label = acp_correxpress_label()
        
        attach_ids = attach_obj.search(cr, uid, [('res_model','=','stock.picking'),('res_id','=',picking.id),('name','like','correosexpress-')], context=context)
        if attach_ids:
            attach_obj.unlink(cr, uid, attach_ids, context=context)        
        
        if company.correxpress_printer == 'pdf':
            merger = PdfFileMerger() 
            for bulto in acp_correxpress_bultos_obj.browse(cr, uid, bultos_ids, context=context):
                if bulto.codbarras:
                    data = self.pool.get('stock.picking').get_data(cr, uid, ids, bulto.id,context=context)
                    out_filename = self.pool.get('stock.picking').adjunta_etiqueta_pdf(cr, uid, ids, data, bulto.codbarras, context=context)
                    merger.append(PdfFileReader(file(out_filename, 'rb')))
            nombre_pdf = 'correosexpress-'+picking.carrier_tracking_ref+'-label.pdf'                      
            ruta_pdf = tempfile.gettempdir() +'/'+  nombre_pdf
            merger.write( ruta_pdf)
            files = open(ruta_pdf,'rb').read().encode('base64')
            ir_values={'name':nombre_pdf,
                       'datas_fname': nombre_pdf,
                       'type':'binary',
                       'datas':files,
                       'create_uid':uid,
                       'res_model':'stock.picking',
                       'res_id':ids[0],
                       }
            attach_id = self.pool.get('ir.attachment').create(cr,uid,ir_values,context=context)         
        else:
            for bulto in acp_correxpress_bultos_obj.browse(cr, uid, bultos_ids, context=context):
                if bulto.codbarras:
                    data = self.pool.get('stock.picking').get_data(cr, uid, ids, bulto.id,context=context)
                    self.pool.get('stock.picking').adjunta_etiqueta_txt(cr, uid, ids, data, bulto.codbarras, company.correxpress_printer, context=context)
       

        #~ if bultos_ids:
            #~ for bulto in acp_correxpress_bultos_obj.browse(cr, uid, bultos_ids, context=context):
#~ 
                #~ if bulto.codbarras:
                    #~ data = self.pool.get('stock.picking').get_data(cr, uid, ids, bulto.id,context=context)
#~ 
                    #~ if company.correxpress_printer == 'pdf':
                        #~ self.pool.get('stock.picking').adjunta_etiqueta_pdf(cr, uid, ids, data, bulto.codbarras, context=context)
                    #~ else:
                        #~ self.pool.get('stock.picking').adjunta_etiqueta_txt(cr, uid, ids, data, bulto.codbarras, company.correxpress_printer, context=context)
                        
        # Muestra etiqueta en pantalla
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url',default=False,context=context)
        url = ''
        attach_ids = attach_obj.search(cr, uid, [('res_model','=','stock.picking'),('res_id','=',picking.id),('name','like','correosexpress-')], context=context)
        for attach in attach_obj.browse(cr,uid,attach_ids, context=context):
            url = base_url + "/atth?id=" + str(attach.id)
            
        return {'name'     : 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type'     : 'ir.actions.act_url',
                'tag'      : 'new',
                'url'      : url
               }                                       


    def adjunta_etiqueta_txt(self, cr, uid, ids,  data, codbarras, plantilla,context=None):
        attach_obj = self.pool.get('ir.attachment')
        label=''
        #obtiene etiqueta en zebra

        correxpress_label = acp_correxpress_label()
        if plantilla == 'zpl':
            label = correxpress_label.zpl(data)

        if plantilla == 'tec':
            label = correxpress_label.tec(data)

        if plantilla == 'citoh':
            label = correxpress_label.citoh(data)

        if plantilla == 'etl':
            label = correxpress_label.etl(data)

        if label:
            prefix =  'correosexpress-%s-label.' % codbarras[:17]
            fd, out_filename = tempfile.mkstemp(suffix=".txt",prefix=prefix)

            with open(out_filename,"wb") as f:
                f.write(label)
            os.close(fd)

            files = open(out_filename,'rb').read().encode('base64')
            ir_values={'name':prefix + 'txt',
                       'datas_fname': prefix+ 'txt',
                       'type':'binary',
                       'datas':files,
                       'create_uid':uid,
                       'res_model':'stock.picking',
                       'res_id':ids[0],
                       }

            attach_id = self.pool.get('ir.attachment').create(cr,uid,ir_values,context=context)
        else:
            raise osv.except_osv(
                        _('Error Etiqueta'),
                        _('No esta configurada la plantilla'))
        return True

    def adjunta_etiqueta_pdf(self, cr, uid, ids,  data, codbarras, context=None):
        attach_obj = self.pool.get('ir.attachment')
        zpl_pdf_label = ''
        #obtiene etiqueta en zebra en pdf

        correxpress_label = acp_correxpress_label()
        label = correxpress_label.zpl(data)
        
        zpl_label = ZPLlabel()
        zpl_pdf_label = zpl_label.connect(label)
        print zpl_pdf_label        

        prefix =  'correosexpress-%s-label.' % codbarras[:17]
        fd, out_filename = tempfile.mkstemp(suffix=".pdf",prefix=prefix)

        with open(out_filename,"wb") as f:
            f.write(zpl_pdf_label)
        os.close(fd)

        return out_filename
        
    def destino (self, cr, uid, ids, context=None):
        destino = {
            '010': 'VITORIA 010',
            '020': 'ALBACETE 020',
            '030': 'ALICANTE 030',
            '040': 'ALMERIA 040',
            '061': 'MERIDA 061',
            '070': 'PALMA DE MALLORCA 070',
            '072': 'MENORCA 072',
            '080': 'BARCELONA 080',
            '090': 'BURGOS 090',
            '100': 'CACERES 100',
            '111': 'JEREZ DE LA FRONTERA 111',
            '112': 'ALGECIRAS 112',
            '120': 'CASTELLON 120',
            '130': 'CIUDAD REAL 130',
            '140': 'CORDOBA 140',
            '150': 'LA CORUÑA 150',
            '151': 'SANTIAGO DE COMPOSTELA 151',
            '160': 'CUENCA 160',
            '170': 'GERONA 170',
            '180': 'GRANADA 180',
            '200': 'SAN SEBASTIAN 200',
            '210': 'HUELVA 210',
            '220': 'HUESCA 220',
            '230': 'JAEN 230',
            '240': 'LEON 240',
            '250': 'LERIDA 250',
            '260': 'LOGROÑO 260',
            '270': 'LUGO 270',
            '280': 'MADRID 280',
            '281': 'COSLADA 281',
            '290': 'MALAGA 290',
            '300': 'MURCIA 300',
            '310': 'PAMPLONA 310',
            '320': 'ORENSE 320',
            '330': 'OVIEDO 330',
            '340': 'PALENCIA 340',
            '350': 'LAS PALMAS 350',
            '361': 'VIGO 361',
            '380': 'TENERIFE 380',
            '390': 'SANTANDER 390',
            '400': 'SEGOVIA 400',
            '410': 'SEVILLA 410',
            '420': 'SORIA 420',
            '430': 'TARRAGONA 430',
            '450': 'TOLEDO 450',
            '460': 'VALENCIA 460',
            '470': 'VALLADOLID 470',
            '480': 'BILBAO 480',
            '491': 'ZAMORA 491',
            '500': 'ZARAGOZA 500',
        }
        return destino  
    def create(self, cr, uid, vals, context=None):

        #Actualiza los datos de correoexpress al crear el albaran
        if 'origin' in vals:
          carrier_obj = self.pool.get('delivery.carrier')
          sale_line_obj = self.pool.get('sale.order.line')
          mrw_carrier_id = False
          mrw_carrier_ids = carrier_obj.search(cr, uid,[('name','=','CORREOSEXPRESS')], context=context,limit=1)

          if len(mrw_carrier_ids) > 0:
              mrw_carrier_id = carrier_obj.browse(cr,uid,mrw_carrier_ids[0]).id
          sale_line_ids = sale_line_obj.search(cr, uid,[('order_id.name','=',vals['origin']),('product_id.name','=','Shipping'),('name','ilike','Correos Express')], context=context)
          for sale_line in sale_line_obj.browse(cr,uid,sale_line_ids):

            if mrw_carrier_id:
                vals['carrier_id'] = mrw_carrier_id
                
                if sale_line.order_id.payment_mode_id.name == 'CONTRA REEMBOLSO':
                  vals['correxpress_reembolso'] = str(sale_line.order_id.amount_total)                
                
            prod = False    
            
            sale_line_ids24 = sale_line_obj.search(cr, uid,[('id','=',sale_line.id),('name','ilike','24H')], context=context)
            if len(sale_line_ids24) > 0:
                prod = 'PAQ24'
                print 'encontrato PAQ72 1'            
            sale_line_ids72 = sale_line_obj.search(cr, uid,[('id','=',sale_line.id),('name','ilike','24H a 72H')], context=context)
            if len(sale_line_ids72) > 0:
                prod = 'PAQ72'
                print 'encontrato PAQ72 1'
                
            sale_line_ids72 = sale_line_obj.search(cr, uid,[('id','=',sale_line.id),('name','ilike','max. 72H')], context=context)
            if len(sale_line_ids72) > 0:
                prod = 'PAQ72'
                print 'encontrato PAQ72 2'
                
            sale_line_ids48 = sale_line_obj.search(cr, uid,[('id','=',sale_line.id),('name','ilike','24H a 48H')], context=context)
            if len(sale_line_ids48) > 0:
                prod = 'PAQ48'
                print 'encontrato PAQ48 1'
                
            sale_line_ids48 = sale_line_obj.search(cr, uid,[('id','=',sale_line.id),('name','ilike','24H-48H')], context=context)    
            if len(sale_line_ids48) > 0:
                prod = 'PAQ48'
                print 'encontrato PAQ48 3'
                
            sale_line_ids48 = sale_line_obj.search(cr, uid,[('id','=',sale_line.id),('name','ilike','max. 48H')], context=context)    
            if len(sale_line_ids48) > 0:
                prod = 'PAQ48'
                print 'encontrato PAQ48 2'
                
            sale_line_idsae = sale_line_obj.search(cr, uid,[('id','=',sale_line.id),('name','ilike','Canarias aereo')], context=context)        
            if len(sale_line_idsae) > 0:
                prod = 'CANA'            
                print 'encontrato  1'    
            if prod:    
                ir_model_data = self.pool.get('ir.model.data')
                try:
                    prod_id = ir_model_data.get_object_reference(cr, uid, 'acp_correosexpress', prod)[1]
                except ValueError:
                    prod_id = False
                vals['correxpress_producto'] = prod_id

                

        return super(stock_picking, self).create(cr, uid, vals, context=context)



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

