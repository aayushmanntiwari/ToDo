from django.db import models
import datetime
from datetime import date
from django.contrib.auth.models import User,Group
from current_date_today import *
import time

# Create your models here.
class ExtendeRegisterUser(models.Model):
    mobilenumber = models.CharField(max_length=17,unique=True)
    paid_until = models.DateField(null=True,blank=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='User_Registration')
    def set_paid_until(self,date_or_timestamp):
        #there will be case that date can either be pass has integer i.e 20211201 or in string  '20211131'
        print(date_or_timestamp)
        paid_until = datetime.datetime.strptime(str(date_or_timestamp), '%Y%m%d').strftime('%Y-%m-%d')
        self.paid_until = paid_until
        self.save()

    #this function validate for user paid for the subscription or not  
    def has_paid_for_current_month(self):
        current_date =  time.strptime(custom_today_date(),"%Y-%m-%d")
        if self.paid_until is not None:
            next_paid_until = time.strptime(str(self.paid_until),"%Y-%m-%d")
        #paid_untl is returing None means user haven't paid the bill yet return False 
        #if the user buy any subscrption we have to set new paid_until date using set_paid_until() method based on the current subscription validaty and it should always we greater than current date   
        if self.paid_until is None:
            return False
        return current_date < next_paid_until