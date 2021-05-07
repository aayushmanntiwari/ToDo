from django.shortcuts import render,redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User,Group
from django.contrib import messages
from .models import ExtendeRegisterUser
from django.db.models import Q
from rest_framework.authtoken.models import Token
from django.contrib import auth

# Create your views here.
@api_view(['POST','GET'])
def register(request):
    if request.method == 'POST':
        if request.POST.get('signupPassword') ==  request.POST.get('signupPasswordagain'):
            try:
                extenderegisteruser = ExtendeRegisterUser.objects.filter(Q(mobilenumber = request.POST.get('mobilenumber') ) | Q(user_id = User.objects.get(username = request.POST.get('signupEmail')).id))
                messages.info(request,'User already registered with us !')
                return redirect('register')
            except: 
                    try:
                        extenderegisteruser = ExtendeRegisterUser.objects.get(mobilenumber = request.POST.get('mobilenumber'))
                        messages.info(request,'mobile number already registered with us ,please use different number ! ')
                        return redirect('register')
                    except:
                        user = User.objects.create_user(username = request.POST.get('signupEmail'),password = request.POST.get('signupPassword'),first_name = request.POST.get('signupFirstName'),last_name = request.POST.get('signupLastName'),email = request.POST.get('signupEmail'))
                        token = Token.objects.create(user=user)
                        group = Group.objects.get(name='user')
                        user.groups.add(group)
                        extendeduser = ExtendeRegisterUser(mobilenumber = request.POST.get('mobilenumber'),user = user)
                        extendeduser.save()
                        messages.success(request,'User register succesfully , please sing in !')
                        return redirect('register')
                    
        else:
            messages.info(request,'Password not match!')
            return redirect('register')
    else:
        return render(request,'registration.html')

@api_view(['GET','POST'])
def login(request):
    if request.method == 'POST':
        try:
            extenderegisteruser = ExtendeRegisterUser.objects.get(mobilenumber = request.POST.get('mobileoremail'))
            validate = User.objects.get(id = extenderegisteruser.user_id)
            user = auth.authenticate(username = validate.username,password = request.POST.get('password'))
            if user is not None:
                auth.login(request,user)
                return redirect('/')
            else:
                messages.info(request,'Wrong mobile number or password ,Please check again !')
                return redirect('/auth/sign-in/')
        except:
            user = auth.authenticate(username = request.POST.get('mobileoremail'),password = request.POST.get('password'))
            if user is not None:
                auth.login(request,user)
                return redirect('/')
            else:
                messages.info(request,'Wrong email or password ,Please check again !')
                return redirect('/auth/sign-in/')
    else:
        return render(request,'login.html')


@api_view(['GET'])
def logout(request):
    auth.logout(request)
    return redirect('/')