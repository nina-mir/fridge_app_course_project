from users.models import AuthUser
from users.models import User
from .models import Fridge, Item, FridgeContent
from django.db.models import Q
from django.shortcuts import redirect
from datetime import datetime
from datetime import timedelta
from users.models import AuthUser
from users.models import User

current_fridge_id = None

def initialCurrentFridge(request):
    global current_fridge_id
    current_fridge_id = None
    # Set current fridge as primary fridge (if available)
    try:
        pass
    except:
        print("No primary fridge found.")
    # Set current fridge as first fridge found with user's id
    try:
        user_id = User.objects.filter(username=request.user.username).get()
        if user_id.ownedfridges[0]: 
            current_fridge_id = user_id.ownedfridges[0] 
        elif user_id.friendedfridges[0]:
            current_fridge_id = user_id.friendedfridges[0] 
        else:
            current_fridge_id = None
            print("No Fridges found.")
            return redirect('/fridge/')
    except:
        print("No Fridges found.")
    return redirect('/fridge/')

def getCurrentFridge():
    if(current_fridge_id):
        current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
        return current_fridge
    else:
        return None

def getCurrentFridgeContent():
    fridge_content = FridgeContent.objects.filter(Q(fridge_id=current_fridge_id))
    return fridge_content

def getCurrentFridgeContentByExpiration():
    fridge_content_expiration = FridgeContent.objects.filter(Q(fridge_id=current_fridge_id)).order_by('expirationdate')
    return fridge_content_expiration

def changeCurrentFridge(fridge_id):
    global current_fridge_id
    current_fridge_id = fridge_id
    return None

def renameCurrentFridge(new_name):
    current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
    current_fridge.name = new_name
    current_fridge.save()
    return None

def deleteItem(item_id):
    fridge_content = FridgeContent.objects.get(id=item_id)
    fridge_content.eff_end_ts = datetime.now()
    fridge_content.save()
    return None

def addItem(item_name, current_username):
    item = Item.objects.filter(name=item_name).get()
    item_dict = {item.id: item.age}
    user_id = User.objects.filter(username=current_username).get().id
    save_to_db(item_dict, current_fridge_id, user_id)
    return None

def addFriend(friend_email):
    # Get friend's username
    friend_auth_user_username = AuthUser.objects.filter(email=friend_email).get().username
    # Save fridge to friend's account
    friend_auth_user_username = AuthUser.objects.filter(email=friend_email).get().username
    friend_user = User.objects.filter(username=friend_auth_user_username).get()
    if current_fridge_id not in friend_user.friendedfridges:
        friend_user.friendedfridges.append(current_fridge_id)
        friend_user.save()
    # Save friend to current fridge
    friends_id = User.objects.filter(username=friend_auth_user_username).get().id
    current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
    if friends_id not in current_fridge.friends:
        current_fridge.friends.append(friends_id)
        current_fridge.save()
    return None

def save_to_db(id_age_list, Owndfridge_id, addedby_person_id):
    try:
        for item_id in id_age_list:
            fridge_content = FridgeContent(expirationdate=(datetime.now()+timedelta(hours=id_age_list[item_id])), size=1, creation_date=datetime.now(
            ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31), addedby_id=addedby_person_id, fridge_id=Owndfridge_id, item_id=item_id)
            fridge_content.save()
    except:
        print("Error saving item to db")
    return None

def createFridge(fridge_name, current_username):
    global current_fridge_id
    user = User.objects.filter(username=current_username).get()
    fridge = Fridge(name=fridge_name, owner=user, creation_date=datetime.now(
    ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31))
    fridge.save()
    user.ownedfridges.append(fridge.id)
    user.save()
    current_fridge_id = fridge.id
    return None

def getAllItems():
    return Item.objects.all()
