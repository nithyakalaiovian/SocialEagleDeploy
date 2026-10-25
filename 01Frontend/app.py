"""Social Eagle Streamlit interface.

The page is organized with the user's SCALE framework:
Subject, Composition, Action, Location, and Aesthetics.
"""

# ---------------------------------------------------------------------------
# 1. Imports and project paths
#    Keep the existing RAG backend importable when Streamlit runs this file.
# ---------------------------------------------------------------------------
from html import escape
from importlib import import_module
from pathlib import Path
import sys

import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# The backend folder starts with a number, so import it dynamically.
backend = import_module("02Backend.rag")
answer_question = backend.answer_question


# ---------------------------------------------------------------------------
# 2. Page setup and design tokens
#    Set the document subject and centralize the visual style choices.
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Spotify Architecture Assistant",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

COLORS = {
    "red": "#B4232F",
    "red_dark": "#851B25",
    "red_soft": "#FBEAEC",
    "off_white": "#FAF8F5",
    "white": "#FFFFFF",
    "ink": "#242326",
    "muted": "#6C6870",
    "line": "#E8E2DE",
    "green": "#168348",
    "green_bg": "#E8F5EC",
    "yellow": "#9A6900",
    "yellow_bg": "#FFF4D6",
    "not_found": "#B4232F",
    "not_found_bg": "#FBEAEC",
}


# ---------------------------------------------------------------------------
# 3. SCALE visual system
#    Aesthetics: use the requested red and off-white palette consistently.
#    Composition: establish clear hierarchy, spacing, and reusable card styles.
#    Accessibility: keep readable contrast, visible focus, and reduced motion.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    :root {
        --brand-red: #B4232F;
        --brand-red-dark: #851B25;
        --brand-red-soft: #FBEAEC;
        --page: #FAF8F5;
        --surface: #FFFFFF;
        --ink: #242326;
        --muted: #6C6870;
        --line: #E8E2DE;
        --green: #168348;
        --green-bg: #E8F5EC;
        --yellow: #9A6900;
        --yellow-bg: #FFF4D6;
    }

    .stApp {
        background: var(--page);
        color: var(--ink);
    }

    .block-container {
        max-width: 1440px;
        padding: 1.2rem 1.6rem 2.4rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
        height: 2.2rem;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0.85rem;
    }

    .hero {
        background: #FFFFFF;
        color: var(--ink);
        border: 1px solid var(--line);
        border-left: 7px solid var(--brand-red);
        border-radius: 0.65rem;
        padding: 1.45rem 1.6rem;
        box-shadow: 0 5px 18px rgba(36, 35, 38, 0.045);
    }

    .hero h1 {
        color: var(--brand-red-dark);
        font-size: clamp(1.9rem, 3vw, 2.55rem);
        letter-spacing: -0.035em;
        line-height: 1.15;
        margin: 0 0 0.45rem;
    }

    .hero p {
        color: var(--muted);
        font-size: 0.96rem;
        margin: 0;
    }

    .tag-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.45rem;
        margin-top: 1rem;
    }

    .tag {
        border: 1px solid #EBC9CC;
        background: var(--brand-red-soft);
        color: var(--brand-red-dark);
        border-radius: 0.35rem;
        padding: 0.32rem 0.65rem;
        font-size: 0.76rem;
    }

    .panel {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 0.65rem;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(36, 35, 38, 0.035);
    }

    .panel-title {
        color: var(--ink);
        font-size: 1.02rem;
        font-weight: 750;
        margin: 0 0 0.45rem;
    }

    .zone-heading {
        color: var(--ink);
        font-size: 1.55rem;
        font-weight: 780;
        letter-spacing: -0.02em;
        margin: 0 0 0.9rem;
    }

    .panel-copy {
        color: var(--muted);
        font-size: 0.82rem;
        line-height: 1.45;
        margin: 0;
    }

    .info-metric {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 1px solid var(--line);
        color: var(--muted);
        font-size: 0.8rem;
        line-height: 1.35;
        padding: 0.42rem 0;
    }

    .info-metric:last-child { border-bottom: 0; }
    .info-metric strong { color: var(--brand-red-dark); font-weight: 750; }

    .engine-chip {
        display: inline-block;
        color: var(--brand-red-dark);
        background: var(--brand-red-soft);
        border: 1px solid #F2D1D4;
        border-radius: 999px;
        padding: 0.3rem 0.55rem;
        margin: 0.25rem 0.2rem 0 0;
        font-size: 0.72rem;
        font-weight: 650;
    }

    .answer-heading {
        color: var(--muted);
        font-size: 1rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        margin: 0.35rem 0 0;
        text-transform: uppercase;
    }

    .status-badge {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        border-radius: 0.6rem;
        padding: 0.75rem 0.95rem;
        font-size: 1.05rem;
        font-weight: 800;
        margin: 0.25rem 0 0.75rem;
    }

    .status-complete {
        color: #116B3A;
        background: var(--green-bg);
        border: 1px solid #B9E3C8;
    }

    .status-partial {
        color: #805700;
        background: var(--yellow-bg);
        border: 1px solid #F0D48C;
    }

    .status-not-found {
        color: var(--brand-red-dark);
        background: var(--brand-red-soft);
        border: 1px solid #F0C5C9;
    }

    .answer-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-left: 5px solid var(--brand-red);
        border-radius: 0.55rem;
        color: var(--ink);
        font-size: 1.3rem;
        line-height: 1.75;
        padding: 1.5rem 1.6rem;
        white-space: pre-line;
        overflow-wrap: anywhere;
        box-shadow: 0 5px 18px rgba(36, 35, 38, 0.045);
    }

    .answer-card.complete { border-left-color: var(--green); }
    .answer-card.partial { border-left-color: #D99A00; }
    .answer-card.not-found { border-left-color: var(--brand-red); }

    div[data-testid="stTextArea"] textarea {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 0.8rem;
        color: var(--ink);
        font-size: 1.18rem;
        line-height: 1.65;
        min-height: 8rem;
    }

    div[data-testid="stForm"] {
        background: #FFFFFF;
        border: 1px solid var(--line);
        border-radius: 1rem;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(36, 35, 38, 0.035);
    }

    div[data-testid="stForm"] label {
        color: var(--ink);
        font-size: 1rem;
        font-weight: 700;
    }

    div[data-testid="stTextArea"] textarea:focus {
        border-color: var(--brand-red);
        box-shadow: 0 0 0 0.15rem rgba(180, 35, 47, 0.14);
    }

    div[data-testid="stFormSubmitButton"] button {
        background: var(--brand-red);
        border: 1px solid var(--brand-red);
        border-radius: 0.45rem;
        color: #FFFFFF;
        font-weight: 700;
        min-height: 2.7rem;
        padding: 0.5rem 1.15rem;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: var(--brand-red-dark);
        border-color: var(--brand-red-dark);
        color: #FFFFFF;
    }

    div[data-testid="stFormSubmitButton"] button:focus-visible {
        outline: 3px solid #F0A6AD;
        outline-offset: 2px;
    }

    div[data-testid="stMetric"] {
        background: #FFFCFA;
        border: 1px solid var(--line);
        border-radius: 0.75rem;
        padding: 0.65rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border-color: var(--line) !important;
        border-radius: 1rem;
        padding: 0.85rem;
        box-shadow: 0 4px 16px rgba(36, 35, 38, 0.035);
    }

    .footer {
        color: var(--muted);
        font-size: 0.78rem;
        padding-top: 1rem;
        text-align: center;
    }

    @media (max-width: 800px) {
        .block-container { padding: 0.8rem 0.8rem 2rem; }
        .hero { padding: 1.2rem; }
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            scroll-behavior: auto !important;
            animation-duration: 0.01ms !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 4. Answer coverage classification
#    The current backend returns answer text plus search-result counts, not a
#    formal confidence score. This transparent heuristic colors the badge.
#    A future backend coverage field can replace these text-based rules.
# ---------------------------------------------------------------------------
def classify_answer(answer_text: str, search_status: dict) -> tuple[str, str, str]:
    """Return (category, label, CSS class) using answer wording and evidence."""
    text = str(answer_text or "").strip().lower()

    no_answer_phrases = (
        "i could not find",
        "i couldn't find",
        "could not find that",
        "couldn't find that",
        "not found in this pdf",
        "not found in the document",
        "no relevant information",
        "does not contain information",
        "don't have enough information",
        "do not have enough information",
    )
    partial_phrases = (
        "does not specify",
        "doesn't specify",
        "not specified",
        "does not state",
        "doesn't state",
        "not explicitly stated",
        "not explicitly described",
        "only partially",
        "partial information",
        "some details are missing",
        "the document mentions",
        "the pdf mentions",
    )

    if not text or any(phrase in text for phrase in no_answer_phrases):
        return ("not_found", "Not found in the documents", "status-not-found")

    if any(phrase in text for phrase in partial_phrases):
        return ("partial", "Partially found", "status-partial")

    # Do not show a green status when the search produced no evidence.
    evidence_keys = ("FAISS passages", "BM25 matches", "Neo4j facts")
    has_evidence = any(
        int(search_status.get(key, 0) or 0) > 0
        for key in evidence_keys
    )
    if not has_evidence:
        return ("not_found", "No supporting passages found", "status-not-found")

    return ("complete", "Answer supported by retrieved evidence", "status-complete")


# ---------------------------------------------------------------------------
# 5. Subject and page introduction
#    Identify Social Eagle and establish the document-questioning purpose.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <section class="hero">
      <h1>Spotify Architecture Assistant</h1>
      <p>Explore the Spotify web app architecture with answers grounded in your project documents.</p>
      <div class="tag-row">
        <span class="tag">Hybrid RAG</span>
        <span class="tag">Document search</span>
        <span class="tag">FAISS · BM25 · Neo4j</span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# 6. Composition and location
#    Left: compact informational panels. Main: the prominent assistant workflow.
#    Search sources joins the other read-only details in the left information pane.
# ---------------------------------------------------------------------------
left_col, main_col = st.columns([0.95, 3.15], gap="large")

# Set up session state so the last answer remains visible after form submission.
if "social_eagle_result" not in st.session_state:
    st.session_state.social_eagle_result = None

# Common Spotify architecture questions users can select as a starting point.
FAQ_QUESTIONS = (
    "What services handle playback, and where is playback state stored?",
    "What happens after an artist uploads a track?",
    "How does the frontend communicate with backend services?",
    "How are playlists created, stored, and updated?",
    "How does the system stream audio to a listener?",
    "What role do the knowledge graph and Neo4j play?",
)


def copy_faq_to_question() -> None:
    """Copy the selected FAQ into the editable question field."""
    selected_faq = st.session_state.get("faq_choice", "")
    if selected_faq in FAQ_QUESTIONS:
        st.session_state.question_text = selected_faq


# ---------------------------------------------------------------------------
# 7. Location: compact information panels
#    Keep knowledge-base and search details in the smaller left information pane.
# ---------------------------------------------------------------------------
with left_col:
    st.markdown(
        """
        <section class="panel">
          <div class="panel-title">Knowledge base</div>
          <p class="panel-copy">
            Ask questions about the documents indexed for this assistant.
          </p>
          <div style="margin-top:0.7rem">
            <span class="engine-chip">FAISS</span>
            <span class="engine-chip">BM25</span>
            <span class="engine-chip">Neo4j</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <section class="panel">
          <div class="panel-title">How it searches</div>
          <p class="panel-copy">
            Vector passages, keyword matches, and graph facts are combined
            when answering a question.
          </p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    # Search-source descriptions and the latest result counts are informational.
    with st.container(border=True):
        st.markdown('<div class="panel-title">Search sources</div>', unsafe_allow_html=True)
        result = st.session_state.social_eagle_result

        if result:
            status = result["status"]
            for label, key in (
                ("FAISS passages", "FAISS passages"),
                ("BM25 matches", "BM25 matches"),
                ("Neo4j facts", "Neo4j facts"),
            ):
                value = escape(str(status.get(key, 0)))
                st.markdown(
                    f'<div class="info-metric"><span>{escape(label)}</span>'
                    f'<strong>{value}</strong></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="info-metric"><span>FAISS</span><strong>Similar passages</strong></div>
                <div class="info-metric"><span>BM25</span><strong>Keyword matches</strong></div>
                <div class="info-metric"><span>Neo4j</span><strong>Graph facts</strong></div>
                """,
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# 8. Action: FAQ selector, question form, and answer card
#    Users can choose a suggested FAQ, edit it, or type their own question.
# ---------------------------------------------------------------------------
with main_col:
    st.markdown('<div class="zone-heading">Architecture Q&amp;A</div>', unsafe_allow_html=True)
    st.selectbox(
        "Frequently asked questions",
        options=("Choose a suggested question…", *FAQ_QUESTIONS),
        key="faq_choice",
        on_change=copy_faq_to_question,
        help="Choose a question to place it in the editable box below.",
    )
    with st.form("question_form", clear_on_submit=False):
        question = st.text_area(
            "Your question",
            placeholder="For example: How does playback state move through the system?",
            height=105,
            key="question_text",
            help="Specific questions usually make it easier to find relevant evidence.",
        )
        submitted = st.form_submit_button("Get answer", use_container_width=True)

    if submitted:
        if not question.strip():
            st.warning("Enter a question first.")
        else:
            try:
                with st.spinner("Searching the documents and knowledge graph…"):
                    answer_text = answer_question(question.strip())
                latest_status = getattr(backend, "LAST_SEARCH_STATUS", {}) or {}
                category, label, css_class = classify_answer(
                    answer_text,
                    latest_status,
                )
                st.session_state.social_eagle_result = {
                    "question": question.strip(),
                    "answer": str(answer_text),
                    "status": latest_status,
                    "category": category,
                    "label": label,
                    "css_class": css_class,
                }
            except Exception as error:
                st.session_state.social_eagle_result = None
                st.error(f"Could not get an answer: {error}")

    result = st.session_state.social_eagle_result
    if result:
        st.markdown('<div class="answer-heading">Answer status</div>', unsafe_allow_html=True)
        st.markdown(
            f'<span class="status-badge {escape(result["css_class"])}">'
            f'{escape(result["label"])}</span>',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="answer-heading">Answer</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="answer-card {escape(result["category"])}">'
            f'{escape(result["answer"])}</div>',
            unsafe_allow_html=True,
        )

        # Expose retrieval counts for transparency without cluttering the main view.
        with st.expander("Search diagnostics"):
            status = result["status"]
            d1, d2, d3 = st.columns(3)
            d1.metric("FAISS passages", status.get("FAISS passages", 0))
            d2.metric("BM25 matches", status.get("BM25 matches", 0))
            d3.metric("Neo4j facts", status.get("Neo4j facts", 0))

            if status.get("Neo4j query ran"):
                st.caption(
                    "Neo4j was queried. A zero count means no matching graph "
                    "facts were returned for this question."
                )
            else:
                st.caption("The Neo4j query did not run for this question.")

        # Keep the user's question visible as context for the answer.
        with st.expander("Your question"):
            st.write(result["question"])


# ---------------------------------------------------------------------------
# 10. Aesthetics: footer
#     Finish with a quiet product identifier without the removed brand block.
# ---------------------------------------------------------------------------
st.markdown(
    '<div class="footer">Spotify Architecture Assistant · Hybrid document search</div>',
    unsafe_allow_html=True,
)

