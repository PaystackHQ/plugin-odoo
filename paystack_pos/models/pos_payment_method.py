import json
import logging
import requests
from odoo import fields, models, api, _
import qrcode
import base64
from io import BytesIO
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    def _valid_field_parameter(self, field, name):
        return name == 'required_if_use_payment_terminal' or super()._valid_field_parameter(field, name)

    def _get_payment_terminal_selection(self):
        return super(PosPaymentMethod, self)._get_payment_terminal_selection() + [('paystack', 'Paystack')]
    
    paystack_merchant_key = fields.Char(string="Secret Key", required_if_use_payment_terminal="paystack", groups="base.group_user")

    pos_allowed_currencies = fields.Many2many("res.currency", string="Allowed Currencies")


    def create_paystack_payment_request(self, paystack_merchant_key, payment_data):

        endpoint = "https://api.paystack.co/paymentrequest"
        
        bearer_token = "Bearer "+str(paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        api_call = requests.post(endpoint, data=json.dumps(payment_data), headers=headers)

        try:
            response = api_call.json()
        except:
            response = {
                'status': False,
                'message': "Invalid Secret Key/URL"
            }
        
        return response
    
    def send_payment_request_to_terminal(self, paystack_merchant_key, terminal_id, request_data):

        endpoint = "https://api.paystack.co/terminal/{}/event".format(terminal_id)
        _logger.info("@API endpoint======={}".format(endpoint))
        
        bearer_token = "Bearer "+str(paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        _logger.info("@API Data Sending======={}".format(json.dumps(request_data)))

        api_call = requests.post(endpoint, data=json.dumps(request_data), headers=headers)
        _logger.info("@API api_call status======={}".format(api_call.status_code))

        try:
            response = api_call.json()
        except:
            response = {
                'status': False,
                'message': "Invalid Secret Key/URL"
            }
        
        return response


    def start_paystack_payment_process(self, paystack_terminal, customer_data, payment_data):

        customer_data = json.loads(customer_data)

        paystack_method = self.env["pos.payment.method"].search([('use_payment_terminal','=','paystack')],limit=1)
        if paystack_method and paystack_method.pos_allowed_currencies:
            if customer_data.get("currency_id")  not in paystack_method.pos_allowed_currencies.ids:
                return_response = {
                'status': False,
                'message': "Selected currency is not supported by Paystack",
                'payment_request_status': "false",
                'payment_request_message': "false",
                'payment_request_code': "false",
                'offline_reference': "false",
                'payment_qrcode_url': "false",
                }
                return return_response
        if not paystack_terminal:
            return_response = {
                'status': False,
                'message': "Terminal not found",
                'payment_request_status': "false",
                'payment_request_message': "Please configure terminal first",
                'payment_request_code': "false",
                'offline_reference': "false",
                'payment_qrcode_url': "false",
            }

            return return_response

        # customer_data = json.loads(customer_data)
        payment_data = json.loads(payment_data)

        # create customer in paystack
        partner_obj = self.env['res.partner'].sudo().browse(int(customer_data.get("partner_id")))

        names = partner_obj.name.split(" ",1)
        data = {
            "email": partner_obj.email,
            "first_name": names[0] if len(names)>=1 else partner_obj.name,
            "last_name": names[1] if len(names)>1 else "",
        }

        if partner_obj.mobile:
            data.update({
                "phone": partner_obj.mobile,
            })
        elif partner_obj.phone:
            data.update({
                "phone": partner_obj.phone,
            })

        endpoint = "https://api.paystack.co/customer"
        
        bearer_token = "Bearer "+str(customer_data.get("paystack_merchant_key"))
        headers = {"Authorization": bearer_token}

        api_call = requests.post(endpoint, data=data, headers=headers)

        try:
            response = api_call.json()
            return_response = {
                'status': response.get("status"),
                'message': response.get("message"),
                'payment_request_status': "false",
                'payment_request_message': "Payment request not send",
                'payment_request_code': "false",
                'offline_reference': "false",
                'payment_qrcode_url': "false",
            }
            
        except:
            return_response = {
                'status': False,
                'message': "Invalid Secret Key/URL",
                'payment_request_status': "false",
                'payment_request_message': "Payment request not send",
                'payment_request_code': "false",
                'offline_reference': "false",
                'payment_qrcode_url': "false",
            }
                
        if return_response.get("status") == True:
            response_data = response.get("data")
            # create/update paystack pos order in odoo
            get_pos_paystack = self.env["pos.order.paystack"].sudo().search([('pos_receipt_number','=',customer_data.get("receipt_number"))], limit=1)
            if not get_pos_paystack:
                get_pos_paystack = self.env["pos.order.paystack"].sudo().create(
                    {
                        'pos_receipt_number': customer_data.get("receipt_number"),
                        'customer_id': response_data.get("id"),
                        'customer_code': response_data.get("customer_code"),
                        'partner_id': partner_obj.id,
                        'email': partner_obj.email,
                        'currency_id': int(customer_data.get("currency_id")),
                        'amount_untaxed_total': float(customer_data.get("amount_untaxed_total")),
                        'amount_tax_total': float(customer_data.get("amount_tax_total")),
                        'amount_total': float(customer_data.get("amount_total")),
                    }
                )
            else:
                get_pos_paystack.update(
                    {
                        'customer_id': response_data.get("id"),
                        'customer_code': response_data.get("customer_code"),
                        'partner_id': partner_obj.id,
                        'email': partner_obj.email,
                        'currency_id': int(customer_data.get("currency_id")),
                        'amount_untaxed_total': float(customer_data.get("amount_untaxed_total")),
                        'amount_tax_total': float(customer_data.get("amount_tax_total")),
                        'amount_total': float(customer_data.get("amount_total")),
                    }
                )

            payment_data.update({
                "customer": get_pos_paystack.customer_code
            })

            # create payment requests in paystack
            payment_request_response = self.create_paystack_payment_request(customer_data.get("paystack_merchant_key"), payment_data)

            # store paystack payment requests responses in odoo

            if payment_request_response.get("status") == True:
                payment_request_data = payment_request_response.get("data")

                # generate QR Code
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(payment_request_data.get("offline_reference"))
                qr.make(fit=True)
                img = qr.make_image()
                temp = BytesIO()
                img.save(temp, format="PNG")
                qr_image = base64.b64encode(temp.getvalue())

                # create attachment for qr image

                qr_attachment = self.env['ir.attachment'].sudo().create(
                    {
                        'name': payment_request_data.get("offline_reference"),
                        'type': 'binary',
                        'datas': qr_image,
                        'res_model': 'pos.payment.paystack',
                    }
                )

                # create img url
                if qr_attachment:
                    qrcode_url = "/web/image/ir.attachment/{}/datas".format(qr_attachment.id)
                else:
                    qrcode_url = False
                
                if get_pos_paystack.paystack_payment_ids:
                    for pay in get_pos_paystack.paystack_payment_ids:
                        pay.payment_status = "cancelled"

                pos_paystack = self.env["pos.payment.paystack"].sudo().create(
                    {
                        'paystack_pos': get_pos_paystack.id,
                        'response_message': payment_request_response.get("message"),
                        'paystack_payment_id': payment_request_data.get("id"),
                        'paystack_customer_id': payment_request_data.get("customer"),
                        'request_code': payment_request_data.get("request_code"),
                        'offline_reference': payment_request_data.get("offline_reference"),
                        'invoice_number': payment_request_data.get("invoice_number"),
                        'description': payment_request_data.get("description"),
                        'payment_status': payment_request_data.get("status"),
                        'payment_qr_code': qr_image,
                        'payment_qr_code_attachment': qr_attachment.id if qr_attachment else False,
                        'payment_qrcode_img_url': qrcode_url,
                    }
                )

                if pos_paystack:
                    
                    # send payment request to terminal
                    terminal_request_data = {
                                "type": "invoice",
                                "action": "process",
                                "data": {
                                    "id": str(pos_paystack.paystack_payment_id),
                                    "reference": str(pos_paystack.offline_reference),
                                }
                            }
                                            
                    pos_paystack.paystack_terminal_id = paystack_terminal.name
                    terminal_response = self.send_payment_request_to_terminal(customer_data.get("paystack_merchant_key"), paystack_terminal.name, terminal_request_data)

                    _logger.info("@API terminal_response======={}".format(terminal_response))

                    if terminal_response.get("status"):
                        pos_paystack.paystack_terminal_response = terminal_response.get("message")
                        pos_paystack.paystack_terminal_response_id = terminal_response.get("data").get("id") if terminal_response.get("data") else ""
                    else:
                        pos_paystack.paystack_terminal_response = terminal_response.get("message")
                        return_response.update(
                            {
                                "payment_request_status": "false",
                                "payment_request_message": "Problem in terminal: "+str(terminal_response.get("message")),
                                "payment_request_code": pos_paystack.request_code,
                                "offline_reference": pos_paystack.offline_reference,
                                "payment_qrcode_url": pos_paystack.payment_qrcode_img_url,
                            }
                        )
                        return return_response

                    return_response.update(
                        {
                            "payment_request_status": "true",
                            "payment_request_message": payment_request_response.get("message"),
                            "payment_request_code": pos_paystack.request_code,
                            "offline_reference": pos_paystack.offline_reference,
                            "payment_qrcode_url": pos_paystack.payment_qrcode_img_url,
                        }
                    )

                return return_response
            else:
                return_response.update(
                    {
                        "payment_request_status": payment_request_response.get("status"),
                        "payment_request_message": payment_request_response.get("message"),
                        "payment_request_code": "false",
                        "offline_reference": "false",
                        "payment_qrcode_url": "false",
                    }
                )
                return return_response
            
        else:
            return return_response

        return return_response


    def get_latest_paystack_status(self, payment_request_code):
        paystack_payment = self.env["pos.payment.paystack"].sudo().search([('request_code','=',str(payment_request_code))],limit=1)

        if paystack_payment:

            if paystack_payment.payment_status == "pending":
                response = {
                    'status': "waitingCard",
                }
            elif paystack_payment.payment_status == "success":
                response = {
                    'status': "success",
                }
            else:
                response = {
                    'status': paystack_payment.payment_status,
                }
        else:
            response = {
                    'status': "pending",
                }

        return response
    


    def get_paystack_terminal_ids(self):
        if self.open_session_ids:
            raise UserError('Please close and validate the following open PoS Sessions before modifying this payment method.\n'
                            'Open sessions: %s' % (' '.join(self.open_session_ids.mapped('name')),))

        endpoint = "https://api.paystack.co/terminal"

        bearer_token = "Bearer "+str(self.paystack_merchant_key)
        headers = {"Authorization": bearer_token}

        api_call = requests.get(endpoint, headers=headers)
        try:
            response = api_call.json()
        except:
            response = {
                'status': False,
                'message': "Invalid Secret Key/URL"
            }

        
        if response.get("status")==True:
            #unlink existing terminal ids
            self.env['paystack.terminal'].sudo().search([]).unlink()
            for data in response.get("data"):
                # create terminal ids
                terminal_data = {
                    'name': data.get("terminal_id"),
                    'serial_number': data.get("serial_number"),
                    'device_name': data.get("name"),
                    'status': data.get("status"),
                }
                self.env['paystack.terminal'].sudo().create(terminal_data)
        else:
            raise UserError('Invalid Secret Key, Please check the secret key entered!')

    def cron_get_paystack_terminal_ids(self):
        paystack_payment_method = self.env['pos.payment.method'].sudo().search([('use_payment_terminal','=','paystack')],limit=1)

        if paystack_payment_method:
            paystack_payment_method.get_paystack_terminal_ids()

    def create(self, vals):
        res = super(PosPaymentMethod, self).write(vals)
        res.get_paystack_terminal_ids()
        return res
    
    def write(self, vals):
        res =  super(PosPaymentMethod, self).write(vals)
        if vals.get("paystack_merchant_key"):
            #update terminal ids if secret key is changed
            self.get_paystack_terminal_ids()
        return res