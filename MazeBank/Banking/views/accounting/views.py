from django.views.generic import CreateView
from django.urls import reverse_lazy
from Banking.forms import CustomUserCreationForm


class UserCreateView(CreateView):
    """
    View for user registration.
    viene utilizzato il model User indicato nel settings.py che è quello da noi personalizzato
    """
    form_class = CustomUserCreationForm 
    template_name = 'registration/register.html'
    success_url = reverse_lazy('homepage')