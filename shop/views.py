from django.shortcuts import render,get_object_or_404
from .models import Product
from .services import summarizer,vector_finder
# Create your views here.
from django.http import JsonResponse

def home(request):
    query = request.GET.get("q", "").strip()
    products = vector_finder.search_by_vector(query) if query else Product.objects.all()

    if request.GET.get("partial") == "true":
        return render(request, "product/product_list.html", {"products": products})
    else:
        return render(request, "index.html", {"products": products})

def summarize_review(req,product_id):
    
    if req.method == "GET":
        product = Product.objects.get(id=product_id)
        
        reviews = product.reviews.all().values_list('content',flat=True)
        
        if not reviews:
            return JsonResponse({'summary':'리뷰가 없습니다'})
        summary = summarizer.summarize_reviews(product_id,list(reviews))
        
        return JsonResponse({'summary':summary})
    

    