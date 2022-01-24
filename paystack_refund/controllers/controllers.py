# -*- coding: utf-8 -*-
# from odoo import http


# class PaystackRefund(http.Controller):
#     @http.route('/paystack_refund/paystack_refund/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/paystack_refund/paystack_refund/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('paystack_refund.listing', {
#             'root': '/paystack_refund/paystack_refund',
#             'objects': http.request.env['paystack_refund.paystack_refund'].search([]),
#         })

#     @http.route('/paystack_refund/paystack_refund/objects/<model("paystack_refund.paystack_refund"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('paystack_refund.object', {
#             'object': obj
#         })
