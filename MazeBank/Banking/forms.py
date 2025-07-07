# UserCreationForm Personalizzato per aggiungere tutti i campi che ci servono
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from .models import User

User = get_user_model()

###################################################################################
# Form per la creazione di un nuovo utente
# Lo vediamo nella fase di registrazione
###################################################################################
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'email', 'first_name', 'last_name', 'data_nascita', 'indirizzo', 'citta', 'cellulare', 'immagine_profilo'
        )

####################################################################################
# Form per l'autenticazione dell'utente
# Lo vediamo nella fase di login -> chiediamo solamente l'email e la password invece dell'username
####################################################################################
class NewLoginAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"autofocus": True}))

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            try:
                user = User.objects.get(email=email)
                username = user.username # si prende l'username associato alla mail
            except User.DoesNotExist:
                raise forms.ValidationError("Email o password non validi.", code='invalid_login')
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None: # se la password inserita associata all'user ricavato è sbagliata ritorna errore
                raise forms.ValidationError("Email o password non validi.", code='invalid_login')
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data
    
####################################################################################
# Form per effettuare un bonifico:
# Lo vediamo nella fase di invio bonifico
# Chiediamo IBAN, nome, cognome e importo
####################################################################################

class BonificoForm(forms.Form):
    iban = forms.CharField(label="IBAN destinatario", max_length=34, widget=forms.TextInput(attrs={'placeholder': 'IT60X0542811101000000123456'}))
    nome = forms.CharField(label="Nome destinatario", max_length=100)
    cognome = forms.CharField(label="Cognome destinatario", max_length=100)
    importo = forms.DecimalField(label="Importo (€)", min_value=0.01, decimal_places=2, max_digits=12)
    causale = forms.CharField(label="Causale", max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'Facoltativo'}))

#####################################################################################
# Form dedicato al filtraggio delle transazioni:
# Lo vediamo nella fase di visualizzazione delle transazioni
#####################################################################################
class FiltroTransazioniForm(forms.Form):
    CAMPI_CHOICES = [
        ('nome', 'Nome'),
        ('cognome', 'Cognome'),
        ('iban', 'IBAN'),
        ('importo', 'Importo'),
        ('tipo', 'Tipo'),
    ]
    campo = forms.ChoiceField(choices=CAMPI_CHOICES, required=False, label='Filtra per')
    valore = forms.CharField(required=False, label='Valore')