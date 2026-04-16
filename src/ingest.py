import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

load_dotenv()

def ensure_env_vars():
    required_env_vars = (
        "DATABASE_URL",
        "PG_VECTOR_COLLECTION_NAME",
        "PDF_PATH",
    )

    for env_var in required_env_vars:
        if not os.getenv(env_var):
            raise RuntimeError(f"Environment variable {env_var} is not set")

    api_keys = [
        key for key in ("GOOGLE_API_KEY", "OPENAI_API_KEY")
        if os.getenv(key)
    ]

    if len(api_keys) == 0:
        raise RuntimeError(
            "One of GOOGLE_API_KEY or OPENAI_API_KEY must be set."
        )

ensure_env_vars()

PDF_PATH = os.getenv("PDF_PATH")

def ingest_pdf():
    docs = PyPDFLoader(str(PDF_PATH)).load()

    splits = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, add_start_index=False).split_documents(docs)
    if not splits:
        print("No splits were created from the document.")
        raise SystemExit(0)
    
    enriched = [
        Document(
            page_content=split.page_content,
            metadata={k: v for k, v in split.metadata.items() if v not in ("", None)}
        ) for split in splits
    ]

    ids = [f"doc-{i}" for i in range(len(enriched))]

    embeddings = GoogleGenerativeAIEmbeddings(
        model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/embedding-001"))
    
    #embeddings = OpenAIEmbeddings(model=os.getenv("OPENAI_MODEL","text-embedding-3-small"))

    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PG_VECTOR_COLLECTION_NAME"),
        connection=os.getenv("DATABASE_URL"),
        use_jsonb=True
    )

    store.add_documents(ids=ids, documents=enriched)
    print(f"Added {len(enriched)} documents to PGVector collection {os.getenv('PG_VECTOR_COLLECTION_NAME')}")


if __name__ == "__main__":
    ingest_pdf()