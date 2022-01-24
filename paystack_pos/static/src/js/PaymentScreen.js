odoo.define('paystack_pos.PaymentScreen', function (require) {
    'use strict';

    const { _t } = require('web.core');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const Registries = require('point_of_sale.Registries');

    const PosPaystackPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {

            /**
             * @override
             */
            addNewPaymentLine({ detail: paymentMethod }) {
                const order = this.env.pos.get_order();
                const res = super.addNewPaymentLine(...arguments);

                if(this.selectedPaymentLine.payment_method.use_payment_terminal=="paystack")
                {
                    var payment_terminal = this.selectedPaymentLine.payment_method.payment_terminal;
                
                    var cid = this.selectedPaymentLine.cid;
                    
                    payment_terminal.send_payment_request(cid,this);

                    // this.deletePaymentLine({ detail: { cid: cid } });
                }            
            }
        };

    Registries.Component.extend(PaymentScreen, PosPaystackPaymentScreen);

    return PaymentScreen;
});
