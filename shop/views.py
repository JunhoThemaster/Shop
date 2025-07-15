from django.shortcuts import render,get_object_or_404
from .models import Product
from .services import summarizer
# Create your views here.
from django.http import JsonResponse

def main_index(req):
    
    products = Product.objects.all()
    return render(req,"product_list.html",{'products':products})


def summarize_review(req,product_id):
    
    if req.method == "GET":
        product = Product.objects.get(id=product_id)
        
        reviews = product.reviews.all().values_list('content',flat=True)
        
        if not reviews:
            return JsonResponse({'summary':'리뷰가 없습니다'})
        summary = summarizer.summarize_reviews(list(product_id,reviews))
        
        return JsonResponse({'summary':summary})
    
    
    
    