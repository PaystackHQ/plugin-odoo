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

class AccountMoveReversalInherit(models.TransientModel):
    _inherit = 'account.move.reversal'

    def _prepare_default_reversal(self, move):
        res = super(AccountMoveReversalInherit, self)._prepare_default_reversal(move)

        res.update({
            'transaction_ids': move.transaction_ids,
        })

        return res


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMoveInherit, self).action_post()

        for move in self:
            if move.move_type == "out_refund":
                for transaction in move.transaction_ids:
                    if transaction.acquirer_id.provider == "paystack":
                        data = {
                            'transaction': transaction.acquirer_reference,
                            'amount': round(transaction.amount, 2)*100,
                            'currency': transaction.currency_id.name,
                            'customer_note': move.ref,
                        }

                        refund_initiate = transaction.sudo().acquirer_id.call_paystack_transaction_refund(data)

                        if refund_initiate.get("status") ==  True:
                            refund_data = dict(refund_initiate.get("data"))
                            transaction.paystack_refund = True
                            paystack_refund = self.env['payment.paystack.refund'].create({
                                'transaction_id': transaction.id,
                                'paystack_refund_status': "Refund Initiated",
                                'paystack_refund_message': refund_initiate.get("message"),
                                'refund_details': str(refund_initiate),
                                # 'dispute': str(refund_data.get("dispute")),
                                'refund_id': refund_data.get("id"),
                                'refund_amount': int(refund_data.get("amount"))/100,
                                'refund_fees': float(refund_data.get("fees")) if refund_data.get("fees") else 0.00,
                                'refunded_by': refund_data.get("refunded_by"),
                                # 'refunded_at': refund_data.get("refunded_at"),
                                'expected_at': refund_data.get("expected_at"),
                                'created_at': refund_data.get("createdAt"),
                                'updated_at': refund_data.get("updatedAt"),
                                'refund_customer_note': refund_data.get("customer_note"),
                                'refund_merchant_note': refund_data.get("merchant_note"),
                            })
                        else:
                            transaction.paystack_refund = True
                            paystack_refund = self.env['payment.paystack.refund'].create({
                                'transaction_id': transaction.id,
                                'paystack_refund_status': "Refund Failed",
                                'paystack_refund_message': refund_initiate.get("message"),
                                'refund_details': str(refund_initiate),
                                
                            })

        return res