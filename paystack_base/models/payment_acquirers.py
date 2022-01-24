from odoo.exceptions import UserError, Warning
from odoo import api, fields, models
import requests
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PaymentAcquirerPaystack(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paystack', 'Paystack')], ondelete={'paystack': 'set default'})

    paystack_transaction_initialize = fields.Char(string="Transaction Initialize", default="https://api.paystack.co/transaction/initialize", required_if_provider="paystack", groups="base.group_user", help="Used to initiate payment for the customer")

    paystack_transaction_verify = fields.Char(string="Transaction Verify", default="https://api.paystack.co/transaction/verify", required_if_provider="paystack", groups="base.group_user", help="verify/validate the payment details after the gateway response")

    paystack_transaction_refund = fields.Char(string="Transaction Refund", default="https://api.paystack.co/refund", required_if_provider="paystack", groups="base.group_user",help="Used to initiate refund to customer")

    paystack_merchant_key = fields.Char("Secret Key", required_if_provider="paystack", groups="base.group_user")

    ecom_allowed_currencies = fields.Many2many("res.currency",string="Allowed Currencies")

    def test_paystack_initialization(self):
        endpoint = self.paystack_transaction_initialize.rstrip("/")
        data = { 
            "email": "test@gmail.com", #mandatory
            "amount": "1000", #mandatory
            'currency': "NGN", #optional
            'callback_url': "https://www.pptservices.com", #optional
            }
        bearer_token = "Bearer "+str(self.paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        api_call = requests.post(endpoint, data=data, headers=headers)
        if api_call.status_code==200:
            raise Warning("Payment Credential Seems Perfect")
        else:
            raise UserError("Invalid Initialize URL/Secret Key")
    
    def test_paystack_refund(self):
        data = {
                'transaction': "test", #mandatory
                'amount': "500", #optional
                'currency': "NGN", #optional
                'customer_note': "Test", #optional
                'merchant_note': "Test", #optional
            }

        endpoint = self.paystack_transaction_refund.rstrip("/")
        
        bearer_token = "Bearer "+str(self.paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        api_call = requests.post(endpoint, data=data, headers=headers)
        
        try:
            response = api_call.json()
            if response.get("message") == "Transaction not found":
                verification = "success"
            else:
                verification = "failed"
        except:
            verification = "failed"
        
        if verification=="success":
            raise Warning("Refund Credential Seems Perfect")
        else:
            raise UserError("Invalid Refund URL/Secret Key")
        

    def call_paystack_transaction_initialize(self, data):

        endpoint = self.paystack_transaction_initialize.rstrip("/")
        
        bearer_token = "Bearer "+str(self.paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        api_call = requests.post(endpoint, data=data, headers=headers)
        if api_call.status_code==200:
            response = api_call.json()
        else:
            response = {
                'status': False,
                'message': "Invalid Url/Secret Key"
            }

        return response
    
    def call_paystack_transaction_verify(self, reference):

        endpoint = self.paystack_transaction_verify.rstrip("/")+"/"+str(reference)
        
        bearer_token = "Bearer "+str(self.paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        api_call = requests.get(endpoint, headers=headers)
        if api_call.status_code==200:
            response = api_call.json()
        else:
            response = {
                'status': False,
                'message': "Transaction Not Found"
            }

        return response

    def call_paystack_transaction_refund(self, data):
        
        endpoint = self.paystack_transaction_refund.rstrip("/")
        
        bearer_token = "Bearer "+str(self.paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        api_call = requests.post(endpoint, data=data, headers=headers)
        if api_call.status_code==200:
            response = api_call.json()
        else:
            try:
                response = api_call.json()
            except:
                response = {
                    'status': False,
                    'message': "Invalid Reference Key"
                }

        return response
    
    def paystack_get_form_action_url(self):
        if request.session.get("sale_order_id"):
            sale_order = self.env["sale.order"].sudo().browse(int(request.session.get("sale_order_id")))

            if sale_order:
                email = sale_order.partner_id.email
                amount = sale_order.amount_total
                base_url=self.env ['ir.config_parameter'].sudo ().get_param ('web.base.url')
                callback_url = base_url.rstrip("/")+"/paystack/response"
                data = {
                    'email': sale_order.partner_id.email,
                    'amount': round(sale_order.amount_total, 2)*100,
                    'currency': sale_order.currency_id.name,
                    'callback_url': callback_url,
                }

                initialize_authorization = self.call_paystack_transaction_initialize(data)

                if initialize_authorization.get("status") == True:
                    authorization_credential = initialize_authorization.get("data")

                    if authorization_credential:
                        transaction = self.env["payment.transaction"].sudo().browse(int(request.session.get("__website_sale_last_tx_id")))
                        if transaction:
                            transaction.paystack_authorization_url = authorization_credential.get("authorization_url")
                            transaction.paystack_access_code = authorization_credential.get("access_code")
                            transaction.acquirer_reference = authorization_credential.get("reference")
                        
                    return authorization_credential.get("authorization_url")
                else:
                    return False
            else:
                return False
        else:
            return False
        

class PaystackPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    provider = fields.Selection(string="Provider", related="acquirer_id.provider")

    paystack_authorization_url = fields.Char(string="Paystack Authorization")
    paystack_access_code = fields.Char(string="Paystack Access Code")
