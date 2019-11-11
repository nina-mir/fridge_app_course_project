import json
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required  #for using @login_required decorator on top of a function
from refrigerator_app.models import Item,Fridge
from users.models import User
from django.db.models import Q
from refrigerator_app import views as fridge_views

@login_required
def recipe_landing(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return fridge_views.receipt_upload(request)
    except:
        print("No image.")
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            fridge_views.receipt_upload(request)
    except:
        print("No Selected items.")

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
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return fridge_views.receipt_upload(request)
    except:
        print("No image.")
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            fridge_views.receipt_upload(request)
    except:
        print("No Selected items.")

    inventory_items = Item.objects.all()
    return render(request, 'recipes/recipe_search.html', context={'inventory_items':inventory_items})

@login_required
def recipe_search_results(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return fridge_views.receipt_upload(request)
    except:
        print("No image.")
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            fridge_views.receipt_upload(request)
    except:
        print("No Selected items.")

    if request.method == 'GET':
        response = request.GET
        list =response.getlist('ingredient', default=None)
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
    return render(request, 'recipes/recipe_search_results.html', {'count':context['count'],
    'recipes':context['recipes']} )

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
        'sort': 'r', #(optional) How the results should be sorted. See Below for details.
        'page': '0' #(optional) Used to get additional results} 
    }
    
    responsePost = requests.post(url, paramsPost)
    if responsePost.status_code == 202: # everything went well!
        print('food2dork: all good!')
    #print(responsePost.content)
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