function pos_paystack_qrcode_click(obj) {

  payment_method = this.posmodel.get_order().selected_paymentline;

  no_qrcode = '<h3>QR CODE GENERATE HERE </h3><h4>Before that you must send payment request to the customer.</h4>';

  if(payment_method.payment_qrcode_url && payment_method.offline_reference)
  {
    if(payment_method.payment_qrcode_url!="false" && payment_method.offline_reference!="false")
    {
      offline_reference = '<h3>'+payment_method.offline_reference+'</h3>';
      qrcode_image = '<img src="'+payment_method.payment_qrcode_url+'"/>';
  
      qrcode = offline_reference+qrcode_image;
  
      $("#paystack_qrcode_popup_id").replaceWith("<div class='content' id='paystack_qrcode_popup_id'>"+qrcode+"</div>");
  
    }
    else
    {
      $("#paystack_qrcode_popup_id").replaceWith("<div class='content' id='paystack_qrcode_popup_id'>"+no_qrcode+"</div>");
  
    }
  }
  else
  {
    $("#paystack_qrcode_popup_id").replaceWith("<div class='content' id='paystack_qrcode_popup_id'>"+no_qrcode+"</div>");
  }
 
  

}


// $(".paystack_qrcode_close").click();
