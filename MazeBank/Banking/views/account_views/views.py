from Banking.models import User, ContoCorrente, Transazione, ContattoSalvato
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from Banking.forms import BonificoForm, FiltroTransazioniForm, ContattoSalvatoForm
from django.db import models
from decimal import Decimal
from Banking.utils import solo_clienti_required, SoloClientiRequiredMixin

######################################################################################
# VIEW CHE GESTISCE LA VISUALIZZAZIONE DEL PROFILO UTENTE
######################################################################################
class DetailProfilo(SoloClientiRequiredMixin, LoginRequiredMixin ,DetailView):
    model = User
    template_name = 'Banking/profilo.html'
    context_object_name = 'utente'

######################################################################################
# VIEW CHE GESTISCE LA MODIFICA DEI CAMPI DEL PROFILO UTENTE:
#   È UNA FUNZIONE AJAX, DALLA VISTA PRECEDENTE (NEL TEMPLATE) JS MANDA UNA REQUEST ALL'URL CHE CHIAMA QUESTA FUNZIONE
#   E  VIENE GESTITA LA MODIFICA DEI CAMPI DEL PROFILO UTENTE
######################################################################################
@login_required
@solo_clienti_required
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

class DettaglioContoCorrente(SoloClientiRequiredMixin, LoginRequiredMixin, DetailView):
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
@solo_clienti_required
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
                # Dopo aver aggiornato i saldi...

                # Creiamo qui le entry Transazione per il bonifico
                Transazione.objects.create(
                    tipo='bonifico',
                    conto_sorgente=conto_mitt,
                    conto_destinazione=conto_dest,
                    importo=importo,
                    causale=causale
                )
                
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
@login_required
@solo_clienti_required
def bonifico_esito(request):
    # Questa view va protetta solo se serve, altrimenti lasciare libera per redirect post-bonifico
    if request.user.is_superuser or request.user.groups.filter(name='consulenti').exists():
        return redirect('warning')
    esito = request.session.pop('esito_bonifico', None) 
    if not esito:
        return redirect('Banking:bonifici')
    return render(request, "Banking/bonifico_esito.html", {"esito": esito})


######################################################################################
# VIEW CHE GESTISCE L'ESTRATTO CONTO DELL'UTENTE:
#   MOSTRA TUTTE LE TRANSAZIONI DEL CONTO CORRENTE
#   OVVIAMENTE SIA LE TRANSAZIONI IN USCITA CHE IN ENTRATA
######################################################################################

class estratto_conto(SoloClientiRequiredMixin, LoginRequiredMixin, ListView):
    model = Transazione
    template_name = 'Banking/estratto_conto.html'
    context_object_name = 'transazioni'

    def get_queryset(self):
        conto_utente = self.request.user.conto_corrente
        return Transazione.objects.filter(
            models.Q(conto_sorgente=conto_utente) | models.Q(conto_destinazione=conto_utente)
        ).order_by('-data')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_form'] = FiltroTransazioniForm()
        conto_utente = self.request.user.conto_corrente
        transazioni = context['transazioni']

        data = []
        for t in transazioni:
            is_uscita = t.conto_sorgente == conto_utente
            controparte = t.conto_destinazione if is_uscita else t.conto_sorgente

            nome_rubrica = None
            if t.tipo == 'invio_soldi_amico':
                contatto = ContattoSalvato.objects.filter(
                    proprietario=self.request.user, utente_salvato=controparte.utente
                ).first()
                if contatto and contatto.nome:
                    nome_rubrica = contatto.nome
                else:
                    nome_rubrica = controparte.utente.cellulare

            descrizione = (
                f"Bonifico inviato a {controparte.utente.get_full_name()} ({controparte.iban})" if is_uscita and t.tipo == 'bonifico'
                else f"Bonifico ricevuto da {controparte.utente.get_full_name()} ({controparte.iban})" if not is_uscita and t.tipo == 'bonifico'
                else f"Soldi inviati a {nome_rubrica}" if is_uscita and t.tipo == 'invio_soldi_amico'
                else f"Soldi ricevuti da {nome_rubrica}" if not is_uscita and t.tipo == 'invio_soldi_amico'
                else "Transazione"
            )

            data.append({
                'data': t.data.strftime("%d/%m/%Y %H:%M"),
                'tipo': t.get_tipo_display(),
                'tipo_tecnico': t.tipo,
                'descrizione': (
                    f"Bonifico inviato a {controparte.utente.get_full_name()} ({controparte.iban})" if is_uscita and t.tipo == 'bonifico'
                    else f"Bonifico ricevuto da {controparte.utente.get_full_name()} ({controparte.iban})" if not is_uscita and t.tipo == 'bonifico'
                    else f"Soldi inviati a {nome_rubrica}" if is_uscita and t.tipo == 'invio_soldi_amico'
                    else f"Soldi ricevuti da {nome_rubrica}" if not is_uscita and t.tipo == 'invio_soldi_amico'
                    else "Transazione"
                ),
                'importo': f"{'-' if is_uscita else '+'}{t.importo} €",
                'importo_class': "importo-uscita" if is_uscita else "importo-entrata",
                'causale': getattr(t, 'causale', ''),
                'controparte': nome_rubrica or controparte.utente.get_full_name() or controparte.utente.cellulare,
                'iban': getattr(controparte, 'iban', ''),
            })

        context['transazioni_data'] = data
        return context
    

######################################################################################
# VIEW AJAX PER FILTRARE LE TRANSAZIONI DELL'UTENTE:
#   RICEVE I PARAMETRI DI FILTRO (CAMPO E VALORE)
#   E RESTITUISCE UN JSON CON LE TRANSAZIONI FILTRATE
######################################################################################

@login_required
@solo_clienti_required
@require_GET
def ajax_filtra_transazioni(request):
    campo = request.GET.get('campo')
    valore = request.GET.get('valore', '').strip()
    conto_utente = request.user.conto_corrente

    transazioni = Transazione.objects.filter(
        models.Q(conto_sorgente=conto_utente) | models.Q(conto_destinazione=conto_utente)
    )

    if campo and valore:
        if campo == 'nome':
            transazioni = transazioni.filter(
                models.Q(conto_sorgente__utente__first_name__icontains=valore) |
                models.Q(conto_destinazione__utente__first_name__icontains=valore)
            )
        elif campo == 'cognome':
            transazioni = transazioni.filter(
                models.Q(conto_sorgente__utente__last_name__icontains=valore) |
                models.Q(conto_destinazione__utente__last_name__icontains=valore)
            )
        elif campo == 'iban':
            transazioni = transazioni.filter(
                models.Q(conto_sorgente__iban__icontains=valore) |
                models.Q(conto_destinazione__iban__icontains=valore)
            )
        elif campo == 'importo':
            try:
                importo_val = float(valore.replace(',', '.'))
                transazioni = transazioni.filter(importo=importo_val)
            except ValueError:
                transazioni = transazioni.none()
        elif campo == 'tipo':
            transazioni = transazioni.filter(tipo__icontains=valore)

    data = []
    for t in transazioni.order_by('-data'):
        is_uscita = t.conto_sorgente == conto_utente
        controparte = t.conto_destinazione if is_uscita else t.conto_sorgente

        # Logica nome rubrica o cellulare
        nome_rubrica = None
        if t.tipo == 'invio_soldi_amico':
            contatto = ContattoSalvato.objects.filter(
                proprietario=request.user, utente_salvato=controparte.utente
            ).first()
            if contatto and contatto.nome:
                nome_rubrica = contatto.nome
            else:
                nome_rubrica = controparte.utente.cellulare

        data.append({
            'data': t.data.strftime("%d/%m/%Y %H:%M"),
            'tipo': t.get_tipo_display(),
            'tipo_tecnico': t.tipo,
            'descrizione': (
                f"Bonifico inviato a {controparte.utente.get_full_name()} ({controparte.iban})" if is_uscita and t.tipo == 'bonifico'
                else f"Bonifico ricevuto da {controparte.utente.get_full_name()} ({controparte.iban})" if not is_uscita and t.tipo == 'bonifico'
                else f"Soldi inviati a {nome_rubrica}" if is_uscita and t.tipo == 'invio_soldi_amico'
                else f"Soldi ricevuti da {nome_rubrica}" if not is_uscita and t.tipo == 'invio_soldi_amico'
                else "Transazione"
            ),
            'importo': f"{'-' if is_uscita else '+'}{t.importo} €",
            'importo_class': "importo-uscita" if is_uscita else "importo-entrata",
            'causale': getattr(t, 'causale', ''),
            'controparte': nome_rubrica or controparte.utente.get_full_name() or controparte.utente.cellulare,
            'iban': getattr(controparte, 'iban', ''),
        })
    return JsonResponse({'transazioni': data})


######################################################################################
# VIEW CHE GESTISCE L'INVIO DI SOLDI TRA AMICI:
#   PERMETTE DI VISUALIZZARE I CONTATTI SALVATI NELLA RUBRICA ED INVIARGLI I SOLDI
######################################################################################

class ListaContattiSalvati(SoloClientiRequiredMixin, LoginRequiredMixin, ListView):
    model = ContattoSalvato
    template_name = 'Banking/contatti_salvati.html'
    context_object_name = 'contatti'

    def get_queryset(self):
        return ContattoSalvato.objects.filter(proprietario=self.request.user)

######################################################################################
# VIEW CHE GESTISCE L'AGGIUNTA DI UN CONTATTO SALVATO:
#   PERMETTE DI AGGIUNGERE ALLA RUBRICA DELL'UTENTE LOGGATO UN NUOVO CONTATTO
######################################################################################

@login_required
@solo_clienti_required
def add_contatto(request):
    if request.method == "POST":
        form = ContattoSalvatoForm(request.POST)
        if form.is_valid():
            telefono = form.cleaned_data['telefono'].strip().replace(' ', '')
            if not telefono.startswith('+'):
                telefono = '+39' + telefono.lstrip('0')
            nome = form.cleaned_data['nome']
            try:
                utente_salvato = User.objects.get(cellulare=telefono)
            except User.DoesNotExist:
                form.add_error('telefono', "Nessun utente trovato con questo numero di telefono.")
            else:
                # Non puoi aggiungere te stesso
                if utente_salvato == request.user:
                    form.add_error('telefono', "Non puoi aggiungere te stesso come contatto.")
                # Non puoi aggiungere admin o consulenti
                elif utente_salvato.is_superuser or utente_salvato.groups.filter(name='consulenti').exists():
                    form.add_error('telefono', "Puoi aggiungere solo clienti alla rubrica.")
                elif ContattoSalvato.objects.filter(proprietario=request.user, utente_salvato=utente_salvato).exists():
                    form.add_error('telefono', "Hai già salvato questo contatto.")
                else:
                    ContattoSalvato.objects.create(
                        proprietario=request.user,
                        utente_salvato=utente_salvato,
                        nome=nome
                    )
                    return redirect('Banking:contatti_salvati')
    else:
        form = ContattoSalvatoForm()
    return render(request, "Banking/add_contact.html", {"form": form})

#######################################################################################
# VIEW AJAX PER INVIARE SOLDI A UN AMICO:
#   RICEVE L'ID DEL CONTATTO E L'IMPORTO DA INVIARE
#   ESEGUIRÀ IL TRASFERIMENTO TRA I CONTI CORRENTE
#   E RESTITUISCE UN JSON CON L'ESITO DELL'OPERAZIONE
#######################################################################################
@login_required
@solo_clienti_required
@require_POST
def ajax_invia_soldi_amico(request):
    try:
        data = json.loads(request.body)
        contatto_id = int(data.get('contatto_id'))
        importo = Decimal(str(data.get('importo')))
    except Exception:
        return JsonResponse({'success': False, 'error': 'Dati non validi.'})

    if importo <= 0:
        return JsonResponse({'success': False, 'error': 'Importo non valido.'})

    try:
        contatto = ContattoSalvato.objects.get(pk=contatto_id, proprietario=request.user)
        conto_mitt = request.user.conto_corrente
        conto_dest = contatto.utente_salvato.conto_corrente
    except ContattoSalvato.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Contatto non trovato.'})

    if conto_mitt.saldo < importo:
        return JsonResponse({'success': False, 'error': 'Saldo insufficiente.'})

    if conto_dest.pk == conto_mitt.pk:
        return JsonResponse({'success': False, 'error': 'Non puoi inviare soldi a te stesso.'})

    # Esegui trasferimento
    conto_mitt.saldo -= importo
    conto_dest.saldo += importo
    conto_mitt.save()
    conto_dest.save()
    # Crea la transazione
    Transazione.objects.create(
        tipo='invio_soldi_amico',
        conto_sorgente=conto_mitt,
        conto_destinazione=conto_dest,
        importo=importo,
        causale='Invio soldi ad amico'
    )
    return JsonResponse({'success': True})

