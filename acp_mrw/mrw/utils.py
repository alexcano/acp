#This file is part of mrw. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

def mrw_url(debug=False):
    """
    MRW URL connection

    :param debug: If set to true, use Envialia test URL
    """
    if debug:
        return 'http://sagec-test.mrw.es/MRWEnvio.asmx'
    else:
        return 'https://sagec.mrw.es/MRWEnvio.asmx'
        
def services():
    services = {
        '0000': 'Urgente 10',
        '0005': 'Urgente Hoy',
        '0010': 'Promociones',
        '0100': 'Urgente 12',
        '0110': 'Urgente 14',
        '0120': 'Urgente 22',
        '0200': 'Urgente 19',
        '0205': 'Urgente 19 Expedicion',
        '0210': 'Urgente 19 Mas 40 Kilos',
        '0220': '48 Horas Portugal',
        '0230': 'Bag 19',
        '0235': 'Bag 14',
        '0300': 'Economico',
        '0310': 'Economico Mas 40 Kilos',
        '0350': 'Economico Interinsular',
        '0400': 'Express Documentos',
        '0450': 'Express 2 Kilos',
        '0480': 'Caja Express 3 Kilos',
        '0490': 'Documentos 14',
        '0800': 'Ecommerce',
        '0810': 'Ecommerce Canje',
    }
    return services
