import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class PaystackTerminal(models.Model):
    _name = 'paystack.terminal'

    _description = "Paystack Terminal master"

    name = fields.Char(string="Terminal ID")

    serial_number = fields.Char(string="Serial Number")

    device_name = fields.Char(string="Terminal Name")

    status = fields.Char(string="Status")
    
