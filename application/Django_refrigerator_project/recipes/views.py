import json
import requests
import refrigerator_app.fridge as fridge_import

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
# for using @login_required decorator on top of a function
from django.contrib.auth.decorators import login_required
from refrigerator_app.models import Item, Fridge, FridgeContent
from users.models import User
from django.db.models import Q
from refrigerator_app import views as fridge_views
from django.shortcuts import redirect


@login_required
def recipe_landing(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return fridge_views.receipt_upload(request)
    except:
        pass
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            fridge_views.receipt_upload(request)
            return redirect('/fridge/')
    except:
        pass

    fridge_manager = fridge_import.fridge_manager(request)
    try:
        current_fridge = fridge_manager.getCurrentFridge()
        context = {'current_fridge': current_fridge}
        return render(request, 'recipes/recipe_landing.html', context=context)
    except:
        return render(request, 'recipes/recipe_landing.html')


@login_required
def recipe_search(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return fridge_views.receipt_upload(request)
    except:
        pass
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            fridge_views.receipt_upload(request)
            return redirect('/fridge/')
    except:
        pass

    # Variables
    fridge_manager = fridge_import.fridge_manager(request)
    inventory_items = None
    fridge_con_items = fridge_manager.getCurrentFridgeContentByExpiration()
    tmp_list = list(set([x.item.id for x in fridge_con_items]))
    inventory_items = Item.objects.filter(id__in=tmp_list)

    if inventory_items:
        return render(request, 'recipes/recipe_search.html', context={'inventory_items': inventory_items})
    else:
        inventory_items = Item.objects.all()
        return render(request, 'recipes/recipe_search.html', context={'inventory_items': inventory_items})


@login_required
def recipe_search_results(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return fridge_views.receipt_upload(request)
    except:
        pass
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            fridge_views.receipt_upload(request)
            return redirect('/fridge/')
    except:
        pass

    if request.method == 'GET':
        response = request.GET
        list = response.getlist('ingredient', default=None)
        print(response)
        print(list)
        # Using for loop
        kompi = ""
        for i in list:
            kompi = i + "," + kompi
        print(kompi)
        get_recipes = food2fork_call(kompi)
        context = process_recipes(get_recipes)
        print(context['count'])
        print(type(context))
    return render(request, 'recipes/recipe_search_results.html', {'count': context['count'],
                                                                  'recipes': context['recipes']})

# method to mkae API call to food2fork recipe API


def food2fork_call(list):
    # you have to sign up for an API key, which has some allowances.
    # Check the API documentation for further details:
    url = 'https://www.food2fork.com/api/search'

    key = '6e81eadfd535b092815e395bcc38be11'
    #key = '57604ca61ce33d68532bb9af7f0472f9'
    paramsPost = {
        'key': key,
        'q': list,
        # (optional) How the results should be sorted. See Below for details.
        'sort': 'r',
        'page': '0'  # (optional) Used to get additional results}
    }

    responsePost = requests.post(url, paramsPost)
    if responsePost.status_code == 202:  # everything went well!
        print('food2dork: all good!')
    # print(responsePost.content)
    try:
        result = responsePost.json()
    except ValueError:
        result = {'error': 'No JSON content returned'}
    return responsePost.text


def process_recipes(str):
    toSee = json.loads(str)
    print(type(toSee))
    print("string value: %s" % toSee["count"])
    recipes = toSee["recipes"]
    print(type(recipes))
    return toSee
    # print(len(recipes))
    # for x in range(len(recipes)):
    #     print(x)
    #     #print(recipes[x])
    #     print(recipes[x]["title"])
    #     print(recipes[x]["publisher"])
