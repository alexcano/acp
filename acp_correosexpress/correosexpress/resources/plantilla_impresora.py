#This file is part of envialia. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.

from datetime import date


class acp_correxpress_label(object):
    """
    CORREOS EXPRESS Plantillas impresoras termicas
    """
    __slots__ = ()

    def zpl(self,data):
        
        if len(data.get('codPosNacDest','' )) <> 0:
            codigo_postal = data.get('codPosNacDest','' )
        else:
            codigo_postal = data.get('codPosIntDest','' )
                    

        plantilla = '^XA\r\n'\
                    '^PR8,8,8\r\n'\
                    '^LH03,0^FS\r\n'\
                    '^LL1583\r\n'\
                    '^MD10\r\n'\
                    '^MNY\r\n'\
                    '^BY4,3.0^FO50,100^BCR,256,N,N,N,A^FR^FD%(CODBARRAS)s^FS\r\n'\
                    '^BY2^FO20,880^CVY^B7N,7,1,6,N^FR^FH_^FD%(PDF417)s^FS\r\n'\
                    '^FO760,90^ADR,17,9^CI10^FR^FD%(CODNOMRTE)s^FS\r\n'\
                    '^FO740,90^ADR,17,9^CI10^FR^FD%(DOMRTE)s^FS\r\n'\
                    '^FO720,90^ADR,17,9^CI10^FR^FD%(POBCPRTE)s^FS\r\n'\
                    '^FO720,460^ADR,17,9^CI10^FR^FDTelf:%(TELRTE)s^FS\r\n'\
                    '^FO665,90^AQR,51,9^CI10^FR^FD%(NOMCONS)s^FS\r\n'\
                    '^FO630,90^ADR,40,9^CI10^FR^FD%(DOMCONS)s^FS\r\n'\
                    '^FO475,90^AQR,130,132^CI10^FR^FD%(CPCONS)s^FS\r\n'\
                    '^FO395,30^AQR,50,9^CI10^FR^FD%(POBCONS)s^FS\r\n'\
                    '^FO445,30^ASR,50,70^CI10^FR^FD%(DESTINO)s^FS\r\n'\
                    '^FO445,30^ASR,50,70^CI10^FR^FD%(PAIS)s^FS\r\n'\
                    '^FO375,30^ADR,17,9^CI10^FR^FDATT: %(CONTACTO)s^FS\r\n'\
                    '^FO355,30^ADR,17,9^CI10^FR^FDTELF.: %(TELCONS)s^FS\r\n'\
                    '^FO713,86^GB0,1200,2^FS\r\n'\
                    '^FO351,16^GB0,640,2^FS\r\n'\
                    '^FO655,656^GB0,700,2^FS\r\n'\
                    '^FO600,656^GB0,700,2^FS\r\n'\
                    '^FO470,656^GB0,700,2^FS\r\n'\
                    '^FO560,670^ADR,40,9^CI10^FR^FDREF: %(REFERENCIA)s^FS\r\n'\
                    '^FO510,670^ADR,40,9^CI10^FR^FDCOD.BULTO:%(CODBARRAS)s^FS\r\n'\
                    '^FO470,670^ADR,40,9^CI10^FR^FDBUL.CLI:%(CODBUL_CLTE)s^FS\r\n'\
                    '^FO600,860^GB113,0,2^FS\r\n'\
                    '^FO600,1020^GB113,0,2^FS\r\n'\
                    '^FO351,655^GB590,0,2^FS\r\n'\
                    '^FO715,770^ADR,17,9^CI10^FR^FDEnvio retorno: %(RETORNO)s^FS\r\n'\
                    '^FO730,700^AQR,61,40^CI10^FR^FDEXP:%(ENVIO)s^FS\r\n'\
                    '^FO635,880^ADR,17,9^CI10^FR^FDPESO:^FS\r\n'\
                    '^FO605,880^AQR,17,9^CI10^FR^FD%(KILOS)s Kgs.^FS\r\n'\
                    '^FO690,880^ADR,17,9^CI10^FR^FDBULTOS:^FS\r\n'\
                    '^FO660,880^AQR,17,9^CI10^FR^FD%(PARCIAL)s de %(BULTOS)s^FS\r\n'\
                    '^FO690,680^ADR,17,9^CI10^FR^FDREEMBOLSO:^FS\r\n'\
                    '^FO635,680^ADR,17,9^CI10^FR^FDTIPO PORTES :^FS\r\n'\
                    '^FO605,680^AQR,17,9^CI10^FR^FD%(SEMPOR)s^FS\r\n'\
                    '^FO660,680^AQR,17,9^CI10^FR^FD%(REEMBOLSO)s^FS\r\n'\
                    '^FO690,1040^ADR,17,9^CI10^FR^FDFECHA:^FS\r\n'\
                    '^FO660,1040^AQR,17,9^CI10^FR^FD%(FECHA)s^FS\r\n'\
                    '^FO410,680^ADR,45,25^CI10^FR^FD%(TSV_ABREVIA)s^FS\r\n'\
                    '^FO600,90^ADR,40,9^CI10^FD%(OBSER1)s^FS\r\n'\
                    '^FO570,90^ADR,40,9^CI10^FD%(OBSER2)s^FS\r\n'\
                    '^FO360,680^ADR,45,25^CI10^FR^FD%(SABADO)s^FS\r\n'\
                    '^PQ1,0,0,N\r\n'\
                    '^XZ' % {
                    'CODBARRAS': data.get('codbarras', ''),
                    'PDF417': '',
                    'CODNOMRTE': data.get('etiq_nomRte', ''),
                    'DOMRTE': data.get('dirRte', ''),
                    'POBCPRTE': data.get('codPosNacRte', ''),
                    'TELRTE': data.get('telefRte', ''),
                    'NOMCONS': data.get('nomDest', ''),
                    'DOMCONS': data.get('dirDest', ''),
                    'CPCONS': codigo_postal,
                    'POBCONS': data.get('pobDest', ''),
                    'DESTINO': data.get('etiq_destino', ''),
                    'PAIS': data.get('etiq_pais', ''),
                    'CONTACTO': data.get('contacDest', ''),
                    'TELCONS': data.get('telefDest', ''),
                    'REFERENCIA': data.get('ref', ''),
                    'CODBUL_CLTE': '',
                    'RETORNO': data.get('numEnvioVuelta', ''),
                    'ENVIO': data.get('numenvio', ''),
                    'KILOS': data.get('kilos', ''),
                    'PARCIAL': data.get('etiq_bulto', ''),
                    'BULTOS': data.get('numBultos', ''),
                    'SEMPOR': data.get('etiq_portes', ''),
                    'REEMBOLSO': data.get('etiq_reembolso', ''),
                    'FECHA': data.get('etiq_fecha', ''),
                    'TSV_ABREVIA': data.get('etiq_tsv_abrevia', ''),
                    'OBSER1': data.get('observac', ''),
                    'OBSER2': data.get('observac_bulto', ''),
                    'SABADO': data.get('etiq_entrSabado', ''),

                     }
        return plantilla

    def tec(self,data):
        
        if len(data.get('codPosNacDest','' )) <> 0:
            codigo_postal = data.get('codPosNacDest','' )
        else:
            codigo_postal = data.get('codPosIntDest','' )
                    
        plantilla = '{D1480,1020,1480|}\r\n'\
                    '{AX;+000,+000,+00|}\r\n'\
                    '{AY;+00,1|}\r\n'\
                    '{C|}\r\n'\
                    '{PV00;0965,0021,0020,0020,B,11,B,P1|}\r\n'\
                    '{RV00;%(CODNOMRTE)s|}\r\n'\
                    '{PV01;0945,0021,0020,0020,B,11,B,P1|}\r\n'\
                    '{RV01;%(DOMRTE)s|}\r\n'\
                    '{PV02;0925,0021,0020,0020,B,11,B,P1|}\r\n'\
                    '{RV02;%(POBCPRTE)s|}\r\n'\
                    '{LC;0915,0011,0915,0621,0,4|}\r\n'\
                    '{PV02;0945,0458,0020,0020,B,11,B,P1|}\r\n'\
                    '{RV02;TELF.:%(TELRTE)s|}\r\n'\
                    '{XB00;0360,0050,9,1,03,1,0280,+0000000000,000,0,00|}\r\n'\
                    '{RB00;%(CODBARRAS)s|}\r\n'\
                    '{PV03;0381,0021,0022,0025,A,11,B,P1|}\r\n'\
                    '{RV03;COD.BULTO: %(CODBARRAS)s|}\r\n'\
                    '{PV04;0850,0021,0026,0034,B,11,B,P1|}\r\n'\
                    '{RV04;%(NOMCONS)s|}\r\n'\
                    '{PV05;0820,0021,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV05;ATT: %(CONTACTO)s|}\r\n'\
                    '{PV06;0790,0021,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV06;%(DOMCONS)s|}\r\n'\
                    '{PV07;0760,0021,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV07;TELF.:%(TELCONS)s|}\r\n'\
                    '{PV41;0720,0021,0020,0020,B,11,B,P1|}\r\n'\
                    '{RV41;OBSERV:%(OBSER1)s|}\r\n'\
                    '{PV41;0680,0021,0020,0020,B,11,B,P1|}\r\n'\
                    '{RV41;%(OBSER2)s|}\r\n'\
                    '{PV08;0550,0021,0084,0079,B,11,B,P1|}\r\n'\
                    '{RV08;%(CPCONS)s|}\r\n'\
                    '{PV10;0500,0021,0038,0049,A,11,B,P1|}\r\n'\
                    '{RV10;%(POBCONS)s|}\r\n'\
                    '{PV09;0550,0321,0050,0059,B,11,B,P1|}\r\n'\
                    '{RV09; %(DESTINO)s|}\r\n'\
                    '{PV11;0508,0791,0033,0038,A,11,B,P1|}\r\n'\
                    '{RV11;|}\r\n'\
                    '{PV12;0630,0021,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV12;REF: %(REFERENCIA)s|}\r\n'\
                    '{PV13;0240,0821,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV13;PESO:|}\r\n'\
                    '{PV22;0240,0920,0023,0025,B,11,B,P1|}\r\n'\
                    '{RV22;%(KILOS)s Kgs.|}\r\n'\
                    '{PV14;0210,0821,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV14;BULTOS:|}\r\n'\
                    '{PV15;0210,0920,0023,0025,B,11,B,P1|}\r\n'\
                    '{RV15;%(PARCIAL)s de %(BULTOS)s|}\r\n'\
                    '{PV21;0160,0821,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV21;%(TSV_DENOM)s|}\r\n'\
                    '{PV21;0340,0821,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV21;Envio Retorno: %(RETORNO)s|}\r\n'\
                    '{PV18;0300,0821,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV18;REEMBOLSO: %(REEMBOLSO)s|}\r\n'\
                    '{PV19;0270,0821,0020,0025,B,11,B,P1|}\r\n'\
                    '{RV19;TIPO DE PORTES:|}\r\n'\
                    '{PV20;0270,1030,0023,0025,B,11,B,P1|}\r\n'\
                    '{RV20;%(SEMPOR)s|}\r\n'\
                    '{PV25;0420,0021,0029,0034,B,11,B,P1|}\r\n'\
                    '{RV25;EXP: %(ENVIO)s|}\r\n'\
                    '{LC;0460,0011,0460,0621,0,4|}\r\n'\
                    '{PV39;0100,0821,0023,0034,B,11,B,P1|}\r\n'\
                    '{RV39;FECHA: %(FECHA)s|}\r\n'\
                    '{XB01;0940,0700,P,00,02,09,1,0010|}\r\n'\
                    '{RB01;%(PDF417)s|}\r\n'\
                    '{XS;I,0001,0002C6000|}' % {
                    'CODBARRAS': data.get('codbarras', ''),
                    'PDF417':'',
                    'CODNOMRTE': data.get('etiq_nomRte', ''),
                    'DOMRTE': data.get('dirRte', ''),
                    'POBCPRTE': data.get('codPosNacRte', ''),
                    'TELRTE': data.get('telefRte', ''),
                    'NOMCONS': data.get('nomDest', ''),
                    'DOMCONS': data.get('dirDest', ''),
                    'CPCONS': codigo_postal,
                    'POBCONS': data.get('pobDest', ''),
                    'DESTINO': data.get('etiq_destino', ''),
                    'PAIS': data.get('etiq_pais', ''),
                    'CONTACTO': data.get('contacDest', ''),
                    'TELCONS': data.get('telefDest', ''),
                    'REFERENCIA': data.get('ref', ''),
                    'CODBUL_CLTE': '',
                    'RETORNO': data.get('numEnvioVuelta', ''),
                    'ENVIO': data.get('numenvio', ''),
                    'KILOS': data.get('kilos', ''),
                    'PARCIAL': data.get('etiq_bulto', ''),
                    'BULTOS': data.get('numBultos', ''),
                    'SEMPOR': data.get('etiq_portes', ''),
                    'REEMBOLSO': data.get('etiq_reembolso', ''),
                    'FECHA': data.get('etiq_fecha', ''),
                    'TSV_DENOM': data.get('etiq_tsv_abrevia', ''),
                    'OBSER1': data.get('observac', ''),
                    'OBSER2': data.get('observac_bulto', ''),
                    'SABADO': data.get('etiq_entrSabado', ''),

                     }
        return plantilla

    def etl(self,data):
        
        if len(data.get('codPosNacDest','' )) <> 0:
            codigo_postal = data.get('codPosNacDest','' )
        else:
            codigo_postal = data.get('codPosIntDest','' )
                    
        plantilla = 'N\r\n'\
                    'OD\r\n'\
                    'q816\r\n'\
                    'I8,1\r\n'\
                    'Q1583,24+0\r\n'\
                    'S4\r\n'\
                    'D13\r\n'\
                    'ZT\r\n'\
                    'LO5,540,467,4\r\n'\
                    'LO93,330,120,4\r\n'\
                    'LO93,170,120,4\r\n'\
                    'LO352,5,4,535\r\n'\
                    'LO150,5,4,535\r\n'\
                    'LO210,5,4,535\r\n'\
                    'LO90,5,4,1100\r\n'\
                    'LO468,540,4,660\r\n'\
                    'A25,1100,3,1,2,1,N,"%(CODNOMRTE)s"\r\n'\
                    'A55,1100,3,1,1,1,N,"%(DOMRTE)s"\r\n'\
                    'A75,1100,3,1,1,1,N,"%(POBCPRTE)s"\r\n'\
                    'A75,830,3,1,1,1,N,"Telf.:%(TELRTE)s"\r\n'\
                    'A270,520,3,3,2,1,N,"COD.BULTO: %(CODBARRAS)s"\r\n'\
                    'B770,410,1,1,4,2,256,N,"%(CODBARRAS)s"\r\n'\
                    'A100,1100,3,3,2,1,N,"%(NOMCONS)s"\r\n'\
                    'A435,1150,3,1,2,1,N,"ATT: %(CONTACTO)s"\r\n'\
                    'A435,800,3,1,2,1,N,"TELF.: %(TELCONS)s"\r\n'\
                    'A140,1100,3,2,2,1,N,"%(DOMCONS)s"\r\n'\
                    'A250,1100,3,5,2,2,N,"%(CPCONS)s"\r\n'\
                    'A390,1150,3,3,2,1,N,"%(POBCONS)s"\r\n'\
                    'A220,520,3,3,2,1,N,"REF: %(REFERENCIA)s"\r\n'\
                    'A350,1150,3,3,2,3,N,"%(DESTINO)s"\r\n'\
                    'A350,1150,3,3,2,3,N,"%(PAIS)s"\r\n'\
                    'A20,530,3,2,3,2,N,"EXP: %(ENVIO)s"\r\n'\
                    'A158,320,3,2,1,1,N,"PESO:"\r\n'\
                    'A175,320,3,2,2,1,N,"%(KILOS)sKgs."\r\n'\
                    'A98,320,3,2,1,1,N,"BULTOS:"\r\n'\
                    'A115,320,3,2,2,1,N,"%(PARCIAL)sDE %(BULTOS)s"\r\n'\
                    'A98,520,3,2,1,1,N,"REEMBOLSO:"\r\n'\
                    'A115,520,3,2,2,1,N,"%(REEMBOLSO)s"\r\n'\
                    'A158,520,3,2,1,1,N,"TIPO DE PORTES:"\r\n'\
                    'A175,520,3,2,2,1,N,"%(SEMPOR)s"\r\n'\
                    'A70,450,3,1,1,1,N,"Envio retorno: %(RETORNO)s"\r\n'\
                    'A400,520,3,3,2,2,N,"%(TSV_ABREVIA)s"\r\n'\
                    'A180,1100,3,2,2,1,N,"%(OBSER1)s"\r\n'\
                    'A220,1100,3,2,2,1,N,"%(OBSER2)s"\r\n'\
                    'A115,160,3,2,2,1,N,"%(FECHA)s"\r\n'\
                    'A98,160,3,2,1,1,N,"FECHA:"\r\n'\
                    'b760,340,P,800,600,s1,c0,f0,x2,y5,l5,t0,o2,"%(PDF417)s"\r\n'\
                    'P1\r\n'\
                    'N' % {
                    'CODBARRAS': data.get('codbarras', ''),
                    'PDF417': '',
                    'CODNOMRTE': data.get('etiq_nomRte', ''),
                    'DOMRTE': data.get('dirRte', ''),
                    'POBCPRTE': data.get('codPosNacRte', ''),
                    'TELRTE': data.get('telefRte', ''),
                    'NOMCONS': data.get('nomDest', ''),
                    'DOMCONS': data.get('dirDest', ''),
                    'CPCONS': codigo_postal,
                    'POBCONS': data.get('pobDest', ''),
                    'DESTINO': data.get('etiq_destino', ''),
                    'PAIS': data.get('etiq_pais', ''),
                    'CONTACTO': data.get('contacDest', ''),
                    'TELCONS': data.get('telefDest', ''),
                    'REFERENCIA': data.get('ref', ''),
                    'CODBUL_CLTE': '',
                    'RETORNO': data.get('numEnvioVuelta', ''),
                    'ENVIO': data.get('numenvio', ''),
                    'KILOS': data.get('kilos', ''),
                    'PARCIAL': data.get('etiq_bulto', ''),
                    'BULTOS': data.get('numBultos', ''),
                    'SEMPOR': data.get('etiq_portes', ''),
                    'REEMBOLSO': data.get('etiq_reembolso', ''),
                    'FECHA': data.get('etiq_fecha', ''),
                    'TSV_ABREVIA': data.get('etiq_tsv_abrevia', ''),
                    'OBSER1': data.get('observac', ''),
                    'OBSER2': data.get('observac_bulto', ''),
                    'SABADO': data.get('etiq_entrSabado', ''),

                     }
        return plantilla

    def citoh(self,data):
        
        if len(data.get('codPosNacDest','' )) <> 0:
            codigo_postal = data.get('codPosNacDest','' )
        else:
            codigo_postal = data.get('codPosIntDest','' )
                    
        plantilla = 'n\r\n'\
                    'c01\r\n'\
                    'RN\r\n'\
                    'V4\r\n'\
                    'O0000\r\n'\
                    'M1480\r\n'\
                    'L\r\n'\
                    'A1\r\n'\
                    'D11\r\n'\
                    'R0020\r\n'\
                    'Pp\r\n'\
                    'SK\r\n'\
                    'H08\r\n'\
                    '1X1100000010345L002565\r\n'\
                    '221100005510371%(CODNOMRTE)s\r\n'\
                    '221100005510361%(DOMRTE)s\r\n'\
                    '221100005510351%(POBCPRTE)s\r\n'\
                    '221100003550351Telf.:%(TELRTE)s\r\n'\
                    '2e2412205310025C%(CODBARRAS)s\r\n'\
                    '231100005510330%(NOMCONS)s\r\n'\
                    '221100005510320ATT: %(CONTACTO)s\r\n'\
                    '221100005510310%(DOMCONS)s\r\n'\
                    '261100005510240%(CPCONS)s\r\n'\
                    '221100005510300TELF.: %(TELCONS)s\r\n'\
                    '221100005510280REF: %(REFERENCIA)s\r\n'\
                    '241100005510220%(DESTINO)s\r\n'\
                    '241100005510200%(POBCONS)s\r\n'\
                    'A5\r\n'\
                    '231100005510180EXP: %(ENVIO)s\r\n'\
                    'A1\r\n'\
                    '321100000110270Envio retorno: %(RETORNO)s\r\n'\
                    'A5\r\n'\
                    '221100001400170PESO:\r\n'\
                    'A1\r\n'\
                    '221100001400160%(KILOS)s Kgs.\r\n'\
                    'A5\r\n'\
                    '221100001400140BULTOS:\r\n'\
                    'A1\r\n'\
                    '221100001400130%(PARCIAL)s de %(BULTOS)s\r\n'\
                    'A5\r\n'\
                    '221100001400110PRODUCTO:\r\n'\
                    'A1\r\n'\
                    '221100001400100%(TSV_ABREVIA)s\r\n'\
                    'A5\r\n'\
                    '221100001400090REEMBOLSO:\r\n'\
                    'A1\r\n'\
                    '221100001400080%(REEMBOLSO)s\r\n'\
                    'A5\r\n'\
                    '221100001400060TIPO DE PORTES:\r\n'\
                    'A1\r\n'\
                    '221100001400050%(SEMPOR)s\r\n'\
                    '221100002800210OBSERVACIONES:\r\n'\
                    '221100002800200%(OBSER1)s\r\n'\
                    '221100002800190%(OBSER2)s\r\n'\
                    '231100001400020FECHA: %(FECHA)s\r\n'\
                    '221100005510150CODIGO BULTO: %(CODBARRAS)s\r\n'\
                    'A5\r\n'\
                    '231100002700370%(TSV_ABREVIA)s\r\n'\
                    '2z2900202200238F0002708%(PDF417)s\r\n'\
                    '^01\r\n'\
                    'Q0001\r\n'\
                    'E' % {
                    'CODBARRAS': data.get('codbarras', ''),
                    'PDF417': '',
                    'CODNOMRTE': data.get('etiq_nomRte', ''),
                    'DOMRTE': data.get('dirRte', ''),
                    'POBCPRTE': data.get('codPosNacRte', ''),
                    'TELRTE': data.get('telefRte', ''),
                    'NOMCONS': data.get('nomDest', ''),
                    'DOMCONS': data.get('dirDest', ''),
                    'CPCONS': codigo_postal,
                    'POBCONS': data.get('pobDest', ''),
                    'DESTINO': data.get('etiq_destino', ''),
                    'PAIS': data.get('etiq_pais', ''),
                    'CONTACTO': data.get('contacDest', ''),
                    'TELCONS': data.get('telefDest', ''),
                    'REFERENCIA': data.get('ref', ''),
                    'CODBUL_CLTE': '',
                    'RETORNO': data.get('numEnvioVuelta', ''),
                    'ENVIO': data.get('numenvio', ''),
                    'KILOS': data.get('kilos', ''),
                    'PARCIAL': data.get('etiq_bulto', ''),
                    'BULTOS': data.get('numBultos', ''),
                    'SEMPOR': data.get('etiq_portes', ''),
                    'REEMBOLSO': data.get('etiq_reembolso', ''),
                    'FECHA': data.get('etiq_fecha', ''),
                    'TSV_ABREVIA': data.get('etiq_tsv_abrevia', ''),
                    'OBSER1': data.get('observac', ''),
                    'OBSER2': data.get('observac_bulto', ''),
                    'SABADO': data.get('etiq_entrSabado', ''),

                     }
        return plantilla


