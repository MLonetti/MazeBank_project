from django.contrib import admin
from .models import User, Transazione, ContoCorrente

# Register your models here.

admin.site.register(User)
admin.site.register(Transazione)
admin.site.register(ContoCorrente)