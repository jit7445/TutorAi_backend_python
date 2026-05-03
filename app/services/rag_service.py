import os
import json
import logging
import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import PyPDFLoader, WikipediaLoader
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from app.core.config import settings
from quickscraper_sdk import QuickScraper

logger = logging.getLogger(__name__)

# Initialize Embedding Model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def process_rag(topic: str = None, pdf_path: str = None) -> dict:
    documents = []
    
    # 1. Load Data from PDF or Web
    if pdf_path and os.path.exists(pdf_path):
        logger.info(f"Loading PDF: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
    elif topic:
        logger.info(f"Searching for topic: {topic}")
        
        # Initialize QuickScraper if token is available
        qs_client = None
        if settings.QUICK_SCRAPER_ACCESS_TOKEN:
            try:
                qs_client = QuickScraper(settings.QUICK_SCRAPER_ACCESS_TOKEN.strip())
            except Exception as e:
                logger.error(f"Failed to initialize QuickScraper: {e}")

        # Step A: Search for relevant URLs using DuckDuckGo
        urls = []
        try:
            search = DuckDuckGoSearchAPIWrapper()
            results = search.results(topic, max_results=3)
            urls = [res.get("link") for res in results if res.get("link")]
            logger.info(f"Found URLs via DuckDuckGo: {urls}")
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed: {e}")

        # Step B: Scrape top 3 URLs using QuickScraper (or fallback to Wikipedia)
        if qs_client and urls:
            for url in urls:
                try:
                    logger.info(f"Scraping {url} via QuickScraper...")
                    response = qs_client.getHtml(url)
                    # response._content usually contains the HTML string
                    html_content = getattr(response, '_content', None) or getattr(response, 'text', None)
                    
                    if html_content:
                        soup = BeautifulSoup(html_content, 'html.parser')
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        text = soup.get_text(separator=' ', strip=True)
                        if len(text) > 200:
                            documents.append(Document(page_content=text, metadata={"source": url}))
                except Exception as e:
                    logger.warning(f"Failed to scrape {url} via QuickScraper: {e}")

        # Step C: Fallback to Wikipedia if we still have nothing
        if not documents:
            try:
                logger.info("Falling back to Wikipedia...")
                wiki_loader = WikipediaLoader(query=topic, load_max_docs=2)
                wiki_docs = wiki_loader.load()
                documents.extend(wiki_docs)
            except Exception as e:
                logger.warning(f"Wikipedia fallback failed: {e}")
    else:
        raise ValueError("Must provide topic or pdf_path")
        
    # Final Safety fallback
    if not documents:
        logger.warning("No documents found! Using default content fallback.")
        fallback_content = f"Information about {topic if topic else 'the requested topic'} including its main concepts and educational points."
        documents.append(Document(page_content=fallback_content, metadata={"source": "fallback"}))

    # 2. Split into Chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    
    # 3. Store in ChromaDB
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    
    # 4. Retrieve Context
    query = topic if topic else "Comprehensive Summary"
    retrieved_docs = retriever.invoke(query)
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    
    # 5. Generate Response using Local Phi-3
    llm = OllamaLLM(
        model="phi3",
        base_url="http://localhost:11434",
        temperature=0.3
    )
    
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
    
    # 6. Parse and Clean JSON response
    try:
        resp_text = response.content if hasattr(response, "content") else str(response)
        clean_resp = resp_text.strip()
        if clean_resp.startswith("```json"):
            clean_resp = clean_resp[7:-3]
        elif clean_resp.startswith("```"):
            clean_resp = clean_resp[3:-3]
        
        return json.loads(clean_resp)
    except Exception as e:
        logger.error(f"Failed to parse JSON response: {e}")
        return {
            "topic": topic if topic else "Extracted Notes",
            "notes": [resp_text] if 'resp_text' in locals() else ["Could not generate structured notes."]
        }
