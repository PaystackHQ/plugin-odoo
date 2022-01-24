odoo.define('paystack_pos.payment', function (require) {
"use strict";

var core = require('web.core');
var rpc = require('web.rpc');
var PaymentInterface = require('point_of_sale.PaymentInterface');
const { Gui } = require('point_of_sale.Gui');

var _t = core._t;

const delay = ms => new Promise(res => setTimeout(res, ms));


var PaymentPaystack = PaymentInterface.extend({

    send_payment_request: function (cid,payment_obj=false) {
        
        this._super.apply(this, arguments);
        this._reset_state();
        if(payment_obj)
        {
            return this._paystack_pay(payment_obj);
        }
        else
        {
            return this._paystack_pay();
        }
        
    },

    send_payment_cancel: function () {

        this._super.apply(this, arguments);
        
        // set only if we are polling
        this.was_cancelled = !!this.polling;
        clearTimeout(this.polling);
        var line = this.pos.get_order().selected_paymentline;
        line.set_payment_status('retry');
        
        return Promise.resolve(true);
    },

    close: function () {
        this._super.apply(this, arguments);
    },

    // private methods
    _reset_state: function () {
        this.was_cancelled = false;
        this.last_diagnosis_service_id = false;
        this.remaining_polls = 2;
        clearTimeout(this.polling);
    },

    _handle_odoo_connection_failure: function (data) {
        // handle timeout
        var line = this.pos.get_order().selected_paymentline;
        if (line) {
            line.set_payment_status('retry');
        }
        this._show_error(_t('Could not connect to the Odoo server, please check your internet connection and try again.'));

        return Promise.reject(data); // prevent subsequent onFullFilled's from being called
    },

    _paystack_pay: function (payment_obj=false) {
        var self = this;

        if(!this.pos.get_order().attributes.client)
        {
            if(payment_obj)
            {
                var cid = self.pos.get_order().selected_paymentline.cid;
                payment_obj.deletePaymentLine({ detail: { cid: cid } });
            }
            
            this._show_error(_t('Please select the customer to proceed'));
            return Promise.resolve();
        }
        else
        {
            if(!this.pos.get_order().attributes.client.email)
            {
                if(payment_obj)
                {
                    var cid = self.pos.get_order().selected_paymentline.cid;
                    payment_obj.deletePaymentLine({ detail: { cid: cid } });
                }

                this._show_error(_t('The selected customer does not have email address.'));
                return Promise.resolve();
            }
        }

        if (this.pos.get_order().selected_paymentline.amount < 0) {

            if(payment_obj)
            {
                var cid = self.pos.get_order().selected_paymentline.cid;
                payment_obj.deletePaymentLine({ detail: { cid: cid } });
            }

            this._show_error(_t('Cannot process transactions with negative amount.'));
            return Promise.resolve();
        }

        // creating customer
        var partner_id = this.pos.get_order().attributes.client.id;
        var paystack_merchant_key = this.payment_method.paystack_merchant_key;
        var receipt_number = this.pos.attributes.selectedOrder.name;
        var currency_id = this.pos.currency.id;

        var line_items = [];

        var pos_order_lines = this.pos.get_order().orderlines.models;

        var total_line_amount = 0;
        var total_amount = this.pos.attributes.selectedOrder.paymentlines.models[0].amount;
        for (var i in pos_order_lines) {
            var product_data = pos_order_lines[i];

            var items = {
                "name": product_data.product.display_name,
                "amount": Math.round(product_data.price.toFixed(2) * 100),
                "quantity": product_data.quantity,
            }

            line_items.push(items);
            total_line_amount =  total_line_amount + (product_data.price * product_data.quantity);
            
        }

        var total_tax_amount = total_amount - total_line_amount;

        var tax_item = [];
        
        if(total_tax_amount.toFixed(2)!=0.00 && total_tax_amount.toFixed(2)!=0)
        {
            tax_item.push(
                {
                "name": "Tax",
                "amount": Math.round(total_tax_amount.toFixed(2) * 100),
            })
        }

        var customer_data = {
            "partner_id": partner_id,
            "paystack_merchant_key": paystack_merchant_key,
            "receipt_number": receipt_number,
            "currency_id": currency_id,
            "amount_untaxed_total": total_line_amount,
            "amount_tax_total": total_tax_amount,
            "amount_total": total_amount,
        };
        
        var payment_data = {
            "description": "Invoice for receipt: "+receipt_number,
            "line_items": line_items,
            "tax": tax_item,
        };

        $.ajax({
            url: "/paystack/payment/initiate",
            type: 'POST',
            data:{
                "pos_config_id": this.pos.config_id,
                "payment_method_id": self.payment_method.id,
                "customer_data": JSON.stringify(customer_data),
                "payment_data": JSON.stringify(payment_data),
            },
            async : false,
            success: function(result){
                var backend_result = jQuery.parseJSON(result);
                var paystack_status = backend_result['status'];
                var payment_request_status = backend_result['payment_request_status'];
                if(!paystack_status)
                {
                    localStorage.setItem("paystack_status", "false");
                    localStorage.setItem("paystack_message", backend_result['message']);           
                    
                }
                else
                {
                    localStorage.setItem("paystack_status", "true");
                    localStorage.setItem("paystack_message", backend_result['message']);
                }

                if(payment_request_status == "false")
                {
                    localStorage.setItem("payment_request_status", "false");
                    localStorage.setItem("payment_request_message", backend_result['payment_request_message']);   
                    localStorage.setItem("payment_request_code", "false");           

                    
                }
                else
                {
                    localStorage.setItem("payment_request_status", "true");
                    localStorage.setItem("payment_request_message", backend_result['payment_request_message']);  
                    localStorage.setItem("payment_request_code", backend_result['payment_request_code']);
                    localStorage.setItem("offline_reference", backend_result['offline_reference']);
                    localStorage.setItem("payment_qrcode_url", backend_result['payment_qrcode_url']);

                }
            
            },
        });

        var paystack_status = localStorage.getItem("paystack_status");
        var paystack_message = localStorage.getItem("paystack_message");        

        if (paystack_status=="false")
        {
            if(payment_obj)
            {
                var cid = self.pos.get_order().selected_paymentline.cid;
                payment_obj.deletePaymentLine({ detail: { cid: cid } });
            }

            this._show_error(_t(paystack_message));
            return Promise.resolve();
    
        }

        var payment_request_status = localStorage.getItem("payment_request_status");
        var payment_request_message = localStorage.getItem("payment_request_message");
        var payment_request_code = localStorage.getItem("payment_request_code");
        var offline_reference = localStorage.getItem("offline_reference");
        var payment_qrcode_url = localStorage.getItem("payment_qrcode_url");


        if (payment_request_status=="false")
        {
            if(payment_obj)
            {
                var cid = self.pos.get_order().selected_paymentline.cid;
                payment_obj.deletePaymentLine({ detail: { cid: cid } });
            }

            this._show_error(_t(payment_request_message));
            return Promise.resolve();
    
        }

        if (payment_request_status=="true")
        {
            var line = this.pos.get_order().selected_paymentline;
            line.set_payment_status('waiting');

            this.pos.get_order().selected_paymentline["offline_reference"] = offline_reference;
            this.pos.get_order().selected_paymentline["payment_qrcode_url"] = payment_qrcode_url;

            $("#pos_paystack_qrcode_click").click();
            
            // return Promise.resolve(true);
    
        }

        var res = new Promise(function () {
            // clear previous intervals just in case, otherwise
            // it'll run forever
            clearTimeout(self.polling);

            self.polling = setInterval(function () {
                self._paystack_poll_for_response(payment_request_code,payment_obj);
            }, 3000);
        });

        // make sure to stop polling when we're done
        res.finally(function () {
            self._reset_state();
        });

        return res;
    },


    _paystack_poll_for_response: function (payment_request_code,payment_obj) {
        var self = this;
        
        return rpc.query({
            model: 'pos.payment.method',
            method: 'get_latest_paystack_status',
            args: [[this.payment_method.id],payment_request_code],
        }, {
            timeout: 5000,
            shadow: true,
        }).catch(function (data) {
            Promise.reject();
            return self._handle_odoo_connection_failure(data);
        }).then(function (response_status) {
  
            var order = self.pos.get_order();
            var line = order.selected_paymentline;

            if (line)
            {
                if(line.payment_method.use_payment_terminal=="paystack")
                {
                    if(response_status.status == "failed")
                    {
                        line.set_payment_status('force_done');
                    }
                    else
                    {
                        if(response_status.status == "pending")
                        {
                            
                            line.set_payment_status('waiting');
                        }
                        else
                        {
                            if(response_status.status == "success")
                            {
                                line.set_payment_status('done');
                                if(payment_obj)
                                {
                                    payment_obj.validateOrder(true);
                                }

                            }
                            else
                            {
                                if(response_status.status == "waitingCard")
                                {
                                    line.set_payment_status('waitingCard');
                                }
                                else
                                {
                                    line.set_payment_status('retry');
                                }
                                
                            }
                        }
                        
                    }

                }
            
            }            

            Promise.resolve(true);

        });
    },

    _show_error: function (msg, title) {
        if (!title) {
            title =  _t('Paystack Error');
        }
        Gui.showPopup('ErrorPopup',{
            'title': title,
            'body': msg,
        });
    },

});

return PaymentPaystack;
});
