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
import time
from openerp.tools.translate import _

#----------------------------------------------------------
# Sale Order
#----------------------------------------------------------
class sale_order(osv.osv):
    _inherit = 'sale.order'

    '''
    def _carrier_tracking_ref(self, cr, uid, ids, field_name, arg, context=None):
        if not ids:
            return {}  
        result = {}
        picking_obj = self.pool.get('stock.picking')

        for order in self.browse(cr, uid, ids, context=context):  
            tracking =''
            for picking in order.picking_ids:
                if picking.carrier_tracking_ref:                    
                    tracking = tracking + ' ' + str(picking.carrier_id.name)+ ' ' +str(picking.carrier_tracking_ref)
        
            result[order.id] = tracking        
        
        return result  

    _columns = {
        'carrier_tracking_ref': fields.function(_carrier_tracking_ref, method=True, string='Tracking',type='char'),   
        }
    ''' 






                







