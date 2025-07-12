from django.shortcuts import render

# Create your views here.


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from Banking.forms import CustomUserCreationForm

@login_required
def consulent_administer_homepage(request):
    user = request.user
    is_consulente = user.groups.filter(name='consulenti').exists()
    if not (user.is_superuser or is_consulente):
        return redirect('warning')
    return render(request, 'ConsulentiAdmin/homepage.html', {'is_consulente': is_consulente})


class ConsulenteCreateView(CreateView):
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

