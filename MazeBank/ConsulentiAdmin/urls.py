from .views import *
from django.urls import path

app_name = 'ConsulentiAdmin'

urlpatterns = [
    path('homepage/', consulent_administer_homepage, name='homepage'),
    path('crea_consulente/', ConsulenteCreateView.as_view(), name='crea_consulente'),
]