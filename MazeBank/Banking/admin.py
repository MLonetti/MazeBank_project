from django.contrib import admin
from .models import User, Transazione, ContoCorrente, ContattoSalvato

# Register your models here.

admin.site.register(User)
admin.site.register(Transazione)
admin.site.register(ContoCorrente)
admin.site.register(ContattoSalvato)