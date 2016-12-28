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
{
    'name': 'Acp DHL',
    'sequence': 1,
    'summary': '',
    'version': '1.0',
    'category': 'Sales Management',
    'description': """

Generación de Envios y Etiquetas de DHL
===========================================================

En configuración de mensajeria DHL de la compañia, debera indicar los datos de conexión de DHL.

Cuando el albaran tenga como transportista al indicado en configuración de mensajeria DHL, se activarán los botones de Envio DHL y Etiqueta DHL.
Cuando se realice el envio, adjuntará al albaran la etiqueta y enviará un correo al cliente indicando el envio

    """,
    'author': 'InfoAcp',
    'website': 'http://www.infoacp.es',
    'depends': ['sale','sale_stock','delivery','document'],
    'init_xml': [],
    'update_xml': [
        'company_view.xml',
        'stock_view.xml',
        'wizard/acp_wizard_message_view.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
