# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
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
    
class AfipPadron(models.Model):
    _inherit='res.partner'

    padron_type= fields.Selection(string='Tipo de padrón',
                                  selection=[('a13','Padron A13'),('constancia_inscripcion','Constancia de Inscripción')],
                                  default='constancia_inscripcion')
    prov_dict = {
    0: "Ciudad Autónoma de Buenos Aires",
    1: "Buenos Aires",
    2: "Catamarca",
    3: "Córdoba",
    4: "Corrientes",
    5: "Entre Ríos",
    6: "Jujuy",
    7: "Mendoza",
    8: "La Rioja",
    9: "Salta",
    10: "San Juan",
    11: "San Luis",
    12: "Santa Fe",
    13: "Santiago del Estero",
    14: "Tucumán",
    15: "Chaco",
    16: "Chubut",
    17: "Formosa",
    18: "Misiones",
    19: "Neuquén",
    20: "La Pampa",
    21: "Río Negro",
    22: "Santa Cruz",
    23: "Tierra del Fuego",
}
    
    afip_company_id=fields.Many2one(
        comodel_name='res.company',
        string="Compania",
         default=lambda self: self.env['res.company'].browse(1),
        readonly=True,
    )
    
    def _get_l10n_ar_afip_ws(self):
        return [('ws_sr_constancia_inscripcion', _('Constancia de Inscripción')),
                ('ws_sr_padron_a10', _('Consulta de Padrón Alcance 10')),
                ('ws_sr_padron_a13', _('Consulta de Padrón Alcance 13')),
               ]

    
    def update_padron(self):
            if self.padron_type == 'a13':
                datas = self.connectToAfip('ws_sr_padron_a13')
                persona = datas.persona
                if not persona:
                    raise UserError('No se puedo obetener los datos de la persona')
                domicilios = persona['domicilio'] if 'domicilio' in persona else []
                #actividad_principal = self.env['afip.activity'].search([('code', '=', persona['idActividadPrincipal'])],limit=1)
                if persona['razonSocial']:
                    name = persona['razonSocial']
                elif persona['apellido'] and persona['nombre']:
                    name = persona['apellido'] + ' ' + persona['nombre']
                else:
                    name = self.name
                self.write({
                    'name':name,
                    'last_update_padron' : date.today(),
                    'start_date': self.crear_registro_con_fecha(persona['periodoActividadPrincipal']),
                })
                #if actividad_principal:
                #   self.actividades_padron = [6,0,actividad_principal.id]
            
                domicilio_fiscal = next((dom for dom in domicilios if dom['tipoDomicilio'] == 'FISCAL'), None)
                if domicilio_fiscal:
                    state =  self.env['res.country.state'].search([('name', '=', self.prov_dict[domicilio_fiscal['idProvincia']]),('country_id', '=', 10)], limit=1).id,
                    self.write({
                        'street': domicilio_fiscal['calle'] + ' ' + str(domicilio_fiscal['numero']),
                        'zip': domicilio_fiscal['codigoPostal'],
                        'city': domicilio_fiscal['localidad'],
                        'state_id': state,
                        #'street2': 'Piso: ' + str(domicilio_fiscal.get('piso', '')) + ' Dpto: ' + str(domicilio_fiscal.get('oficinaDptoLocal', '')),
                    })
                    for domicilio in domicilios:
                        if domicilio['tipoDomicilio'] != 'FISCAL' and domicilio['calle'] != domicilio_fiscal['calle'] and domicilio['numero'] != domicilio_fiscal['numero']:
                            state =  self.env['res.country.state'].search([('name', '=', self.prov_dict[domicilio_fiscal['idProvincia']]),('country_id', '=', 10)], limit=1).id,
                            street_name = domicilio['calle'] + ' ' + str(domicilio['numero']) if domicilio['numero'] else ' ' + domicilio['localidad']
                            
                            # Buscar si el domicilio ya existe para este contacto
                            existing_domicilio = self.env['res.partner'].search([
                                ('parent_id', '=', self.id),
                                ('street', '=', street_name),
                                ('zip', '=', domicilio['codigoPostal']),
                                ('city', '=', domicilio['localidad']),
                                ('state_id', '=', state)
                            ], limit=1)
                    
                            # Si no existe, creamos el nuevo contacto hijo
                            if not existing_domicilio:
                                vals = {
                                    'name': street_name,
                                    'parent_id': self.id,  # Asignar el contacto base como el padre
                                    'type': 'other',  # O puedes usar 'invoice', 'delivery', etc., según el tipo de domicilio
                                    'street': street_name,
                                    'zip': domicilio['codigoPostal'],
                                    'city': domicilio['localidad'],
                                    'state_id': state,
                                    #'phone': self.phone,  # Opcional
                                    #'email': self.email,  # Opcional
                                }
                                # Crear el nuevo contacto hijo
                                self.env['res.partner'].create(vals)
                            else:
                                # Si ya existe, puedes realizar una acción alternativa, por ejemplo:
                                _logger.info(f"El domicilio {street_name} ya existe para este contacto.")
                                    # Actualizar el registro de res.partner con los datos extraídos  
            else:
                datas = self.connectToAfip('ws_sr_constancia_inscripcion')
                persona = datas['datosGenerales']
                if not persona:
                    raise UserError('No se puedo obetener los datos de la persona,la constancia puede estar bloqueada. Puede probar usar el padron A13 en la pestaña ajustes')
                if persona['razonSocial']:
                    name = persona['razonSocial']
                elif persona['apellido'] and persona['nombre']:
                    name = persona['apellido'] + ' ' + persona['nombre']
                else:
                    name = self.name
                self.write({
                    'name':name,
                    'last_update_padron' : date.today(),
                })
                if persona['domicilioFiscal']:
                    domicilio_fiscal = persona['domicilioFiscal']
                    state =  self.env['res.country.state'].search([('name', '=', self.prov_dict[domicilio_fiscal['idProvincia']]),('country_id', '=', 10)], limit=1).id,
                    self.write({
                        'street': domicilio_fiscal['direccion'],
                        'zip': domicilio_fiscal['codPostal'],
                        'city': domicilio_fiscal['localidad'],
                        'state_id': state,
    
                        #'street2': 'Piso: ' + str(domicilio_fiscal.get('piso', '')) + ' Dpto: ' + str(domicilio_fiscal.get('oficinaDptoLocal', '')),
                    })
                          
    def connectToAfip(self,type):
        """
        Consulta la constancia de inscripción del CUIT proporcionado vía AFIP web service
        :param cuit: El CUIT que se desea consultar
        :return: Datos de la constancia de inscripción en AFIP
        """
        self.ensure_one()
    
        # Modo de prueba
        if self.env.registry.in_test_mode():
            return _("Test mode: no real AFIP connection")
    
        # Obtener la conexión al servicio web de AFIP
        afip_ws = type  # Asegúrate de usar el servicio correcto aquí
        connection = self.afip_company_id._l10n_ar_get_connection(afip_ws)
        client, auth = connection._get_client()
        id_persona = str(self.l10n_ar_vat)
        data={
            'token': auth.get('Token'),  # token ya debe estar en `auth`
            'sign': auth.get('Sign'),    # sign ya debe estar en `auth`
            'cuitRepresentada': (self.afip_company_id.vat),  # Asegúrate de usar el CUIT correcto de la empresa representada
            'idPersona': id_persona  # CUIT de la persona a consultar (asegúrate de que `self.vat` sea un CUIT válido)
        }

        # Llamar al servicio de consulta de la constancia de inscripción
        try:
            if type == 'ws_sr_constancia_inscripcion':
                response = client.service.getPersona_v2(**data)
            else:
                response = client.service.getPersona(**data)
            return response
        except Exception as e:
            # Manejo de errores
            raise UserError(f"Ocurrió un error al obtener la información de la persona: {str(e)}")

    def crear_registro_con_fecha(self, periodo):
        # Convertir periodo (ej: 201311) a fecha
        año = periodo // 100  # Obtener el año
        mes = periodo % 100    # Obtener el mes
        fecha = f'{año}-{mes:02d}-01'  # Crear la fecha como 'YYYY-MM-DD'

        # Crear un nuevo registro con la fecha convertida
        return fecha

            