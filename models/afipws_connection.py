# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class AfipConnection(models.Model):
    _inherit='l10n_ar.afipws.connection'
    
    @api.model
    def _l10n_ar_get_afip_ws_url(self, afip_ws, environment_type):
        """ Function to be inherited on each module that adds a new webservice """
        ws_data = {'wsfe': {'production': "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL",
                            'testing': "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"},
                   'wsfex': {'production': "https://servicios1.afip.gov.ar/wsfexv1/service.asmx?WSDL",
                             'testing': "https://wswhomo.afip.gov.ar/wsfexv1/service.asmx?WSDL"},
                   'wsbfe': {'production': "https://servicios1.afip.gov.ar/wsbfev1/service.asmx?WSDL",
                             'testing': "https://wswhomo.afip.gov.ar/wsbfev1/service.asmx?WSDL"},
                   'wscdc': {'production': "https://servicios1.afip.gov.ar/WSCDC/service.asmx?WSDL",
                             'testing': "https://wswhomo.afip.gov.ar/WSCDC/service.asmx?WSDL"},
                  'ws_sr_constancia_inscripcion': {'production': "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA5?WSDL",
                             'testing': "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA5?WSDL"},
                   'ws_sr_padron_a13': {'production': "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA13?WSDL",
                             'testing': "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA13?WSDL"},
                    'ws_sr_padron_a10': {'production': "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA10?WSDL",
                             'testing': "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA10?WSDL"},
                  }
        return ws_data.get(afip_ws, {}).get(environment_type)

