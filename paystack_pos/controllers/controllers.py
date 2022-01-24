from odoo import fields, http, _
from odoo.http import request
from odoo.exceptions import ValidationError, UserError, Warning
import datetime
from datetime import date, datetime, timedelta
import time
import logging
import json

_logger = logging.getLogger(__name__)

class PaystackPos(http.Controller):

    @http.route(['/paystack/payment/initiate'], type='http', auth="public", website=True, csrf=False, methods=['GET','POST'])
    def paystack_payment_initiate(self, **post):
        result = {}
        if post.get("payment_method_id"):
            get_payment_method = request.env["pos.payment.method"].sudo().browse(int(post.get("payment_method_id")))
            get_pos_configuration = request.env['pos.config'].sudo().browse(int(post.get("pos_config_id")))
            if get_payment_method:
                response = get_payment_method.start_paystack_payment_process(get_pos_configuration.paystack_terminal,post.get("customer_data"),post.get("payment_data"))
                return json.dumps(response)
        return json.dumps(result)



    @http.route(['/paystack/webhook/response'], type='json', auth="public", csrf=False, website=True, methods=['GET','POST'])
    def paystack_webhook_response(self, **post):
        response = request.jsonrequest
        _logger.info("@response {}".format(response))

        if response.get("event") == "paymentrequest.pending":
            paystack_data = response.get("data")
            get_paystack_payment = request.env['pos.payment.paystack'].sudo().search([('request_code','=',paystack_data.get("request_code"))],limit=1)

            if get_paystack_payment:
                integration_data = paystack_data.get("integration")

                paymentrequest_pending = {
                    'payment_status': paystack_data.get("status"),
                    'flat_rate': integration_data.get("flat_rate")/100 if integration_data.get("flat_rate") else 0,
                    'charge_percentage': integration_data.get("charge_percentage") if integration_data.get("charge_percentage") else 0,
                    'international_charge_percentage': integration_data.get("international_charge_percentage") if integration_data.get("international_charge_percentage") else 0,
                    'flat_threshhold': integration_data.get("flat_threshhold")/100 if integration_data.get("flat_threshhold") else 0,
                    'transfer_charge': integration_data.get("transfer_charge")/100 if integration_data.get("transfer_charge") else 0,

                    'event_triggered': "paymentrequest.pending",
                }

                get_paystack_payment.sudo().update(paymentrequest_pending)

                return http.Response(status=200)
        
        # elif response.get("event") == "charge.success":
        #     paystack_data = response.get("data")
        #     if paystack_data:
        #         customer_data = paystack_data.get("customer")

        #         if customer_data:

        #             get_paystack_payment = request.env['pos.payment.paystack'].sudo().search([('customer_code','=',customer_data.get("customer_code")),('payment_status','=','pending')],order="create_date desc", limit=1)

        #             if get_paystack_payment:

        #                 paystack_authorization = paystack_data.get("authorization")

        #                 try:
        #                     paid_date = datetime.strptime(paystack_data.get('paid_at'), "%Y-%m-%dT%H:%M:%S.000Z")
                            
        #                 except:
        #                     paid_date = datetime.now()

        #                 charge_success = {
        #                     'payment_status': paystack_data.get("status"),
        #                     'transaction_reference': paystack_data.get("reference"),
        #                     'fees': paystack_data.get("fees"),
        #                     'paystack_paid_at': paid_date,

        #                     'ip_address': paystack_data.get("ip_address"),

        #                     'authorization_code': paystack_authorization.get("authorization_code"),

        #                     'paystack_channel': paystack_data.get('channel') if paystack_data.get('channel') else '',

        #                     'paystack_bin': paystack_authorization.get('bin') if paystack_authorization else '',

        #                     'paystack_last4': paystack_authorization.get('last4') if paystack_authorization else '',

        #                     'paystack_card_type': paystack_authorization.get('card_type') if paystack_authorization else '',

        #                     'paystack_bank': paystack_authorization.get('bank') if paystack_authorization else '',

        #                     'paystack_country_code': paystack_authorization.get('country_code') if paystack_authorization else '',

        #                     'paystack_signature': paystack_authorization.get('signature') if paystack_authorization else '',

        #                     'paystack_account_name': paystack_authorization.get('account_name') if paystack_authorization else '',

        #                     'event_triggered': "charge.success",
        #                     'gateway_response': paystack_data.get("gateway_response"),
        #                 }

        #                 get_paystack_payment.sudo().update(charge_success)

        #                 return http.Response(status=200)

        elif response.get("event") == "paymentrequest.success":
            paystack_data = response.get("data")
            get_paystack_payment = request.env['pos.payment.paystack'].sudo().search([('request_code','=',paystack_data.get("request_code"))],limit=1)

            if get_paystack_payment:

                try:
                    paid_date = datetime.strptime(paystack_data.get('paid_at'), "%Y-%m-%dT%H:%M:%S.000Z")
                            
                except:
                    paid_date = datetime.now()

                paymentrequest_success = {
                    'paystack_paid_at': paid_date,
                    'payment_status': paystack_data.get("status"),
                    'event_triggered': "paymentrequest.success",
                    'transaction_reference': paystack_data.get("reference") or paystack_data.get("transaction_reference"),
                    'paystack_terminal_response': "Success" if get_paystack_payment.paystack_terminal_response=="Process" else "Failed",
                }

                get_paystack_payment.sudo().update(paymentrequest_success)

                return http.Response(status=200)
        
        else:
            paystack_data = response.get("data")
            if paystack_data:
                customer_data = paystack_data.get("customer")

                if customer_data:

                    get_paystack_payment = request.env['pos.payment.paystack'].sudo().search([('customer_code','=',customer_data.get("customer_code")),('payment_status','=','pending')],order="create_date desc", limit=1)

                    if get_paystack_payment:
                        paymentrequest = {
                            'payment_status': paystack_data.get("status"),
                            'event_triggered': response.get("event"),
                            'transaction_reference': paystack_data.get("reference") or paystack_data.get("transaction_reference"),
                        }

                        get_paystack_payment.sudo().update(paymentrequest)

                        return http.Response(status=200)
            
        return http.Response(status=200)

