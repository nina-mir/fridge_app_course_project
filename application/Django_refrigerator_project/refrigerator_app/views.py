from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import boto3
import io
from io import BytesIO
import sys
import math
# from PIL import Image, ImageDraw, ImageFont
# Create your views here.

def home(request):
    my_dict = {'insert_me':"Hello I am from views.py"}
    return render(request,'refrigerator_project/home.html', context=my_dict)


def simple_upload(request):
    context = {}
    if request.method == 'POST' and request.FILES['image']:
        myfile = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print(filename)
        text = process_text_analysis(filename)
        context['text'] = text
    return render(request, 'refrigerator_project/index.html', context)

def DisplayBlockInformation(block):
    if 'Text' in block:
        return block['Text']
    return ''
    
def process_text_analysis(filename):

    bw_img = open(filename,'rb')

    client = boto3.client('textract')

    response = client.analyze_document(Document={'Bytes': bw_img.read()},
        FeatureTypes=["TABLES", "FORMS"])

    blocks=response['Blocks']
    result = []
    for block in blocks:
        text = DisplayBlockInformation(block)
        result.append(text)
    
    return ' '.join(result) 
