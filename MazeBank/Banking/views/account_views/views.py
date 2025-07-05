from Banking.models import User, ContoCorrente
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from Banking.forms import BonificoForm
from decimal import Decimal

######################################################################################
# VIEW CHE GESTISCE LA VISUALIZZAZIONE DEL PROFILO UTENTE
######################################################################################
class DetailProfilo(DetailView):
    model = User
    template_name = 'Banking/profilo.html'
    context_object_name = 'utente'

######################################################################################
# VIEW CHE GESTISCE LA MODIFICA DEI CAMPI DEL PROFILO UTENTE:
#   È UNA FUNZIONE AJAX, DALLA VISTA PRECEDENTE (NEL TEMPLATE) JS MANDA UNA REQUEST ALL'URL CHE CHIAMA QUESTA FUNZIONE
#   E  VIENE GESTITA LA MODIFICA DEI CAMPI DEL PROFILO UTENTE
######################################################################################
@login_required
@csrf_exempt
@require_POST
def ajax_modifica_campo(request, pk):
    if int(request.user.pk) != int(pk):
        return JsonResponse({'success': False, 'redirect_url': '/warning/'}, status=403)

    # Gestione file upload (immagine profilo)
    if request.FILES.get('immagine_profilo'):
        img = request.FILES['immagine_profilo']
        request.user.immagine_profilo.save(img.name, img)
        request.user.save()
        return JsonResponse({'success': True, 'img_url': request.user.immagine_profilo.url})

    # Gestione campi testuali
    if request.content_type == 'application/json':
        data = json.loads(request.body.decode('utf-8'))
    else:
        data = request.POST
    campo = data.get('campo')
    valore = data.get('valore')
    print('DEBUG campo:', campo, 'valore:', valore, 'data:', data)
    if campo in ['indirizzo', 'cellulare', 'email'] and valore:
        print('PRIMA DI SALVARE:', campo, valore)
        # Normalizza cellulare: aggiungi +39 se manca
        if campo == 'cellulare' and valore and not valore.startswith('+'):
            valore = '+39' + valore.lstrip('0').replace(' ', '')
        setattr(request.user, campo, valore)
        print('DOPO SETATTR, PRIMA DI SAVE:', campo, getattr(request.user, campo))
        try:
            request.user.full_clean(validate_unique=True, exclude=[f.name for f in request.user._meta.fields if f.name != campo])  # Valida solo il campo modificato
            request.user.save()
            print('DOPO IL SALVATAGGIO:', campo, getattr(request.user, campo))
            return JsonResponse({'success': True, 'campo': campo, 'valore': str(getattr(request.user, campo))})
        except Exception as e:
            print('ERRORE DI VALIDAZIONE:', str(e))
            # Gestione messaggi chiari per duplicati
            msg = str(e)
            # Gestione errori come dict (es: {'cellulare': ['User with this Cellulare already exists.']})
            if hasattr(e, 'message_dict'):
                if 'email' in e.message_dict and any('already exists' in m for m in e.message_dict['email']):
                    msg = 'L’indirizzo email inserito è già associato a un altro utente. Scegli un’email diversa.'
                elif 'cellulare' in e.message_dict and any('already exists' in m for m in e.message_dict['cellulare']):
                    msg = 'Il numero di cellulare inserito è già associato a un altro utente. Inserisci un numero diverso.'
            else:
                if 'email' in msg and 'unique' in msg:
                    msg = 'L’indirizzo email inserito è già associato a un altro utente. Scegli un’email diversa.'
                elif 'cellulare' in msg and 'unique' in msg:
                    msg = 'Il numero di cellulare inserito è già associato a un altro utente. Inserisci un numero diverso.'
            return JsonResponse({'success': False, 'error': msg}, status=400)
    return JsonResponse({'success': False, 'error': 'Campo non valido'}, status=400)

#######################################################################################
# VIEW CHE GESTISCE LA VISUALIZZAZIONE DEL CONTO CORRENTE:
#   È UNA VIEW CHE MOSTRA LE INFORMAZIONI DEL CONTO CORRENTE DELL'UTENTE LOGGATO
#######################################################################################

class DettaglioContoCorrente(LoginRequiredMixin, DetailView):
    model = ContoCorrente
    template_name = 'Banking/conto_corrente.html'
    context_object_name = 'conto_corrente'

    def get_object(self, queryset=None):
        user_pk = self.kwargs['pk']
        if int(self.request.user.pk) != int(user_pk):
            return redirect('/warning/')
        return ContoCorrente.objects.get(utente_id=user_pk)

######################################################################################
# VIEW CHE GESTISCE LA CREAZIONE DI UN BONIFICO:
#   È UNA VIEW CHE PERMETTE ALL'UTENTE DI INVIARE UN BONIFICO A UN ALTRO UTENTE
#   CHIEDE L'IBAN, NOME, COGNOME, IMPORTO E CAUSALE DEL BONIFICO
#######################################################################################
@login_required
def make_bonifico(request):
    errore = None  # Inizializza sempre la variabile!
    if request.method == "POST":
        form = BonificoForm(request.POST)
        if form.is_valid():
            iban = form.cleaned_data['iban'].strip()
            nome = form.cleaned_data['nome'].strip()
            cognome = form.cleaned_data['cognome'].strip()
            importo = form.cleaned_data['importo']
            causale = form.cleaned_data['causale'].strip()

            # Controllo che il destinatario esista
            try:
                conto_dest = ContoCorrente.objects.select_related('utente').get(
                    iban=iban,
                    utente__first_name__iexact=nome,
                    utente__last_name__iexact=cognome
                )
            except ContoCorrente.DoesNotExist:
                errore = "Destinatario non trovato. Controlla i dati inseriti."
                conto_dest = None

            # Controllo che il mittente non invii a se stesso
            conto_mitt = request.user.conto_corrente
            if conto_dest and conto_dest.pk == conto_mitt.pk:
                errore = "Non puoi inviare un bonifico a te stesso."

            # Controllo saldo sufficiente
            if not errore and conto_mitt.saldo < importo:
                errore = "Saldo insufficiente per effettuare il bonifico."

            # Esegui il bonifico
            if not errore:
                conto_mitt.saldo -= importo
                conto_dest.saldo += importo
                conto_mitt.save()
                conto_dest.save()
                request.session['esito_bonifico'] = {
                    'nome': nome,
                    'cognome': cognome,
                    'iban': iban,
                    'importo': str(importo),
                    'causale': causale,
                    'successo': True,
                }
                return redirect('Banking:bonifico_esito')
        else:
            errore = "Compila correttamente tutti i campi."
    else:
        form = BonificoForm()
    if errore:  # errore è una stringa con il messaggio di errore
        request.session['esito_bonifico'] = {
            'errore': errore,
            'successo': False,
            'nome': request.POST.get('nome', ''),
            'cognome': request.POST.get('cognome', ''),
            'iban': request.POST.get('iban', ''),
            'importo': request.POST.get('importo', ''),
            'causale': request.POST.get('causale', ''),
            # recuperiamo i dati dal metodo post in quanto sicuramente dal form non sono validi
        }
        return redirect('Banking:bonifico_esito')
    return render(request, "Banking/bonifico.html", {"form": form, "errore": errore})

######################################################################################
# VIEW CHE GESTISCE L'ESITO DEL BONIFICO:
#   MOSTRA UN MESSAGGIO DI SUCCESSO O FALLIMENTO DEL BONIFICO
#   ESTRAE DALLA SESSIONE I DATI DEL BONIFICO E LI MOSTRA, SE SI RICARICA LA PAGINA
#   NON ESISTONO PIÙ I DATI DEL BONIFICO, E SI RITORNA ALLA PAGINA DEI BONIFICI

# INIZIALMENTE INVECE REFRESHANDO LA PAGINA SI RIEFFETTUAVA IL BONIFICO
#######################################################################################

def bonifico_esito(request):
    esito = request.session.pop('esito_bonifico', None) 
    if not esito:
        return redirect('Banking:bonifici')
    return render(request, "Banking/bonifico_esito.html", {"esito": esito})

