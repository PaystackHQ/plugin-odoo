{
    'name': 'Paystack POS',
    'version': '14.0.1.0.0',
    'category': 'eCommerce',
    'summary': 'Paystack Payment Gateway for POS Module Odoo 14',
    'description': 'Paystack Payment Gateway for POS Module Odoo 14, Paystack, payment gateway,Payment Gateway Integration,Paystack payment, odoo 14, odoo payment gateway',
    'author': 'Paystack',
    'company': 'Paystack',
    'website': 'https://paystack.com',
    'depends': ['base','payment','paystack_base', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/point_of_sale_assets.xml',
        'views/paystack_terminal.xml',
        'views/pos_payment_method_views.xml',
        'views/paystack_pos_order_views.xml',
        'views/pos_config.xml',
        'views/ir_cron_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

    'qweb' : [
        'static/src/xml/Screens/PaymentScreen/PaymentScreenElectronicPayment.xml',
    ],

}



