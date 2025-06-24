from django.views.generic import CreateView
from django.urls import reverse
from Banking.forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from Banking.forms import NewLoginAuthenticationForm
from django.http import HttpResponse


class UserCreateView(CreateView):
    """
    View for user registration.
    viene utilizzato il model User indicato nel settings.py che è quello da noi personalizzato
    """
    form_class = CustomUserCreationForm 
    template_name = 'registration/register.html'

    def get_success_url(self):
        return reverse('/banking/login') + '?registration=ok'


class CustomLoginView(LoginView):
    authentication_form = NewLoginAuthenticationForm
    template_name = 'registration/login.html'
