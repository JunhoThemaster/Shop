# summarizer.py
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from chromadb.config import Settings
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from shop.models import Product
import re
import os
load_dotenv()


def summarize_reviews(product_id: int, contents: list[str], chunk_size=1500, chunk_overlap=100) -> str:
    product = Product.objects.get(id=product_id)
    
    if product.summary:
        return product.summary

    # 1. 리뷰 내용 전처리 (너무 짧은 건 제외)
    contents = contents

    # 2. LangChain 준비
    api_key = os.getenv("OPEN_AI_API_KEY")
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0, openai_api_key=api_key)

    # 3. 전체 텍스트 결합 및 chunk 나누기
    text = "\n\n".join(contents)
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_text(text)

    # 4. chunk별 요약 (간단한 핵심 요약)
    chunk_prompt = ChatPromptTemplate.from_messages([
        ("system", "아래는 게임에 대한 유저 리뷰다. 이 리뷰를 통해 알수있는 게임의 주요 특징과 불만/칭찬을 짧게 요약해줘."),
        ("human", "{input}")
    ])
    summaries = []
    for chunk in chunks:
        summary = (chunk_prompt | llm).invoke({"input": chunk})
        summaries.append(summary.content.strip())

    # 5. 최종 요약 프롬프트 (구조화 + 욕설 스타일)
    final_prompt = ChatPromptTemplate.from_messages([
        ("system",
        """
        다음은 게임 리뷰 요약들이다. 아래 5개 항목으로 리뷰를 요약하되, 각 항목은 3문장 이내로 작성하고
        거침없고 자극적인 표현(비속어 포함 가능)을 사용하여 게임의 특성과 반응을 생생하게 전달해줘.
        결과는 아래 양식대로:

        [가격 요약]:  
        [사양 요약]:  
        [그래픽 요약]:  
        [사용자 반응 요약]:  
        [총평 (갓겜/똥겜 판단 포함)]:
        """),
        ("human", "{input}")
    ])

    final_input = f"게임 설명: {product.description}\n장르: {product.genre}\n\n리뷰 요약들:\n" + "\n\n".join(summaries)
    final_summary = (final_prompt | llm).invoke({"input": final_input})

    # 6. 저장
    result = final_summary.content.strip()
    product.summary = result
    product.save()

    flattened_txt = flatten_summary(result)
    print(f"줄글 요약: {flattened_txt}")
    save_to_chroma(product, flattened_txt)

    return result



def save_to_chroma(product:object ,txt):
    api_key = os.getenv("OPEN_AI_API_KEY")
    if txt and product:
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=api_key)

        docs = [txt]
        metadatas = [{'product_id':str(product.id),
                      'product_name':str(product.name),
                      'genre': str(product.genre),
                      'price' :str(product.price),
                      'release_date':product.created_at.strftime("%Y년 %m월 %d일"),
                      'developer' : str(product.developer),
                      'pc_min_req' : str(product.pc_min_req)}]
        db = Chroma(
            collection_name="product_review_summaries",
            embedding_function=embedding_model,
            persist_directory="chroma_db"  # 저장 경로
        )
        db.add_texts(
            texts=docs,
            metadatas=metadatas
        )
        db.persist()
        print("저장된 문서 수:", db._collection.count())
        print(f"저장 완료: product_id={product.id}")
    else: 
        return
    
    
def flatten_summary(summary_text: str) -> str:
    """
    [가격 요약] 같은 블록 구조를 자연어 형태로 풀어서 줄글로 반환 유저들의 비속어와 자연스러운 검색 문장에
    맞게 비속어와, 전문용어를 섞어도 무방 그리고 게임의 특성이 잘 나타나게 요약부탁함.
    """
    lines = summary_text.split("\n")
    output = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("[") and "]" in line:
            # ex) [가격 요약]: → "가격 측면에서는 "
            label = line[1:line.index("]")]
            content = line[line.index("]")+1:].strip(": ").strip()
            prefix = {
                "가격 요약": "가격 측면에서는",
                "사양 요약": "사양 측면에서는",
                "그래픽 요약": "그래픽적으로는",
                "사용자 반응 요약": "사용자 평가는",
                "총평 (갓겜/똥겜 판단 포함)": "전체적으로는"
            }.get(label, "")
            output.append(f"{prefix} {content}")
        else:
            output.append(line)

    return " ".join(output)

    
    
def extract_content(summary_string):
    match = re.search(r"content='(.*?)'", summary_string)
    if match:
        return match.group(1)
    return None