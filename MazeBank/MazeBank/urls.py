"""
URL configuration for MazeBank project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include, re_path
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from Banking.views.authentication_views.views import post_login_redirect 

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r"^$|^home/$|^homepage/$", homepage, name='homepage'),
    path('about/', about, name='us'),
    path('services/', services, name='services'),
    path('warning/', warning, name='warning'),

    path('post-login/', post_login_redirect, name='post_login_redirect'), 

    # URL per le pagine gestite dalla logica dell'app Banking
    path('banking/', include('Banking.urls')),

    # URL per le pagine gestite dalla logica per admin e consulenti
    path('consulent_administer/', include('ConsulentiAdmin.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
