from django.shortcuts import render,get_object_or_404
# from .models import Product
# from .services import summarizer,vector_finder
# Create your views here.
from django.http import JsonResponse
from shop.admservice import review_analyzer
from shop.models import Product,ReviewAnalysis

from django.forms.models import model_to_dict

def admin_home(request):
    
    products = Product.objects.all()

    return render(request, "admin/admin_home.html",{"products": products})

def init_sentiment_ratio(request, product_id):
    
    try:
        product = Product.objects.get(id=product_id)
        try:
            # 객체 불러와보고 있으면 그냥 있는 결과 반환
            analysis= ReviewAnalysis.objects.get(product=product)
            
            return JsonResponse({"msg" : "이미 분석된 결과입니다.",
                                 "sentiment_ratio": analysis.sentiment_ratio()})
         # 만약 없다면 분석 재시도 , 생성 
        except ReviewAnalysis.DoesNotExist:
            
            sentiment_ratio = review_analyzer.analyze_reviews_for_product(product_id)
        
            if sentiment_ratio:
                
                sentiment_ratio = sentiment_ratio.sentiment_ratio()

                return JsonResponse({"msg" : "분석정보가 없습니다. 분석 하겠습니다",
                                     "sentiment_ratio" : sentiment_ratio})    
    # 상품 자체가 없다면
    except Product.DoesNotExist:
        return JsonResponse({"error": "해당 product_id가 존재하지 않습니다."})



def get_sentiment_ratio(request, product_id):
    try:
        analysis = ReviewAnalysis.objects.get(product_id=product_id)
        
        return JsonResponse({
            "msg" : "불러오기 완료",
            "sentiment_ratio" : analysis.sentiment_ratio(),
        })
    except ReviewAnalysis.DoesNotExist:
        print("해당 제품의 리뷰 분석이 존재하지 않습니다.")
        return JsonResponse({
            "msg" : "분석 결과 저장본 없음"
        })
        
        
def get_review_trend(request,product_id):

    trend_data = review_analyzer.analyze_review_trend(product_id=product_id)
    
    if trend_data:
        return JsonResponse({"trend" : trend_data})    
    else:
        return JsonResponse({"msg" : "조회할 리뷰가 없습니다"})