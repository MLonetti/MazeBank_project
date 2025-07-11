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
    consulente = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clienti_associati',
        limit_choices_to={'groups__name': 'consulenti'}
    )

    def __str__(self):
        return f"Conto di {self.utente.email} - IBAN: {self.iban}"
    
class Transazione(models.Model):
    TIPO_CHOICES = [
        ('bonifico', 'Bonifico'),
        ('invio_soldi_amico', 'Invio soldi ad amico'),
        # altri tipi in futuro
    ]
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        default='bonifico' 
    )
    conto_sorgente = models.ForeignKey(
        ContoCorrente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transazioni_uscita'
    )
    conto_destinazione = models.ForeignKey(
        ContoCorrente,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transazioni_entrata'
    )
    importo = models.DecimalField(max_digits=12, decimal_places=2)
    causale = models.CharField(max_length=255, blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} {self.importo}€ da {self.conto_sorgente} a {self.conto_destinazione} il {self.data}"


