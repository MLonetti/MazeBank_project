import random
import string

def generate_iban():
    # Esempio IBAN italiano: ITkk ABBB BBCC CCCC CCCC CCCC CCC
    # IT + 2 cifre di controllo + 1 lettera + 22 cifre
    country_code = "IT"
    check_digits = str(random.randint(10, 99))
    bank_code = ''.join(random.choices(string.ascii_uppercase, k=1))
    account_numbers = ''.join(random.choices(string.digits, k=22))
    return f"{country_code}{check_digits}{bank_code}{account_numbers}"