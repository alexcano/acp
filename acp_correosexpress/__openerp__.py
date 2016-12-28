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
    'name': 'Acp CorreosExpress',
    'sequence': 1,
    'summary': '',
    'version': '1.0',
    'category': 'Generic Modules',
    'description': """
Correos Express.
===========================================================
* Compañia: Configuración de la información de Correos Express
* Albaranes: 
	- Comunicacion de envio para los albaranes con transpostista indicado en la configuración de correos express
	- Generación de Etiquetas automaticamente cuando se realiza la solicitud del envio, estas se adjuntarán en el albaran

    """,
    'author': 'InfoAcp',
    'website': 'http://www.infoacp.es',
    'depends': ['sale','sale_stock','delivery','document'],
    'init_xml': [],
    'update_xml': [
        'company_view.xml',
        'stock_view.xml',
        'wizard/acp_wizard_message_view.xml',
        'data.xml',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
