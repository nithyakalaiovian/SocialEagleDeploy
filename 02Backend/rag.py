import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_neo4j import Neo4jGraph


PROJECT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

load_dotenv(PROJECT_DIR / ".env")

INDEX_DIR = BACKEND_DIR / "faiss_index"
CHUNKS_FILE = BACKEND_DIR / "chunks.json"

# Streamlit reads these counts after answer_question finishes.
LAST_SEARCH_STATUS = {}


def tokenize(text: str) -> list[str]:
    """Split text into lowercase words."""
    return re.findall(r"\w+", text.lower())


def answer_question(question: str) -> str:
    """Search the PDF with FAISS and BM25, add Neo4j facts, and answer."""

    if not INDEX_DIR.exists() or not CHUNKS_FILE.exists():
        raise FileNotFoundError("Run ingest.py first to prepare the PDF.")

    # Load the PDF text pieces for BM25 keyword search.
    saved_chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    documents = [
        Document(page_content=item["text"], metadata=item["metadata"])
        for item in saved_chunks
    ]

    # Ignore common question words when searching for exact terms.
    stop_words = {
        "a", "an", "and", "are", "as", "at", "by", "did", "do", "does",
        "for", "from", "how", "i", "in", "is", "it", "of", "on", "or",
        "the", "this", "to", "was", "what", "when", "where", "which",
        "who", "why", "with",
    }
    query_terms = {
        word
        for word in tokenize(question)
        if len(word) > 2 and word not in stop_words
    }

    # Find chunks containing the question words.
    # Prefix matching lets "track" match "tracks" and "tracking".
    exact_hits = []
    for document in documents:
        document_words = set(tokenize(document.page_content))
        overlap = {
            term
            for term in query_terms
            if any(word.startswith(term) for word in document_words)
        }
        if overlap:
            exact_hits.append((len(overlap), document))

    exact_hits.sort(key=lambda item: item[0], reverse=True)
    exact_documents = [document for _, document in exact_hits[:5]]

    # FAISS finds passages with similar meaning.
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.load_local(
        str(INDEX_DIR),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    vector_results = vector_store.similarity_search(question, k=4)

    # BM25 searches for matching words, ignoring capitalization.
    keyword_retriever = BM25Retriever.from_documents(
        documents,
        preprocess_func=tokenize,
    )
    keyword_retriever.k = 6
    keyword_results = keyword_retriever.invoke(question)

    # Include exact keyword results as well as BM25 and FAISS results.
    selected_documents = []
    seen = set()

    for document in exact_documents + keyword_results + vector_results:
        key = (document.metadata.get("page", 0), document.page_content)
        if key not in seen:
            selected_documents.append(document)
            seen.add(key)

    selected_documents = selected_documents[:10]

    pdf_context = "\n\n".join(
        document.page_content for document in selected_documents
    )

    # Search Neo4j for question terms found in graph entity IDs.
    graph_terms = sorted(query_terms)
    graph_rows = []
    graph_checked = False

    if graph_terms:
        graph = Neo4jGraph(
            url=os.environ["NEO4J_URI"],
            username=os.environ["NEO4J_USERNAME"],
            password=os.environ["NEO4J_PASSWORD"],
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
        )

        graph_rows = graph.query(
            """
            MATCH (node)-[relationship]-(related)
            WHERE any(
                term IN $terms
                WHERE toLower(coalesce(toString(node.id), "")) CONTAINS term
            )
            RETURN
                coalesce(toString(node.id), "Unknown") AS entity,
                type(relationship) AS relationship,
                coalesce(toString(related.id), "Unknown") AS related_entity
            LIMIT 20
            """,
            params={"terms": graph_terms},
        )
        graph.close()
        graph_checked = True

    graph_context = "\n".join(
        f"{row['entity']} --{row['relationship']}--> "
        f"{row['related_entity']}"
        for row in graph_rows
    )

    # Streamlit displays these counts in its Search diagnostics panel.
    LAST_SEARCH_STATUS.clear()
    LAST_SEARCH_STATUS.update(
        {
            "Exact keyword passages": len(exact_documents),
            "FAISS passages": len(vector_results),
            "BM25 passages": len(keyword_results),
            "Neo4j facts": len(graph_rows),
            "Neo4j query ran": graph_checked,
        }
    )

    prompt = f"""Answer using only the PDF passages and knowledge graph facts below.
Keep the answer to exactly 2 short lines.
Do not include sources, citations, page numbers, or explanations.
If the PDF does not state the exact next step, give the related facts it does
state and clearly say that it does not specify the next step.
Only say "I could not find that in this PDF" if there is no related information.
Do not guess.

PDF passages:
{pdf_context}

Knowledge graph facts:
{graph_context}

Question: {question}
"""

    response = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    ).invoke(prompt)

    return str(response.content).strip()


if __name__ == "__main__":
    question = input("Ask a question about your PDF: ").strip()

    if not question:
        print("Please type a question and run the program again.")
    else:
        try:
            print("\n" + answer_question(question))
        except Exception as error:
            print(f"\nSomething went wrong: {error}")