from django.shortcuts import render

# Create your views here.

def consulent_administer_homepage(request):
    return render(request, 'Consulenti-Admin/homepage.html')