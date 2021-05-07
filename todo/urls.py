"""todo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from Home.views import addtask,updatetask,deletetask,gettask,showalltask
from subscription.views import validate_plan,card,payment,stripe_webhooks

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Home.urls')),
    path('',include('frontend.urls')),
    path('auth/',include('authapp.urls')),
    path('subscription/',include('subscription.urls')),
    path('task-list/',showalltask),
    path('task-detail/<int:id>/',gettask),
    path('task-create/',addtask),
    path('task-update/<int:id>/',updatetask),
    path('task-delete/<int:id>/',deletetask),

    #Subscrption urls
    path('validateplan/',validate_plan,name="validateplan"),
    path('payment_type_card/',card,name='card'),
    path('sending/',payment,name="sending"),
    path('stripe-webhooks/', stripe_webhooks, name='stripe_webhooks'),

]
