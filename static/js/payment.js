$(function() {
    var $form = $("#payment-form");
  
    $form.on('submit', function(e) {
      if (!$form.data('cc-on-file')) {
        e.preventDefault();
        Stripe.setPublishableKey($form.data('stripe-publishable-key'));
        var expMonthAndYear = $('input[name=expiry]').val().split(" / ");
        Stripe.card.createToken({
          number: $('.card-number').val(),
          cvc: $('.card-cvc').val(),
          exp_month: expMonthAndYear[0],
          exp_year: expMonthAndYear[1],
        }, stripeResponseHandler);
      }
    });
  
    function stripeResponseHandler(status, response) {
      if (response.error) {
        $('.error')
          .removeClass('hide')
          .find('.alert')
          .text(response.error.message);
      } else {
        // token contains id, last4, and card type
        var token = response['id'];
        // insert the token into the form so it gets submitted to the server
        $form.find('input[type=text]').empty();
        $form.append("<input type='hidden' name='reservation[stripe_token]' value='" + token + "'/>");
        $form.get(0).submit();
      }
    }
  })