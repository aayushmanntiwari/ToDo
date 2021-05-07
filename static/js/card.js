function card(key,email) {
    /*document.addEventListener('DOMContentLoaded',function(event) {*/
        var stripe = Stripe(key)
        var elements = stripe.elements();
        var cardNumberElement = elements.create('card',{
            classes : {
                base: "form-control",
                /* adding custom class and css to strip field  */
                focus: "green",
                invalid:'error'
            },
            style : {
                base : {
                    color:'green'
                }
            }
        });
        /*var cvc = elements.create('cardCvc',{
            classes : {
                base: "form-control",
                focus: "green",
                invalid:'error'
            },
            style : {
                base : {
                    color:'green'
                }
            }
        });
        var exp = elements.create('cardExpiry',{
            classes : {
                base: "form-control",
                focus: "green",
                invalid:'error'
            },
            style : {
                base : {
                    color:'green'
                }
            }
        });*/
        cardNumberElement.mount('#card-number');
        //cvc.mount('#card-cvc');
        //exp.mount('#card-exp');

        //handle real-time validation errors from the card element
        cardNumberElement.addEventListener('change',function(event){
            var displayError = document.getElementById('card-errors');
            if (event.error){
                displayError.textContent = event.error.message;
            }
            else{
                displayError.textContent = '';
            }
        });

        //handle form submission .
        var form = document.getElementById('payment-form');
        form.addEventListener('submit',function(event) {
            loading(true);
            event.preventDefault();
            stripe.createToken(cardNumberElement).then(function(result){
                if (result.error){
                    loading(false);
                    // inform user if ther eis nay error
                    var errorElement = document.getElementById('card-errors');
                    errorElement.textContent = result.error.message;
                }
                else{
                    //send the token to your server
                    // Create Payment Method BEGIN
                    stripe.createPaymentMethod({
                        type: 'card',
                        card: cardNumberElement,
                        billing_details: {
                        email: email,
                        },
                    }).then(function(payment_method_result){ 
                        if (payment_method_result.error) {
                        var errorElement = document.getElementById('card-errors');
                        errorElement.textContent = payment_method_result.error.message;
                        } else {
                        var form = document.getElementById('payment-form');
                        var hiddenInput = document.createElement('input');
                        hiddenInput.setAttribute('type', 'hidden');
                        hiddenInput.setAttribute('name', 'payment_method_id');
                        hiddenInput.setAttribute('value', payment_method_result.paymentMethod.id);
                        console.log(payment_method_result.paymentMethod.id)
                        form.appendChild(hiddenInput);
                        // Submit the form
                        form.submit();
                        };
                    });
                    // Create Payment Method END
                }
            });
        });

        //submit the form with token id
        /*function stripeTokenHandler(token){
            console.log(token)
            form.submit();
        }*/
/*});*/
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