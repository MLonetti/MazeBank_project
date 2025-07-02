from Banking.models import User
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json

class DetailProfilo(DetailView):
    model = User
    template_name = 'Banking/profilo.html'
    context_object_name = 'utente'

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
        setattr(request.user, campo, valore)
        print('DOPO SETATTR, PRIMA DI SAVE:', campo, getattr(request.user, campo))
        try:
            request.user.full_clean(validate_unique=False)  # Valida i campi secondo il model
            request.user.save()
            print('DOPO IL SALVATAGGIO:', campo, getattr(request.user, campo))
            return JsonResponse({'success': True, 'campo': campo, 'valore': str(getattr(request.user, campo))})
        except Exception as e:
            print('ERRORE DI VALIDAZIONE:', str(e))
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False, 'error': 'Campo non valido'}, status=400)