function _3dsec(stripe_publishable_key, pi_secret) {
    document.addEventListener("DOMContentLoaded", function(event){
      loading(true);
      var stripe = Stripe(stripe_publishable_key);
      stripe.confirmCardPayment(pi_secret).then(function(result) {
        if (result.error) {
          // Display error.message in your UI.
          loading(false);
          var errorElement = document.getElementById('3ds_result');
          errorElement.textContent = result.error.message;
          $("#3ds_result").addClass("text-danger");
        } else {
          loading(false);
          // The payment has succeeded. Display a success message.
          $("#3ds_result").text("Thank you for payment");
          $("#3ds_result").addClass("text-success");
        }
      });
    }); // DOMContentLoaded
}



var loading = function(isLoading) {
  if (isLoading) {
    // Disable the button and show a spinner
    document.querySelector("#button-submit").disabled = true;
    document.querySelector('.spinner-border').classList.remove("hide-logo");
    document.querySelector("#button-submit").classList.add("hide-logo");
  } else {
      document.querySelector("#button-submit").disabled = false;
      document.querySelector('.spinner-border').classList.add("hide-logo");
      document.querySelector("#button-submit").classList.remove("hide-logo");
  }
};


function my_onkeydown_handler( event ) {
  switch (event.keyCode) {
      case 116 : // 'F5'
          event.preventDefault();
          event.keyCode = 0;
          window.status = "F5 disabled";
          break;
  }
}
document.addEventListener("keydown", my_onkeydown_handler);