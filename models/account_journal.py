from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _get_l10n_ar_afip_ws(self):
        return [('wsfe', _('Domestic market -without detail- RG2485 (WSFEv1)')),
                ('wsfex', _('Export -with detail- RG2758 (WSFEXv1)')),
                ('wsbfe', _('Fiscal Bond -with detail- RG2557 (WSBFE)')),
                ('ws_sr_padron_a13', _('Consulta padrón A13')),
                ('ws_sr_constancia_inscripcion', _('Consulta Constancia de inscripción')),
               ]
        