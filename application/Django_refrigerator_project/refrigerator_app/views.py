import io
import sys
import math
import datetime

from io import BytesIO

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

from .models import Fridge, Item, FridgeContent

from users.models import AuthUser
from users.models import User
import refrigerator_app.fridge as fridge_manager

from datetime import datetime
from datetime import timedelta
# for using @login_required decorator on top of a function


def home(request):
    return render(request, 'refrigerator_project/home.html')


@login_required
def groceries(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return receipt_upload(request)
    except:
        pass
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            receipt_upload(request)
            return redirect('/fridge/')
    except:
        pass

    # Variables
    all_items = fridge_manager.getAllItems()
    match = None
    missing_items = None
    manual_item_list = None
    tracked_item_list = None

    # Get list of manual items
    try:
        manual_item_list = fridge_manager.getCurrentFridge().manually_added_list
    except:
        print(("Error getting manual groceries."))

    # Compute list of missing items
    try:
        tracked_item_list = fridge_manager.getCurrentFridge().auto_gen_grocery_list
        inventory_items = fridge_manager.getCurrentFridgeContent()

        # Check for Tracked items missing from fridge
        missing_items = []
        current_time = datetime.now()
        for tItems in tracked_item_list:
            inFridge = False
            for iItems in inventory_items:
                if (iItems.eff_end_ts > current_time):
                    if (tItems == iItems.item.name):
                        inFridge = True
            if (inFridge == False):
                missing_items.append(tItems)
    except:
        print('Error getting tracked groceries.')

    # Tracked item selection
    if request.method == 'POST' and request.POST.get('tracked_selector_submit') == 'selection':
        try:
            # user_id = User.objects.filter(username=request.user.username).get().id
            fridge = fridge_manager.getCurrentFridge()
            list = request.POST.getlist('tracked_items', default=None)
            fridge.auto_gen_grocery_list.clear()
            for each in list:
                fridge.auto_gen_grocery_list.append(each)
            fridge.save()
            return redirect('/groceries/')
        except:
            print("Error saving selected items to grocery list.")

    # Selected items added to manual list
    if request.method == 'POST' and request.POST.get('grocery_selector_submit') == 'selection':
        try:
            fridge = fridge_manager.getCurrentFridge()
            list = request.POST.getlist('grocery_items', default=None)
            for each in list:
                fridge.manually_added_list.append(each)
            fridge.save()
            return redirect('/groceries/')
        except:
            print("Error saving selected items to grocery list.")

    # Delete Item from manual list
    if request.method == 'POST' and request.POST.get('delete_item'):
        try:
            fridge = fridge_manager.getCurrentFridge()
            delete_this_item = request.POST.get('delete_item')
            fridge.manually_added_list.remove(delete_this_item)
            fridge.save()
            return redirect('/groceries/')
        except:
            print("Error removing selected items to grocery list.")
    return render(request, 'refrigerator_project/groceries.html', {'all_items': all_items, 'sr': match, 'missing_items': missing_items, 'tracked_items': tracked_item_list, 'manual_items': manual_item_list})


@login_required
def profile(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return receipt_upload(request)
    except:
        pass
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            receipt_upload(request)
            return redirect('/fridge/')
    except:
        pass

    # previous line printed all users
    # current_user = request.user
    user_info = User.objects.filter(username=request.user.username)
    user_id = User.objects.filter(username=request.user.username).get().id
    ownedfridgelist = Fridge.objects.filter(owner_id=user_id)

    # for friended fridges column I will assume that it will be a list of fridge ids
    friendedfridgeidlist = User.objects.filter(
        username=request.user.username).get().friendedfridges

    #this is a list of the actual fridge objects matching the friendedfridgeidlist; note the __in allows us to query by list  
    friendedfridgelist = Fridge.objects.filter(id__in = friendedfridgeidlist)
    
    #account for the deleted fridges
    actualownedfridges = fridge_manager.make_verified_fridge_list(ownedfridgelist)
    actualfriendedfridges = fridge_manager.make_verified_fridge_list(friendedfridgelist)

    #An object that holds the info from fridges in ownedfridgelist, except the there is a friends_name_list to hold names
    ownedfridge_objectlist = []
    #parameters: name, creation_date, friends_name_list, id
    for fridge in actualownedfridges:
        f_obj = fridge_manager.fridge_Object(fridge.name, fridge.creation_date, fridge_manager.get_name_list_from_id_list(fridge.friends), fridge.id)
        ownedfridge_objectlist.append(f_obj)

    
    #An object that holds the info from fridges in friendedfridgelist, except the there is a friends_name_list to hold names
    friendedfridge_objectlist = []
    #parameters: name, creation_date, friends_name_list, id
    for fridge in actualfriendedfridges:
        f_obj = fridge_manager.fridge_Object(fridge.name, fridge.creation_date, fridge_manager.get_name_list_from_id_list(fridge.friends), fridge.id)
        friendedfridge_objectlist.append(f_obj)

    actualownedfridges = fridge_manager.make_verified_fridge_list(ownedfridgelist)
    actualfriendedfridges = fridge_manager.make_verified_fridge_list(friendedfridgelist)
    
    context = {
        'user_info': user_info,
        'ownedfridge_objectlist': ownedfridge_objectlist,
        'friendedfridge_objectlist': friendedfridge_objectlist
    }

    return render(request, 'refrigerator_project/profile.html', context)


@login_required
def fridge(request):
    # Send user to receipt upload page upon "+" button click
    try:
        if request.method == 'POST' and request.FILES['receipt_image']:
            return receipt_upload(request)
    except:
        pass
    try:
        if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
            receipt_upload(request)
            return redirect('/fridge/')
    except:
        print("No Selected items.")

    # Variables
    current_user = request.user

    inventory_items = None
    current_fridge = None
    is_primary_fridge = None
    current_time = datetime.now()
    week_time = current_time + timedelta(days=7)
    all_fridges = fridge_manager.get_all_the_related_fridges()

    # Adding Fridge
    if request.method == 'POST' and request.POST.get('add_fridge'):
        try:
            if request.POST.get('fridge_name') != '':
                fridge_manager.createFridge(request.POST.get(
                    'fridge_name'))
                return redirect('/fridge/')
        except:
            print('Error adding fridge')
    # Deleting Fridge
    if request.method == 'POST' and request.POST.get('delete_fridge'):
        try:
            fridge_manager.delete_current_fridge()
        except:
            print("Error deleting fridge")
    # Adding Friends
    if request.method == 'POST' and request.POST.get('add_friend_by_email'):
        try:
            fridge_manager.addFriend(request.POST.get('friend_email'))
        except:
            print('Error adding friend')
    # Deleting items via trash icon
    if request.method == 'POST' and request.POST.get('delete_item'):
        try:
            fridge_manager.deleteItem(request.POST.get('delete_item'))
        except:
            print('Error deleting item from fridge.')
    # Adding items via text field
    if request.method == 'POST' and request.POST.get('add_item'):
        try:
            fridge_manager.addItem(request.POST.get('item_name').lower())
            return redirect('/fridge/')
        except:
            print('Error adding item.')
    # Rename current primary fridge name :: to be added checks on ownership.
    if request.method == 'POST' and request.POST.get('rename_fridge'):
        try:
            fridge_manager.renameCurrentFridge(
                request.POST.get('rename_fridge'))
            return redirect('/fridge/')
        except:
            print('Error Renaming Fridge')
    # Setting Primary Fridge
    if request.method == 'POST' and request.POST.get('primary_checkbox')  == 'check':
        try:
            fridge_manager.setPrimaryFridge()
        except:
            print('Failed setting primary fridge.')
    # Check if Primary Fridge
    if fridge_manager.checkIfPrimaryFridge():
        is_primary_fridge = True
    else:
        is_primary_fridge = False
    # Get current fridge data
    try:
        inventory_items = fridge_manager.getCurrentFridgeContentByExpiration()
        current_fridge = fridge_manager.getCurrentFridge()
    except:
        print('Error')
        return render(request, 'refrigerator_project/fridge.html')
    return render(request, 'refrigerator_project/fridge.html', {'inventory_items': inventory_items, 'current_fridge': current_fridge, 'is_primary_fridge': is_primary_fridge,
                   'current_date': current_time, 'week_time': week_time, 'all_fridges': all_fridges})


@login_required
def receipt_upload(request):
    context = {}
    current_user = request.user
    # Display found receipt content upon image receipt
    print(request.POST)
    if request.method == 'POST':
        try:
            if request.FILES['receipt_image']:
                myfile = request.FILES['receipt_image']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                text = detect_text(filename)[1]
                # text = {'coffee'} #used for testing
                context = {'text': text}
        except:
            print("No items detected.")
    # Get list of selected found items and save it to db
    if request.method == 'POST' and request.POST.get('validate_items') == 'selection':
        print("submitted")
        try:
            list = request.POST.getlist('selected_items', default=None)
            print(list)
            selected_items = {}
            for i in list:
                temp_ = Item.objects.filter(Q(name__icontains=i))
                for j in temp_:
                    if j.name.lower() == i.lower():
                        selected_items[j.id] = j.age
                        break
            user = User.objects.filter(username=current_user.username).get()
            Owndfridge_id = user.ownedfridges[0]
            # Save to fridgeContent Table
            fridge_manager.save_to_db(selected_items, Owndfridge_id, user.id)
            return redirect('/fridge/')
        except:
            print("Error saving selected items to fridge.")
    return render(request, 'refrigerator_project/receipt_upload.html', context)

# Google Vision


def detect_text(filename):
    post_processing_results = []
    tmp_id_exp_age_store = {}
    # Detects text in the file.
    from google.cloud import vision
    import io
    client = vision.ImageAnnotatorClient()
    with io.open(filename, 'rb') as image_file:
        content = image_file.read()
    image = vision.types.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    nina = next(iter(texts))
    output = nina.description.splitlines()
    for x in output:
        splitted = x.split()
        for i in splitted:
            temp = Item.objects.filter(Q(name__icontains=i))
            for each in temp:
                if each.name.lower() == i.lower():
                    post_processing_results.append(each.name)
                    tmp_id_exp_age_store[each.id] = each.age
                    break
    return tmp_id_exp_age_store, post_processing_results


@login_required
def search(request):
    if(request.method == 'POST'):
        srch = request.POST['itemname']
        if srch:
            match = Item.objects.filter(Q(name__icontains=srch) | Q(
                id__icontains=srch) | Q(calories__icontains=srch))
            if match:
                return render(request, 'refrigerator_project/search.html', {'sr': match})
    return render(request, 'refrigerator_project/search.html')


# def delete_item(content_id):
#     fridge_content = FridgeContent.objects.get(id=content_id)
#     fridge_content.eff_end_ts = datetime.now()
#     fridge_content.save()


# def add_item(item_name, current_username):
#     item = Item.objects.filter(name=item_name).get()
#     item_dict = {item.id: item.age}
#     temp = User.objects.filter(username=current_username).get()
#     Owndfridge_id = temp.ownedfridges[0]
#     addedby_person_id = temp.id
#     save_to_db(item_dict, Owndfridge_id, addedby_person_id)


# def add_fridge(fridge_name, current_username):
#     # creating fridge
#     user = User.objects.filter(username=current_username).get()
#     fridge = Fridge(name=fridge_name, owner=user, creation_date=datetime.now(
#     ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31))
#     fridge.save()
#     # adding fridge to the owner
#     user.ownedfridges.append(fridge.id)
#     user.save()

# def save_to_db(id_age_list, Owndfridge_id, addedby_person_id):
#     try:
#         for item_id in id_age_list:
#             fridge_content = FridgeContent(expirationdate=(datetime.now()+timedelta(hours=id_age_list[item_id])), size=1, creation_date=datetime.now(
#             ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31), addedby_id=addedby_person_id, fridge_id=Owndfridge_id, item_id=item_id)
#             fridge_content.save()
#     except:
#         print("Error saving item to db")
