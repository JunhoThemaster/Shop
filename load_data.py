import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopbot.settings')  # 'Shop'은 settings.py가 있는 폴더 이름
django.setup()


import csv
from datetime import datetime
from shop.models import Product, Review
import re, emoji
# from konlpy.tag import Okt
from django.db import transaction
from django.conf import settings

# STOPWORDS = {"이", "그", "저", "것", "수", "좀"}
# okt = Okt()


# def preprocess(text: str) -> list[str]:
#     # ① 기본 정규화
#     text = emoji.replace_emoji(text, "")
#     text = re.sub(r'https?://\S+', ' ', text)              # URL 제거
#     text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)       # 특수문자
#     text = text.strip()

#     # ② Okt 형태소
#     tokens = okt.morphs(text)
#     tokens = [t for t in tokens if len(t) > 1 and t not in STOPWORDS]
#     return tokens


def update_product_tokens(product_id: int):
    
    qs = Review.objects.filter(product_id= product_id)
    
    for r in qs:
        r.tokens = ",".join(preprocess([r.content]))
        
    with transaction.atomic():
        Review.objects.bulk_update(qs,['tokens'])



def parse_price(price_str):
    return int(price_str.replace("₩", "").replace(",", "").strip())

DATA_DIR = os.path.join(settings.BASE_DIR, 'data')
data_li = [os.path.join(DATA_DIR, fname) 
           for fname in os.listdir(DATA_DIR) if fname.endswith('.csv')]

review_dir = os.path.join(settings.BASE_DIR, 'preprocessor')
review_li = [os.path.join(review_dir,fname) for fname in os.listdir(review_dir) if fname.endswith('.csv')]

link = 'https://store.steampowered.com/app/{appid}'
for info_path, review_path in zip(data_li, review_li):
    # 1. Product 저장
    with open(info_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product,created = Product.objects.get_or_create(
                name=row["게임제목"],
                defaults={
                     "price": 0 if row["가격"] == "가격 정보 없음" else parse_price(row["가격"]),
                     "link" : f"https://store.steampowered.com/app/{row["appid"]}",
                     "genre" : row['장르'],
                    "developer": row["유통사"],
                    "pc_min_req": row["PC_최소사양"],
                    "description": row["상세설명"],
                    "created_at": row["출시일"],
                }
            )
            if created:
                
                print(f"✅ 새 Product 저장 완료: {product.name}")
            else:
                print(f"⚠️ 이미 존재하는 Product: {product.name}")

    # 2. 해당 Product 불러오기
    product = Product.objects.get(name=row["게임제목"])  # 위 row 사용

    # 3. Review 저장
    with open(review_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 날짜 파싱
            created_at = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S")

            # 리뷰 저장
            review, created = Review.objects.get_or_create(
                product=product,  # 또는 product_id=product.id
                content=row["content"].strip(),
                created_at=created_at,
                defaults={
                    "recommend": row["recommend"].lower() == "true"
                }
            )
            if created: # 프로덕트 저장 , 이후 리뷰 까지 저장후 update review token 호출 하면 token화된 결과까지 다 저장
                
                print(f"✅ 리뷰 저장됨: {review.content[:30]}...")
            else:
                print(f"⚠️ 이미 존재하는 리뷰: {review.content[:30]}...")

        print(f"✅ Review 저장 완료: {product.name}")
