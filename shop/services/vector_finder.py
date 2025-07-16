

from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.config import Settings
from chromadb import PersistentClient
from shop.models import Product
import os 

api_key = os.getenv("OPEN_AI_API_KEY")
    
def search_by_vector(query,k=10):
    
    if not query:
        return []
    
    embedding_model = OpenAIEmbeddings(model ='text-embedding-3-small',openai_api_key=api_key)
    
    client = PersistentClient(path="chroma_db")  # 이전 persist_directory 역할

# 📌 기존 저장된 컬렉션을 연결하거나 새로 생성
    collection_name = "product_review_summaries"

# ✅ LangChain과 연결
    db = Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embedding_model
    )
    
    results = db.similarity_search_with_score(query, k=k)

    ranked_ids = []  # (id, score) 튜플
    for doc, score in results:
        product_id = doc.metadata.get("product_id")
        if product_id:
            ranked_ids.append((int(product_id), score))

    if not ranked_ids:
        return []

    # 유사도 점수 높은 순으로 정렬
    ranked_ids.sort(key=lambda x: x[1], reverse=True)
    id_only = [pid for pid, _ in ranked_ids]

    # product_id 기준으로 상품 가져오기
    products = list(Product.objects.filter(id__in=id_only))

    # 쿼셋은 순서 보장 X -> 정렬 필요
    ordered_products = sorted(products, key=lambda p: id_only.index(p.id))

    return ordered_products
    