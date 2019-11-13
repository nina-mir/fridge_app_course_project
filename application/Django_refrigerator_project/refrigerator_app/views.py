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
from django.shortcuts import redirect


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
    all_items = Item.objects.all()
    match = None
    missing_items = None
    manual_item_list = None

    # Get list of manual items
    try:
        current_user = request.user
        user_id = User.objects.filter(username=request.user.username).get().id
        fridge = Fridge.objects.filter(owner_id=user_id).get()
        manual_item_list = fridge.manually_added_list
        print(manual_item_list)
    except:
        print(("Error getting manual groceries."))

    # Compute list of missing items
    try:
        current_user = request.user
        user_id = User.objects.filter(username=request.user.username).get().id
        fridge = Fridge.objects.filter(owner_id=user_id).get()
        tracked_item_list = fridge.auto_gen_grocery_list.split(',')

        temp = User.objects.filter(username=current_user.username).get()
        Owndfridge_id = temp.ownedfridges[0]
        inventory_items = FridgeContent.objects.filter(
            Q(fridge_id=Owndfridge_id))

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

    # Search functionality
    try:
        if request.method == 'POST':
            srch = request.POST['itemname']
            if srch:
                match = Item.objects.filter(Q(name__icontains=srch) | Q(
                    id__icontains=srch) | Q(calories__icontains=srch))
    except:
        print("Error searching for items.")

    # Selected items added to manual list
    if request.method == 'POST' and request.POST.get('grocery_selector_submit') == 'selection':
        try:
            user_id = User.objects.filter(username=request.user.username).get().id
            fridge = Fridge.objects.filter(owner_id=user_id).get()
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
            user_id = User.objects.filter(username=request.user.username).get().id
            fridge = Fridge.objects.filter(owner_id=user_id).get()
            delete_this_item = request.POST.get('delete_item')
            fridge.manually_added_list.remove(delete_this_item)
            fridge.save()
            return redirect('/groceries/')
        except:
            print("Error removing selected items to grocery list.")


    
    return render(request, 'refrigerator_project/groceries.html', {'all_items': all_items, 'sr': match, 'missing_items': missing_items,  'manual_items': manual_item_list})


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
    current_user = request.user
    user_info = User.objects.filter(username=request.user.username)
    user_id = User.objects.filter(username=request.user.username).get().id
    # ownedfridgelist = Fridges.objects.filter(id = )
    return render(request, 'refrigerator_project/profile.html', context={'user_info': user_info})


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

    current_user = request.user
    current_time = datetime.now()
    week_time = current_time + timedelta(days=7)
    # Adding Fridge
    try:
        if request.method == 'POST' and request.POST.get('add_fridge'):
            add_fridge(request.POST.get('fridge_name'), current_user.username)
    except:
        print('Error adding fridge')
    # Adding Friends
    try:
        if request.method == 'POST' and request.POST.get('add_friend_by_email'):
            print('adding friend')
            user_id = User.objects.filter(
                username=current_user.username).get().id
            friend_mail = request.POST.get('friend_email')
            friend_auth_user_username = AuthUser.objects.filter(
                email=friend_mail).get().username
            friend_user = User.objects.filter(
                username=friend_auth_user_username).get()
            fridge_id = Fridge.objects.filter(owner_id=user_id).get().id
            friend_user.friendedfridges.append(fridge_id)
            friend_user.save()
    except:
        print('Error adding friend')
    # Deleting items via trash icon
    try:
        if request.method == 'POST' and request.POST.get('delete_item'):
            delete_item(request.POST.get('delete_item'))
    except:
        print('Error deleting item from fridge.')
    # Adding items via text field
    try:
        if request.method == 'POST' and request.POST.get('add_item'):
            add_item(request.POST.get('item_name').lower(),
                     current_user.username)
    except:
        print('Error adding item.')
    try:
        # Getting primary fridge of logged in user
        temp = User.objects.filter(username=current_user.username).get()
        Owndfridge_id = temp.ownedfridges[0]

        # Sort items from their fridge based on expiration date
        inventory_items = FridgeContent.objects.filter(
            Q(fridge_id=Owndfridge_id)).order_by('expirationdate')
        fridge_name = Fridge.objects.filter(id=Owndfridge_id).get().name
    except:
        print('Error')
        return render(request, 'refrigerator_project/fridge.html')
    return render(request, 'refrigerator_project/fridge.html', {'inventory_items': inventory_items, 'fridge_name': fridge_name, 'current_date': current_time, 'week_time': week_time})


def save_to_db(id_age_list, Owndfridge_id, addedby_person_id):
    try:
        for item_id in id_age_list:
            fridge_content = FridgeContent(expirationdate=(datetime.now()+timedelta(hours=id_age_list[item_id])), size=1, creation_date=datetime.now(
            ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31), addedby_id=addedby_person_id, fridge_id=Owndfridge_id, item_id=item_id)
            fridge_content.save()
    except:
        print("Error saving item to db")


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
            print("Either missing a fridge or nothing detected")
            return redirect('/fridge/')
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
            save_to_db(selected_items, Owndfridge_id, user.id)
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
                    print('Found one jose')
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


def delete_item(content_id):
    fridge_content = FridgeContent.objects.get(id=content_id)
    fridge_content.eff_end_ts = datetime.now()
    fridge_content.save()


def add_item(item_name, current_username):
    item = Item.objects.filter(name=item_name).get()
    item_dict = {item.id: item.age}
    temp = User.objects.filter(username=current_username).get()
    Owndfridge_id = temp.ownedfridges[0]
    addedby_person_id = temp.id
    save_to_db(item_dict, Owndfridge_id, addedby_person_id)


def add_fridge(fridge_name, current_username):
    # creating fridge
    user = User.objects.filter(username=current_username).get()
    fridge = Fridge(name=fridge_name, owner=user, creation_date=datetime.now(
    ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31))
    fridge.save()
    # adding fridge to the owner
    user.ownedfridges.append(fridge.id)
    user.save()
