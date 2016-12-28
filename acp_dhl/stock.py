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
from datetime import datetime, date, timedelta
from xml.dom.minidom import parseString
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import time
import pytz
from dateutil import tz

from dhl.resources.address import DHLPerson, DHLCompany
from dhl.resources.package import DHLPackage
from dhl.resources.shipment import DHLShipment
from dhl.resources.response import DHLShipmentResponse, DHLPodResponse, DHLTrackingResponse, DHLTrackingEvent
from dhl.service import DHLService
import os.path
import base64
from openerp import tools

# Overloaded stock_picking to manage carriers :
class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_dhl(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context=context):
            carrier_id = pick.carrier_id.id
            dhl_company_id = pick.company_id.dhl_carrier_id.id
            picking_type = pick.picking_type_id.code
            if carrier_id == dhl_company_id and pick.state in ['done','waiting','confirmed','assigned','partially_available'] and picking_type == 'outgoing':
                res[pick.id] = True
            else:
                res[pick.id] = False
        return res

    def get_dhl_pickup_time(self, cr, uid, ids, context=None):
        fecha_pickup_time = ''
        for pick in self.browse(cr, uid, ids, context=context):
            actual_date = date.today().strftime('%Y-%m-%d') + ' 00:00:00'
            actual_datetime = datetime.strptime(actual_date, '%Y-%m-%d %H:%M:%S')
            pickup_minute = pick.dhl_pickup_time * 60
            fecha_pickup_time = actual_datetime + timedelta(minutes=pickup_minute)

        return fecha_pickup_time

    def onchange_carrier_id(self, cr, uid, ids,  carrier_id, company_id, state, context=None):
        if not carrier_id:
            return {'value': {'dhl': False}}

        picking = self.browse(cr,uid,ids[0])
        company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
        picking_type = picking.picking_type_id.code
        if carrier_id == company.dhl_carrier_id.id and state in ['done','waiting','confirmed','assigned','partially_available'] and picking_type == 'outgoing':
            vals = {}
            vals['dhl'] = True
            return {'value': vals}
        else:
            return {'value': {'dhl': False}}


    _columns = {
        'dhl': fields.function(_get_dhl, type='boolean', string='Campos visibles dhl'),
        'dhl_accountnumber_id': fields.many2one('acp_dhl.company', 'Numero Cuenta DHL'),
        'dhl_reference_code': fields.char('Referencia', size=64, help = "Referencia de cliente en el envio"),
        'dhl_drop_off_type': fields.selection([('REGULAR_PICKUP', 'Recogida Regular'),
                                               ('REQUEST_COURIER', 'Recogida Adicional'),], 'Tipo Recogida',
                                               help = "Se utiliza para indicar si se requiere una recogida programada como parte de la consideración de la solicitud"),
        'dhl_ship_datetime': fields.datetime('Fecha Envio', help="Es la fecha/hora cuando el envío estará listo para el envío y ofrecido a la compañía, ya sea como parte de una camioneta programada, recogida regular, dropoff estación, etc. Tenga en cuenta que la marca de tiempo para este evento no representa el momento de la ejecución del servicio, y no debe ser considerada un evento del sistema."),
        'dhl_request_pickup': fields.boolean('Solicitud de Recogida Programada'),
        'dhl_pickup_time': fields.float('Hora de Recogida Programada', help="Identifica la hora de cierre ubicación de recogida"),
        'dhl_service_type': fields.selection([('U', 'Servicio Europa'),
                                               ('P', 'Servicio Internacional'),
                                               ('D', 'Servicio Internacional'),
                                               ('N', 'Servicio Local'),], 'Tipo Servicio',
                                               help="Se corresponde con el código de producto global de DHL, que describe el producto solicitado para este envío. Estos códigos de los productos están disponibles como salida de Tasa de solicitud, y los códigos de los productos proporcionados serán validados contra el origen-destino solicitado en la solicitud de envío."),
        'dhl_currency': fields.char('Moneda', size=64),
        'dhl_unit': fields.selection([('SI', 'Simeta metrico Internacional (KG, CM)'),
                                      ('SU', 'Sistema Medidión (LB, IN)'), ], 'Unidad de Medidas',
                                      help = "Unidades de medida usadas en la operación"),
        'dhl_customs_content': fields.char('Documentos', size=64),
        'dhl_special_pickup_instructions': fields.text('Instrucciones Envio', size=64),
        'dhl_tracking_number': fields.char('Numero Envio', size=64),
        'dhl_identification_number': fields.char('Numero Albaran DHL', size=64),
        'dhl_dispatch_number': fields.char('dispatch_number', size=64),
        'dhl_label': fields.text('Etiqueta'),
    }

    _defaults ={
        'dhl_request_pickup':lambda *a: 0,
        }

    def send_mail_dhl(self, cr, uid, ids, context=None):
        email_template_obj = self.pool.get('email.template')
        template_ids = email_template_obj.search(cr, uid,[('name','=','Enviar Aviso Tracking (DHL)')],context=context)
        print 'ENVI POR EMAIL'
        print template_ids
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

    def button_dhl_envio(self, cr, uid, ids, context=None):
        picking = self.browse(cr,uid,ids[0], context=context)
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr,uid,picking.company_id.id)
        #username = company.dhl_username or False
        username = picking.dhl_accountnumber_id.username or False
        #password = company.dhl_password or False
        password = picking.dhl_accountnumber_id.password or False
        #accountnumber = company.dhl_accountnumber or False
        accountnumber = picking.dhl_accountnumber_id.name or False
        #debug = company.dhl_debug
        debug = picking.dhl_accountnumber_id.debug or False

        #Comprobación de datos
        if picking.carrier_tracking_ref:
            raise osv.except_osv(
                        _('Error Envio DHL'),
                        _('Ya tiene numero de envio'))

        if not picking.weight or picking.weight == 0:
            raise osv.except_osv(
                        _('Error Envio DHL'),
                        _('Falta indicar el peso del envio'))
                        
        if not picking.partner_id.street or not picking.partner_id.city or not picking.partner_id.zip or not picking.partner_id.country_id:
            raise osv.except_osv(
                        _('Error Envio DHL'),
                        _('Falta completar la dirección del cliente, compruebe los datos de calle, ciudad, codigo postal o pais')) 
                                                                                                                   

        if not picking.number_of_packages or picking.number_of_packages == 0:
            bultos = 1
        else:
            bultos = picking.number_of_packages


        service = DHLService(username, password, accountnumber, debug)


        sender = DHLCompany(
                    company_name = company.name,
                    person_name = company.name,
                    street_lines = company.street,
                    city = company.city,
                    postal_code = company.zip,
                    country_code = company.country_id.code,
                    phone = company.phone,
                    email = company.email
                    )
                    
        partner_street = ''
        if picking.partner_id.street2:
            partner_street = picking.partner_id.street + ' ' +  picking.partner_id.street2
        else:
            partner_street = picking.partner_id.street
            
        persona_contacto = ''
        if picking.partner_id.persona_contacto:
            persona_contacto = picking.partner_id.persona_contacto[:45]
        else:
            persona_contacto = picking.partner_id.name[:45]

        if picking.partner_id.is_company:
            receiver = DHLCompany(
                        company_name = picking.partner_id.name[:35],
                        person_name = persona_contacto[:45],
                        street_lines = partner_street[:35],
                        street_lines2 = partner_street[35:70] or None,
                        street_lines3 = partner_street[70:105] or None,
                        city = picking.partner_id.city[:35],
                        postal_code = picking.partner_id.zip[:12],
                        country_code = picking.partner_id.country_id.code[:2],
                        phone = picking.partner_id.phone[:25],
                        email = picking.partner_id.email[:50]
                        )
        else:
            receiver = DHLCompany(
                        company_name = picking.partner_id.parent_id.name[:35],
                        person_name = picking.partner_id.name[:45],
                        street_lines = partner_street[:35],
                        street_lines2 = partner_street[35:70] or None,
                        street_lines3 = partner_street[70:105] or None,
                        city = picking.partner_id.city[:35],
                        postal_code = picking.partner_id.zip[:12],
                        country_code = picking.partner_id.country_id.code[:2],
                        phone = picking.partner_id.phone[:25],
                        email = picking.partner_id.email[:50]
                        )


        packages = []

        for paquete in range(bultos):
            packages.append(
                DHLPackage(
                    weight = 1, # apeticion de RC se pone siempre a 1 , lo normal es:picking.weight,
                    width=0,
                    length=0,
                    height=0,
                    price=0,
                    description = picking.name[:35]
                ))


        shipment = DHLShipment(sender, receiver, packages)

        if picking.opencart_id:
           dhl_reference_code = 'PEDIDO: ' + picking.opencart_id
        else:
           dhl_reference_code = 'PEDIDO: ' + picking.origin

        shipment.reference_code = dhl_reference_code[:35]



        dhl_ship_datetime = datetime.now()
        shipment.ship_datetime = dhl_ship_datetime

        dhl_request_pickup = picking.dhl_request_pickup or False
        shipment.request_pickup = dhl_request_pickup

        if dhl_request_pickup:
            dhl_pickup_time = self.pool.get('stock.picking').get_dhl_pickup_time(cr, uid, ids, context=context)
            if dhl_pickup_time:
                shipment.pickup_time = dhl_pickup_time

        dhl_drop_off_type = shipment.get_drop_off_type()
        shipment.drop_off_type = dhl_ship_datetime

        dhl_service_type = shipment.get_service_type()
        shipment.service_type = dhl_service_type

        dhl_currency = 'EUR'
        shipment.currency = dhl_currency

        dhl_unit = 'SI' #'KG y CM"
        shipment.unit = dhl_unit


        response = service.send(shipment)

        if response.success:
            tracking_number = ''
            if len(response.tracking_numbers) > 1:
                separador = ", "
            else:
                separador = ""
            for tracking in response.tracking_numbers:

                tracking_number += tracking + separador
            identification_number = response.identification_number
            label_bytes = response.label_bytes
            dispatch_number = response.dispatch_number
            super(stock_picking, self).write(cr, uid,picking.id,{'carrier_tracking_ref':identification_number,
                                           'dhl_tracking_number':tracking_number,
                                           'dhl_identification_number':identification_number,
                                           'dhl_label':label_bytes,
                                           'dhl_dispatch_number':dispatch_number,
                                           'dhl_reference_code':dhl_reference_code,
                                           'dhl_ship_datetime':dhl_ship_datetime,
                                           'dhl_drop_off_type':dhl_drop_off_type,
                                           'dhl_service_type':dhl_service_type,
                                           'dhl_currency':dhl_currency,
                                           'dhl_unit':dhl_unit,
                                           'number_of_packages':bultos,
                                            }, context=context)


            if picking.sale_id:
                self.pool.get('sale.order').write(cr, uid, picking.sale_id.id,{'tracking':'DHL ' + identification_number})
                #Email al cliente
                self.send_mail_dhl(cr, uid, ids[0],context=None)
                
            if label_bytes:
                # adjunta la etiqueta al albaran
                return self.pool.get('stock.picking').button_dhl_etiqueta(cr, uid, ids, context=context)                
            else:
                return True
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




    def button_dhl_etiqueta(self, cr, uid, ids, context=None):
        picking = self.browse(cr,uid,ids[0], context=context)
        attach_obj = self.pool.get('ir.attachment')
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url',default=False,context=context)
        url = ''
        if picking.dhl_label:
            attach_ids = attach_obj.search(cr, uid, [('res_model','=','stock.picking'),('res_id','=',picking.id),('name','like','dhl-'+picking.dhl_identification_number )], context=context)

            if attach_ids:
                for attach in attach_obj.browse(cr,uid,attach_ids, context=context):
                    url = base_url + "/atth?id=" + str(attach.id)
            else:
                pdf_decoded = base64.b64decode(picking.dhl_label)
                prefix =  'dhl-%s-label.' % picking.dhl_identification_number
                fd, out_filename = tempfile.mkstemp(suffix=".pdf",prefix=prefix)

                with open(out_filename,"wb") as f:
                    f.write(pdf_decoded)
                with open(out_filename, 'rb') as pdf_file:
                    pdf = pdf_file.read()
                os.close(fd)

                files = open(out_filename,'rb').read().encode('base64')

                ir_values={
                    'name':prefix + 'pdf',
                    'datas_fname': prefix+ 'pdf',
                    'type':'binary',
                    'datas':files,
                    'create_uid':uid,
                    'res_model':'stock.picking',
                    'res_id':ids[0],
                    }

                attach_id = self.pool.get('ir.attachment').create(cr,uid,ir_values,context=context)
                url = base_url + "/atth?id=" + str(attach_id)

            print "<<<<<<<<<<<<<<  url: ",url
            return {'name'     : 'Go to website',
                    'res_model': 'ir.actions.act_url',
                    'type'     : 'ir.actions.act_url',
                    'target'   : 'new',
                    'url'      : url
                   }
        else:
            return True

    def button_dhl_tracking(self, cr, uid, ids, context=None):
        picking = self.browse(cr,uid,ids[0], context=context)
        company_obj = self.pool.get('res.company')
        company = company_obj.browse(cr,uid,picking.company_id.id)
        #username = company.dhl_username or False
        username = picking.dhl_accountnumber_id.username or False
        #password = company.dhl_password or False
        password = picking.dhl_accountnumber_id.password or False
        #accountnumber = company.dhl_accountnumber or False
        accountnumber = picking.dhl_accountnumber_id.name or False
        #debug = company.dhl_debug
        debug = picking.dhl_accountnumber_id.debug or False
        service = DHLService(username, password, accountnumber, debug)
        shipment_awb = picking.dhl_identification_number
        response = service.tracking(shipment_awb)
        if response.success:
            print "<<<<<<<<<<<<<<<<  success: ",response.success
            print "<<<<<<<<<<<<<<<<  shipment_events: ",response.shipment_events
            for shipment in response.shipment_events:
                print "<<<<<<<<<<<<<<<<  code: ",shipment.code, "   location: ",shipment.location_code, "   location: ",shipment.location_description
            print "<<<<<<<<<<<<<<<<  pieces_events: ",response.pieces_events
            for pieces in response.pieces_events:
                print "<<<<<<<<<<<<<<<<  pieces_events: ",pieces
                for pieces2 in pieces[0]:
                    print "<<<<<<<<<<<<<<<<  pieces_events: ",pieces2.date
        else:
            print "<<<<<<<<<<<<<<<<  success: ",response.success
            print "<<<<<<<<<<<<<<<<  errors: ",response.errors

        return True

    def create(self, cr, uid, vals, context=None):

        #Actualiza los datos de DHL al crear el albaran
        if 'origin' in vals:
          carrier_obj = self.pool.get('delivery.carrier')
          sale_line_obj = self.pool.get('sale.order.line')
          mrw_carrier_id = False
          mrw_carrier_ids = carrier_obj.search(cr, uid,[('name','=','DHL')], context=context,limit=1)

          if len(mrw_carrier_ids) > 0:
              mrw_carrier_id = carrier_obj.browse(cr,uid,mrw_carrier_ids[0]).id
          sale_line_ids = sale_line_obj.search(cr, uid,[('order_id.name','=',vals['origin']),('product_id.name','=','Shipping'),('name','ilike','DHL')], context=context)
          for sale_line in sale_line_obj.browse(cr,uid,sale_line_ids):


            if mrw_carrier_id:
                vals['carrier_id'] = mrw_carrier_id

        return super(stock_picking, self).create(cr, uid, vals, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

