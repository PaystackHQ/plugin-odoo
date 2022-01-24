{
    'name': 'Paystack Ecommerce',
    'version': '14.0.1.0.0',
    'category': 'eCommerce',
    'summary': 'Paystack Payment Gateway for Ecommerce Module Odoo 14',
    'description': 'Paystack Payment Gateway for Ecommerce Module Odoo 14, Paystack, payment gateway,Payment Gateway Integration,Paystack payment, odoo 14, odoo payment gateway',
    'author': 'Paystack',
    'company': 'Paystack',
    'website': 'https://paystack.com',
    'depends': ['base','payment','paystack_base', 'website_sale'],
    'data': [
        'views/payment_transaction_view.xml',
        'views/assets.xml',
        'views/payment_template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}



