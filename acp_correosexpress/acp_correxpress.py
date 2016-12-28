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


class acp_correxpress_product(osv.osv):
    _name = "acp_correxpress.product"

    _columns = {
        'name': fields.char('Denominación', size=60),
        'codigo': fields.char('Codigo', size=2),
        'sigla': fields.char('Sigla', size=30),
        'cod_porte_pagado': fields.char('Codigo Portes Pagados', size=30),
        'cod_porte_debido': fields.char('Codigo Portes Debidos', size=30),
        }

class acp_correxpress_picking_bultos(osv.osv):
    _name = "acp_correxpress.picking_bultos"

    _columns = {
        'picking_id':fields.many2one('stock.picking','Albaran'),
        'numbulto': fields.integer('Numero Bulto'),
        'referencia': fields.char('Referencia', size=30),
        'descripcion': fields.char('Descripcion', size=30),
        'observaciones': fields.char('Observaciones', size=50),
        'kilos': fields.float('Kilos'),
        'volumen': fields.float('Volumen'),
        'alto': fields.float('Alto'),
        'largo': fields.float('Largo'),
        'ancho': fields.float('Ancho'),
        'codbarras': fields.char('Codigo Barras',),
        }

