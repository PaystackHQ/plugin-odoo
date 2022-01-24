from odoo import http, _
from odoo.http import request
import datetime
from datetime import datetime
import logging
from odoo.addons.website_sale.controllers.main import WebsiteSale


_logger = logging.getLogger(__name__)


class EcommercePaystackIntegration(WebsiteSale):

    @http.route(['/shop/payment'], type='http', auth="public", website=True, sitemap=False)
    def payment(self, **post):
        order = request.website.sale_get_order()
        print(order.currency_id,'00000000000000000000000')
        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        paystack = request.env['payment.acquirer'].sudo().search([('provider','=','paystack')])
        if paystack:
            paystack_currencies =[]
            for line in  paystack.ecom_allowed_currencies.ids:
                currency = request.env['res.currency'].sudo().browse(line).name
                paystack_currencies.append(currency)
                render_values['paystack_currencies'] = paystack_currencies
                render_values['order_currency'] = order.currency_id.name
                render_values['paystack_id'] = paystack.id

        if render_values['errors']:
            render_values.pop('acquirers', '')
            render_values.pop('tokens', '')

        print(render_values)
        return request.render("website_sale.payment", render_values)


    @http.route(['/paystack/response'], type='http', auth="public", website=True)
    def paystack_transaction_check_response(self, **post):
        if post.get("reference"):
            transaction = request.env['payment.transaction'].sudo().search([('acquirer_reference','=',str(post.get("reference")))],limit=1)
            print("transaction")
            if request.session.get("sale_order_id"):
                sale_order = request.env['sale.order'].sudo().browse(int(request.session.get("sale_order_id")))
            else:
                sale_order = False

            if transaction:
                if transaction.acquirer_id.state in ["enabled", "test"]:
                    # verify payment done
                    response = transaction.acquirer_id.call_paystack_transaction_verify(transaction.acquirer_reference)

                    if response.get("status")==True:
                        if sale_order:
                            try:
                                
                                verified_data = response.get("data")
                                if verified_data.get('status') == "success":
                                    authorization_data = response.get("data").get("authorization")
                                    try:
                                        paid_date = datetime.strptime(verified_data.get('paid_at'), "%Y-%m-%dT%H:%M:%S.000Z")
                                        
                                    except:
                                        paid_date = datetime.now()
                                    
                                    transaction_state = 'done'
                                    sale_order.with_context(send_email=True).action_confirm()
                                    try:
                                        fees = float(verified_data.get("fees"))/100
                                    except:
                                        fees = 0
                                    transaction.update({
                                        'date': datetime.now(),
                                        'paystack_verified_transaction_detail': str(verified_data),
                                        'fees':fees,
                                        'state': transaction_state,

                                        'paystack_verification_status': verified_data.get('status'),
                                        'paystack_gateway_response': verified_data.get('gateway_response'),
                                        'paystack_paid_at': paid_date,
                                        'paystack_ip_address': verified_data.get('ip_address'),
                                        'paystack_channel': verified_data.get('channel'),

                                        'paystack_authorization_code': authorization_data.get('authorization_code') if authorization_data else '',
                                        
                                        'paystack_bin': authorization_data.get('bin') if authorization_data else '',

                                        'paystack_last4': authorization_data.get('last4') if authorization_data else '',

                                        'paystack_card_type': authorization_data.get('card_type') if authorization_data else '',

                                        'paystack_bank': authorization_data.get('bank') if authorization_data else '',

                                        'paystack_country_code': authorization_data.get('country_code') if authorization_data else '',

                                        'paystack_signature': authorization_data.get('signature') if authorization_data else '',

                                        'paystack_account_name': authorization_data.get('account_name') if authorization_data else '',
                                        
                                    })

                                    try:
                                        transaction._cron_post_process_after_done()
                                    except:
                                        pass
                                else:
                                    transaction_state = 'error'
                                    try:
                                        fees = float(verified_data.get("fees"))/100
                                    except:
                                        fees = 0
                                    transaction.update({
                                        'date': datetime.now(),
                                        'paystack_verified_transaction_detail': str(verified_data),
                                        'fees':fees,
                                        'state': transaction_state,
                                    })

                            
                            except:
                                
                                verified_data = response.get("data")
                                if verified_data.get('status') == "success":
                                    authorization_data = response.get("data").get("authorization")

                                    try:
                                        paid_date = datetime.strptime(verified_data.get('paid_at'), "%Y-%m-%dT%H:%M:%S.000Z")
                                        
                                    except:
                                        paid_date = datetime.now()

                                    sale_order.state="sent"
                                    try:
                                        fees = float(verified_data.get("fees"))/100
                                    except:
                                        fees = 0

                                    transaction.update({
                                        'date': datetime.now(),
                                        'paystack_verified_transaction_detail': str(verified_data),
                                        'fees':fees,
                                        'state': transaction_state,

                                        'paystack_verification_status': verified_data.get('status'),
                                        'paystack_gateway_response': verified_data.get('gateway_response'),
                                        'paystack_paid_at': paid_date,
                                        'paystack_ip_address': verified_data.get('ip_address'),
                                        'paystack_channel': verified_data.get('channel'),

                                        'paystack_authorization_code': authorization_data.get('authorization_code') if authorization_data else '',
                                        
                                        'paystack_bin': authorization_data.get('bin') if authorization_data else '',

                                        'paystack_last4': authorization_data.get('last4') if authorization_data else '',

                                        'paystack_card_type': authorization_data.get('card_type') if authorization_data else '',

                                        'paystack_bank': authorization_data.get('bank') if authorization_data else '',
                                        
                                        'paystack_country_code': authorization_data.get('country_code') if authorization_data else '',

                                        'paystack_signature': authorization_data.get('signature') if authorization_data else '',

                                        'paystack_account_name': authorization_data.get('account_name') if authorization_data else '',
                                    })

                                    try:
                                        transaction._cron_post_process_after_done()
                                    except:
                                        pass
                                    
                                else:
                                    transaction_state = 'error'
                                    try:
                                        fees = float(verified_data.get("fees"))/100
                                    except:
                                        fees = 0
                                    transaction.update({
                                        'date': datetime.now(),
                                        'paystack_verified_transaction_detail': str(verified_data),
                                        'fees':fees,
                                        'state': transaction_state,
                                    })
                             
                            # try:
                            #     wiz_id = request.env['sale.advance.payment.inv'].sudo().create({"advance_payment_method": "delivered"})
                            #     wiz_id.with_context(active_ids=sale_order.id).sudo().create_invoices()
                            #     if sale_order.invoice_ids:
                            #         sale_order.invoice_ids[0].sudo().action_post()
                            # except:
                            #     pass
                    else:
                        if sale_order:
                            sale_order.state = "sent"
                        transaction.update({
                            'paystack_verified_transaction_detail': str(response),
                            'state': 'pending',
                        })

                    
                    return request.redirect("/shop/payment/validate")
                    
                # if transaction.acquirer_id.state=="test":
                #     if sale_order:
                #         try:
                #             sale_order.with_context(send_email=True).action_confirm()
                            
                #             transaction.update({
                #                 'date': datetime.now(),
                #                 'state': 'done',
                #             })
                            
                #             transaction._cron_post_process_after_done()
                #         except:
                #             sale_order.state = "sent"
                            
                #             transaction.update({
                #                 'date': datetime.now(),
                #                 'state': 'done',
                #             })
           

                #     return request.redirect("/shop/payment/validate")
                if transaction.acquirer_id.state=="disabled":
                    return request.redirect("/shop/confirmation")
            else:
                return request.redirect("/shop/confirmation")
        else:
            return request.redirect("/shop")
