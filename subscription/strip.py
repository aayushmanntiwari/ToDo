import logging
import stripe
import json
from authapp.models import ExtendeRegisterUser
from django.conf import settings
from django.contrib.auth.models import User
from datetime import timedelta
from datetime import datetime
from current_date_today import custom_today_date

stripe.api_key =  settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)

#You can customise this class as you want if add new subscription don't forget to add in here as well 

class Monthly:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_MONTHLY_ID
        self.amount = stripe.Price.retrieve(self.stripe_plan_id).unit_amount

class Annually:
    def __init__(self):
        self.stripe_plan_id = settings.STRIPE_PLAN_ANNUL_ID
        self.amount = stripe.Price.retrieve(self.stripe_plan_id).unit_amount


class Tax:
    def __init__(self):
        self.rate = stripe.TaxRate.retrieve(settings.STRIPE_TAX_RATE).percentage

class Plan:
    def __init__(self,plan_type):
        '''
        plan_type is either string 'm' (stands for monthly)
        or a string letter 'a' (which stands for annual)
        can be update customise based on your requirment
        '''
        self.plan_type = plan_type
        if self.plan_type == 'm':
            self.plan = Monthly()
            self.tax_rate = Tax()
            self.id = 'Monthly'
        elif self.plan_type == 'a':
            self.plan = Annually()
            self.tax_rate = Tax()
            self.id = 'Annually'
        else:
            raise ValueError('invalid plan type')
            
        self.currency = 'inr'

    @property
    def stripe_plan_id(self):
        return self.plan.stripe_plan_id

    @property
    def amount(self):
        return self.plan.amount 





def set_paid_until(email,charge):
    logger.info(f"set_paid_until with {charge}")
    print("charge: ",charge)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    pi = stripe.PaymentIntent.retrieve(charge.payment_intent)
    if pi.customer:
        customer = stripe.Customer.retrieve(pi.customer, expand = ['subscriptions'])
        email = customer.email
        if customer:
            subscr = stripe.Subscription.retrieve(
                customer['subscriptions'].data[0].id
            )
            current_period_end = subscr['current_period_end'] #return timestamp ,need to convert to date

        try:
            user = User.objects.get(email=email)
            extenderegisteruser = ExtendeRegisterUser.objects.get(user_id = user.id) 
        except User.DoesNotExist:
            logger.warning(
                f"User with email {email} not found"
            )
            return False
        extenderegisteruser.set_paid_until(''.join(str(datetime.fromtimestamp(int(current_period_end)).date()).split('-')))
        logger.info(
            f"Profile with {current_period_end} saved for user {email}"
        )
    else:
        #print(charge.invoice)
        #invoice = stripe.Invoice.retrieve(charge.invoice)
        # charge.amount  1990 | 19995
        print(charge.amount_captured)
        if charge.amount_captured == 300000:
            next_date = ''.join((datetime.strptime(str(custom_today_date()), '%Y-%m-%d').date()+timedelta(days=365)).isoformat().split('-'))
        elif charge.amount_captured == 20000:
            next_date = ''.join((datetime.strptime(str(custom_today_date()), '%Y-%m-%d').date()+timedelta(days=30)).isoformat().split('-'))
        # this was one time payment, update
        if charge.status == 'succeeded':
            user = User.objects.get(email=email)
            extenderegisteruser = ExtendeRegisterUser.objects.get(user_id = user.id) 
            extenderegisteruser.set_paid_until(next_date)