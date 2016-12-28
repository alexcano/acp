class CORREOSEXPRESResponse:
    def __init__(self, success,codigo_retorno, errors=None):
        self.success = success
        self.errors = errors
        self.codigo_retorno = codigo_retorno

    def __str__(self):
        return '%s' % ('Success' if self.success else 'Fail: '+str(self.errors))


class CORREOSEXPRESShipmentResponse(CORREOSEXPRESResponse):
    def __init__(self, success, datos_resultado=None, lista_bultos=None,
                 resultado=None, errors=None, codigo_retorno=None):
        CORREOSEXPRESResponse.__init__(self, success, codigo_retorno, errors)

        self.datos_resultado = datos_resultado
        self.lista_bultos = lista_bultos
        self.resultado = resultado
