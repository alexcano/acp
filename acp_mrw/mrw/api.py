#This file is part of mrw. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from utils import mrw_url
from xml.dom.minidom import parseString
import urllib2
import os
import datetime
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class API(object):
    """
    Generic API to connect to mrw
    """
    __slots__ = (
        'url',
        'username',
        'password',
        'franchise',
        'subscriber',
        'department',
    )

    def __init__(self, username, password, franchise, subscriber, department, debug=False):
        """
        This is the Base API class which other APIs have to subclass. By
        default the inherited classes also get the properties of this
        class which will allow the use of the API with the `with` statement

        Example usage ::

            from mrw.api import API

            with API(username, password, franchise, subscriber, department) as mrw_api:
                return mrw_api.test_connection()

        :param username: API username of the Seur Web Services.
        :param password: API password of the Seur Web Services.
        :param franchise: Code franchise (franquicia)
        :param subscriber: Code subscriber (abonado)
        :param department: Code departament
        """
        self.url = mrw_url(debug)
        self.username = username
        self.password = password
        self.franchise = franchise
        self.subscriber = subscriber
        self.department = department

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return self

    def connect(self, xml):
        """
        Connect to the Webservices and return XML data from mrw

        :param xml: XML data.
        
        Return XML object
        """
        headers = {
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'Content-Type': 'text/xml; charset=utf-8',
            'Content-Length': len(xml),
            }
        print "<<<<<<<<<<<<<<<<<<  self.url: " ,self.url
        print "<<<<<<<<<<<<<<<<<<  xml: " ,xml
        print "<<<<<<<<<<<<<<<<<<  headers: " ,headers
        request = urllib2.Request(self.url, xml, headers)
        print "<<<<<<<<<<<<<<<<<<  request: " ,request
        response = urllib2.urlopen(request)
        return response.read()

    def test_connection(self):
        """
        Test connection to MRW webservices
        Send XML to MRW label method and wrong reference.
        Return error connection message
        """
        tmpl = loader.load('picking_label.xml')

        vals = {
            'username': self.username,
            'password': self.password,
            'franchise': self.franchise,
            'subscriber': self.subscriber,
            'department': self.department,
            'numero': 'xxxxxxxx', #  wrong reference
            'separador_numero': '',
            'inicio_fecha': datetime.date.today().strftime("%d/%m/%Y"),
            'fin_envio': (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d/%m/%Y"),
            'etiqueta_envio': '0',
            'top_margin': '10',
            'left_margin': '10',
            }
        xml = tmpl.generate(**vals).render()
        result = self.connect(xml)
        print "<<<<<<<<  Result: ", result
        dom = parseString(result)

        #Get message connection
        #username and password wrong, get error message
        message = dom.getElementsByTagName('Mensaje')
        if message:
            msg = message[0].firstChild
            if msg:
                return message[0].firstChild.data
            return 'Connection API MRW successfully'
        return 'Error. Not get message info'
