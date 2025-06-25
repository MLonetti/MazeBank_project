from django.views.generic import CreateView
from django.urls import reverse
from Banking.forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from Banking.forms import NewLoginAuthenticationForm
from django.shortcuts import redirect
from Banking.models import User, ContoCorrente
from Banking.utils import generate_iban


class UserCreateView(CreateView):
    """
    View for user registration.
    viene utilizzato il model User indicato nel settings.py che è quello da noi personalizzato
    """
    form_class = CustomUserCreationForm 
    template_name = 'registration/register.html'

    def get_success_url(self):
        return reverse('Banking:create_conto_corrente') + f'?user_id={self.object.pk}'


class CustomLoginView(LoginView):
    authentication_form = NewLoginAuthenticationForm
    template_name = 'registration/login.html'


def create_conto_corrente(request):
    user_id = request.GET.get('user_id')
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect('warning')

    # Crea il conto solo se non esiste già
    if not ContoCorrente.objects.filter(utente=user).exists():
        ContoCorrente.objects.create(
            utente=user,
            saldo=50.00,
            iban=generate_iban()
        )
        url = reverse('Banking:login') + '?registration=succesfull'
        return redirect(url)
    else:
        return redirect('warning')
