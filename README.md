# MazeBank

MazeBank è una web application bancaria completa, sviluppata in Django, che simula le principali funzionalità di una banca digitale moderna. Il progetto offre un'esperienza utente avanzata sia per clienti che per consulenti, con un'interfaccia responsive, sicura e ricca di funzionalità.

---

## Caratteristiche principali

- **Registrazione e autenticazione utenti**
  - Registrazione clienti con bonus di benvenuto
  - Login/logout sicuro
  - Gestione profilo personale e immagine profilo

- **Gestione conto corrente**
  - Visualizzazione saldo e movimenti
  - Dettaglio conto con IBAN e dati personali
  - Storico transazioni (estratto conto) con filtri avanzati

- **Bonifici e trasferimenti**
  - Invio bonifici SEPA ad altri utenti
  - Invio soldi rapido ad amici salvati in rubrica
  - Causale e conferma operazione tramite modale

- **Rubrica contatti**
  - Salvataggio e gestione dei contatti frequenti
  - Restrizioni: solo clienti possono essere aggiunti alla rubrica
  - Invio soldi diretto dalla rubrica

- **Area consulenti**
  - Gestione clienti seguiti
  - Visualizzazione dettagli clienti e conti associati
  - Aggiunta e gestione consulenti (per admin)

- **Sicurezza**
  - Permessi e gruppi utenti (clienti, consulenti, admin)
  - Decoratori personalizzati per restrizione accessi
  - Validazione dati lato backend e frontend

- **Interfaccia utente**
  - Responsive e mobile-friendly (Bootstrap 4)
  - Temi personalizzati MazeBank
  - Modali, toast di notifica, feedback visivi

---

## Struttura del progetto

```
MazeBank_project/
│
├── MazeBank/                # Configurazione principale Django
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── Banking/                 # App principale (clienti, conti, bonifici)
│   ├── models.py
│   ├── views/
│   ├── forms.py
│   ├── templates/
│   ├── static/
│   └── tests.py
│
├── ConsulentiAdmin/         # App per gestione consulenti e area admin
│   ├── models.py
│   ├── views.py
│   ├── templates/
│   └── ...
│
├── static/                  # Risorse statiche globali (css, immagini)
├── media/                   # Upload immagini profilo
└── templates/               # Template globali (home, about, ecc.)
```

---

## Installazione

1. **Clona il repository**
   ```bash
   git clone <repo-url>
   cd MazeBank_project
   ```

2. **Crea un virtualenv e attivalo**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

4. **Applica le migrazioni**
   ```bash
   python manage.py migrate
   ```

5. **Crea un superuser (opzionale, per area admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Avvia il server di sviluppo**
   ```bash
   python manage.py runserver
   ```

7. **Accedi a [http://localhost:8000](http://localhost:8000)**

---

## Come usare MazeBank

- **Registrazione:**  
  Clicca su "Apri il tuo conto ora" dalla home e compila il form. Riceverai un bonus di benvenuto.
- **Login:**  
  Accedi con le tue credenziali.
- **Gestione conto:**  
  Visualizza saldo, movimenti, dettagli conto e invia bonifici.
- **Rubrica:**  
  Salva i tuoi amici/clienti preferiti e invia loro denaro rapidamente.
- **Area consulenti:**  
  Se sei un consulente, puoi vedere i clienti seguiti e i loro conti.
- **Admin:**  
  Gestisci consulenti e clienti dall’area riservata.

---

## Testing

Per eseguire i test automatici:
```bash
python manage.py test
```
Sono inclusi test per:
- Rubrica contatti (restrizioni sui gruppi)
- Bonifici (aggiornamento saldi e creazione transazione)
- Altre funzionalità core

---

## Personalizzazione

- **Stili:**  
  Modifica i file CSS in `static/css/Banking/` e `static/css/ConsulentiAdmin/`.
- **Template:**  
  Personalizza l’interfaccia modificando i file in `templates/`.
- **Modelli:**  
  Aggiungi campi o funzionalità nei modelli in `Banking/models.py` e `ConsulentiAdmin/models.py`.

---

## Dipendenze principali

- Django
- Bootstrap 4
- Pillow (per upload immagini)
- django-phonenumber-field (per gestione numeri di telefono)
- crispy-forms (per form più belli)

---

## Crediti

MazeBank è un progetto didattico sviluppato per simulare una banca digitale moderna, con attenzione a sicurezza, UX e best practice Django.

---

## Licenza

Questo progetto è distribuito sotto licenza MIT.  
Vedi il file LICENSE per
