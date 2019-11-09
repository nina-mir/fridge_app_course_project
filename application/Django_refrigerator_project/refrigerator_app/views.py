from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
# for using @login_required decorator on top of a function
from django.contrib.auth.decorators import login_required
import io
from io import BytesIO
import sys
import math
from .models import Item, FridgeContent
from users.models import User
from users.models import AuthUser
from django.db.models import Q
from .models import Fridge
import datetime
from datetime import timedelta
from datetime import datetime
# Create your views here.


def home(request):
    return render(request, 'refrigerator_project/home.html')

@login_required
def delete_item(request):
    inventory_items = Item.objects.all()

    return render(request, 'refrigerator_project/home.html', context={'inventory_items': inventory_items})


@login_required
def groceries(request):
    all_items = Item.objects.all()
    try:
        current_user = request.user
        user_id = User.objects.filter(username=request.user.username).get().id
        fridge = Fridge.objects.filter(owner_id = user_id).get()
        tracked_items = fridge.auto_gen_grocery_list.split(',')
        manual_items = fridge.manually_added_list.split(',')
        temp = User.objects.filter(username = current_user.username).get()
        Owndfridge_id = int(temp.ownedfridges.split(',')[0])
        inventory_items = FridgeContent.objects.filter(Q(fridge_id = Owndfridge_id))

        # Check for Tracked items missing from fridge
        missing_items = []
        for tItems in tracked_items:
            inFridge = False
            for iItems in inventory_items:
                if (tItems == iItems):
                    inFridge = True
            if (inFridge == False):
                missing_items.append(tItems)

        # Search for item functionality
        if(request.method == 'POST'):
            srch = request.POST['itemname']
            if srch:
                match = Item.objects.filter(Q(name__icontains=srch) | Q(
                    id__icontains=srch) | Q(calories__icontains=srch))
                if match:
                    return render(request, 'refrigerator_project/groceries.html', {'sr': match, 'missing_items': missing_items,  'manual_items': manual_items})
        return render(request, 'refrigerator_project/groceries.html', {'all_items': all_items, 'missing_items': missing_items,  'manual_items': manual_items})
    except:
        print('Error Finding Grocery Lists')
    return render(request, 'refrigerator_project/groceries.html', {'all_items': all_items})



@login_required
def profile(request):
    user_info = User.objects.all()
    return render(request, 'refrigerator_project/profile.html', context={'user_info': user_info})


@login_required
def fridge(request):
    current_user = request.user
    current_time = datetime.now()
    week_time = current_time + timedelta(days=7)
    # Deleting item with using button
    try:
        if request.method == 'POST':
            if request.POST.get('delete_item'):
                content_id = request.POST.get('delete_item')
                fridge_content = FridgeContent.objects.get(id = content_id)
                fridge_content.eff_end_ts = datetime.now()
                fridge_content.save()
    except:
        print('Error from adding deleteing an item')
    # adding item using Button
    try:
        if request.method == 'POST':
            if request.POST.get('add_item'):
                item_name = request.POST.get('item_name').lower()
                item = Item.objects.filter(name=item_name).get()
                item_dict = {item.id:item.age}
                temp = User.objects.filter(username = current_user.username).get()
                Owndfridge_id = int(temp.ownedfridges.split(',')[0])
                addedby_person_id = temp.id
                save_to_db(item_dict, Owndfridge_id, addedby_person_id)
    except:
        print('Add item failed')
    try:
        #Getting primary fridge of logged in user
        temp = User.objects.filter(username = current_user.username).get()
        Owndfridge_id = int(temp.ownedfridges.split(',')[0])

        #Sort items from their fridge based on expiration date
        inventory_items = FridgeContent.objects.filter(Q(fridge_id = Owndfridge_id)).order_by('expirationdate')
        fridge_name = Fridge.objects.filter(id = Owndfridge_id).get().name
    except:
        print('Error')
        return render(request,'refrigerator_project/fridge.html')
    return render(request,'refrigerator_project/fridge.html', {'inventory_items':inventory_items, 'fridge_name':fridge_name, 'current_date': current_time, 'week_time': week_time})


def save_to_db(id_age_list, Owndfridge_id, addedby_person_id):
    try:
        for item_id in id_age_list:
            fridge_content = FridgeContent(expirationdate= (datetime.now()+timedelta(hours=id_age_list[item_id])), size=1, creation_date=datetime.now(), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999,12,31), addedby_id=addedby_person_id, fridge_id=Owndfridge_id, item_id=item_id)
            fridge_content.save()
    except:
        print("Error saving item to db")


# this function does 2 things:
# 1) user uploads an image of a receipt which will be processed
# And, returns a list of item names to be verified by the user. (POST request)
# 2) The user verifies which items they want to be added to their fridge
# they can do so by selecting appropriate checkboxes and submitting the result. (GET request) 

@login_required
def simple_upload(request):
    context = {}
    current_user = request.user
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print(filename)

        id_list, text = detect_text(filename)
        context={'text':text}
        return render(request, 'refrigerator_project/receipt_upload.html', context)
    else:
        if request.method == 'GET':
            response = request.GET
            list =response.getlist('ingredient', default=None)
        
        tmp_id_exp_age_store = {}
        for i in list:
            temp_ = Item.objects.filter(Q(name__icontains = i))
            for each in temp_:
                if each.name.lower() == i.lower():
                    print('Found one')
                    tmp_id_exp_age_store[each.id] = each.age
                    break

        temp = User.objects.filter(username = current_user.username).get()
        Owndfridge_id = int(temp.ownedfridges.split(',')[0])
        addedby_person_id = temp.id

        #Save to fridgeContent Table
        save_to_db(tmp_id_exp_age_store,Owndfridge_id,addedby_person_id)
    return render(request, 'refrigerator_project/receipt_upload.html', context)



# Google Vision
def detect_text(filename):
    post_processing_results = []
    tmp_id_exp_age_store = {}

    """Detects text in the file."""
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()

    with io.open(filename, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    nina = next(iter(texts))
    #print(type(nina))
    #print(type(nina.description))
    output = nina.description.splitlines( )
    for x in output:
        splitted = x.split()
        for i in splitted:
            temp = Item.objects.filter(Q(name__icontains = i))
            for each in temp:
                if each.name.lower() == i.lower():
                    print('Found one')
                    post_processing_results.append(each.name)
                    tmp_id_exp_age_store[each.id] = each.age
                    break
    return tmp_id_exp_age_store, post_processing_results


@login_required
def search(request):
    if(request.method == 'POST'):
        srch = request.POST['itemname']
        if srch:
            match = Item.objects.filter(Q(name__icontains = srch) | Q(id__icontains = srch) | Q(calories__icontains = srch))
            if match:
                return render(request,'refrigerator_project/search.html',{'sr':match})
    return render(request,'refrigerator_project/search.html')
