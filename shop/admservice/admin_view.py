from django.shortcuts import render,get_object_or_404
# from .models import Product
# from .services import summarizer,vector_finder
# Create your views here.
from django.http import JsonResponse
from shop.admservice import review_analyzer

def admin_home(request):
    
    return render(request, "admin/admin_home.html")
    