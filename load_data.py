import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shopbot.settings')  # 'Shop'은 settings.py가 있는 폴더 이름
django.setup()


import csv
from datetime import datetime
from shop.models import Product, Review

def parse_price(price_str):
    return int(price_str.replace("₩", "").replace(",", "").strip())

data_li = ['data/garry_info.csv', 'data/portal_info.csv']
review_li = ['preprocessor/fixed_garry_review.csv', 'preprocessor/fixed_portal_reviews.csv']

for info_path, review_path in zip(data_li, review_li):
    # 1. Product 저장
    with open(info_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            product = Product.objects.create(
                name=row["게임제목"],
                price=parse_price(row["가격"]),
                pc_min_req=row["PC_최소사양"],
                description=row["상세설명"]
            )
            print(f"✅ Product 저장 완료: {product.name}")

    # 2. 해당 Product 불러오기
    product = Product.objects.get(name=row["게임제목"])  # 위 row 사용

    # 3. Review 저장
    with open(review_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 날짜 파싱
            created_at = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S")

            # 리뷰 저장
            Review.objects.create(
                product=product,
                recommend=row["recommend"].lower() == "true",
                content=row["content"],
                created_at=created_at
            )
        print(f"✅ Review 저장 완료: {product.name}")
