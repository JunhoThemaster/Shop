# summarizer.py
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from shop.models import Product
import os
load_dotenv()
def summarize_reviews(product_id : int ,contents: list[str], chunk_size=1500, chunk_overlap=100) -> str:
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
        ("system", "다음은 사용자의 리뷰입니다. 내용을 한국어로 간결하지만 게임의 핵심 후기를 가격대와,사양,그래픽 등을 포함하여 짧은 3문장으로 요약하세요."),
        ("human", "{input}")
    ])
    api_key = os.getenv("OPEN_AI_API_KEY")
    # 3. 요약 실행
    llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0,openai_api_key=api_key)

    summaries = []
    for chunk in chunks:
        chain = prompt | llm
        summary = chain.invoke({"input": chunk})
        summaries.append(summary.content.strip())
        
    final_input = "\n\n".join(summaries)
    final_summary = (prompt | llm).invoke({'input' : final_input})
    product = Product.objects.get(id=product_id)
    # 최종 요약본 product 테이블의 summary 필드에 저장
    if not product.summary:
        product.summary = final_summary
        product.save()
        
    # 최종 요약본 전달 
    return final_summary.content.strip()
