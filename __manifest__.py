# -*- coding: utf-8 -*-
{
    'name': "AFIP consultar Padron",

    'summary': "Módulo para actualizar datos del cliente utilizando el padrón AFIP.",
    
    'description': """
        Este módulo permite la actualización de los datos de los clientes directamente desde los servicios de padrón de AFIP, ya sea mediante la Constancia de Inscripción o el Padrón A13.
    """,

    'author': "OutsourceArg",
    'website': "https://www.outsourcearg.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Localization/Argentina',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','l10n_ar_edi','account'],
    # always loaded
    'data': [
        'views/res_partner_view.xml',
    ],
    # only loaded in demonstration mode
    'installable':True,
    'application':False,
}