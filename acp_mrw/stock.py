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
from mrw.api import API
from mrw.picking import *
from mrw.utils import services
import tempfile
from datetime import datetime
import math
import sys
reload(sys)
sys.setdefaultencoding('iso-8859-1')
from urllib import unquote_plus




# Overloaded stock_picking to manage carriers :
class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def _get_delivery_address(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context=context):
            direccion = pick.partner_id.street
            #if pick.partner_id.street2:
            #    direccion = direccion + ' ' + pick.partner_id.street2
            codigo_postal = pick.partner_id.zip
            poblacion = pick.partner_id.city
            provincia = pick.partner_id.state_id.name
            pais = pick.partner_id.country_id.name
            telefono = pick.partner_id.phone
            contacto = pick.partner_id.persona_contacto

            if field_name == 'delivery_direccion':
                res[pick.id] = direccion

            if field_name == 'delivery_zip':
                res[pick.id] = codigo_postal
                #si el codigo postal es del portugal, solo tomamos los 4 primeros digitos
                if pick.partner_id.country_id: 
                    if pick.partner_id.country_id.code == 'PT' and codigo_postal:
                        res[pick.id] = codigo_postal[:4]

            if field_name == 'delivery_poblacion':
                res[pick.id] = poblacion

            if field_name == 'delivery_provincia':
                res[pick.id] = provincia

            if field_name == 'delivery_pais':
                res[pick.id] = pais

            if field_name == 'delivery_telefono':
                res[pick.id] = telefono

            if field_name == 'delivery_contacto':
                res[pick.id] = contacto                                                                                                      

        return res


    _columns = {
        'observaciones': fields.text('Observaciones', help="Estas observaciones apareceran en la etiqueta de envio"),
        'mrw_codigo_servicio': fields.selection([('0000', 'Urgente 10'),
                                   ('0005', 'Urgente Hoy'),
                                   ('0010', 'Promociones'),
                                   ('0100', 'Urgente 12'),
                                   ('0110', 'Urgente 14'),
                                   ('0120', 'Urgente 22'),
                                   ('0200', 'Urgente 19'),
                                   ('0205', 'Urgente 19 Expedicion'),
                                   ('0210', 'Urgente 19 Mas 40 Kilos'),
                                   ('0220', 'Urgente 19 Portugal'),
                                   ('0230', 'Bag 19'),
                                   ('0235', 'Bag 14'),
                                   ('0300', 'Economico'),
                                   ('0310', 'Economico Mas 40 Kilos'),
                                   ('0350', 'Economico Interinsular'),
                                   ('0400', 'Express Documentos'),
                                   ('0450', 'Express 2 Kilos'),
                                   ('0480', 'Caja Express 3 Kilos'),
                                   ('0490', 'Documentos 14'),
                                   ('0800', 'Ecommerce'),
                                   ('0810', 'Ecommerce Canje'),
                                   ], 'Código Servicio'),       
        'mrw_fecha_recogida': fields.datetime('Date', help='Fecha de recogida, por defecto pasara la fecha actual'),
        'mrw_reembolso': fields.selection([('N', 'Sin reembolso'),
                                   ('O', 'Con reembolso comisión en origen'),
                                   ('D', 'Con reembolso comisión en destino'),
                                   ], 'Reembolso', help='Indica el parametro a pasar a mrw segun el modo de pago del pedido'),
        'mrw_importe_reembolso': fields.float('Importe Reembolso',digits_compute=dp.get_precision('Totales RC'), help='Importe del pedido cuando el modo de pago es contra-reembolso'),
        'delivery_direccion': fields.function(_get_delivery_address, type='char', string='Direccion Entrega', help='Direccion del Cliente de Entrega'),
        'delivery_zip': fields.function(_get_delivery_address, type='char', string='Codigo Postal Entrega', help='Codigo Postal del Cliente de Entrega'),
        'delivery_poblacion': fields.function(_get_delivery_address, type='char', string='Población Entrega', help='Población del Cliente de Entrega'),
        'delivery_provincia': fields.function(_get_delivery_address, type='char', string='Provincia Entrega', help='Provincia del Cliente de Entrega'),
        'delivery_pais': fields.function(_get_delivery_address, type='char', string='Pais Entrega', help='Pais del Cliente de Entrega'),
        'delivery_telefono': fields.function(_get_delivery_address, type='char', string='Telefono Entrega', help='Telefono del Cliente de Entrega'),
        'delivery_contacto': fields.function(_get_delivery_address, type='char', string='Contacto Entrega', help='Persona de contacto del Cliente de Entrega'),
        'carrier_error': fields.char('Resultado solicitud',readonly=True, size=255),
        'mrw_enfranquicia': fields.boolean('Entrega en Franquicia'),
        'mrw_entregasabado': fields.selection([('N', 'No'),
                                   ('S', 'Si'),                                 
                                   ], 'Entrega en Sabado'),     

        }

    _defaults ={
        'codigo_servicio': '0800',
      'mrw_enfranquicia': lambda *a: 0,
      'mrw_entregasabado': 'N',
        }

    def create(self, cr, uid, vals, context=None):

        #Actualiza los datos de MRW al crear el albaran
        if 'origin' in vals:      
          carrier_obj = self.pool.get('delivery.carrier')
          sale_line_obj = self.pool.get('sale.order.line')          
          mrw_carrier_id = False
          mrw_carrier_ids = carrier_obj.search(cr, uid,[('name','=','MRW')], context=context,limit=1)
          
          if len(mrw_carrier_ids) > 0:
              mrw_carrier_id = carrier_obj.browse(cr,uid,mrw_carrier_ids[0]).id
          sale_line_ids = sale_line_obj.search(cr, uid,[('order_id.name','=',vals['origin']),('product_id.name','=','Shipping'),('name','ilike','MRW')], context=context)
          for sale_line in sale_line_obj.browse(cr,uid,sale_line_ids):
            mrw_entregasabado = 'N'
            mrw_reembolso = 'N'
            mrw_importe_reembolso = ''
            mrw_codigo_servicio = '0800' 
            
            mrw_shipping_desc = sale_line.name.upper()
            if ( ( mrw_shipping_desc.find('SABADO') == -1) & (mrw_shipping_desc.find('SATURDAY') == -1)):
              mrw_entregasabado = 'N'
            else:
              mrw_entregasabado = 'S'

            if sale_line.order_id.payment_mode_id.name == 'CONTRA REEMBOLSO':
              mrw_reembolso = 'O'
              mrw_importe_reembolso = str(sale_line.order_id.amount_total)
            
            if mrw_carrier_id:
                vals['carrier_id'] = mrw_carrier_id
            vals['mrw_reembolso'] = mrw_reembolso
            vals['mrw_importe_reembolso'] = mrw_importe_reembolso
            vals['mrw_codigo_servicio'] = mrw_codigo_servicio
            vals['mrw_entregasabado'] = mrw_entregasabado

        return super(stock_picking, self).create(cr, uid, vals, context=context)
    '''
    def write(self, cr, uid, ids, vals, context=None):

        #Actualiza los datos de MRW al actualizar el albaran
        deliv =  self.browse(cr, uid, ids, context=context)
        carrier_obj = self.pool.get('delivery.carrier')
        sale_line_obj = self.pool.get('sale.order.line')
        mrw_carrier_id = False
        mrw_carrier_ids = carrier_obj.search(cr, uid,[('name','=','MRW')], context=context,limit=1)
          
        if len(mrw_carrier_ids) > 0:
            mrw_carrier_id = carrier_obj.browse(cr,uid,mrw_carrier_ids[0]).id
 
 



        sale_line_ids = sale_line_obj.search(cr, uid,[('order_id','=',deliv.sale_id.id),('product_id.name','=','Shipping'),('name','ilike','MRW')], context=context)
        for sale_line in sale_line_obj.browse(cr,uid,sale_line_ids):
            mrw_entregasabado =  'N'
            mrw_reembolso = 'N'
            mrw_importe_reembolso = ''
            mrw_codigo_servicio = '0800' 
            
            mrw_shipping_desc = sale_line.name.upper()
            if mrw_shipping_desc.find('SABADO') == -1:
              mrw_entregasabado = 'N'
            else:
              mrw_entregasabado = 'S'

            if sale_line.order_id.payment_mode_id.name == 'CONTRA REEMBOLSO':
              mrw_reembolso = 'O'
              mrw_importe_reembolso = str(sale_line.order_id.amount_total)
            
            if mrw_carrier_id:
                vals['carrier_id'] = mrw_carrier_id
            vals['mrw_reembolso'] = deliv.mrw_reembolso or mrw_reembolso
            vals['mrw_importe_reembolso'] = deliv.mrw_importe_reembolso or mrw_importe_reembolso
            vals['mrw_codigo_servicio'] = deliv.mrw_codigo_servicio or mrw_codigo_servicio 
            vals['mrw_entregasabado'] = mrw_entregasabado or False       

        return super(stock_picking, self).write(cr, uid, ids, vals, context=context)   
    '''
    
    def send_mail_tracking(self, cr, uid, ids, context=None):
        email_template_obj = self.pool.get('email.template')
        template_ids = email_template_obj.search(cr, uid,[('name','=','Enviar Aviso Tracking (MRW)')],context=context)
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



    def button_mrwenvio(self, cr, uid, ids, context=None):
        print 'Comienzo creacion etiqueta MRW'
        carrier_obj = self.pool.get('delivery.carrier')
        deliv = self.browse(cr,uid,ids[0])
        # Recuperamos los datos de transporte de pedidos
        sale_obj = self.pool.get('sale.order')
        sale_line_obj = self.pool.get('sale.order.line')
        carrier_obj = self.pool.get('delivery.carrier')
        reference= False
        mrw_carrier_id = False
        mrw_carrier_ids = carrier_obj.search(cr, uid,[('name','=','MRW')], context=context,limit=1)          
        if len(mrw_carrier_ids) > 0:
            mrw_carrier_id = carrier_obj.browse(cr,uid,mrw_carrier_ids[0]).id
        if not mrw_carrier_id:
            raise osv.except_osv(
                        _('Error Envio MRW'),
                        _('No se encuentra tranportista MRW'))  
     
        if mrw_carrier_id != deliv.carrier_id.id:
            raise osv.except_osv(
                        _('Error Envio MRW'),
                        _('Este albaran no tiene como transportista a MRW'))  

        if deliv.carrier_tracking_ref:
          mess_id = self.pool.get('acp_wizard.message').create(cr, uid, {'text':'El pedido tiene ya generado un numero de tracking'})
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


                                 
        # Buscamos si en las lineas del pedido tiene el articulo shipping con descripcion MRW

        #sale_line_ids = sale_line_obj.search(cr, uid,[('order_id','=',deliv.sale_id.id),('product_id.name','=','Shipping'),('name','ilike','MRW')], context=context)
        #mrw = False

        #for sale_line in sale_line_obj.browse(cr,uid,sale_line_ids):
          #mrw = True

          #mrw_entregasabado = 'N'
          #mrw_reembolso = 'N'
          #mrw_importe_reembolso = ''
          #mrw_codigo_servicio = '0800'

          
          #mrw_shipping_desc = sale_line.name.upper()
          #if mrw_shipping_desc.find('SABADO') == -1:
          #  mrw_entregasabado = 'N'
          #else:
          #  mrw_entregasabado = 'S'

          #if sale_line.order_id.payment_mode_id.name == 'CONTRA REEMBOLSO':
          #  mrw_reembolso = 'O'
          #  mrw_importe_reembolso = str(round(sale_line.order_id.amount_total,2))     

          #self.write(cr, uid, ids[0],{'mrw_reembolso':mrw_reembolso, 'mrw_importe_reembolso':mrw_importe_reembolso,'mrw_codigo_servicio':mrw_codigo_servicio,'mrw_entregasabado':mrw_entregasabado})  

        mrw = True
        if mrw:

          #Valores Obligatorios
          #if deliv.number_of_packages == 0:
          #  raise osv.except_osv(
          #              _('Error Envio MRW'),
          #              _('Es necesario indicar Número de Bultos y Fecha Recogida'))   

          #if not deliv.mrw_fecha_recogida:
          #  raise osv.except_osv(
          #              _('Error Envio MRW'),
          #              _('Es necesario indicar Número de Bultos y Fecha Recogida'))              

          mrw_conf_obj = self.pool.get('acp_mrw.configuracion')
          mrw_conf_ids = mrw_conf_obj.search(cr, uid,[('active','=',True)], context=context)

          if not mrw_conf_ids:
            raise osv.except_osv(
                        _('Error Envio MRW'),
                        _('No están configurados los datos de conexión para MRW'))               

          else:
            mrw_conf = mrw_conf_obj.browse(cr,uid,mrw_conf_ids)
            username = mrw_conf.username or ''
            password = mrw_conf.password or ''
            franchise = mrw_conf.franchise or ''
            subscriber = mrw_conf.subscriber or ''
            department = mrw_conf.department or ''
            debug = mrw_conf.debug
            fecha_c = ''

            if deliv.weight:
              peso = int(math.ceil(deliv.weight))
            else:
              peso = ''            

            if deliv.mrw_fecha_recogida:
                fecha_d = datetime.strptime(deliv.mrw_fecha_recogida, '%Y-%m-%d %H:%M:%S')
                fecha_c = fecha_d.strftime('%d/%m/%Y')
            else:
                fecha_d = datetime.strptime(fields.datetime.now(), '%Y-%m-%d %H:%M:%S')
                fecha_c = fecha_d.strftime('%d/%m/%Y')  
                
            if deliv.number_of_packages == 0:
               bultos = 1
            else:
               bultos = deliv.number_of_packages
                    
            if deliv.mrw_enfranquicia:
              mrw_enfranquicia = 'E'
            else:
              mrw_enfranquicia = 'N'

            mrw_entregasabado = deliv.mrw_entregasabado
            if deliv.opencart_id:
                ref = 'PEDIDO: ' + deliv.opencart_id
            else:
                ref = 'PEDIDO: ' + deliv.origin
                
            importe = str(deliv.mrw_importe_reembolso).replace(".", ",")
            print 'Empiezo a contruir API de Solicitud de Envio'
            #API de Solicitud de Envio
            picking_api = Picking(username, password, franchise, subscriber, department, debug)
            data = {}
            data['via'] = deliv.delivery_direccion and unquote_plus(deliv.delivery_direccion.encode('utf-8','xmlcharrefreplace')) or ''
            data['codigo_postal'] = deliv.delivery_zip or ''
            data['poblacion'] = deliv.delivery_poblacion and unquote_plus(deliv.delivery_poblacion.encode('utf-8','xmlcharrefreplace')) or '' 
            data['provincia'] =  deliv.delivery_provincia and unquote_plus(deliv.delivery_provincia.encode('utf-8','xmlcharrefreplace')) or ''
            data['nif'] = deliv.partner_id.vat or ''
            data['nombre'] = deliv.partner_id.name and unquote_plus(deliv.partner_id.name.encode('utf-8','xmlcharrefreplace')) or ''
            data['telefono'] = deliv.delivery_telefono or ''
            data['contacto'] = deliv.delivery_contacto and unquote_plus(deliv.delivery_contacto.encode('utf-8','xmlcharrefreplace')) or ''
            data['atencion_de'] = deliv.delivery_contacto and unquote_plus(deliv.delivery_contacto.encode('utf-8','xmlcharrefreplace')) or ''
            data['observaciones'] = deliv.observaciones or ''
            data['fecha'] = fecha_c or ''
            data['referencia'] = ref
            data['codigo_servicio'] = deliv.mrw_codigo_servicio
            data['bultos'] = bultos or ''
            data['peso'] = 1 #peso ###lo pasamos siempre a 1Kg
            data['reembolso'] = deliv.mrw_reembolso
            data['importe_reembolso'] = importe
            data['entregasabado'] = deliv.mrw_entregasabado
            data['enfranquicia'] = mrw_enfranquicia
            print 'Llamada a API de Solicitud de Envio'
            reference, error = picking_api.create(data)
            url = ''

            if reference:
                #Actualiza numero de tracking en albaran y pedido
                deliv.write({'carrier_tracking_ref':reference, 'mrw_fecha_recogida':fecha_d,'number_of_packages':bultos})
                # Al actualizar el numero de tracking en pedido, se envia un correo al cliente
                if deliv.sale_id:
                    sale_obj.write(cr, uid, deliv.sale_id.id,{'tracking':'MRW ' + reference})
                #Email al cliente
                self.send_mail_tracking(cr, uid, ids[0],context=None)

                #Obtiene la url para ver la etiqueta
                if debug:
                    url = 'http://sagec-test.mrw.es/Panel.aspx?Franq=%s&Ab=%s&Dep=&Pwd=%s&Usr=%s&NumEnv=%s' %(franchise, subscriber, password, username, reference)
                else:
                    url = 'http://sagec.mrw.es/Panel.aspx?Franq=%s&Ab=%s&Dep=&Pwd=%s&Usr=%s&NumEnv=%s' %(franchise, subscriber, password, username, reference)


            if error:
                self.write(cr, uid, ids[0],{'carrier_error':error})            
                mess_id = self.pool.get('acp_wizard.message').create(cr, uid, {'text':error})
         

        if reference:
          return {'name'     : 'Go to website',
                  'res_model': 'ir.actions.act_url',
                  'type'     : 'ir.actions.act_url',
                  'target'   : 'new',
                  'url'      : url
                 }    
        else:
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



    def button_mrwetiqueta(self, cr, uid, ids, context=None):

        deliv = self.browse(cr,uid,ids[0])
        mrw_conf_obj = self.pool.get('acp_mrw.configuracion')
        mrw_conf_ids = mrw_conf_obj.search(cr, uid,[('active','=',True)], context=context)

        if mrw_conf_ids:
            mrw_conf = mrw_conf_obj.browse(cr,uid,mrw_conf_ids)
            username = mrw_conf.username or ''
            password = mrw_conf.password or ''
            franchise = mrw_conf.franchise or ''
            subscriber = mrw_conf.subscriber or ''
            department = mrw_conf.department or ''
            debug = mrw_conf.debug 
            reference = deliv.carrier_tracking_ref
            

            if debug:
                url = 'http://sagec-test.mrw.es/Panel.aspx?Franq=%s&Ab=%s&Dep=&Pwd=%s&Usr=%s&NumEnv=%s' %(franchise, subscriber, password, username, reference)
            else:
                url = 'http://sagec.mrw.es/Panel.aspx?Franq=%s&Ab=%s&Dep=&Pwd=%s&Usr=%s&NumEnv=%s' %(franchise, subscriber, password, username, reference)


            
            #picking_api = Picking(username, password, franchise, subscriber, department, debug)

            #print "<<<<<<<<<<<<< Get PDF label"
            #if deliv.carrier_tracking_ref:
            #    reference = deliv.carrier_tracking_ref
            #    data = {}
            #    data['numero'] = deliv.carrier_tracking_ref
                #~ data['separador_numero'] = ''
                #~ data['inicio_fecha'] = ''
                #~ data['fin_envio'] = ''
                #~ data['etiqueta_envio'] = ''
                #~ data['top_margin'] = ''
                #~ data['left_margin'] = ''
   

            #    label = picking_api.label(data)
            #    print "<<<<<<<<<<<<<<<<<<<<<  LABEL ",label
            #    if label:
            
            #        prefix =  'mrw-%s-label.' % reference
            #        fd, out_filename = tempfile.mkstemp(suffix=".pdf",prefix=prefix)    

            #        print "<<<<<<<<<<<<<<<<  out_filename: ",out_filename            
            #        print "<<<<<<<<<<<<<<<<  fd: ",fd         
            #        with open(out_filename,"wb") as f:
            #            f.write(label)
            #        os.close(fd)
            #        print "<<<<<<<<<<<<< Generated PDF label in %s" % out_filename

            #        with open(out_filename, 'rb') as pdf_file:
            #            pdf = pdf_file.read()                
            #    
            #    else:
            #        print "<<<<<<<<<<<<< Error get pdf file"
        #return pdf 

        return {'name'     : 'Go to website',
                'res_model': 'ir.actions.act_url',
                'type'     : 'ir.actions.act_url',
                'target'   : 'new',
                'url'      : url
               }               


