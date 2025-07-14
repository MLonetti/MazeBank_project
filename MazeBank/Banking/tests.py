from django.test import TestCase
from django.contrib.auth import get_user_model
from Banking.models import ContoCorrente, ContattoSalvato, Transazione
from django.urls import reverse
from datetime import date

class RubricaContattiTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.cliente = User.objects.create_user(
            username='cliente', password='test', first_name='Mario', last_name='Rossi',
            email='cliente@test.com', cellulare='+391234567890', data_nascita=date(1990,1,1)
        )
        self.consulente = User.objects.create_user(
            username='consulente', password='test', first_name='Luca', last_name='Bianchi',
            email='consulente@test.com', cellulare='+391234567891', data_nascita=date(1990,1,1)
        )
        self.admin = User.objects.create_superuser(
            username='admin', password='test', email='admin@test.com', cellulare='+391234567899', data_nascita=date(1990,1,1)
        )
        # Aggiungi il consulente al gruppo 'consulenti'
        from django.contrib.auth.models import Group
        group, _ = Group.objects.get_or_create(name='consulenti')
        self.consulente.groups.add(group)

    def test_cliente_non_puo_aggiungere_admin_o_consulente(self):
        self.client.login(username='cliente', password='test')
        # Prova ad aggiungere il consulente

        response = self.client.post(reverse('Banking:add_contact'), {'telefono': self.consulente.cellulare, 'nome': 'Luca'})
        self.assertEqual(response.status_code, 200, "La view dovrebbe restituire la pagina con il form e l'errore, non un redirect.")
        form = response.context.get('form')
        self.assertIsNotNone(form, "Il form non è presente nel context della response.")
        self.assertIn('telefono', form.errors)
        self.assertIn('Puoi aggiungere solo clienti alla rubrica.', form.errors['telefono'])

        # Prova ad aggiungere l'admin

        response = self.client.post(reverse('Banking:add_contact'), {'telefono': self.admin.cellulare if hasattr(self.admin, 'cellulare') else '', 'nome': 'Admin'})
        self.assertEqual(response.status_code, 200, "La view dovrebbe restituire la pagina con il form e l'errore, non un redirect.")
        form = response.context.get('form')
        self.assertIsNotNone(form, "Il form non è presente nel context della response.")
        self.assertIn('telefono', form.errors)
        self.assertIn('Puoi aggiungere solo clienti alla rubrica.', form.errors['telefono'])

        # Prova ancora con il consulente (per coprire entrambi gli url)

        response = self.client.post(reverse('Banking:add_contact'), {'telefono': self.consulente.cellulare, 'nome': 'Luca'})
        self.assertEqual(response.status_code, 200, "La view dovrebbe restituire la pagina con il form e l'errore, non un redirect.")
        form = response.context.get('form')
        self.assertIsNotNone(form, "Il form non è presente nel context della response.")
        self.assertIn('telefono', form.errors)
        self.assertIn('Puoi aggiungere solo clienti alla rubrica.', form.errors['telefono'])

class BonificoTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.mittente = User.objects.create_user(
            username='mittente', password='test', first_name='Anna', last_name='Verdi',
            email='mittente@test.com', cellulare='+391234567892', data_nascita=date(1990,1,1)
        )
        self.destinatario = User.objects.create_user(
            username='destinatario', password='test', first_name='Paolo', last_name='Neri',
            email='dest@test.com', cellulare='+391234567893', data_nascita=date(1990,1,1)
        )
        self.conto_mitt = ContoCorrente.objects.create(utente=self.mittente, iban='IT00A1234567890123456789012', saldo=1000)
        self.conto_dest = ContoCorrente.objects.create(utente=self.destinatario, iban='IT00A1234567890123456789013', saldo=500)

    def test_bonifico_aggiorna_saldi_e_transazione(self):
        self.client.login(username='mittente', password='test')
        url = reverse('Banking:bonifici')
        data = {
            'iban': self.conto_dest.iban,
            'nome': self.destinatario.first_name,
            'cognome': self.destinatario.last_name,
            'importo': 200,
            'causale': 'Test bonifico'
        }
        response = self.client.post(url, data, follow=True)
        self.conto_mitt.refresh_from_db()
        self.conto_dest.refresh_from_db()
        self.assertEqual(self.conto_mitt.saldo, 800)
        self.assertEqual(self.conto_dest.saldo, 700)
        self.assertTrue(Transazione.objects.filter(conto_sorgente=self.conto_mitt, conto_destinazione=self.conto_dest, importo=200, causale='Test bonifico').exists())
