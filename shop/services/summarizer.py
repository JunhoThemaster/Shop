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


def summarize_reviews(product_id : int ,contents: list[str], chunk_size=1500, chunk_overlap=100) -> str:
    product = Product.objects.get(id=product_id)
    
    if product.summary:
        summary = product.summary
        match = extract_content(summary)
        
        if match != None:
            return match
        
    else:
        """
        contents: 리뷰 텍스트 리스트
        return: LangChain 기반 요약 결과
        """
        text = "\n\n".join(contents)

        # 1. Chunk 나누기
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        chunks = splitter.split_text(text)

        # 2. LangChain 요약 프롬프트 구성
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
                """
                다음 정보를 필드별로 요약하세요. 각 필드는 반드시 한 문장으로 작성합니다.

                    [가격 요약]: ...
                    [사양 요약]: ...
                    [그래픽 요약]: ...
                    [사용자 반응 요약]: ...
                    [총평 (갓겜/똥겜 판단 포함)]: 
                """
                )
        ,
            ("human", "{input}")
        ])
        api_key = os.getenv("OPEN_AI_API_KEY")
        # 3. 요약 실행
        llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0,openai_api_key=api_key)

        summaries = []
        for chunk in chunks:
            chain = prompt | llm
            summary = chain.invoke({"input":f"게임 설명:{product.description}\n 리뷰 : "+chunk})
            summaries.append(summary.content.strip())
            
        final_input = "\n\n".join(summaries)
        final_summary = (prompt | llm).invoke({'input' : final_input})
        product = Product.objects.get(id=product_id)
        # 최종 요약본 product 테이블의 summary 필드에 저장

        product.summary = final_summary.content.strip()
        product.save()
        
        flattened_txt = flatten_summary(final_summary.content.strip())
        print(f"줄글로 요약된 서머리:{flattened_txt}")
        save_to_chroma(product,flattened_txt)
            
 
        return final_summary.content.strip()



def save_to_chroma(product:object ,txt):
    api_key = os.getenv("OPEN_AI_API_KEY")
    if txt and product:
        embedding_model = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=api_key)

        docs = [txt]
        metadatas = [{'product_id':str(product.id),
                      'product_name':str(product.name),
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
    맞게 비속어와, 전문용어를 섞어도 무방함.
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