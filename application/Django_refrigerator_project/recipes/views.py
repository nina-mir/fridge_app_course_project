from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings

# Create your views here.

def recipe_landing(request):
    return render(request, 'recipes/recipe_landing.html')
