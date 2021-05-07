import stripe
import logging
import json
from django.shortcuts import render,redirect
from django.http import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User,Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings
from random import randint
from .strip import Plan,set_paid_until
from encrypt import Decode,Encode,Todict
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User

# Create your views here.

logger = logging.getLogger(__name__)

@login_required(login_url='/auth/sign-in/')
@api_view(['POST'])
def validate_plan(request):
    id = Encode(str(randint(10**(9-1), (10**9)-1)))
    plan = request.POST.get('plan')
    automatic = request.POST.get('automatic','off')
    payment_method_type = request.POST.get('payment_method')
    if payment_method_type == "card" and plan!="Please Choose a Plan":
        context = {}
        context['request'] = Encode(Decode(id))
        context['plan'] = Encode(plan)
        context['automatic'] = Encode(automatic)
        context['payment_method_type'] = Encode(payment_method_type)
        Encoded_string = Todict(context)
        return redirect('/payment_type_card/?%s'%Encoded_string)
    elif payment_method_type == "paypal" and plan!="Please Choose a Plan":
        messages.info(request,"This payment method is not yet integreted, please user other options.")
        return redirect(f'/?upgradetopro=show&request={id}')
    else:
        messages.info(request,"Please Choose a Plan !")
        return redirect(f'/?upgradetopro=show&request={id}')

@login_required(login_url='/auth/sign-in/')
@api_view(['GET','POST'])
def card(request):
    context = {}
    stripe.api_key =  settings.STRIPE_SECRET_KEY
    plan = Decode(request.GET.get('plan'))
    automatic = Decode(request.GET.get('automatic'))
    payment_method_type = Decode(request.GET.get('payment_method_type'))
    plan_instant = Plan(plan)
    amount = plan_instant.amount
    tax = plan_instant.tax_rate.rate
    interval = plan_instant.id
    if request.method == 'POST':
        content = {}
        try:
            payment_intent = stripe.PaymentIntent.create(amount=int(amount),currency=plan_instant.currency,payment_method_types=["card"],receipt_email=request.user.email)
        except stripe.error.CardError as e:
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
        except stripe.error.RateLimitError as e:
                    # Too many requests made to the API too quickly
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
                
        except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
        except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
        except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                    messages.info(request,e.user_message)
                    return redirect('/')
        except stripe.error.StripeError as e:
                    # Display a very generic error to the user, and maybe send
                    # yourself an email
                    messages.info(request,e.user_message)
                    return redirect('/')
        except stripe.error.InvalidRequestError as e:
                    messages.info(request,e.user_message)
                    return redirect('/')
        except Exception as e:
                    # Something else happened, completely unrelated to Stripe
                    messages.info(request,e.user_message)
                    return redirect('/')
        content['key'] = Encode(payment_intent.client_secret)
        content['payment_intent_id'] = Encode(payment_intent.id)
        content['payment_method_id'] = Encode(request.POST.get('payment_method_id'))
        content['subscrption_id'] = Encode(plan_instant.stripe_plan_id)
        content['automatic'] = Encode(automatic)
        Encoded_string = Todict(content)
        return redirect('/sending/?%s'%Encoded_string) 
    else:
        context['showcard'] = True
        context['plan'] = plan
        context['automatic'] = automatic
        context['payment_method_type'] = payment_method_type
        context['interval'] = interval
        context['amount'] = amount
        context['STRIPE_PUBLISHABLE_KEY'] = settings.STRIPE_PUBLISHABLE_KEY
        context['customer_email'] = request.user.email
        return render(request,'index.html',context)

@login_required(login_url='/auth/sign-in/')
@api_view(['GET','POST'])
def payment(request):
    stripe.api_key =  settings.STRIPE_SECRET_KEY
    payment_intent_id =  Decode(request.GET.get('payment_intent_id'))
    payment_method_id = Decode(request.GET.get('payment_method_id'))
    plan_id = Decode(request.GET.get('subscrption_id'))
    automatic = Decode(request.GET.get('automatic'))
    
    #If user will be charge automatically based on there subscrption selection 
    if automatic == 'on':
            #creating customer
            try:
                customer = stripe.Customer.create(
                    email = request.user.email,
                    name = request.user.first_name + request.user.last_name,
                    payment_method = payment_method_id,
                    description = 'subscrption charge automatically',
                    invoice_settings = {
                        'default_payment_method':payment_method_id
                    }
                )


                #creating subscrption
                s = stripe.Subscription.create(
                    customer= customer.id,
                    items=[
                        {"plan": plan_id},
                    ],
                )

                latest_invoice = stripe.Invoice.retrieve(s.latest_invoice)

                ret = stripe.PaymentIntent.confirm(latest_invoice.payment_intent)
                #3-d secure authication validation
                if ret.status == "succeeded":
                    messages.info(request,"Payment successful,Thank you!")
                    return redirect('/')
                elif ret.status == 'requires_action':
                    context = {}
                    pi = stripe.PaymentIntent.retrieve(
                        latest_invoice.payment_intent,
                    )
                    context['payment_intent_secret'] = Encode(pi.client_secret)
                    context['authenticatedSecure'] = 'show'
                    context['stripe_publishable_key'] = Encode(settings.STRIPE_PUBLISHABLE_KEY)
                    context['showupgradeplan'] = False
                    Encoded_string = Todict(context)
                    return redirect('/?%s'%Encoded_string)
            except stripe.error.CardError as e:
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
            except stripe.error.RateLimitError as e:
                    # Too many requests made to the API too quickly
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
            except stripe.error.InvalidRequestError as e:
                    # Invalid parameters were supplied to Stripe's API
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
            except stripe.error.AuthenticationError as e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    # Since it's a decline, stripe.error.CardError will be caught
                    messages.info(request,e.user_message)
                    return redirect('/')
            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                    messages.info(request,e.user_message)
                    return redirect('/')
            except stripe.error.StripeError as e:
                    # Display a very generic error to the user, and maybe send
                    # yourself an email
                    #print('Status is: %s' % e.http_status)
                    #print('Code is: %s' % e.code)
                    messages.info(request,e.user_message)
                    return redirect('/')
            except stripe.error.InvalidRequestError as e:
                    messages.info(request,e.user_message)
                    return redirect('/')
            except Exception as e:
                    # Something else happened, completely unrelated to Stripe
                    messages.info(request,e.user_message)
                    return redirect('/')   
    else:
        #single or one-time payment check 
        stripe.PaymentIntent.modify(payment_intent_id,payment_method = payment_method_id)
        ret = stripe.PaymentIntent.confirm(payment_intent_id,receipt_email=request.user.email)
        if ret.status == "succeeded":
            messages.info(request,"Payment successful,Thank you!")
            return redirect('/')
        elif ret.status == 'requires_action':
            context = {}
            context['payment_intent_secret'] = Encode(ret.client_secret)
            context['authenticatedSecure'] = 'show'
            context['stripe_publishable_key'] = Encode(settings.STRIPE_PUBLISHABLE_KEY)
            context['showupgradeplan'] = False
            Encoded_string = Todict(context)
            return redirect('/?%s'%Encoded_string)
        elif ret.status == "requires_payment_method":
            messages.info(request,"Payment failed")
            return redirect('/')
        







#this is call automatically after every payment in order to track wheather payment is successfull or not . 
@require_POST
@csrf_exempt
def stripe_webhooks(request):
    stripe.api_key =  settings.STRIPE_SECRET_KEY
    payload = request.body
    received_sig = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload,received_sig,settings.STRIPE_WEBHOOK_SIGNING_KEY
        )
        logger.info("Event constructed correctly")
    except ValueError as e:
        # Invalid payload
        logger.warning(e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.warning(e)
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'charge.succeeded':
        # object has  payment_intent attr
        set_paid_until(event.data.object.receipt_email,event.data.object)

    return HttpResponse(status=200)
