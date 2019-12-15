from users.models import AuthUser
from users.models import User
from .models import Fridge, Item, FridgeContent
from django.db.models import Q
from django.shortcuts import redirect
from datetime import datetime
from datetime import timedelta
from users.models import AuthUser
from users.models import User


def initialCurrentFridge(request):
    # Delete Previous Session data
    request.session['current_user_id'] = None
    request.session['current_fridge_id'] = None
    # Save user id to session
    request.session['current_user_id'] = User.objects.filter(
        username=request.user.username).get().id
    # Get user
    user = User.objects.filter(id=request.session['current_user_id']).get()
    # Set current fridge as primary fridge (if available)
    if user.primary_fridge != -1:
        try:
            request.session['current_fridge_id'] = Fridge.objects.filter(
                id=user.primary_fridge).get().id
        except:
            print("FRIDGE INITIALIZER: No primary fridge found.")
    # Set current fridge as first fridge found with user's id
    else:
        try:
            try:
                request.session['current_fridge_id'] = user.ownedfridges[0]
            except:
                request.session['current_fridge_id'] = user.friendedfridges[0]
        except:
            print("FRIDGE INITIALIZER: No Fridges found.")
    return redirect('/fridge/')


class fridge_manager():
    def __init__(self, request):
        self.session = request.session
        try:
            self.session['current_fridge_id']
            self.session['current_user_id']
        except:
            initialCurrentFridge(request)

    def refindCurrentFridge(self):
        self.session['current_fridge_id'] = None
        # Get User
        user = User.objects.filter(id=self.session['current_user_id']).get()
        # Set current fridge as primary fridge (if available)
        if user.primary_fridge != -1:
            try:
                self.session['current_fridge_id'] = Fridge.objects.filter(
                    id=user.primary_fridge).get().id
            except:
                print("FRIDGE REFINDER: No primary fridge found.")
        # Set current fridge as first fridge found with user's id
        else:
            try:
                try:
                    self.session['current_fridge_id'] = user.ownedfridges[0]
                except:
                    self.session['current_fridge_id'] = user.friendedfridges[0]
            except:
                print("FRIDGE INITIALIZER: No Fridges found.")

    def getCurrentFridge(self):
        if(self.session['current_fridge_id']):
            current_fridge = Fridge.objects.filter(
                id=self.session['current_fridge_id']).get()
            return current_fridge
        else:
            return None

    def getCurrentFridgeContent(self):
        fridge_content_expiration = FridgeContent.objects.filter(
            Q(fridge_id=self.session['current_fridge_id'])).order_by('expirationdate')
        current_fridge_content = []
        for each in fridge_content_expiration:
            if each.eff_end_ts > datetime.now():
                current_fridge_content.append(each)
        return current_fridge_content

    def getCurrentFridgeContentByExpiration(self):
        # Get Current Items
        current_time = datetime.now()
        current_fridge_content = []
        fridge_content = FridgeContent.objects.filter(
            Q(fridge_id=self.session['current_fridge_id'])).order_by('expirationdate')
        for each in fridge_content:
            if each.eff_end_ts > current_time:
                current_fridge_content.append(each)
        
        # Organize items into dictionary
        week_time = current_time + timedelta(days=7)
        fridge_content_expiration = {'expired': [], 'expiring': [], 'fresh': []}
        for each in current_fridge_content:
            if each.expirationdate < current_time:
                fridge_content_expiration['expired'].append(each)
            elif each.expirationdate > week_time:
                fridge_content_expiration['fresh'].append(each)
            else:
                fridge_content_expiration['expiring'].append(each)
        return fridge_content_expiration

    def changeCurrentFridge(self, fridge_id):
        self.session['current_fridge_id'] = fridge_id
        return self.session['current_fridge_id']

    def setPrimaryFridge(self, fridge_id):
        user = User.objects.filter(id=self.session['current_user_id']).get()
        if (fridge_id):
            user.primary_fridge = fridge_id
        else:
            user.primary_fridge = -1
        user.save()

    def getPrimaryFridge(self):
        user_primary_fridge = User.objects.filter(
            id=self.session['current_user_id']).get().primary_fridge
        return user_primary_fridge

    def renameCurrentFridge(self, new_name):
        current_fridge = Fridge.objects.filter(
            id=self.session['current_fridge_id']).get()
        current_fridge.name = new_name
        current_fridge.save()

    def delete_current_fridge(self):
        # Set fridge as End of Life
        current_fridge = Fridge.objects.filter(
            id=self.session['current_fridge_id']).get()
        current_fridge.eff_end_ts = datetime.now()
        current_fridge.save()
        # Remove Fridge from friend's accounts
        try:
            friends_list = current_fridge.friends
            for each in friends_list:
                friend = User.object.filter(id=each).get()
                friend.friendedfridges.remove(
                    self.session['current_fridge_id'])
                friend.save()
        except:
            pass
        # Reset Primary Fridge (if necessary)
        user = User.objects.filter(id=self.session['current_user_id']).get()
        if user.primary_fridge == self.session['current_fridge_id']:
            user.primary_fridge = -1
            user.save()
        # Remove Fridge from user's account
        user.ownedfridges.remove(self.session['current_fridge_id'])
        user.save()
        # Refind Current Fridge
        self.refindCurrentFridge()

    def deleteItem(self, item_id):
        fridge_content = FridgeContent.objects.get(id=item_id)
        fridge_content.eff_end_ts = datetime.now()
        fridge_content.save()

    def addItem(self, item_name):
        item = Item.objects.filter(name=item_name).get()
        item_dict = {item.id: item.age}
        for item_id in item_dict:
            fridge_content = FridgeContent(
                expirationdate=(
                    datetime.now()+timedelta(hours=item_dict[item_id])),
                size=1,
                creation_date=datetime.now(),
                modified_date=datetime.now(),
                eff_bgn_ts=datetime.now(),
                eff_end_ts=datetime(9999, 12, 31),
                addedby_id=self.session['current_user_id'],
                fridge_id=self.session['current_fridge_id'],
                item_id=item_id)
            fridge_content.save()

    def save_to_db(self, item_dict):
        for item_id in item_dict:
            fridge_content = FridgeContent(
                expirationdate=(
                    datetime.now()+timedelta(hours=item_dict[item_id])),
                size=1, creation_date=datetime.now(),
                modified_date=datetime.now(),
                eff_bgn_ts=datetime.now(),
                eff_end_ts=datetime(9999, 12, 31),
                addedby_id=self.session['current_user_id'],
                fridge_id=self.session['current_fridge_id'],
                item_id=item_id)
            fridge_content.save()

    def addFriend(self, friend_email):
        # Get friend's username
        friend_auth_user_username = AuthUser.objects.filter(
            email=friend_email).get().username
        # Save fridge to friend's account
        friend_auth_user_username = AuthUser.objects.filter(
            email=friend_email).get().username
        friend_user = User.objects.filter(
            username=friend_auth_user_username).get()
        if self.session['current_fridge_id'] not in friend_user.friendedfridges:
            friend_user.friendedfridges.append(
                self.session['current_fridge_id'])
            friend_user.save()
        # Save friend to current fridge
        friends_id = User.objects.filter(
            username=friend_auth_user_username).get().id
        current_fridge = Fridge.objects.filter(
            id=self.session['current_fridge_id']).get()
        if friends_id not in current_fridge.friends:
            current_fridge.friends.append(friends_id)
            current_fridge.save()

    def createFridge(self, fridge_name):
        user = User.objects.filter(id=self.session['current_user_id']).get()
        fridge = Fridge(name=fridge_name, owner=user,
                        creation_date=datetime.now(),
                        modified_date=datetime.now(),
                        eff_bgn_ts=datetime.now(),
                        eff_end_ts=datetime(9999, 12, 31))
        fridge.save()
        user.ownedfridges.append(fridge.id)
        user.save()
        self.session['current_fridge_id'] = fridge.id
        self.session['current_fridge_id'] = fridge.id

    def getAllItems(self):
        return Item.objects.all().order_by('name')

    def get_all_the_related_fridges(self):
        # Get all the fridges a user has access to
        user_fridges = []
        temp = User.objects.filter(id=self.session['current_user_id']).get()
        Owndfridge_id_list = temp.ownedfridges
        Friendfridge_id_list = temp.friendedfridges
        try:
            for i in Owndfridge_id_list:
                fridge_obj = Fridge.objects.filter(id=i).get()
                if(fridge_obj.eff_end_ts > datetime.now()):
                    user_fridges.append(fridge_obj)
        except:
            print('FRIDGE MANAGER: Error Getting Owned Fridges.')
        try:
            for i in Friendfridge_id_list:
                fridge_obj = Fridge.objects.filter(id=i).get()
                if(fridge_obj.eff_end_ts > datetime.now()):
                    user_fridges.append(fridge_obj)
        except:
            print('FRIDGE MANAGER: Error Getting friended fridges.')
        return user_fridges

    class fridge_Object:
        def __init__(self, name, creation_date, friends_name_list, id):
            self.name = name
            self.creation_date = creation_date
            self.friends_name_list = friends_name_list
            self.id = id

    def get_name_list_from_id_list(self, id_list):
        name_list = []
        for i in id_list:
            name_list.append(User.objects.filter(id=i).get().username)
        return name_list

    def make_verified_fridge_list(self, fridge_list):
        new_fridge_list = []
        for fridge in fridge_list:
            if fridge.eff_end_ts > datetime.now():
                new_fridge_list.append(fridge)
        return new_fridge_list

    def set_personal_notes(self, notes):
        # print(notes)
        # Get user
        user = User.objects.filter(id=self.session['current_user_id']).get()
        # print(user)
        # if there are no notes, do nothing, else update notes and save
        user.personalnotes = notes
        user.save()

    def getCurrentFridgeFriendsUsername(self):
        current_fridge_friend = User.objects.filter(
            friendedfridges=self.session['current_fridge_id'])
        friend_list_name = []
        for each in current_fridge_friend:
            friend_list_name.append(each.username)
        return friend_list_name

    def remove_friend(self, username):
        friend = User.objects.filter(username=username).get()
        friend.friendedfridges.remove(self.session['current_fridge_id'])
        if(friend.primary_fridge == self.session['current_fridge_id']):
            friend.primary_fridge = -1
        current_fridge = Fridge.objects.filter(
            id=self.session['current_fridge_id']).get()
        current_fridge.friends.remove(friend.id)
        friend.save()
        current_fridge.save()

    def is_owner(self):
        ownership = False

        # Get user id
        user_id = User.objects.filter(
            id=self.session['current_user_id']).get().id

        # Get Current Fridge
        curr_fridge = self.getCurrentFridge()

        # Get Owner of the Current Fridge
        owner_fridge = curr_fridge.owner.id

        if owner_fridge != user_id:
            ownership = False
        else:
            ownership = True
        return ownership


"""----------------------- OLD FRIDGE MANAGER --------------------------"""

# current_fridge_id = None
# current_user_id = None

# def initialCurrentFridge(request):
#     global current_fridge_id, current_user_id
#     current_fridge_id = None
#     current_user_id = User.objects.filter(
#         username=request.user.username).get().id
#     # Get user
#     user = User.objects.filter(id=current_user_id).get()
#     # Set current fridge as primary fridge (if available)
#     if user.primary_fridge != -1:
#         try:
#             current_fridge_id = Fridge.objects.filter(
#                 id=user.primary_fridge).get().id
#         except:
#             print("FRIDGE MANAGER: No primary fridge found.")
#     # Set current fridge as first fridge found with user's id
#     else:
#         try:
#             if user.ownedfridges[0]:
#                 current_fridge_id = user.ownedfridges[0]
#             elif user.friendedfridges[0]:
#                 current_fridge_id = user.friendedfridges[0]
#         except:
#             print("FRIDGE MANAGER: No Fridges found.")
#     return redirect('/fridge/')


# def refindCurrentFridge():
#     global current_fridge_id
#     current_fridge_id = None
#     # Get user
#     user = User.objects.filter(id=current_user_id).get()
#     # Set current fridge as primary fridge (if available)
#     if user.primary_fridge != -1:
#         try:
#             current_fridge_id = Fridge.objects.filter(
#                 id=user.primary_fridge).get().id
#         except:
#             print("FRIDGE MANAGER: No primary fridge found.")
#     # Set current fridge as first fridge found with user's id
#     else:
#         try:
#             if user.ownedfridges[0]:
#                 current_fridge_id = user.ownedfridges[0]
#             elif user.friendedfridges[0]:
#                 current_fridge_id = user.friendedfridges[0]
#         except:
#             print("FRIDGE MANAGER: No Fridges found.")
#     return redirect('/fridge/')


# def getCurrentFridge():
#     if(current_fridge_id):
#         current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
#         return current_fridge
#     else:
#         return None


# def getCurrentFridgeContent():
#     fridge_content = FridgeContent.objects.filter(
#         Q(fridge_id=current_fridge_id))
#     return fridge_content


# def getCurrentFridgeContentByExpiration():
#     fridge_content_expiration = FridgeContent.objects.filter(
#         Q(fridge_id=current_fridge_id)).order_by('expirationdate')
#     return fridge_content_expiration


# def changeCurrentFridge(fridge_id):
#     global current_fridge_id
#     current_fridge_id = fridge_id
#     return current_fridge_id


# def setPrimaryFridge(fridge_id):
#     user = User.objects.filter(id=current_user_id).get()
#     if (fridge_id):
#         user.primary_fridge = fridge_id
#     else:
#         user.primary_fridge = -1
#     user.save()


# def getPrimaryFridge():
#     global current_fridge_id
#     user_primary_fridge = User.objects.filter(
#         id=current_user_id).get().primary_fridge
#     return user_primary_fridge


# def renameCurrentFridge(new_name):
#     current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
#     current_fridge.name = new_name
#     current_fridge.save()


# def delete_current_fridge():
#     # Set fridge as End of Life
#     current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
#     current_fridge.eff_end_ts = datetime.now()
#     current_fridge.save()
#     # Remove Fridge from friend's accounts
#     try:
#         friends_list = current_fridge.friends
#         for each in friends_list:
#             friend = User.object.filter(id=each).get()
#             friend.friendedfridges.remove(current_fridge_id)
#             friend.save()
#     except:
#         pass
#     # Reset Primary Fridge (if necessary)
#     user = User.objects.filter(id=current_user_id).get()
#     if user.primary_fridge == current_fridge_id:
#         user.primary_fridge = -1
#         user.save()
#     # Remove Fridge from user's account
#     user.ownedfridges.remove(current_fridge_id)
#     user.save()
#     # Refind Current Fridge
#     refindCurrentFridge()


# def deleteItem(item_id):
#     fridge_content = FridgeContent.objects.get(id=item_id)
#     fridge_content.eff_end_ts = datetime.now()
#     fridge_content.save()


# def addItem(item_name):
#     item = Item.objects.filter(name=item_name).get()
#     item_dict = {item.id: item.age}
#     save_to_db(item_dict)


# def addFriend(friend_email):
#     # Get friend's username
#     friend_auth_user_username = AuthUser.objects.filter(
#         email=friend_email).get().username
#     # Save fridge to friend's account
#     friend_auth_user_username = AuthUser.objects.filter(
#         email=friend_email).get().username
#     friend_user = User.objects.filter(username=friend_auth_user_username).get()
#     if current_fridge_id not in friend_user.friendedfridges:
#         friend_user.friendedfridges.append(current_fridge_id)
#         friend_user.save()
#     # Save friend to current fridge
#     friends_id = User.objects.filter(
#         username=friend_auth_user_username).get().id
#     current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
#     if friends_id not in current_fridge.friends:
#         current_fridge.friends.append(friends_id)
#         current_fridge.save()


# def save_to_db(id_age_list):
#     try:
#         for item_id in id_age_list:
#             fridge_content = FridgeContent(expirationdate=(datetime.now()+timedelta(hours=id_age_list[item_id])), size=1, creation_date=datetime.now(
#             ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31), addedby_id=current_user_id, fridge_id=current_fridge_id, item_id=item_id)
#             fridge_content.save()
#     except:
#         print("FRIDGE MANAGER: Error saving item to db")


# def createFridge(fridge_name):
#     global current_fridge_id
#     user = User.objects.filter(id=current_user_id).get()
#     fridge = Fridge(name=fridge_name, owner=user, creation_date=datetime.now(
#     ), modified_date=datetime.now(), eff_bgn_ts=datetime.now(), eff_end_ts=datetime(9999, 12, 31))
#     fridge.save()
#     user.ownedfridges.append(fridge.id)
#     user.save()
#     current_fridge_id = fridge.id


# def getAllItems():
#     return Item.objects.all()


# def get_all_the_related_fridges():
#     # Get all the fridges a user has access to
#     owned = {}
#     friends = {}
#     temp = User.objects.filter(id=current_user_id).get()
#     Owndfridge_id = temp.ownedfridges
#     Friendfridge_id = temp.friendedfridges

#     try:
#         for i in Owndfridge_id:
#             fridge_obj = Fridge.objects.filter(id=i).get()
#             if(fridge_obj.eff_end_ts > datetime.now()):
#                 owned[fridge_obj.name] = fridge_obj.id
#     except:
#         print('FRIDGE MANAGER: Error in 130')
#     try:
#         for i in Friendfridge_id:
#             fridge_obj = Fridge.objects.filter(id=i).get()
#             if(fridge_obj.eff_end_ts > datetime.now()):
#                 friends[fridge_obj.name] = fridge_obj.id
#     except:
#         print('FRIDGE MANAGER: Error in 136')

#     # print("owned", owned)
#     # print(friends)
#     user_fridges = owned.copy()
#     user_fridges.update(friends)
#     # print(user_fridges)
#     return user_fridges


# class fridge_Object:
#     def __init__(self, name, creation_date, friends_name_list, id):
#         self.name = name
#         self.creation_date = creation_date
#         self.friends_name_list = friends_name_list
#         self.id = id


# def get_name_list_from_id_list(id_list):
#     name_list = []
#     for i in id_list:
#         name_list.append(User.objects.filter(id=i).get().username)
#     return name_list


# def make_verified_fridge_list(fridge_list):
#     new_fridge_list = []
#     for fridge in fridge_list:
#         if fridge.eff_end_ts > datetime.now():
#             new_fridge_list.append(fridge)
#     return new_fridge_list


# def set_personal_notes(notes):
#     # print(notes)
#     # Get user
#     user = User.objects.filter(id=current_user_id).get()
#     # print(user)
#     # if there are no notes, do nothing, else update notes and save
#     user.personalnotes = notes
#     user.save()


# def getCurrentFridgeFriendsUsername():
#     current_fridge_friend = User.objects.filter(
#         friendedfridges=current_fridge_id)
#     friend_list_name = []
#     for each in current_fridge_friend:
#         friend_list_name.append(each.username)
#     return friend_list_name


# def remove_friend(username):
#     friend = User.objects.filter(username=username).get()
#     friend.friendedfridges.remove(current_fridge_id)
#     if(friend.primary_fridge == current_fridge_id):
#         friend.primary_fridge = -1
#     current_fridge = Fridge.objects.filter(id=current_fridge_id).get()
#     current_fridge.friends.remove(friend.id)
#     friend.save()
#     current_fridge.save()
