from html import escape
from importlib import import_module
from pathlib import Path
import sys

import streamlit as st


# Find the project folder and make the backend importable.
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

# The folder name begins with a number, so import it this way.
backend = import_module("02Backend.rag")
answer_question = backend.answer_question


st.set_page_config(
    page_title="Social Eagle | Offline Session | Hybrid RAG | Docker Check",
    page_icon="🦅",
    layout="wide",
)


st.markdown(
    """
    <style>
    :root {
        --navy: #10253f;
        --teal: #18a999;
        --ink: #172b45;
        --muted: #65758b;
        --panel: #ffffff;
        --line: #e5ebf2;
        --background: #f4f7fb;
    }

    .stApp {
        background: var(--background);
    }

    .block-container {
        max-width: 1000px;
        padding-top: 2.2rem;
        padding-bottom: 3rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 1.6rem;
    }

    .brand-name {
        color: var(--navy);
        font-size: 1.35rem;
        font-weight: 750;
        letter-spacing: -0.03em;
        line-height: 1.2;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 4px;
    }

    .hero {
        background: linear-gradient(120deg, #10253f 0%, #183e5b 100%);
        border-radius: 22px;
        padding: 2rem 2.1rem;
        color: white;
        margin-bottom: 1.4rem;
        box-shadow: 0 14px 35px rgba(16, 37, 63, 0.12);
    }

    .hero h1 {
        color: white;
        font-size: 2rem;
        margin: 0 0 0.45rem 0;
        letter-spacing: -0.04em;
    }

    .hero p {
        color: #d8e5ef;
        margin: 0;
        font-size: 1rem;
    }

    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 1.25rem;
    }

    .tag {
        border: 1px solid rgba(255, 255, 255, 0.24);
        background: rgba(255, 255, 255, 0.09);
        color: #eef7fb;
        padding: 6px 11px;
        border-radius: 999px;
        font-size: 0.78rem;
    }

    div[data-testid="stTextArea"] textarea {
        border-radius: 12px;
        border: 1px solid var(--line);
        background: white;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: var(--teal);
        border: 0;
        color: white;
        border-radius: 10px;
        padding: 0.55rem 1.2rem;
        font-weight: 650;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #128b7e;
        color: white;
        border: 0;
    }

    .answer-label {
        color: var(--teal);
        font-size: 0.76rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 1.2rem 0 0.65rem 0;
    }

    .answer-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-left: 5px solid var(--teal);
        border-radius: 14px;
        padding: 1.25rem 1.4rem;
        color: var(--ink);
        font-size: 1.05rem;
        line-height: 1.65;
        white-space: pre-line;
        box-shadow: 0 8px 24px rgba(16, 37, 63, 0.05);
    }

    .footer {
        color: var(--muted);
        text-align: center;
        font-size: 0.78rem;
        margin-top: 2.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Custom eagle-style emblem and brand name.
st.markdown(
    """
    <div class="brand">
      <svg width="48" height="48" viewBox="0 0 48 48"
           xmlns="http://www.w3.org/2000/svg" role="img"
           aria-label="Social Eagle emblem">
        <rect width="48" height="48" rx="15" fill="#10253f"/>
        <path d="M7 17 L19 20 L24 13 L29 20 L41 17 L34 27
                 L27 25 L24 34 L21 25 L14 27 Z"
              fill="#18a999"/>
        <path d="M17 31 L24 28 L31 31 L24 38 Z" fill="#ffffff"/>
        <circle cx="29" cy="21" r="1.4" fill="#ffffff"/>
      </svg>
      <div>
        <div class="brand-name">Social Eagle</div>
        <div class="brand-subtitle">Knowledge Assistant</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <section class="hero">
      <h1>Ask your documents</h1>
      <p>Get clear answers grounded in your PDF using hybrid search and a knowledge graph.</p>
      <div class="tag-row">
        <span class="tag">Offline Session</span>
        <span class="tag">Hybrid RAG</span>
        <span class="tag">Docker Check</span>
        <span class="tag">FAISS · BM25 · Neo4j</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)


with st.form("question_form"):
    question = st.text_area(
        "Your question",
        placeholder="For example: How does the frontend communicate with the backend?",
        height=100,
    )
    submitted = st.form_submit_button("Get answer")


if submitted:
    if not question.strip():
        st.warning("Type a question first.")
    else:
        try:
            with st.spinner("Searching your PDF and knowledge graph..."):
                answer = answer_question(question.strip())

            st.markdown(
                '<div class="answer-label">Answer</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="answer-card">{escape(str(answer))}</div>',
                unsafe_allow_html=True,
            )

            # Show how many results each search returned.
            with st.expander("Search diagnostics"):
                status = backend.LAST_SEARCH_STATUS
                col1, col2, col3 = st.columns(3)

                col1.metric(
                    "FAISS passages",
                    status.get("FAISS passages", 0),
                )
                col2.metric(
                    "BM25 matches",
                    status.get("BM25 matches", 0),
                )
                col3.metric(
                    "Neo4j facts",
                    status.get("Neo4j facts", 0),
                )

                if status.get("Neo4j query ran"):
                    st.caption(
                        "Neo4j was queried. Zero facts means it found no "
                        "matching graph facts for this question."
                    )
                else:
                    st.caption(
                        "The Neo4j query did not run for this question."
                    )

        except Exception as error:
            st.error(f"Could not get an answer: {error}")


st.markdown(
    '<div class="footer">Social Eagle · Offline Session · Hybrid RAG</div>',
    unsafe_allow_html=True,
)