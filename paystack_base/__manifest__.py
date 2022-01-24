{
    'name': 'Paystack Payment Gateway',
    'version': '14.0.1.0.0',
    'category': 'Website',
    'summary': 'Paystack Payment Gateway Integration for Odoo 14',
    'description': 'Paystack Payment Gateway Integration for Odoo 14, Paystack, payment gateway,Payment Gateway Integration,Paystack payment, odoo 14, odoo payment gateway',
    'author': 'Paystack',
    'company': 'Paystack',
    'website': 'https://paystack.com',
    'depends': ['base','payment'],
    'data': [
        'views/payment_acquirers_views.xml',
        'views/templates.xml',
        'data/data.xml'
    ],
    'images': [
        'static/src/img/logo.png',
        'static/src/img/Paystack_Logo.png', 'static/description/icon.png', 'static/images/banner.png',
    ],
    'installable': True,
    'auto_install': True,
    'application': True,

}



