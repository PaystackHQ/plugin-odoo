import json
import logging
import pprint
import random
import requests
import string
from werkzeug.exceptions import Forbidden

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class PaystackPosOrder(models.Model):
    _name = 'pos.order.paystack'
    _description = "Handling the POS order through paystack"

    _rec_name = "pos_receipt_number"

    customer_id = fields.Char(string="Paystack Customer Id")
    customer_code = fields.Char(string="Paystack Customer Code")
    partner_id = fields.Many2one(comodel_name="res.partner",string="Odoo Partner")
    email = fields.Char(string="email")

    pos_receipt_number = fields.Char(string="Pos Receipt Number")
    pos_order = fields.Many2one(comodel_name="pos.order", string="Pos Order", compute="_compute_pos_order")

    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency')

    amount_untaxed_total = fields.Monetary(string='Untaxed amount', currency_field='currency_id')
    
    amount_tax_total = fields.Monetary(string='Tax amount', currency_field='currency_id')

    amount_total = fields.Monetary(string='Total amount', currency_field='currency_id')

    paystack_payment_ids = fields.One2many("pos.payment.paystack","paystack_pos")

    @api.depends("pos_receipt_number")
    def _compute_pos_order(self):
        for pos in self:
            if pos.pos_receipt_number:
                get_pos_order = self.env['pos.order'].sudo().search([('pos_reference','=',pos.pos_receipt_number)],limit=1)

                if get_pos_order:
                    pos.pos_order = get_pos_order.id
                else:
                    pos.pos_order = False
            else:
                pos.pos_order = False

class PaystackPosPayment(models.Model):
    _name = 'pos.payment.paystack'

    _description = "Handling the paystack payment details for the POS order"

    paystack_pos = fields.Many2one(comodel_name="pos.order.paystack", string="Paystack POS Order")

    customer_code = fields.Char(string="Customer Code", related="paystack_pos.customer_code", store=True)

    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related="paystack_pos.currency_id", store=True)

    transaction_reference = fields.Char(string="Transaction Reference")
    event_triggered = fields.Char(string="Event Triggered")
    
    response_message = fields.Char(string="Response Message")
    gateway_response = fields.Char(string="Gateway Response")

    paystack_payment_id = fields.Char(string="Payment Id")
    paystack_terminal_id = fields.Char(string="Terminal Id")
    paystack_terminal_response = fields.Char(string="Payment Terminal Status")
    paystack_terminal_response_id = fields.Char(string="Terminal Response Id")

    paystack_customer_id = fields.Char(string="Customer Id")
    request_code = fields.Char(string="Request Code")
    offline_reference = fields.Char(string="Offline Reference")
    invoice_number = fields.Char(string="Invoice Number")
    description = fields.Char(string="Description")
    payment_status = fields.Char(string="Payment Status")

    payment_qr_code = fields.Binary("Payment QR Code")

    payment_qr_code_attachment = fields.Many2one(comodel_name="ir.attachment", string="QR Code Attachment")

    payment_qrcode_img_url = fields.Char(string="QR Code Img Url")

    # additional fees
    fees = fields.Monetary(string='Fees', currency_field='currency_id')

    flat_rate = fields.Monetary(string='Flat rate', currency_field='currency_id')
    charge_percentage = fields.Float(string='Charge (%)')
    international_charge_percentage = fields.Float(string='International charge (%)')
    flat_threshhold = fields.Monetary(string='Flat thershold', currency_field='currency_id')
    transfer_charge = fields.Monetary(string='Transfer charge', currency_field='currency_id')

    paystack_paid_at = fields.Datetime(string="Paid at")

    # authorization
    ip_address = fields.Char(string="IP address")
    authorization_code = fields.Char(string="Authorization Code")
    paystack_channel = fields.Char(string="Channel")
    paystack_bin = fields.Char(string="bin")
    paystack_last4 = fields.Char(string="last4")
    paystack_card_type = fields.Char(string="Card Type")
    paystack_bank = fields.Char(string="Bank")
    paystack_country_code = fields.Char(string="Country Code")
    paystack_signature = fields.Char(string="Electronic Signature")
    paystack_account_name = fields.Char(string="Account name")
    
