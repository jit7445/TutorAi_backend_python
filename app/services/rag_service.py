import os
import json
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from app.core.config import settings
from firecrawl import Firecrawl
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_rag(topic: str = None, pdf_path: str = None) -> dict:
    documents = []
    
    if pdf_path:
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
    elif topic:
        client = Firecrawl(api_key=os.getenv("firecrawl_api_key", "fc-9da27046b0a44ce5a02e19e1fcb4fbb5"))
        try:
            search_response = client.search(query=topic)
            # search_response usually has 'data' in v1 or 'web' in v2
            if hasattr(search_response, 'data'):
                urls = [res.get("url", res.url) if hasattr(res, 'url') else res.get("url") for res in search_response.data[:2]]
            elif hasattr(search_response, 'web'):
                urls = [res.url for res in search_response.web[:2] if res.url]
            else:
                urls = []
        except Exception as e:
            print(f"Firecrawl search failed: {e}")
            urls = []
        
        if not urls:
            urls = [f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"]
            
        for url in urls:
            try:
                doc = client.scrape(
                    url,
                    formats=["markdown"],
                    only_main_content=True,
                    remove_base64_images=True,
                )
                
                markdown_content = doc.markdown if hasattr(doc, 'markdown') else doc.get('markdown')
                if markdown_content:
                    documents.append(Document(page_content=markdown_content, metadata={"source": url}))
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
    else:
        raise ValueError("Must provide topic or pdf_path")
        
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    
    # Store in ChromaDB
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    query = topic if topic else "Comprehensive Summary"
    retrieved_docs = retriever.invoke(query)
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=settings.Gemini_api_key)
    
    prompt = PromptTemplate(
        input_variables=["context", "topic"],
        template="""You are an expert tutor. Based on the context, create structured notes for the topic '{topic}'.
Output ONLY valid JSON in the exact given format:
{{
    "topic": "{topic}",
    "notes": [
        "Point 1...",
        "Point 2...",
        "Point 3..."
    ]
}}
Context:
{context}
"""
    )
    
    chain = prompt | llm
    response = chain.invoke({"context": context, "topic": topic if topic else "Document notes"})
    
    try:
        resp_text = response.content if hasattr(response, "content") else str(response)
        clean_resp = resp_text.strip()
        if clean_resp.startswith("```json"):
            clean_resp = clean_resp[7:-3]
        elif clean_resp.startswith("```"):
            clean_resp = clean_resp[3:-3]
        return json.loads(clean_resp)
    except Exception as e:
        return {
            "topic": topic if topic else "Extracted Notes",
            "notes": [resp_text if 'resp_text' in locals() else str(response)]
        }
