import random
import string
from django.shortcuts import redirect

def generate_iban():
    # Esempio IBAN italiano: ITkk ABBB BBCC CCCC CCCC CCCC CCC
    # IT + 2 cifre di controllo + 1 lettera + 22 cifre
    country_code = "IT"
    check_digits = str(random.randint(10, 99))
    bank_code = ''.join(random.choices(string.ascii_uppercase, k=1))
    account_numbers = ''.join(random.choices(string.digits, k=22))
    return f"{country_code}{check_digits}{bank_code}{account_numbers}"

# Decoratore per permettere l'accesso solo ai clienti (no admin, no consulenti)
def solo_clienti_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='consulenti').exists():
            return redirect('warning')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Mixin per class-based views: accesso solo clienti
class SoloClientiRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name='consulenti').exists():
            return redirect('warning')
        return super().dispatch(request, *args, **kwargs)