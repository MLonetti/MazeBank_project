from .views import *
from django.urls import path

app_name = 'ConsulentiAdmin'

urlpatterns = [
    path('homepage/', consulent_administer_homepage, name='homepage'),
    path('crea_consulente/', ConsulenteCreateView.as_view(), name='crea_consulente'),
    path('lista_consulenti/', ConsulenteListView.as_view(), name='lista_consulenti'),
    path('consulente/<int:pk>/', ConsulenteDetailView.as_view(), name='dettaglio_consulente'),
    path('clienti_seguiti/', ClientiSeguitiListView.as_view(), name='clienti_seguiti'),
]