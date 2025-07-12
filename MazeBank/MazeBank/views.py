
from django.shortcuts import render, redirect


def homepage(request):
    """
    View function for the home page of the site.
    """
    if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='consulenti').exists()):
        return redirect('ConsulentiAdmin:homepage')
    
    return render(request, 'home.html')
 

def warning(request):
    """
    View function for the warning page of the site.
    """
    return render(request, 'warning.html')


def about(request):
    """
    View function for the about page of the site.
    """
    return render(request, 'about.html')

def services(request):
    """
    View function for the services page of the site.
    """
    return render(request, 'services.html')

