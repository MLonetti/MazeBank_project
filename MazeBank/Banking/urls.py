from django.urls import path, include
from Banking.views.authentication_views.views import *
from Banking.views.account_views.views import *
from django.contrib.auth import views as auth_views



app_name = 'Banking'

urlpatterns = [
    # URL authentication_views
    path('register/', UserCreateView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('create_conto_corrente/', create_conto_corrente, name='create_conto_corrente'),
    path('post-login/', post_login_redirect, name='post_login_redirect'),

    # URL account_views
    path('profilo/<pk>', DetailProfilo.as_view(), name='profilo'),
    path('profilo/<pk>/ajax_modifica_campo/', ajax_modifica_campo, name='ajax_modifica_campo'),
    path('conto_corrente/<pk>', DettaglioContoCorrente.as_view(), name='conto_corrente'),
    path('bonifici/', make_bonifico, name='bonifici'),
    path('bonifico_esito/', bonifico_esito, name='bonifico_esito'),
    path('estratto_conto/', estratto_conto.as_view(), name='transazioni'),
    path('ajax_filtra_transazioni/', ajax_filtra_transazioni, name='ajax_filtra_transazioni'),
    path('contatti_salvati/', ListaContattiSalvati.as_view(), name='contatti_salvati'),
    path('aggiungi_contatto/', add_contatto, name='add_contact'),
    path('ajax_invia_soldi_amico/', ajax_invia_soldi_amico, name='ajax_invia_soldi_amico'),
    
]