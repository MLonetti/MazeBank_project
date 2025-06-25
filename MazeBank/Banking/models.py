from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    # Usiamo gli attributi già presenti: email, first_name, last_name
    # Rendi obbligatoria l'email (unique e blank=False già su AbstractUser, ma puoi rafforzare così:)
    email = models.EmailField('Email', unique=True, blank=False, null=False)
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)  

    data_nascita = models.DateField()
    indirizzo = models.CharField(max_length=255)
    citta = models.CharField(max_length=100)
    cellulare = PhoneNumberField(unique=True) 
    immagine_profilo = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    # USERNAME_FIELD resta 'username' (default, che è un CharField)
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'data_nascita', 'indirizzo', 'citta', 'cellulare']

    def __str__(self):
        return self.username

class ContattoSalvato(models.Model):
    proprietario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='contatti_salvati'
    )
    utente_salvato = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='salvato_da'
    )
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nome} (salvato da {self.proprietario.email})"

class ContoCorrente(models.Model):
    utente = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='conto_corrente'
    )
    iban = models.CharField(max_length=34, unique=True)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Conto di {self.utente.email} - IBAN: {self.iban}"
    
class Transazione(models.Model):
    conto = models.ForeignKey(
        ContoCorrente,
        on_delete=models.CASCADE,
        related_name='transazioni'
    )
    data = models.DateTimeField(auto_now_add=True)
    importo = models.DecimalField(max_digits=12, decimal_places=2)
    descrizione = models.CharField(max_length=255)

    def __str__(self):
        return f"Transazione {self.id} - {self.importo} su {self.conto.iban} il {self.data}"


