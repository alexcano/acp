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

from dhl.resources.address import DHLPerson, DHLCompany
from dhl.resources.package import DHLPackage
from dhl.resources.shipment import DHLShipment
from dhl.resources.response import DHLShipmentResponse, DHLPodResponse, DHLTrackingResponse, DHLTrackingEvent
from dhl.service import DHLService

class res_company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'dhl_username':fields.char('Usuario', size=64),
        'dhl_password':fields.char('Contraseña', size=64),
        'dhl_accountnumber':fields.char('Numero de Cuenta', size=64),
        'dhl_status':fields.char('Estado conexión',readonly=True, size=255),
        'dhl_debug':fields.boolean('Test'),
        'dhl_carrier_id':fields.many2one('delivery.carrier','Transportista'),
        'dhl_ids' : fields.one2many('acp_dhl.company', 'company_id', 'DHL'),
    }

    _defaults ={
        'dhl_debug':lambda *a: 1,
    }

    def dhl_test_connection(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids[0])
        username = obj.dhl_username or False
        password = obj.dhl_password or False
        accountnumber = obj.dhl_accountnumber or False
        debug = obj.dhl_debug


        service = DHLService(username, password, accountnumber,debug)
        status = correos_api.test_connection()
        if status['error']:
            self.write(cr, uid, ids[0],{'dhl_status':status['error']})
        else:
            self.write(cr, uid, ids[0],{'dhl_status':'Conexión Correcta'})
        return True

class acp_dhl_company(osv.osv):
    _name = "acp_dhl.company"

    _columns = {
        'company_id': fields.many2one('res.company', 'Compañia', ondelete='cascade'),
        'name':fields.char('Numero de Cuenta', size=64),
        'username':fields.char('Usuario', size=64),
        'password':fields.char('Contraseña', size=64),
        'status':fields.char('Estado conexión',readonly=True, size=255),
        'debug':fields.boolean('Modo Test'),
    }
    _defaults ={
        'debug':lambda *a: 1,
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
