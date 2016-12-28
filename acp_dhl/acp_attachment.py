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

import urllib
from openerp.osv import fields, osv
from openerp import http, SUPERUSER_ID
from openerp.tools.translate import _
from openerp import tools
import urllib2
import requests
import base64


class download_atth(http.Controller):


    @http.route(['/atth',], type='http', auth='none')
    def get_attachment(self, **post):
        print '<<<<<<<<<<<<<<<<<<  post'
        print post
        if post.get('id', False) and http.request.context.get('uid', False):
            ir = http.request.registry['ir.attachment']
            ids = ir.search(http.request.cr, http.request.context.get('uid', False), [('id', '=', post.get('id', False))])
            print 'ids'
            print ids
            atthachment = ir.browse(http.request.cr, http.request.context.get('uid', False), ids[0])
            store = atthachment.store_fname          
            name = atthachment.name
            mimetype = atthachment.file_type
            #data = open('/tmp/dhl-4769328432-label.1VH8an.pdf', 'rb').read()
            full_path = ir._full_path(http.request.cr, http.request.context.get('uid', False), store)
            print "<<<<<<<<<<<<< full_path: ",full_path
            data = open(full_path, 'rb').read()            
            
            return http.request.make_response(data,
                 headers=[
                     ('Content-Disposition', 'filename='+name),
                     ('Content-Type', mimetype),
                     ('Content-Length', len(data))]
                 )
        else:
            return ''
download_atth()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
