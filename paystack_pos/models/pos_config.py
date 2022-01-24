import logging
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

class POSConfig(models.Model):
    _inherit = 'pos.config'

    def get_first_paystack_terminal_id(self):
        terminal_id = self.env['paystack.terminal'].sudo().search([],limit=1)
        return terminal_id.id if terminal_id else False

    paystack_terminal = fields.Many2one(comodel_name="paystack.terminal", string="Paystack Terminal", default=get_first_paystack_terminal_id)