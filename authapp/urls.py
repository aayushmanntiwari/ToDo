from . import views
from django.urls import path,include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('sign-in/',views.login,name="login"),
    path('sign-up/',views.register,name="register"),
    path('logout/',views.logout,name="logout"),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('api/token/',obtain_auth_token,name="obtain-token"),
]