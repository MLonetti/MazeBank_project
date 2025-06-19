
from django.urls import path
from Banking.views.accounting.views import *

app_name = 'Banking'

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),

]