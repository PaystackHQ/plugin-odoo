# -*- coding: utf-8 -*-
# from odoo import http


# class PaystackBase(http.Controller):
#     @http.route('/paystack_base/paystack_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/paystack_base/paystack_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('paystack_base.listing', {
#             'root': '/paystack_base/paystack_base',
#             'objects': http.request.env['paystack_base.paystack_base'].search([]),
#         })

#     @http.route('/paystack_base/paystack_base/objects/<model("paystack_base.paystack_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('paystack_base.object', {
#             'object': obj
#         })
