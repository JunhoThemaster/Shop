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
from transformers import pipeline

# 감성 분석 모델 (사전학습된 모델 사용)
sentiment_pipeline = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

def classify_review(text: str) -> str:
    label = sentiment_pipeline(text[:512])[0]['label']
    if '5' in label or '4' in label:
        return '긍정'
    elif '1' in label or '2' in label:
        return '부정'
    else:
        return '애매'
    





    