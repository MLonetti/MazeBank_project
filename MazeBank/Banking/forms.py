# UserCreationForm Personalizzato per aggiungere tutti i campi che ci servono
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + (
            'email', 'first_name', 'last_name', 'data_nascita', 'indirizzo', 'citta', 'cellulare', 'immagine_profilo'
        )