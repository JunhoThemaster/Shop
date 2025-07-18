# 일단 리뷰수가 적은게임이 있고 많은 게임이 있다, 이마저도 전처리 이후에 줄어들 가능성이 존재하기에
# 무거운 모델을 사용하기보다는 tf-idf 

from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import tempfile
from django.core.files.base import ContentFile
from shop.models import Product,Review,ReviewAnalysis
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="alsgyu/sentiment-analysis-fine-tuned-model",
    tokenizer="beomi/KcBERT-base"
)
def classify_review(text: str) -> str:
    result = sentiment_pipeline(text[:512])[0]
    label = result['label'].lower()
    
    if '2' in label:
        return '긍정'
    elif '1' in label:
        return '애매'
    elif '0' in label:
        return '부정'
    

def analyze_reviews_for_product(product_id: int):
    product = Product.objects.get(id=product_id)
    reviews = Review.objects.filter(product=product).values_list("content", flat=True)
    
    # 감성 분류
    sentiments = [classify_review(text) for text in reviews]

    if not sentiments:
        return None

    # 감성 비율 계산
    counts = Counter(sentiments)
    total = len(sentiments)
    pos = counts.get("긍정", 0)
    neg = counts.get("부정", 0)
    neu = counts.get("애매", 0)

    # 평균 길이 계산
    avg_len = np.mean([len(t) for t in reviews if isinstance(t, str)])

    # 결과 저장
    analysis, _ = ReviewAnalysis.objects.get_or_create(product=product)
    
    analysis.total_reviews = total
    analysis.positive_count = pos
    analysis.negative_count = neg
    analysis.neutral_count = neu
    analysis.average_length = avg_len
    analysis.save()

    print(f"분석 완료: {product.name} / 총 리뷰: {total} / 긍정: {pos}, 부정: {neg}, 애매: {neu}")
    return analysis


from django.db.models import Count
from django.db.models.functions import TruncDate

def review_trend(product_id):
    
        queryset = (
        Review.objects
        .annotate(date=TruncDate("created_at"))  # 날짜만 추출
        .values("product_id", "date")            # product_id + 날짜 기준 그룹화
        .annotate(count=Count("id"))             # 해당 조합의 리뷰 수
        .order_by("product_id", "date")
        )
        result = {}
        
        for row in queryset:
            pid = row["product_id"]
            date = row["date"].strftime("%Y-%m-%d")
            count = row["count"]

            if pid not in result:
                result[pid] = []
            result[pid].append({
                "date": date,
                "count": count
            })
            
        return result
