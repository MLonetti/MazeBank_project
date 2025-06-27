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

    # si sovrascrive il metodo dispatch per reindirizzare gli utenti autenticati
    # alla pagina di warning invece che alla pagina di registrazione

    # dispatch è il metodo delle class based view che rappresenta il punto di ingresso per gestire le richieste
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('warning')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('Banking:create_conto_corrente') + f'?user_id={self.object.pk}'


class CustomLoginView(LoginView):
    authentication_form = NewLoginAuthenticationForm
    template_name = 'registration/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('warning')
        return super().dispatch(request, *args, **kwargs)


def create_conto_corrente(request):
    # se l'utente è autenticato reindirizza alla pagina di warning. Non esiste un decoratore come @login_required.
    if request.user.is_authenticated:
        return redirect('warning')
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
