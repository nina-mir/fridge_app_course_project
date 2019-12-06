import json
import requests
import refrigerator_app.fridge as fridge_import

from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from refrigerator_app.models import Item, Fridge, FridgeContent, Recipe
from users.models import User
from django.db.models import Q
from refrigerator_app import views as fridge_views
from django.shortcuts import redirect

from datetime import datetime
from datetime import timedelta


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

    # Variables
    fridge_manager = fridge_import.fridge_manager(request)
    context = None

    # Delete Saved Recipes
    if request.method == 'POST' and request.POST.get('delete_recipe'):
        try:
            Recipe.objects.filter(
                id=request.POST.get('delete_recipe')).delete()
            return redirect('/recipes/')
        except:
            pass

    # Get Fridge data and saved recipe data
    try:
        current_fridge = fridge_manager.getCurrentFridge()
        saved_recipes = Recipe.objects.filter(fridge_id=current_fridge.id)
        context = {'current_fridge': current_fridge,
                   'saved_recipes': saved_recipes}
    except:
        pass
    return render(request, 'recipes/recipe_landing.html', context)


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
    current_fridge = fridge_manager.getCurrentFridge()
    inventory_items = None
    fridge_con_items = fridge_manager.getCurrentFridgeContentByExpiration()
    tmp_list = list(set([x.item.id for x in fridge_con_items]))
    inventory_items = Item.objects.filter(id__in=tmp_list)

    if not inventory_items:
        inventory_items = Item.objects.all()

    context = {'current_fridge': current_fridge,
               'inventory_items': inventory_items}
    return render(request, 'recipes/recipe_search.html', context)


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

    # Variables
    fridge_manager = fridge_import.fridge_manager(request)
    current_fridge = None
    recipe_data = None
    context = None

    # Get refrigerator data
    try:
        current_fridge = fridge_manager.getCurrentFridge()
        context = {'current_fridge': current_fridge}
    except:
        print('RECIPE_RESULTS VIEW: No Fridge found.')

    # Get recipe results
    if request.method == 'GET':
        try:
            list = request.GET.getlist('ingredient', default=None)
            ingredients = ""
            for i in list:
                ingredients = i + "," + ingredients
            recipe_data = food2fork_call(ingredients)
            context = {'current_fridge': current_fridge,
                       'recipes': recipe_data['recipes']}
        except:
            print('RECIPE_RESULTS VIEW: Error getting food2fork data.')

    # Save recipes
    if request.method == 'POST' and request.POST.get('saved_recipe'):
        try:
            title,sourceurl,imageurl = request.POST.get("saved_recipe").split(",")

            recipe_save = Recipe(
            eff_bgn_ts=datetime.now(),
            eff_end_ts=datetime(9999, 12, 31),
            user_id=request.session['current_user_id'],
            fridge_id=request.session['current_fridge_id'],
            title = title,
            sourceurl = sourceurl,
            imageurl = imageurl
            )
            recipe_save.save()
            return redirect('/recipes/')

        except:
            print('RECIPE_RESULTS VIEW: Error saving recipe.')
    return render(request, 'recipes/recipe_search_results.html', context)


def food2fork_call(list):
    # Key 1 Attempt
    key = '6e81eadfd535b092815e395bcc38be11'
    paramsPost = {
         'key': key,
         'q': list,
         'sort': 'r',
         'page': '0'
    }
    responsePost = requests.post('https://www.food2fork.com/api/search', paramsPost)

     # Key 2 Attempt
    if responsePost.text == '{"error": "limit"}':
        key = '57604ca61ce33d68532bb9af7f0472f9'
        paramsPost = {
             'key': key,
             'q': list,
             'sort': 'r',
             'page': '0'
        }
        responsePost = requests.post('https://www.food2fork.com/api/search', paramsPost)

    if responsePost.status_code == 202:
        print('FOOD2FORK: Data received.')

    #fakePost = '{"count": 30, "recipes": [{"publisher": "Simply Recipes", "f2f_url": "http://food2fork.com/view/36482", "title": "How to Make Fruit Leather", "source_url": "http://www.simplyrecipes.com/recipes/how_to_make_fruit_leather/", "recipe_id": "36482", "image_url": "http://static.food2fork.com/fruitleather300x2001f9f84c4.jpg", "social_rank": 99.99999999999989, "publisher_url": "http://simplyrecipes.com"}, {"publisher": "Simply Recipes", "f2f_url": "http://food2fork.com/view/37128", "title": "Waldorf Salad", "source_url": "http://www.simplyrecipes.com/recipes/waldorf_salad/", "recipe_id": "37128", "image_url": "http://static.food2fork.com/waldorfsalad300x20000f287fd.jpg", "social_rank": 99.9999667957302, "publisher_url": "http://simplyrecipes.com"}, {"publisher": "All Recipes", "f2f_url": "http://food2fork.com/view/15768", "title": "Groovy Green Smoothie", "source_url": "http://allrecipes.com/Recipe/Groovy-Green-Smoothie/Detail.aspx", "recipe_id": "15768", "image_url": "http://static.food2fork.com/4511209622.jpg", "social_rank": 99.97384730336904, "publisher_url": "http://allrecipes.com"}]}'
    return json.loads(responsePost.text)
    #return json.loads(fakePost)
