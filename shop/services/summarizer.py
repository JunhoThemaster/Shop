# summarizer.py
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
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
            ("system", "다음은  게임의 설명과 사용자의 리뷰입니다. 내용을 한국어로 간결하지만 게임의 핵심 후기를 가격대와,사양,그래픽 등등, 그리고 유저들이 자주쓰는 비속어 똥겜, 갓겜, 등등의 비속어를 포함하여 짧은 3문장으로 요약부탁드림 만약 전체적으로 평가가 좋다면 갓겜 평가가 안좋다면 똥겜 이유를 같이 붙여서 요약 부탁함."),
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

        product.summary = final_summary
        product.save()
        
        save_to_chroma(product,final_summary.content.strip())
            
    # 최종 요약본 전달 
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
        print(f"저장 완료: product_id={product.id}")
    else: 
        return
    
    
    
    
    
def extract_content(summary_string):
    match = re.search(r"content='(.*?)'", summary_string)
    if match:
        return match.group(1)
    return None