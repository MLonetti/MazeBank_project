

from django.shortcuts import render

def homepage(request):
    """
    View function for the home page of the site.
    """
    return render(request, 'home.html')