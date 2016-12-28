#This file is part of mrw. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from api import API

from xml.dom.minidom import parseString
import os
import datetime
import base64
import genshi
import genshi.template

loader = genshi.template.TemplateLoader(
    os.path.join(os.path.dirname(__file__), 'template'),
    auto_reload=True)


class Picking(API):
    """
    Picking API
    """
    __slots__ = ()

    def create(self, data):
        """
        Create a MRW shipment using the given data

        :param data: Dictionary of values
        :return: reference (str), error (str)
        """
        reference = None
        error = None

        tmpl = loader.load('picking_send.xml')

        today = datetime.date.today().strftime("%d/%m/%Y")


        vals = {
            'username': self.username,
            'password': self.password,
            'franchise': self.franchise,
            'subscriber': self.subscriber,
            'department': self.department,
            'codigo_direccion': data.get('codigo_direccion', ''),
            'codigo_via': data.get('codigo_via', ''),
            'via': data.get('via', ''),
            'numero': data.get('numero', ''),
            'resto': data.get('resto', ''),
            'codigo_postal': data.get('codigo_postal', ''),
            'poblacion': data.get('poblacion', ''),
            'provincia': data.get('provincia', ''),
            'nif': data.get('nif', ''),
            'nombre': data.get('nombre', ''),
            'telefono': data.get('telefono', ''),
            'contacto': data.get('contacto', ''),
            'atencion_de': data.get('atencion_de', ''),
            'observaciones': data.get('observaciones', ''),
            'fecha': data.get('fecha', today),
            'referencia': data.get('referencia', ''),
            'enfranquicia': data.get('enfranquicia', ''),
            'codigo_servicio': data.get('codigo_servicio', '0300'),
            'bultos': data.get('bultos', '1'),
            'peso': data.get('peso', '1'), # weight is integer value, not float
            'entregasabado': data.get('entregasabado', ''), 
            'reembolso': data.get('reembolso', ''), #O: Origen, D: Destino
            'importe_reembolso': data.get('importe_reembolso', ''),
            }

        xml = tmpl.generate(**vals).render()
        result = self.connect(xml)
        dom = parseString(result)

        print "<<<<<<<<<<<<<<<<<<< result: ", result

        Mensaje = dom.getElementsByTagName('Mensaje')
        if Mensaje and Mensaje[0].firstChild:
            error = Mensaje[0].firstChild.data
            NumeroEnvio = dom.getElementsByTagName('NumeroEnvio')
            if NumeroEnvio[0].firstChild:
                reference = NumeroEnvio[0].firstChild.data                      
        else:
            NumeroEnvio = dom.getElementsByTagName('NumeroEnvio')
            reference = NumeroEnvio[0].firstChild.data

        return reference, error

    def label(self, data):
        """
        Get PDF label from MRW service

        :param data: Dictionary of values
        :return: label (pdf)
        """
        label = None

        tmpl = loader.load('picking_label.xml')

        today = datetime.date.today().strftime("%d/%m/%Y")
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%d/%m/%Y")

        vals = {
            'username': self.username,
            'password': self.password,
            'franchise': self.franchise,
            'subscriber': self.subscriber,
            'department': self.department,
            'numero': data.get('numero', ''),
            'separador_numero': data.get('separador_numero', ''),
            'inicio_fecha': data.get('inicio_fecha', today),
            'fin_envio': data.get('fin_envio', tomorrow),
            'etiqueta_envio': data.get('etiqueta_envio', '0'),
            'top_margin': data.get('top_margin', '10'),
            'left_margin': data.get('left_margin', '10'),
            }

        xml = tmpl.generate(**vals).render()
        result = self.connect(xml)
        dom = parseString(result)

        EtiquetaFile = dom.getElementsByTagName('EtiquetaFile')
        if EtiquetaFile and EtiquetaFile[0].firstChild:
            pdf = EtiquetaFile[0].firstChild.data
            label = base64.b64decode(pdf)
        return label
