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

from openerp.osv import fields, osv
from correosexpress.service import CORREOSEXPRESService

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'correxpress_username':fields.char('Usuario', size=64),
        'correxpress_password':fields.char('Contraseña', size=64),
        'correxpress_code':fields.char('Codigo', size=64),
        'correxpress_status':fields.char('Estado conexión',readonly=True, size=255),
        'correxpress_debug':fields.boolean('Test'),   
        'correxpress_carrier_id':fields.many2one('delivery.carrier','Transportista para Correos Express'),
        'correxpress_printer':fields.selection([('pdf', 'Salida PDF'),
												('zpl', 'Zebra'),
												('tec', 'Toshiba Tec'),
												('citoh', 'C.ITOH'),
												('etl', 'Epson'),
												], 'Impresora Etiquetas'),
    }
    
    _defaults ={
        'correxpress_debug':lambda *a: 1,   
    }   
    
    def correxpress_test_connection(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids[0])
        username = obj.correxpress_username or False
        password = obj.correxpress_password or False
        code = obj.correxpress_code or False
        debug = obj.correxpress_debug 


        correos_api = CORREOSEXPRESService(username, password, code, debug)
        status = correos_api.test_connection()
        if status['error']:
            self.write(cr, uid, ids[0],{'correxpress_status':status['error']})
        else:
            self.write(cr, uid, ids[0],{'correxpress_status':'Conexión Correcta'})
        return True  


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
