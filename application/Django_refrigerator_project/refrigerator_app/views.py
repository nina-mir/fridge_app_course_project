from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required  #for using @login_required decorator on top of a function
import boto3
import io
from io import BytesIO
import sys
import math
from .models import Items
from .models import Users
from .models import AuthUser
from .models import Fridge
from django.db.models import Q
# Create your views here.


def home(request):
    inventory_items = Items.objects.all()
    return render(request, 'refrigerator_project/home.html', context={'inventory_items': inventory_items})

@login_required
def delete_item(request):
    inventory_items = Items.objects.all()
    return render(request, 'refrigerator_project/home.html', context={'inventory_items': inventory_items})

@login_required
def groceries(request):
    fridge_data = Fridge
    inventory_items = Items.objects.all()
    if(request.method == 'POST'):
        srch = request.POST['itemname']
        if srch:
            match = Items.objects.filter(Q(itemname__icontains=srch) | Q(
                itemid__icontains=srch) | Q(calories__icontains=srch))
            if match:
                return render(request, 'refrigerator_project/groceries.html', {'sr': match})
    return render(request,'refrigerator_project/groceries.html', context={'inventory_items':inventory_items})

@login_required
def profile(request):
    user_info = Users.objects.all()
    return render(request,'refrigerator_project/profile.html', context={'user_info' : user_info })

@login_required
def fridge(request):
    inventory_items = Items.objects.all()
    my_dict = {'insert_me':"Hello I am from views.py"}
    return render(request,'refrigerator_project/fridge.html', context={'inventory_items':inventory_items})

@login_required
def recipe(request):
    my_dict = {'insert_me':"Hello I am from views.py"}
    return render(request,'refrigerator_project/recipe.html', context=my_dict)

@login_required
def simple_upload(request):
    context = {}
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print(filename)
        text = detect_text(filename)
        context['text'] = text
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
    
    """matching against the database function"""
    def is_it_in(a):
        if a.casefold() in (name.casefold() for name in db):
            return True;

    
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
            if is_it_in(i):
                print(i)
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
    return 'nina' #' '.join(result)

@login_required
def search(request):
    if(request.method == 'POST'):
        srch = request.POST['itemname']
        if srch:
            match = Items.objects.filter(Q(itemname__icontains = srch) | Q(itemid__icontains = srch) | Q(calories__icontains = srch))
            if match:
                return render(request,'refrigerator_project/search.html',{'sr':match})
    return render(request,'refrigerator_project/search.html')
