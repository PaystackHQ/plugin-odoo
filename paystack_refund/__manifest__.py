{
    'name': 'Paystack Refund',
    'version': '14.0.1.0.0',
    'category': 'eCommerce',
    'summary': 'Paystack Payment Gateway for Ecommerce Refund Module Odoo 14',
    'description': 'Paystack Payment Gateway for Ecommerce Refund Module Odoo 14, Paystack, payment gateway,Payment Gateway Integration,Paystack payment, odoo 14, odoo payment gateway',
    'author': 'Paystack',
    'company': 'Paystack',
    'website': 'https://paystack.com',
    'depends': ['base','account','payment','paystack_base'],
    'data': [
        'security/ir.model.access.csv',
        'views/payment_transaction_view.xml',
        # 'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}



