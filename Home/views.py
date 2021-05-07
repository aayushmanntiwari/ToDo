from django.shortcuts import render,redirect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializers,AddTaskSerializers
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from authapp.models import ExtendeRegisterUser
from django.views.decorators.http import require_GET, require_POST
from current_date_today import *
from current_date_today import custom_today_date
from random import randint
from django.contrib import messages
from encrypt import Decode,Encode,Todict

# Create your views here.


@api_view(['GET'])
def Home(request):
    upgrade_id = Encode(str(randint(10**(6-1), (10**6)-1)))
    paid_count_days = None
    if request.GET.get('upgradetopro') is not None:
        if request.GET.get('upgradetopro') == 'show':
            showupgradeplan = request.GET.get('upgradetopro')
        else:
            showupgradeplan = None
    else:
        showupgradeplan = None
    if request.GET.get('authenticatedSecure') is not None:
        if request.GET.get('authenticatedSecure') == 'show':
            authenticatedSecur = request.GET.get('authenticatedSecure')
            payment_intent_secret = Decode(request.GET.get('payment_intent_secret'))
            stripe_publishable_key = Decode(request.GET.get('stripe_publishable_key'))
        else:
            authenticatedSecur = None
            payment_intent_secret = None
            stripe_publishable_key = None
    else:
        authenticatedSecur = None
        payment_intent_secret = None
        stripe_publishable_key = None
    if request.user.is_authenticated:
        id = randint(10**(6-1), (10**6)-1)
        #get current logged in user
        extenderegisteruser = ExtendeRegisterUser.objects.get(user = request.user)

        has_paid = extenderegisteruser.has_paid_for_current_month()

        #validate for every user free plan 30 days  trial period is  over or not  yet
        user_joined_date = str(request.user.date_joined.date()).split('-')
        date_today = custom_today_date().split('-')
        d0 = date(int(user_joined_date[0]), int(user_joined_date[1]), int(user_joined_date[2]))
        d1 = date(int(date_today[0]),int(date_today[1]),int(date_today[2]))
        delta = d1 - d0

        trial_days = 30
        #Case - 1 : - when user has the free trial access and has not paid for the month
        if  delta.days + 1 < trial_days  and not has_paid:
            trial_days-=(delta.days + 1)
        else:
            if has_paid:
                next_date = str(extenderegisteruser.paid_until).split('-')
                date_today = custom_today_date().split('-')
                d0 = date(int(next_date[0]), int(next_date[1]), int(next_date[2]))
                d1 = date(int(date_today[0]),int(date_today[1]),int(date_today[2]))
                paid_count_days = int(str(d0 - d1).split(',')[0].split(' ')[0])
                trial_days = None
            else:
                has_paid = None
                trial_days = None
                paid_count_days = None
                if request.GET.get('showupgradeplan'):
                    showupgradeplan = request.GET.get('showupgradeplan')
                else:
                    showupgradeplan = 'show'
    else:
        trial_days = None
        has_paid = None
        paid_count_days = None
    return render(request,'index.html',{'trial_day':trial_days,
                                        'has_paid_for_current_month':has_paid,
                                        'showupgradeplan':showupgradeplan,
                                        'upgrade_id':upgrade_id,
                                        'authenticatedSecur':authenticatedSecur,
                                        'payment_intent_secret':payment_intent_secret,
                                        'stripe_publishable_key':stripe_publishable_key,
                                        'paid_count_days':paid_count_days,
                                        })

@api_view(['GET'])
def showalltask(request):
    tasks = Task.objects.filter(user = request.user).order_by('-id')
    taskserializers = TaskSerializers(tasks,many=True)
    return Response(taskserializers.data)

@login_required(login_url='/auth/sign-in/')
@api_view(['POST'])
def addtask(request):
    addtaskserializers = AddTaskSerializers(data = request.data)
    if addtaskserializers.is_valid():
        addtaskserializers.save(user = request.user)
        return Response(addtaskserializers.data)
    return addtaskserializers(addtaskserializers.errors)

@api_view(['POST'])
def updatetask(request,id):
    task = Task.objects.get(id = id)
    taskserializers = TaskSerializers(data=request.data,instance=task,many=False)
    if taskserializers.is_valid():
        taskserializers.save(user = request.user)
        return Response(taskserializers.data)
    return Response(taskserializers.errors)   


@api_view(['DELETE'])
def deletetask(request,id):
    tasks = Task.objects.get(id = id)
    tasks.delete()


@api_view(['GET'])
def gettask(request,id):
    task = Task.objects.get(id = id)
    taskserializers = TaskSerializers(task,many=False)
    return Response(taskserializers.data)
