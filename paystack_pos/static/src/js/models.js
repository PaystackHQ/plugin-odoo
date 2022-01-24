odoo.define('paystack_pos.models', function (require) {
var models = require('point_of_sale.models');
var PaymentPaystack = require('paystack_pos.payment');

models.register_payment_method('paystack', PaymentPaystack);
models.load_fields('pos.payment.method', 'paystack_merchant_key');
});
