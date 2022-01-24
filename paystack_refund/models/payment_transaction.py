from odoo.exceptions import ValidationError, UserError, Warning
from odoo import api, fields, models
from datetime import datetime
from werkzeug import urls
import json
import base64
import string
import requests
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PaymentTransactionInherit(models.Model):
    _inherit = 'payment.transaction'

    paystack_refund_ids = fields.One2many("payment.paystack.refund","transaction_id","Paystack Refund Details")
    
    paystack_refund = fields.Boolean(default=False)

class PaymentPaystackRefund(models.Model):
    _name = 'payment.paystack.refund'

    _description = "Paystack Refund Details"

    transaction_id = fields.Many2one(comodel_name="payment.transaction", string="Transaction")

    currency_id = fields.Many2one(comodel_name='res.currency', string='Currency', related="transaction_id.currency_id", store=True)

    paystack_refund_status = fields.Char(string="Refund Status")
    paystack_refund_message = fields.Char(string="Refund Message")

    refund_details = fields.Text(string="Paystack Refund Details")

    # dispute = fields.Char(string="dispute")
    refund_id = fields.Char(string="Refund Id")

    refund_amount = fields.Monetary(string='Refund amount', currency_field='currency_id')
    refund_fees = fields.Monetary(string='Refund fees', currency_field='currency_id')
    refunded_by = fields.Char(string="Refunded By")
    # refunded_at = fields.Char(string="Refunded at")
    expected_at = fields.Char(string="Expected at")
    created_at = fields.Char(string="Created at")
    updated_at = fields.Char(string="Updated at")
    refund_customer_note = fields.Char(string="Refund Customer Note")
    refund_merchant_note = fields.Char(string="Refund Merchant Note")



