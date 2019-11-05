from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required  #for using @login_required decorator on top of a function
from refrigerator_app.models import Item,Fridge
from users.models import User
from django.db.models import Q

# Create your views here.

@login_required
def recipe_landing(request):
    current_user = request.user
    try:
        #Getting all fridges of logged in user
        temp = User.objects.filter(username = current_user.username).get()
        Owndfridge_id = temp.ownedfridges.split(',')
        Owndfridge_id = [int(x) for x in Owndfridge_id]

        fridge_list = Fridge.objects.filter(id = Owndfridge_id)
        print(fridge_list)
        context={
        'fridge_list':fridge_list
        }
    except:
        print('Error')
        return render(request, 'recipes/recipe_landing.html')
    return render(request, 'recipes/recipe_landing.html',context = context)

@login_required
def recipe_search(request):
    inventory_items = Item.objects.all()
    return render(request, 'recipes/recipe_search.html', context={'inventory_items':inventory_items})
