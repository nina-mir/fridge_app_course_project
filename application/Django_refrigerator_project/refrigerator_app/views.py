from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
# for using @login_required decorator on top of a function
from django.contrib.auth.decorators import login_required
import boto3
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
# Create your views here.


def home(request):
    # inventory_items = Item.objects.all()
    # current_user = request.user
    # print(current_user.username)
    # print('----------------')
    # temp = User.objects.filter(username = current_user.username)
    # print(temp[0].ownedfridges)
    return render(request, 'refrigerator_project/home.html')


@login_required
def delete_item(request):
    inventory_items = Item.objects.all()
    return render(request, 'refrigerator_project/home.html', context={'inventory_items': inventory_items})


@login_required
def groceries(request):
    inventory_items = Item.objects.all()
    print(inventory_items)

    # Get Manual & Tracked Items List & Fridge Inventory
    try:
        user_id = User.objects.filter(username=request.user.username).get().id
        fridge = Fridge.objects.filter(owner_id = user_id).get()
        tracked_items = fridge.auto_gen_grocery_list.split(',')
        manual_items = fridge.manually_added_list.split(',')
        temp = User.objects.filter(username = current_user.username).get()
        Owndfridge_id = int(temp.ownedfridges.split(',')[0])
        inventory_items = FridgeContent.objects.filter(Q(fridge_id = Owndfridge_id))
    except:
        pass

    # Check for Tracked items missing from fridge
    missing_items = []
    print(tracked_items)
    for tItems in tracked_items:
        inFridge = False
        for iItems in inventory_items:
            if (tItems == iItems.name):
                inFridge = True
        if (inFridge == False):
            missing_items.append(tItems)
    print(missing_items)

    # Search for item functionality
    if(request.method == 'POST'):
        srch = request.POST['itemname']
        if srch:
            match = Item.objects.filter(Q(name__icontains=srch) | Q(
                id__icontains=srch) | Q(calories__icontains=srch))
            if match:
                return render(request, 'refrigerator_project/groceries.html', {'sr': match})


    return render(request, 'refrigerator_project/groceries.html', {'inventory_items': inventory_items, 'missing_items': missing_items,  'manual_items': manual_items})


@login_required
def profile(request):
    user_info = User.objects.all()
    return render(request, 'refrigerator_project/profile.html', context={'user_info': user_info})


@login_required
def fridge(request):
    current_user = request.user

    # Add Item to Fridge
    if(request.method == 'POST'):
        print("ADDED AN APPLE")
        # get id if the specified item
        item_id = Item.objects.filter(name="apple").get().id
        # get id of user
        user_id = User.objects.filter(username=current_user.username).get().id
        # get id of selected fridge
        temp = User.objects.filter(username = current_user.username).get()
        fridge_id = int(temp.ownedfridges.split(',')[0])
        # make new fridge content
        fridge_content = FridgeContent(expirationdate='2019-12-10', size=1, creation_date=datetime.datetime.now(), modified_date=datetime.datetime.now(), eff_bgn_ts=datetime.datetime.now(), eff_end_ts=datetime.datetime.max, addedby_id=user_id, fridge_id=fridge_id, item_id=item_id)
        fridge_content.save()

    # Delete Item from Fridge


    try:
        #Getting primary fridge of logged in user
        temp = User.objects.filter(username = current_user.username).get()
        Owndfridge_id = int(temp.ownedfridges.split(',')[0])
        inventory_items = FridgeContent.objects.filter(Q(fridge_id = Owndfridge_id))
        fridge_name = Fridge.objects.filter(id = Owndfridge_id).get().name
    except:
        print('Error')
        return render(request,'refrigerator_project/fridge.html')
    return render(request,'refrigerator_project/fridge.html', {'inventory_items':inventory_items, 'fridge_name':fridge_name})

@login_required
def simple_upload(request):
    context = {}
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print(filename)
        text = detect_text(filename)
        context={'text':text}
    return render(request, 'refrigerator_project/receipt_upload.html', context)

# AWS TextTract
def DisplayBlockInformation(block):
    if 'Text' in block:
        return block['Text']
    return ''

# AWS TextTract
def process_text_analysis(filename):

    bw_img = open(filename,'rb')

    client = boto3.client('textract')

    response = client.analyze_document(Document={'Bytes': bw_img.read()},
        FeatureTypes=["TABLES", "FORMS"])

    blocks=response['Blocks']
    result = []
    print('Calling From Amazon Textract')
    for block in blocks:
        text = DisplayBlockInformation(block)
        result.append(text)

    return ' '.join(result)

# Google Vision
def detect_text(filename):
    db =['apple', 'pineapple','strawberry', 'bread', 'juice', 'yogurt']
    post_processing_results = []

    """matching against the database function"""
    # def is_it_in(a):
    #     if a.casefold() in (name.casefold() for name in db):
    #         return True;


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
    print(type(nina))
    print(type(nina.description))
    output = nina.description.splitlines( )
    for x in output:
        splitted = x.split()
        for i in splitted:
            temp = Item.objects.filter(Q(name__icontains = i))
            for each in temp:
                if each.name.lower() == i.lower():
                    print('Found one')
                    post_processing_results.append(each.name)
                    break
    # result = []
    # print('Calling From Google Vision')
    # for text in texts:
    #     text = '\n"{}"'.format(text.description)
    #     result.append(text)
    #     print('\n"{}"'.format(text.description))

        # vertices = (['({},{})'.format(vertex.x, vertex.y)
        #             for vertex in text.bounding_poly.vertices])

        # print('bounds: {}'.format(','.join(vertices)))
    #return 'nina' #' '.join(result)
    return post_processing_results


@login_required
def search(request):
    if(request.method == 'POST'):
        srch = request.POST['itemname']
        if srch:
            match = Item.objects.filter(Q(name__icontains = srch) | Q(id__icontains = srch) | Q(calories__icontains = srch))
            if match:
                return render(request,'refrigerator_project/search.html',{'sr':match})
    return render(request,'refrigerator_project/search.html')
