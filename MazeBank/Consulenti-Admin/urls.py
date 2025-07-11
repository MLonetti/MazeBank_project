from .views import *
from django.urls import path

app_name = 'Consulenti-Admin'

urlpatterns = [
    path('Consulent_administer/homepage/', consulent_administer_homepage, name='homepage'),
]