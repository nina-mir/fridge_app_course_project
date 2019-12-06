import io
import sys
import math
import datetime
import refrigerator_app.fridge as fridge_import

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
    fridge_manager = fridge_import.fridge_manager(request)
    all_items = fridge_manager.getAllItems()
    match = None
    missing_items = None
    manual_item_list = None
    tracked_item_list = None

    # Get list of manual items
    try:
        manual_item_list = fridge_manager.getCurrentFridge().manually_added_list
    except:
        # fridge_manager.initialCurrentFridge(request)
        print('GROCERY VIEW: Error getting manual groceries.')
        # return redirect('/groceries/')

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
        print('GROCERY VIEW: Error getting tracked groceries.')

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
            print('GROCERY VIEW: Error saving selected items to grocery list.')

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
            print('GROCERY VIEW: Error saving selected items to grocery list.')

    # Delete Item from manual list
    if request.method == 'POST' and request.POST.get('delete_item'):
        try:
            fridge = fridge_manager.getCurrentFridge()
            delete_this_item = request.POST.get('delete_item')
            fridge.manually_added_list.remove(delete_this_item)
            fridge.save()
            return redirect('/groceries/')
        except:
            print('GROCERY VIEW: Error removing selected items to grocery list.')
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

    fridge_manager = fridge_import.fridge_manager(request)

    # previous line printed all users
    # current_user = request.user
    user_info = User.objects.filter(username=request.user.username)
    user_id = User.objects.filter(username=request.user.username).get().id
    ownedfridgelist = Fridge.objects.filter(owner_id=user_id)

    # for friended fridges column I will assume that it will be a list of fridge ids
    friendedfridgeidlist = User.objects.filter(
        username=request.user.username).get().friendedfridges

    # this is a list of the actual fridge objects matching the friendedfridgeidlist; note the __in allows us to query by list
    friendedfridgelist = Fridge.objects.filter(id__in=friendedfridgeidlist)

    # account for the deleted fridges
    actualownedfridges = fridge_manager.make_verified_fridge_list(
        ownedfridgelist)
    actualfriendedfridges = fridge_manager.make_verified_fridge_list(
        friendedfridgelist)

    # An object that holds the info from fridges in ownedfridgelist, except the there is a friends_name_list to hold names
    ownedfridge_objectlist = []
    # parameters: name, creation_date, friends_name_list, id
    for fridge in actualownedfridges:
        f_obj = fridge_manager.fridge_Object(
            fridge.name, fridge.creation_date, fridge_manager.get_name_list_from_id_list(fridge.friends), fridge.id)
        ownedfridge_objectlist.append(f_obj)

    # An object that holds the info from fridges in friendedfridgelist, except the there is a friends_name_list to hold names
    friendedfridge_objectlist = []
    # parameters: name, creation_date, friends_name_list, id
    for fridge in actualfriendedfridges:
        f_obj = fridge_manager.fridge_Object(
            fridge.name, fridge.creation_date, fridge_manager.get_name_list_from_id_list(fridge.friends), fridge.id)
        friendedfridge_objectlist.append(f_obj)

    actualownedfridges = fridge_manager.make_verified_fridge_list(
        ownedfridgelist)
    actualfriendedfridges = fridge_manager.make_verified_fridge_list(
        friendedfridgelist)

    # Setting Personal Notes
    if request.method == 'POST' and request.POST.get('add_personal_notes'):
        try:
            fridge_manager.set_personal_notes(request.POST.get(
                'personal_notes'))
        except:
            print('Error setting personal notes')

    personalnotes = User.objects.filter(
        username=request.user.username).get().personalnotes

    if personalnotes is None:
        personalnotes = ''

    context = {
        'user_info': user_info,
        'ownedfridge_objectlist': ownedfridge_objectlist,
        'friendedfridge_objectlist': friendedfridge_objectlist,
        'personalnotes': personalnotes
    }

    return render(request, 'refrigerator_project/profile.html', context)


@login_required
def add_button(request):
    print("reached add button area")
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

    

    if request.method == 'GET':
        inventory_items = Item.objects.all()
        return render(request, 'refrigerator_project/item_addition.html', {'all_items': inventory_items})

    # Selected items added to manual list
    if request.method == 'POST' and request.POST.get('grocery_selector_submit') == 'selection':
        try:
            fridge_manager = fridge_import.fridge_manager(request)
            list = request.POST.getlist('grocery_items', default=None)
            for each in list:
                fridge_manager.addItem(each)
            return redirect('/fridge/')
        except:
            print('ADD ITEM VIEW: Error saving selected items to grocery list.')


@login_required
def fridge(request):
    # Variables
    fridge_manager = fridge_import.fridge_manager(request)
    inventory_items = None
    current_fridge = None
    primary_fridge_id = None
    current_time = datetime.now()
    week_time = current_time + timedelta(days=7)
    all_fridges = None
    current_fridge_friends = None
    ownership = None
    # Get current fridge data
    try:
        all_fridges = fridge_manager.get_all_the_related_fridges()
        inventory_items = fridge_manager.getCurrentFridgeContentByExpiration()
        current_fridge = fridge_manager.getCurrentFridge()
        current_fridge_friends = fridge_manager.getCurrentFridgeFriendsUsername()
        ownership = fridge_manager.is_owner()
    except:
        # fridge_manager.initialCurrentFridge(request)
        print('FRIDGE VIEW: Error getting fridge data.')
    # Select a fridge to view
    if request.method == 'POST' and request.POST.get('select_fridge_submit'):
        try:
            fridge_manager.changeCurrentFridge(
                request.POST.get('select_fridge_selected'))
            return redirect('/fridge/')
        except:
            print('FRIDGE VIEW: Error Selecting Fridge.')
    # Setting Primary Fridge
    if request.method == 'POST' and request.POST.get('primary_fridge_submit'):
        try:
            fridge_manager.setPrimaryFridge(
                request.POST.get('primary_fridge_selected'))
        except:
            print('FRIDGE VIEW: Failed setting primary fridge.')
    # Check if Primary Fridge
    try:
        primary_fridge_id = fridge_manager.getPrimaryFridge()
    except:
        print("FRIDGE VIEW: Error getting primary fridge.")
    # Adding Fridge
    if request.method == 'POST' and request.POST.get('add_fridge'):
        try:
            if request.POST.get('fridge_name') != '':
                fridge_manager.createFridge(request.POST.get(
                    'fridge_name'))
                return redirect('/fridge/')
        except:
            print('FRIDGE VIEW: Error adding fridge')
    # Deleting Fridge
    if request.method == 'POST' and request.POST.get('delete_fridge'):
        try:
            fridge_manager.delete_current_fridge()
            return redirect('/fridge/')
        except:
            print('FRIDGE VIEW: Error deleting fridge')
    # Adding Friends
    if request.method == 'POST' and request.POST.get('add_friend_by_email'):
        try:
            fridge_manager.addFriend(request.POST.get('friend_email'))
        except:
            print('FRIDGE VIEW: Error adding friend')
    # Deleting items via trash icon
    if request.method == 'POST' and request.POST.get('delete_item'):
        try:
            fridge_manager.deleteItem(request.POST.get('delete_item'))
        except:
            print('FRIDGE VIEW: Error deleting item from fridge.')
    # Adding items via text field
    if request.method == 'POST' and request.POST.get('add_item'):
        try:
            fridge_manager.addItem(request.POST.get('item_name').lower())
            return redirect('/fridge/')
        except:
            print('FRIDGE VIEW: Error adding item.')
    # Rename current primary fridge name :: to be added checks on ownership.
    if request.method == 'POST' and request.POST.get('rename_fridge'):
        try:
            fridge_manager.renameCurrentFridge(
                request.POST.get('rename_fridge'))
            return redirect('/fridge/')
        except:
            print('FRIDGE VIEW: Error Renaming Fridge')
    # Deleting Selected Friend from fridge
    if request.method == 'POST' and request.POST.get('friend_selected_submit'):
        try:
            username = request.POST.get('select_friend_delete')
            fridge_manager.remove_friend(username)
            return redirect('/fridge/')
        except:
            print('Error deleting friend from the list')
    return render(request, 'refrigerator_project/fridge.html', {'inventory_items': inventory_items, 
            'current_fridge': current_fridge, 'primary_fridge_id': primary_fridge_id,
            'current_date': current_time, 'week_time': week_time, 
            'all_fridges': all_fridges, 'current_fridge_friends': current_fridge_friends, 
            'ownership' : ownership})


@login_required
def receipt_upload(request):
    fridge_manager = fridge_import.fridge_manager(request)
    context = {}
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
            print('RECEIPT VIEW: No items detected.')
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
            # Save to fridgeContent Table
            fridge_manager.save_to_db(selected_items)
            return redirect('/fridge/')
        except:
            print('RECEIPT VIEW: Error saving selected items to fridge.')
    return render(request, 'refrigerator_project/receipt_upload.html', context)


def detect_text(filename):
    # Google Vision
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
