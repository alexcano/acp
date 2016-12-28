import urllib2, httplib, socket
from suds.client import Client
from suds.transport.http import HttpTransport, Reply, TransportError
from suds.wsse import Security, UsernameToken
from suds.xsd.doctor import ImportDoctor, Import
from resources.response import CORREOSEXPRESShipmentResponse
import md5
import os
import sys

#~ Para obtener el certificado en fichero:
#~ Extract the key => openssl.exe pkcs12 -nocerts -in ClientCert.p12 -out key.pem
#~ Extract the certificate => openssl.exe pkcs12 -clcerts -nokeys -in ClientCert.p12 -out cert.pem<br>  
#~ You may also want to remove the passphrase from the key => openssl.exe rsa -in key.pem -out key_nopass.pem


# VER https://code.google.com/p/pysimplesoap/wiki/SoapClient

        
class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    def __init__(self, key, cert):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        #Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=900):
        return httplib.HTTPSConnection(host,
                                       key_file=self.key,
                                       cert_file=self.cert)

class HTTPSClientCertTransport(HttpTransport):
    def __init__(self, key, cert, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert

    def u2open(self, u2request):
        """
        Open a connection.
        @param u2request: A urllib2 request.
        @type u2request: urllib2.Requet.
        @return: The opened file-like urllib2 object.
        @rtype: fp
        """
        tm = self.options.timeout
        url = urllib2.build_opener(HTTPSClientAuthHandler(self.key, self.cert))
        if self.u2ver() < 2.6:
            socket.setdefaulttimeout(tm)
            return url.open(u2request)
        else:
            return url.open(u2request, timeout=tm)        
        
class CORREOSEXPRESService:
    """
    Main class with static data and the main shipping methods.
    """
    #connection_test_url = 'https://www.correosexpress.com/wsp/services/ConectividadChrono?wsdl'
    connection_test_url = 'https://www.correosexpress.com/wp/services/ConectividadChrono?wsdl'
    delivery_test_url = 'https://www.correosexpress.com/wsp/services/GrabacionEnvio?wsdl'
    delivery_url = 'https://www.correosexpress.com/wp/services/GrabacionEnvio?wsdl'
    seguimiento_test_url = 'https://www.correosexpress.com/wsp/services/SeguimientoEnvio?wsdl'
    seguimiento_url = 'https://www.correosexpress.com/wp/services/SeguimientoEnvio?wsdl'    




    def __init__(self, username, password, code, test_mode=False):
        self.username = username
        self.password = None
        self.code = code
        self.test_mode = test_mode        
        self.module_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        self.key = self.module_path+'/auth/userkey_nopass.pem'
        self.cert = self.module_path+'/auth/usercert.pem'  
 
        
    def test_connection(self):   
        connect_client = Client('https://www.correosexpress.com/wp/services/ConectividadChrono?wsdl',transport = HTTPSClientCertTransport(self.key,self.cert))        
        result_code, reply = connect_client.service.conectividadChrono(self.username,self.password)               
        return True
        
    def grabarenvio(self, canalEntrada, numEnvio, ref, refCli, fecha, codRte, nomRte, nifRte, dirRte,
        pobRte, codPosNacRte, paisISORte, codPosIntRte, contacRte, telefRte, emailRte, codDest, nomDest, nifDest, dirDest, pobDest, codPosNacDest, paisISODest, codPosIntDest,
        contacDest, telefDest, emailDest, contacOtrs, telefOtrs, emailOtrs, observac, numBultos, kilos, volumen, alto, largo, ancho, producto, portes, reembolso, entrSabado, seguro,
        numEnvioVuelta) :  
        print "ruta: ",os.getcwd() 
        print "ruta1: ",os.path.realpath(__file__)
        print "ruta2: ",os.path.dirname(os.path.realpath(__file__))
        print "ruta3: ",os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        print "modulo_path: ",self.module_path
        print "self.key: ",self.key
        print "self.cert: ",self.cert
        if self.test_mode:
            url = self.delivery_test_url
        else:
            url = self.delivery_url

           
        connect_client = Client(url,transport = HTTPSClientCertTransport(self.key,self.cert))    

        

        counter = 1
        listaBultos =  ()
        for bulto in range(numBultos):
            crBultos = connect_client.factory.create('ns0:Bulto')
            crBultos.codUnico = None
            crBultos.orden= counter
            crBultos.codBultoCli = None
            crBultos.referencia=refCli
            crBultos.descripcion=None
            crBultos.observaciones=None
            crBultos.kilos=1
            crBultos.volumen=0
            crBultos.alto=0
            crBultos.largo=0
            crBultos.ancho=0   
            
            listaBultos += (crBultos,)
            counter += 1
                          
        result = connect_client.service.grabarEnvio(self.username,canalEntrada,numEnvio,ref,refCli,fecha,codRte,nomRte,nifRte,dirRte,
        pobRte,codPosNacRte,paisISORte,codPosIntRte,contacRte,telefRte,emailRte,codDest,nomDest,nifDest,dirDest,pobDest,codPosNacDest,paisISODest,codPosIntDest,
        contacDest,telefDest,emailDest,contacOtrs,telefOtrs,emailOtrs,observac,numBultos,kilos,volumen,alto,largo,ancho,producto,portes,reembolso,entrSabado,seguro,
        numEnvioVuelta,listaBultos,self.password)  

        
        try:
            codigo_retorno = result.codigoRetorno
            mensaje_retorno =result.mensajeRetorno
            datos_resultado = result.datosResultado
            listaBultosRes = result.listaBultos
            resultado = result.resultado
            
            if codigo_retorno == 0:
                response = CORREOSEXPRESShipmentResponse(
                    success=True,
                    codigo_retorno = codigo_retorno,
                    datos_resultado=datos_resultado,
                    resultado=resultado,
                    lista_bultos=listaBultosRes
                )  
            else: 
               response = CORREOSEXPRESShipmentResponse(
                    success=False,
                    codigo_retorno = codigo_retorno,
                    errors=result.mensajeRetorno
                )                       
        except AttributeError: 
            try:
                response = CORREOSEXPRESShipmentResponse(
                    success=False,
                    codigo_retorno = result.codigoRetorno,
                    errors=result.mensajeRetorno
                )
            except AttributeError: 
                response = CORREOSEXPRESShipmentResponse(
                    success=False,
                    errors='No hay Notificacion'
                )                                               
                              
        return response 
        
    def seguimientoenvio(self,dato) :   
        print "<<<<<<<<<<< SEGUIMIENTO ENVIO"
        if self.test_mode:
            url = self.seguimiento_test_url
        else:
            url = self.seguimiento_url
        print url
           
        connect_client = Client(url,transport = HTTPSClientCertTransport(self.key,self.cert))    
        print connect_client
        print self.username,dato,self.password
        result = connect_client.service.seguimientoEnvio(self.username,dato,self.password) 
        print result         
                                       
                              
        return True           
     
                         
        
 
                    

