from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required  #for using @login_required decorator on top of a function
from refrigerator_app.models import Items

# Create your views here.

@login_required
def recipe_landing(request):
    return render(request, 'recipes/recipe_landing.html')

@login_required
def recipe_search(request):
    inventory_items = Items.objects.all()
    return render(request, 'recipes/recipe_search.html', context={'inventory_items':inventory_items})
