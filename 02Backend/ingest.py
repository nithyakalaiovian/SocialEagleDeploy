from pathlib import Path
import json
import os
import sys

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_neo4j import Neo4jGraph


PROJECT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

INDEX_DIR = BACKEND_DIR / "faiss_index"
CHUNKS_FILE = BACKEND_DIR / "chunks.json"


def ingest_pdf(pdf_path: Path) -> int:
    """Read a PDF and save its FAISS, BM25, and Neo4j graph data."""

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = PyPDFLoader(str(pdf_path)).load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100,
    )
    chunks = splitter.split_documents(pages)

    if not chunks:
        raise ValueError(
            "No readable text was found. The PDF may contain scanned images."
        )

    # Build and save the FAISS meaning-search index.
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(INDEX_DIR))

    # Save the text pieces used later for BM25 word search.
    saved_chunks = [
        {
            "text": chunk.page_content,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]
    CHUNKS_FILE.write_text(
        json.dumps(saved_chunks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Ask the model to identify things and relationships in the PDF.
    graph_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    transformer = LLMGraphTransformer(
        llm=graph_llm,
        allowed_nodes=[
            "System",
            "Component",
            "Technology",
            "Service",
            "DataStore",
            "Protocol",
        ],
        allowed_relationships=[
            "CONTAINS",
            "USES",
            "CONNECTS_TO",
            "SENDS_DATA_TO",
            "STORES_DATA_IN",
            "AUTHENTICATES_WITH",
            "DEPENDS_ON",
        ],
    )
    graph_documents = transformer.convert_to_graph_documents(chunks)

    # Connect to Neo4j Aura using the values in the top-level .env file.
    required_settings = ["NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD"]
    missing_settings = [
        name for name in required_settings if not os.getenv(name)
    ]
    if missing_settings:
        raise ValueError(
            "Missing settings in the project .env file: "
            + ", ".join(missing_settings)
        )

    graph = Neo4jGraph(
        url=os.environ["NEO4J_URI"],
        username=os.environ["NEO4J_USERNAME"],
        password=os.environ["NEO4J_PASSWORD"],
        database=os.getenv("NEO4J_DATABASE", "neo4j"),
    )
    graph.add_graph_documents(graph_documents, include_source=True)
    graph.close()

    return len(chunks)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_file = Path(sys.argv[1])
        if not pdf_file.is_absolute():
            pdf_file = PROJECT_DIR / pdf_file
    else:
        pdf_file = PROJECT_DIR / "spotify_web_app_architecture.pdf"

    try:
        number_of_chunks = ingest_pdf(pdf_file)
        print(f"Done! Prepared {number_of_chunks} searchable text pieces.")
        print("Saved the FAISS index, BM25 text, and Neo4j knowledge graph.")
        print(f"PDF used: {pdf_file}")
    except Exception as error:
        print(f"Could not prepare the PDF: {error}")
        raise