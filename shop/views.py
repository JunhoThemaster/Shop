from django.shortcuts import render
from .models import Product
# Create your views here.


def main_index(req):
    
    products = Product.objects.all()
    return render(req,"product_list.html",{'products':products})