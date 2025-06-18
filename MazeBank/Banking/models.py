from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class User(AbstractUser):
    username = None  # Rimuove il campo username originale
    email = models.EmailField('Email', unique=True)
    nome = models.CharField(max_length=100)
    cognome = models.CharField(max_length=100)
    data_nascita = models.DateField()
    indirizzo = models.CharField(max_length=255)
    citta = models.CharField(max_length=100)
    cellulare = PhoneNumberField()
    immagine_profilo = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome', 'cognome', 'data_nascita', 'indirizzo', 'citta', 'cellulare']

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


