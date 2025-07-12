
# Create your views here.


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from Banking.forms import CustomUserCreationForm
from Banking.models import ContoCorrente

# VIEW DELL'ADMIN E CONSULENTI
@login_required
def consulent_administer_homepage(request):
    user = request.user
    is_consulente = user.groups.filter(name='consulenti').exists()
    if not (user.is_superuser or is_consulente):
        return redirect('warning')
    return render(request, 'ConsulentiAdmin/homepage.html', {'is_consulente': is_consulente})

# VIEW SOLAMENTE PER L'ADMIN

class ConsulenteCreateView(CreateView, LoginRequiredMixin):
    model = get_user_model()
    form_class = CustomUserCreationForm
    template_name = 'ConsulentiAdmin/aggiungi_consulente.html'
    success_url = reverse_lazy('ConsulentiAdmin:homepage')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('warning')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        group, _ = Group.objects.get_or_create(name='consulenti')
        self.object.groups.add(group)
        # Nessun conto corrente creato per i consulenti
        return response

# VIEW SOLAMENTE PER L'ADMIN
class ConsulenteListView(ListView, LoginRequiredMixin):
    model = get_user_model()
    template_name = 'ConsulentiAdmin/lista_consulenti.html'
    context_object_name = 'consulenti'

    def get_queryset(self):
        group = Group.objects.get(name='consulenti')
        return self.model.objects.filter(groups=group)

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('warning')
        return super().dispatch(request, *args, **kwargs)
    
# VIEW SOLAMENTE PER L'ADMIN
class ConsulenteDetailView(LoginRequiredMixin, DetailView):
    model = get_user_model()
    template_name = 'ConsulentiAdmin/dettaglio_consulente.html'
    context_object_name = 'consulente'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('warning')
        return super().dispatch(request, *args, **kwargs)


# FINE VIEW DELL'ADMIN

#############################################################################################

# VIEW PER I CONSULENTI


class ClientiSeguitiListView(LoginRequiredMixin, ListView):
    model = ContoCorrente
    template_name = 'ConsulentiAdmin/clienti_seguiti.html' 
    context_object_name = 'conti'

    def get_queryset(self):
        user = self.request.user
        # Mostra solo i conti seguiti dal consulente loggato
        return ContoCorrente.objects.filter(consulente=user)

    def dispatch(self, request, *args, **kwargs):
        # Solo per utenti nel gruppo consulenti
        if not request.user.groups.filter(name='consulenti').exists():
            return redirect('warning')
        return super().dispatch(request, *args, **kwargs)

