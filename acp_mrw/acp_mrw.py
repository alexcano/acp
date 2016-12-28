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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
from decimal import *
import openerp.tools
import datetime
from mrw.api import API
from mrw.picking import *
from mrw.utils import services


class acp_mrw_configuracion(osv.osv):
	_name="acp_mrw.configuracion"


	_columns = {
		'username':fields.char('Usuario', required=True , size=64),
		'password':fields.char('Contraseña', required=True, size=64),
		'franchise':fields.char('Franquicia', required=True, size=64),
		'subscriber':fields.char('Abonado', required=True, size=64),	
		'department':fields.char('Departamento', size=64),		
		'status':fields.char('Estado conexión',readonly=True, size=255),
		'debug':fields.boolean('Test'),
		'active':fields.boolean('Active'),
	}
	_defaults ={
		'active':lambda *a: 1,
		'debug':lambda *a: 1,	

	}

	def test_connection(self, cr, uid, ids, context=None):
		obj = self.browse(cr,uid,ids[0])
		username = obj.username or False
		password = obj.password or False
		franchise = obj.franchise or False
		subscriber = obj.subscriber or False
		department = obj.department or ''
		debug = obj.debug 

		mrw_api = API(username, password, franchise, subscriber, department, debug)
		status = mrw_api.test_connection()
		self.write(cr, uid, ids[0],{'status':status})
		return True



