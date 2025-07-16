import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopbot.settings')  # 'Shop'은 settings.py가 있는 폴더 이름
django.setup()


import csv
from datetime import datetime
from shop.models import Product, Review

def parse_price(price_str):
    return int(price_str.replace("₩", "").replace(",", "").strip())

data_dir = r'C:\Users\main\Documents\Shop\data'
data_li = [os.path.join(data_dir, fname) 
           for fname in os.listdir(data_dir) if fname.endswith('.csv')]
review_dir = r'c:\Users\main\Documents\Shop\preprocessor'
review_li = [os.path.join(review_dir,fname) for fname in os.listdir(review_dir) if fname.endswith('.csv')]

for info_path, review_path in zip(data_li, review_li):
    # 1. Product 저장
    with open(info_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product,created = Product.objects.get_or_create(
                name=row["게임제목"],
                defaults={
                     "price": 0 if row["가격"] == "가격 정보 없음" else parse_price(row["가격"]),
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
            if created:
                print(f"✅ 리뷰 저장됨: {review.content[:30]}...")
            else:
                print(f"⚠️ 이미 존재하는 리뷰: {review.content[:30]}...")

        print(f"✅ Review 저장 완료: {product.name}")
