from django.urls import path
from Banking.views.accounting.views import *
from django.contrib.auth import views as auth_views


app_name = 'Banking'

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]