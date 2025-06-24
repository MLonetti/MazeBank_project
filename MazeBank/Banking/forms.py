# UserCreationForm Personalizzato per aggiungere tutti i campi che ci servono
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, get_user_model
from .models import User

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'email', 'first_name', 'last_name', 'data_nascita', 'indirizzo', 'citta', 'cellulare', 'immagine_profilo'
        )

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