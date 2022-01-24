from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PaymentTransactionInherit(models.Model):
    _inherit = 'payment.transaction'
    
    # after payment
    paystack_verified_transaction_detail = fields.Text(string="Paystack Transaction Details")

    paystack_verification_status = fields.Char(string="Verification Status")
    paystack_gateway_response = fields.Char(string="Gateway Response")

    
    paystack_authorization_code = fields.Char(string="Authorization code")
    paystack_channel = fields.Char(string="Channel")
    paystack_bin = fields.Char(string="bin")
    paystack_last4 = fields.Char(string="last4")
    paystack_card_type = fields.Char(string="Card Type")
    paystack_bank = fields.Char(string="Bank")
    paystack_country_code = fields.Char(string="Country Code")
    paystack_signature = fields.Char(string="Electronic Signature")
    paystack_account_name = fields.Char(string="Account name")
    paystack_paid_at = fields.Datetime(string="Paid at")
    paystack_ip_address = fields.Char(string="IP address")


