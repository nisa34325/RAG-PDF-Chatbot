<<<<<<< HEAD
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import tempfile
import os

from backend.rag import (
    extract_text_from_pdf,
    get_chunks,
    create_vector_store
)

from groq import Groq


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="RAG PDF Chatbot",
    page_icon="📚",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* App shell */
.stApp {
    background: #0b1220;
    color: #f8fafc;
}

/* Remove Streamlit's empty top header and reclaim the space. */
header[data-testid="stHeader"] {
    display: none;
}

[data-testid="stToolbar"] {
    display: none;
}

/* Do not paint a full-width black strip behind the chat input. */
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottom"] > div > div {
    background: transparent !important;
    border-top: 0 !important;
    box-shadow: none !important;
}

div[data-testid="stBottom"] {
    position: static !important;
}

.block-container {
    max-width: 1120px;
    padding-top: 0.35rem;
    padding-bottom: 0.35rem;
}

/* Sidebar: compact, stable, and without an internal scrollbar. */
section[data-testid="stSidebar"] {
    background: #111a2d;
    border-right: 1px solid #26344d;
}

section[data-testid="stSidebar"] > div:first-child {
    height: 100vh;
    overflow: hidden;
    padding: 0.35rem 0.55rem 0.35rem;
}

section[data-testid="stSidebar"] .block-container,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    margin: 0.2rem 0 0.35rem;
    line-height: 1.2;
}

section[data-testid="stSidebar"] hr {
    margin: 0.45rem 0;
    border-color: #2a3850;
}

section[data-testid="stSidebar"] p {
    margin: 0.2rem 0;
}

/* This app accepts one PDF per chat. Hide Streamlit's add-more (+) control.
   The file chip's own remove (×) control remains available. */
/* Streamlit versions use different wrappers/labels for the add-more button. */
[data-testid="stFileUploader"] button[aria-label*="Add"],
[data-testid="stFileUploader"] button[title*="Add"],
[data-testid="stFileUploader"] button[aria-label*="add"],
[data-testid="stFileUploader"] button[title*="add"],
[data-testid="stFileUploader"] button[aria-label="Upload files"],
[data-testid="stFileUploader"] button[title="Upload files"] {
    display: none !important;
}

/* Compact single-file uploader. */
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    min-height: 0 !important;
    height: auto !important;
    padding: 0.35rem 0.65rem !important;
    margin: 0 !important;
}

[data-testid="stFileUploader"] section {
    padding: 0 !important;
    min-height: 0 !important;
}

/* Hide the chip's tiny remove control; the large control beside the uploader
   below is the single, intentional way to remove the PDF. */
[data-testid="stFileUploader"] button[aria-label*="Remove"],
[data-testid="stFileUploader"] button[title*="Remove"],
[data-testid="stFileUploader"] button[aria-label*="remove"],
[data-testid="stFileUploader"] button[title*="remove"] {
    display: none !important;
}

/* Align the external remove control with the file chip, not the uploader label. */
.pdf-remove-button {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding-top: 1.9rem;
    box-sizing: border-box;
}

.pdf-remove-button button {
    min-height: 2.85rem !important;
    height: 2.85rem !important;
    width: 2.85rem !important;
    padding: 0 !important;
    font-size: 1.45rem !important;
    line-height: 1 !important;
    font-weight: 500 !important;
    border: 1px solid #40516d !important;
    background: #111c30 !important;
    color: #f8fafc !important;
    border-radius: 10px !important;
}

.pdf-remove-button button:hover {
    background: #2a3850 !important;
    border-color: #8b7cff !important;
}

.sidebar-file-card {
    background: #172238;
    border: 1px solid #2b3a54;
    border-radius: 12px;
    padding: 0.8rem 0.9rem;
    margin: 0.35rem 0 0.55rem;
}

.sidebar-file-name {
    font-weight: 700;
    overflow-wrap: anywhere;
}

.sidebar-label {
    color: #aebbd0;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.sidebar-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin: 0.2rem 0;
}

.sidebar-metric {
    font-size: 0.82rem;
    color: #b8c5d9;
}

.sidebar-metric strong {
    display: block;
    color: #f8fafc;
    font-size: 1.45rem;
    font-weight: 500;
    line-height: 1.2;
    margin-top: 0.15rem;
}

/* Main content */
.title {
    text-align: center;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 750;
    color: #ffffff;
    margin: 0.05rem 0 0.2rem;
}

.subtitle {
    text-align: center;
    color: #9fb0c9;
    font-size: 1rem;
    margin-bottom: 0.55rem;
}

.status-box {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    background: #0d302e;
    border: 1px solid #176b58;
    color: #8af0c4;
    font-weight: 600;
    margin: 0.45rem 0 0.65rem;
}

.chat-row {
    width: min(100%, 1040px);
    margin: 0.28rem auto;
    display: flex;
    align-items: flex-end;
    gap: 0.55rem;
}

.chat-row.user-row {
    justify-content: flex-end;
}

.chat-row.bot-row {
    justify-content: flex-start;
}

.chat-avatar {
    width: 1.55rem;
    height: 1.55rem;
    flex: 0 0 1.55rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #1b2942;
    border: 1px solid #334766;
    font-size: 0.78rem;
    line-height: 1;
}

.user-row .chat-avatar {
    order: 2;
    background: #6555dc;
    border-color: #8174ff;
}

.user-message, .bot-message {
    padding: 0.7rem 0.9rem;
    border-radius: 14px;
    margin: 0.45rem 0;
    line-height: 1.55;
}

.user-message {
    background: #243f91;
    color: #ffffff;
    margin-left: 8%;
}

.bot-message {
    background: #141f33;
    color: #e6edf7;
    border: 1px solid #2a3850;
    margin-right: 3%;
}

.chat-label {
    font-weight: 700;
    margin-bottom: 0.3rem;
    color: #ffffff;
}

/* Instagram-inspired conversation layout. */
.chat-label {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.78rem;
    letter-spacing: 0.01em;
    color: #b8c5d9;
    margin-bottom: 0.35rem;
}

.user-message, .bot-message {
    width: fit-content;
    max-width: calc(100% - 2.15rem);
    padding: 0.62rem 0.85rem;
    border-radius: 18px;
    margin: 0;
    line-height: 1.55;
    overflow-wrap: anywhere;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
}

.user-message {
    margin-left: 0;
    margin-right: 0;
    background: linear-gradient(135deg, #765cf6, #4c6ee8);
    color: #ffffff;
    border-bottom-right-radius: 5px;
}

.user-message .chat-label {
    color: #e9e5ff;
    justify-content: flex-end;
}

.bot-message {
    margin-left: 0;
    margin-right: 0;
    background: #141f33;
    color: #e6edf7;
    border: 1px solid #2a3850;
    border-bottom-left-radius: 5px;
}

.bot-message .chat-label {
    color: #9fb0c9;
}

/* Keep the input compact and visually attached to the conversation. */
div[data-testid="stChatInput"] {
    position: static !important;
    width: min(100%, 850px) !important;
    max-width: 850px !important;
    margin: 0.35rem auto 0 !important;
    background: transparent !important;
    border-top: 0 !important;
    padding: 0.15rem 0 0.1rem !important;
}

/* Keep the composer aligned with the conversation column instead of
   stretching across the entire main page. */
div[data-testid="stChatInput"] > div {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 0 !important;
}

div[data-testid="stChatInput"] textarea {
    min-height: 2.35rem !important;
    max-height: 2.35rem !important;
    padding-top: 0.55rem !important;
    padding-bottom: 0.55rem !important;
}

div[data-testid="stChatInput"] > div {
    background: #111c30 !important;
    border: 1px solid #334766 !important;
    border-radius: 999px !important;
    padding: 0.2rem 0.35rem 0.2rem 0.9rem !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ffffff !important;
}

div[data-testid="stChatInput"] button {
    border-radius: 999px !important;
    background: #7563f5 !important;
    color: white !important;
}

div[data-testid="stChatInput"] button:hover {
    background: #8979ff !important;
}

.stButton > button {
    background: #7563f5;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 650;
    padding: 0.55rem 0.75rem;
}

.stButton > button:hover {
    background: #8979ff;
}


.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin: 0.8rem 0 1.1rem;
}

.feature-card {
    background: #111c30;
    border: 1px solid #263752;
    border-radius: 14px;
    padding: 0.9rem;
}

.feature-icon {
    font-size: 1.35rem;
    margin-bottom: 0.35rem;
}

.feature-title {
    color: #f8fafc;
    font-weight: 750;
    font-size: 0.95rem;
}

.feature-copy {
    color: #9fb0c9;
    font-size: 0.78rem;
    line-height: 1.4;
    margin-top: 0.25rem;
}

/* Streamlit adds vertical space around each markdown element. Keep the
   conversation compact so messages read like one continuous thread. */
[data-testid="stVerticalBlock"] > [data-testid="element-container"] {
    margin-bottom: 0 !important;
}

.section-kicker {
    color: #8ea4c7;
    font-size: 0.76rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}

/* Final chat stability pass: keep the composer predictable during Streamlit reruns. */
div[data-testid="stChatInput"] {
    width: min(100%, 1040px) !important;
    max-width: 1040px !important;
    margin: 0.5rem auto 0 !important;
    padding: 0 !important;
    position: static !important;
    min-height: 0 !important;
}

div[data-testid="stChatInput"] > div {
    min-height: 0 !important;
    height: 3rem !important;
    box-sizing: border-box !important;
    padding: 0.25rem 0.35rem 0.25rem 0.9rem !important;
}

div[data-testid="stChatInput"] textarea {
    height: 2.35rem !important;
    min-height: 2.35rem !important;
    max-height: 2.35rem !important;
    line-height: 1.25 !important;
    resize: none !important;
    overflow: hidden !important;
}

/* Prevent Streamlit's rerun layout from introducing extra vertical gaps. */
div[data-testid="stChatInput"] + div,
div[data-testid="stChatInput"] ~ div {
    margin-top: 0 !important;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.85rem 1rem;
    }
    .chat-row {
        width: 100%;
    }
    .user-message, .bot-message {
        max-width: calc(100% - 2.05rem);
    }
    .subtitle {
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    .feature-grid {
        grid-template-columns: 1fr;
        gap: 0.55rem;
    }
}

/* Final alignment override: composer and conversation share one column. */
.chat-row {
    width: 1040px !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

div[data-testid="stChatInput"] {
    width: 1040px !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

div[data-testid="stChatInput"] > div {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

@media (max-width: 768px) {
    .chat-row,
    div[data-testid="stChatInput"] {
        width: 100% !important;
        max-width: 100% !important;
    }
}


/* FINAL COMPOSER ALIGNMENT: match the 1040px conversation column exactly. */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] form > div {
    width: min(1040px, calc(100% - 2rem)) !important;
    max-width: 1040px !important;
    box-sizing: border-box !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stChatInput"] {
    position: static !important;
    padding: 0 !important;
    margin-top: 0.55rem !important;
    margin-bottom: 0 !important;
}

[data-testid="stChatInput"] form {
    padding: 0 !important;
}

[data-testid="stChatInput"] textarea {
    width: 100% !important;
    box-sizing: border-box !important;
}

@media (max-width: 768px) {
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] form,
    [data-testid="stChatInput"] form > div {
        width: 100% !important;
        max-width: 100% !important;
    }
}


/* FINAL STABILITY PATCH: prevent composer growth and browser scroll anchoring jumps. */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], .block-container {
    scroll-behavior: auto !important;
    overflow-anchor: none !important;
}

/* Keep every chat row from changing width/height during a rerun. */
.chat-row {
    min-width: 0 !important;
    min-height: 0 !important;
    contain: layout style !important;
}

.chat-row .user-message,
.chat-row .bot-message {
    min-width: 0 !important;
    box-sizing: border-box !important;
}

/* One-line composer: Enter submits, it never turns into a growing textarea. */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] form > div {
    height: 3rem !important;
    min-height: 3rem !important;
    max-height: 3rem !important;
    overflow: hidden !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    height: 2.35rem !important;
    min-height: 2.35rem !important;
    max-height: 2.35rem !important;
    line-height: 1.25 !important;
    padding-top: 0.55rem !important;
    padding-bottom: 0.55rem !important;
    resize: none !important;
    overflow: hidden !important;
    white-space: nowrap !important;
    field-sizing: fixed !important;
}

/* Do not animate layout changes when Streamlit reruns after Enter. */
[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
.chat-row, .chat-row * {
    transition: none !important;
    animation: none !important;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# TITLE
# ==================================================

st.markdown(
    '<div class="title">📚 RAG PDF Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions from your PDF using Retrieval-Augmented Generation'
    '</div>',
    unsafe_allow_html=True
)



# ==================================================
# GROQ API
# ==================================================

from groq import Groq
import streamlit as st

API_KEY = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=API_KEY)

# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

if "total_characters" not in st.session_state:
    st.session_state.total_characters = 0

if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0


# Keep a stable placeholder in the Streamlit element tree.
# Its content is decided AFTER the uploader has been evaluated, so the
# home cards disappear immediately when a file is selected.
features_placeholder = st.empty()

# ==================================================
# PDF UPLOAD
# ==================================================

if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0

uploader_key = f"pdf_uploader_{st.session_state.uploader_version}"
upload_col, remove_col = st.columns([0.92, 0.08], gap="small")

with upload_col:
    uploaded_file = st.file_uploader(
        "📄 Upload your PDF",
        type=["pdf"],
        key=uploader_key
    )

# Render the home section using the CURRENT uploader value, not stale
# session-state data from the previous Streamlit run.
if uploaded_file is None and st.session_state.pdf_name is None and not st.session_state.messages:
    with features_placeholder.container():
        st.markdown(
            """
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">📄</div>
                    <div class="feature-title">One PDF workspace</div>
                    <div class="feature-copy">Upload one document and keep the conversation focused.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔎</div>
                    <div class="feature-title">Grounded answers</div>
                    <div class="feature-copy">Retrieve relevant content before generating a response.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Simple chat flow</div>
                    <div class="feature-copy">Ask follow-up questions in a clean, familiar interface.</div>
                </div>
            </div>
            <div class="section-kicker">Your document workspace</div>
            """,
            unsafe_allow_html=True
        )
else:
    features_placeholder.empty()

with remove_col:
    if uploaded_file is not None:
        st.markdown('<div class="pdf-remove-button">', unsafe_allow_html=True)
        if st.button("✕", key="remove_pdf", help="Remove the current PDF"):
            # Rotate the uploader key. This is the reliable Streamlit way
            # to clear the visible file chip after a PDF is removed.
            st.session_state.uploader_version += 1
            st.session_state.pdf_name = None
            st.session_state.total_characters = 0
            st.session_state.total_chunks = 0
            st.session_state.messages = []
            st.session_state.vector_store = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# PROCESS UPLOADED PDF
# ==================================================

if uploaded_file is not None:

    # Check if a new PDF was uploaded
    if st.session_state.pdf_name != uploaded_file.name:

        with st.spinner("📄 Processing PDF..."):

            # Save uploaded PDF temporarily
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(uploaded_file.getbuffer())

                pdf_path = temp_file.name

            try:

                # Extract text
                text = extract_text_from_pdf(pdf_path)

                # Check extracted text
                if not text.strip():
                    st.error(
                        "❌ Could not extract text from this PDF."
                    )
                    st.stop()

                # Create chunks
                chunks = get_chunks(text)

                # Create vector database
                vector_store = create_vector_store(chunks)

                # Save in session
                st.session_state.vector_store = vector_store
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.total_characters = len(text)
                st.session_state.total_chunks = len(chunks)

                # Clear previous chat
                st.session_state.messages = []

            finally:

                # Delete temporary PDF
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        # ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.header("📄 PDF Information")

    if st.session_state.pdf_name:
        st.markdown(
            f"""
            <div class="sidebar-file-card">
                <div class="sidebar-label">File</div>
                <div class="sidebar-file-name">{st.session_state.pdf_name}</div>
            </div>
            <div class="sidebar-metrics">
                <div class="sidebar-metric">Characters<strong>{st.session_state.total_characters:,}</strong></div>
                <div class="sidebar-metric">Chunks<strong>{st.session_state.total_chunks}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="sidebar-file-card"><div class="sidebar-label">Status</div>'
            '<div class="sidebar-file-name">No PDF uploaded yet</div></div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.header("💡 How to use")
    st.markdown(
        """
        1. Upload a PDF.
        2. Wait for processing.
        3. Ask a question.
        4. Get an answer grounded in the PDF.
        """
    )

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ==================================================
# CHECK PDF
# ==================================================

if st.session_state.vector_store is None:

    # Do not render a second-looking empty upload state while a file is
    # already selected and being processed. The uploader above is the only
    # upload control in the app.
    if uploaded_file is None:
        st.info("👆 Please upload a PDF to start chatting.")

else:

    # ==================================================
    # PDF STATUS
    # ==================================================

    st.markdown(
        f"""
        <div class="status-box">
            ✅ PDF Ready: {st.session_state.pdf_name}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ==================================================
    # DISPLAY CHAT HISTORY
    # ==================================================

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="chat-row user-row">
                    <div class="user-message">{message["content"]}</div>
                    <div class="chat-avatar" aria-label="User message">👤</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="chat-row bot-row">
                    <div class="chat-avatar" aria-label="Assistant message">🤖</div>
                    <div class="bot-message">{message["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


    # ==================================================
    # QUESTION INPUT
    # ==================================================

    question = st.chat_input(
        "Ask a question about your PDF..."
    )


    # ==================================================
    # PROCESS QUESTION
    # ==================================================

    if question:

        # Save user question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # Display user question
        st.markdown(
            f"""
            <div class="chat-row user-row">
                <div class="user-message">{question}</div>
                <div class="chat-avatar" aria-label="User message">👤</div>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ==================================================
        # RETRIEVAL
        # ==================================================

        with st.spinner("🔎 Searching the PDF..."):

            results = (
                st.session_state.vector_store
                .similarity_search(
                    question,
                    k=2
                )
            )


        # ==================================================
        # CONTEXT
        # ==================================================

        context = "\n\n".join(
            result.page_content
            for result in results
        )


        # ==================================================
        # PROMPT
        # ==================================================

        prompt = f"""
You are a strict RAG PDF Assistant.

Answer the user's question ONLY using the PDF context
provided below.

IMPORTANT RULES:

1. Use only the PDF context.
2. Do not use outside knowledge.
3. Do not invent information.
4. Do not invent examples.
5. If the answer is not available in the PDF context,
   say exactly:

"Sorry, this information is not available in the PDF."

6. Keep the answer simple and clear.
7. Make the answer suitable for a viva.
8. For normal questions use:
   - Definition
   - Important points
   - Example only if present in the PDF.
9. For comparison questions, give clear differences.

PDF CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""


        # ==================================================
        # GROQ RESPONSE
        # ==================================================

        try:

            with st.spinner("🤖 Generating answer..."):

                response = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a strict PDF-based RAG assistant. "
                                "Answer only from the supplied context."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.1,

                    max_completion_tokens=400
                )


            # Get answer
            answer = response.choices[0].message.content


            # Save answer
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )


            # Display answer
            st.markdown(
                f"""
                <div class="chat-row bot-row">
                    <div class="chat-avatar" aria-label="Assistant message">🤖</div>
                    <div class="bot-message">{answer}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


        except Exception as e:

            st.error(
                "❌ Error while generating answer."
            )

            st.write(e)
=======
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
import tempfile
import os

from backend.rag import (
    extract_text_from_pdf,
    get_chunks,
    create_vector_store
)

from groq import Groq


# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(
    page_title="RAG PDF Chatbot",
    page_icon="📚",
    layout="wide"
)


# ==================================================
# CUSTOM CSS
# ==================================================

st.markdown("""
<style>

/* App shell */
.stApp {
    background: #0b1220;
    color: #f8fafc;
}

/* Remove Streamlit's empty top header and reclaim the space. */
header[data-testid="stHeader"] {
    display: none;
}

[data-testid="stToolbar"] {
    display: none;
}

/* Do not paint a full-width black strip behind the chat input. */
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div,
div[data-testid="stBottom"] > div > div {
    background: transparent !important;
    border-top: 0 !important;
    box-shadow: none !important;
}

div[data-testid="stBottom"] {
    position: static !important;
}

.block-container {
    max-width: 1120px;
    padding-top: 0.35rem;
    padding-bottom: 0.35rem;
}

/* Sidebar: compact, stable, and without an internal scrollbar. */
section[data-testid="stSidebar"] {
    background: #111a2d;
    border-right: 1px solid #26344d;
}

section[data-testid="stSidebar"] > div:first-child {
    height: 100vh;
    overflow: hidden;
    padding: 0.35rem 0.55rem 0.35rem;
}

section[data-testid="stSidebar"] .block-container,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.35rem;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    margin: 0.2rem 0 0.35rem;
    line-height: 1.2;
}

section[data-testid="stSidebar"] hr {
    margin: 0.45rem 0;
    border-color: #2a3850;
}

section[data-testid="stSidebar"] p {
    margin: 0.2rem 0;
}

/* This app accepts one PDF per chat. Hide Streamlit's add-more (+) control.
   The file chip's own remove (×) control remains available. */
/* Streamlit versions use different wrappers/labels for the add-more button. */
[data-testid="stFileUploader"] button[aria-label*="Add"],
[data-testid="stFileUploader"] button[title*="Add"],
[data-testid="stFileUploader"] button[aria-label*="add"],
[data-testid="stFileUploader"] button[title*="add"],
[data-testid="stFileUploader"] button[aria-label="Upload files"],
[data-testid="stFileUploader"] button[title="Upload files"] {
    display: none !important;
}

/* Compact single-file uploader. */
[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzone"] {
    min-height: 0 !important;
    height: auto !important;
    padding: 0.35rem 0.65rem !important;
    margin: 0 !important;
}

[data-testid="stFileUploader"] section {
    padding: 0 !important;
    min-height: 0 !important;
}

/* Hide the chip's tiny remove control; the large control beside the uploader
   below is the single, intentional way to remove the PDF. */
[data-testid="stFileUploader"] button[aria-label*="Remove"],
[data-testid="stFileUploader"] button[title*="Remove"],
[data-testid="stFileUploader"] button[aria-label*="remove"],
[data-testid="stFileUploader"] button[title*="remove"] {
    display: none !important;
}

/* Align the external remove control with the file chip, not the uploader label. */
.pdf-remove-button {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    padding-top: 1.9rem;
    box-sizing: border-box;
}

.pdf-remove-button button {
    min-height: 2.85rem !important;
    height: 2.85rem !important;
    width: 2.85rem !important;
    padding: 0 !important;
    font-size: 1.45rem !important;
    line-height: 1 !important;
    font-weight: 500 !important;
    border: 1px solid #40516d !important;
    background: #111c30 !important;
    color: #f8fafc !important;
    border-radius: 10px !important;
}

.pdf-remove-button button:hover {
    background: #2a3850 !important;
    border-color: #8b7cff !important;
}

.sidebar-file-card {
    background: #172238;
    border: 1px solid #2b3a54;
    border-radius: 12px;
    padding: 0.8rem 0.9rem;
    margin: 0.35rem 0 0.55rem;
}

.sidebar-file-name {
    font-weight: 700;
    overflow-wrap: anywhere;
}

.sidebar-label {
    color: #aebbd0;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.sidebar-metrics {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
    margin: 0.2rem 0;
}

.sidebar-metric {
    font-size: 0.82rem;
    color: #b8c5d9;
}

.sidebar-metric strong {
    display: block;
    color: #f8fafc;
    font-size: 1.45rem;
    font-weight: 500;
    line-height: 1.2;
    margin-top: 0.15rem;
}

/* Main content */
.title {
    text-align: center;
    font-size: clamp(2rem, 4vw, 3rem);
    font-weight: 750;
    color: #ffffff;
    margin: 0.05rem 0 0.2rem;
}

.subtitle {
    text-align: center;
    color: #9fb0c9;
    font-size: 1rem;
    margin-bottom: 0.55rem;
}

.status-box {
    padding: 0.75rem 1rem;
    border-radius: 12px;
    background: #0d302e;
    border: 1px solid #176b58;
    color: #8af0c4;
    font-weight: 600;
    margin: 0.45rem 0 0.65rem;
}

.chat-row {
    width: min(100%, 1040px);
    margin: 0.28rem auto;
    display: flex;
    align-items: flex-end;
    gap: 0.55rem;
}

.chat-row.user-row {
    justify-content: flex-end;
}

.chat-row.bot-row {
    justify-content: flex-start;
}

.chat-avatar {
    width: 1.55rem;
    height: 1.55rem;
    flex: 0 0 1.55rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background: #1b2942;
    border: 1px solid #334766;
    font-size: 0.78rem;
    line-height: 1;
}

.user-row .chat-avatar {
    order: 2;
    background: #6555dc;
    border-color: #8174ff;
}

.user-message, .bot-message {
    padding: 0.7rem 0.9rem;
    border-radius: 14px;
    margin: 0.45rem 0;
    line-height: 1.55;
}

.user-message {
    background: #243f91;
    color: #ffffff;
    margin-left: 8%;
}

.bot-message {
    background: #141f33;
    color: #e6edf7;
    border: 1px solid #2a3850;
    margin-right: 3%;
}

.chat-label {
    font-weight: 700;
    margin-bottom: 0.3rem;
    color: #ffffff;
}

/* Instagram-inspired conversation layout. */
.chat-label {
    display: flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.78rem;
    letter-spacing: 0.01em;
    color: #b8c5d9;
    margin-bottom: 0.35rem;
}

.user-message, .bot-message {
    width: fit-content;
    max-width: calc(100% - 2.15rem);
    padding: 0.62rem 0.85rem;
    border-radius: 18px;
    margin: 0;
    line-height: 1.55;
    overflow-wrap: anywhere;
    box-shadow: 0 5px 18px rgba(0,0,0,0.08);
}

.user-message {
    margin-left: 0;
    margin-right: 0;
    background: linear-gradient(135deg, #765cf6, #4c6ee8);
    color: #ffffff;
    border-bottom-right-radius: 5px;
}

.user-message .chat-label {
    color: #e9e5ff;
    justify-content: flex-end;
}

.bot-message {
    margin-left: 0;
    margin-right: 0;
    background: #141f33;
    color: #e6edf7;
    border: 1px solid #2a3850;
    border-bottom-left-radius: 5px;
}

.bot-message .chat-label {
    color: #9fb0c9;
}

/* Keep the input compact and visually attached to the conversation. */
div[data-testid="stChatInput"] {
    position: static !important;
    width: min(100%, 850px) !important;
    max-width: 850px !important;
    margin: 0.35rem auto 0 !important;
    background: transparent !important;
    border-top: 0 !important;
    padding: 0.15rem 0 0.1rem !important;
}

/* Keep the composer aligned with the conversation column instead of
   stretching across the entire main page. */
div[data-testid="stChatInput"] > div {
    width: 100% !important;
    max-width: 100% !important;
    min-height: 0 !important;
}

div[data-testid="stChatInput"] textarea {
    min-height: 2.35rem !important;
    max-height: 2.35rem !important;
    padding-top: 0.55rem !important;
    padding-bottom: 0.55rem !important;
}

div[data-testid="stChatInput"] > div {
    background: #111c30 !important;
    border: 1px solid #334766 !important;
    border-radius: 999px !important;
    padding: 0.2rem 0.35rem 0.2rem 0.9rem !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}

div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #ffffff !important;
}

div[data-testid="stChatInput"] button {
    border-radius: 999px !important;
    background: #7563f5 !important;
    color: white !important;
}

div[data-testid="stChatInput"] button:hover {
    background: #8979ff !important;
}

.stButton > button {
    background: #7563f5;
    color: white;
    border: none;
    border-radius: 9px;
    font-weight: 650;
    padding: 0.55rem 0.75rem;
}

.stButton > button:hover {
    background: #8979ff;
}


.feature-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.75rem;
    margin: 0.8rem 0 1.1rem;
}

.feature-card {
    background: #111c30;
    border: 1px solid #263752;
    border-radius: 14px;
    padding: 0.9rem;
}

.feature-icon {
    font-size: 1.35rem;
    margin-bottom: 0.35rem;
}

.feature-title {
    color: #f8fafc;
    font-weight: 750;
    font-size: 0.95rem;
}

.feature-copy {
    color: #9fb0c9;
    font-size: 0.78rem;
    line-height: 1.4;
    margin-top: 0.25rem;
}

/* Streamlit adds vertical space around each markdown element. Keep the
   conversation compact so messages read like one continuous thread. */
[data-testid="stVerticalBlock"] > [data-testid="element-container"] {
    margin-bottom: 0 !important;
}

.section-kicker {
    color: #8ea4c7;
    font-size: 0.76rem;
    font-weight: 750;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}

/* Final chat stability pass: keep the composer predictable during Streamlit reruns. */
div[data-testid="stChatInput"] {
    width: min(100%, 1040px) !important;
    max-width: 1040px !important;
    margin: 0.5rem auto 0 !important;
    padding: 0 !important;
    position: static !important;
    min-height: 0 !important;
}

div[data-testid="stChatInput"] > div {
    min-height: 0 !important;
    height: 3rem !important;
    box-sizing: border-box !important;
    padding: 0.25rem 0.35rem 0.25rem 0.9rem !important;
}

div[data-testid="stChatInput"] textarea {
    height: 2.35rem !important;
    min-height: 2.35rem !important;
    max-height: 2.35rem !important;
    line-height: 1.25 !important;
    resize: none !important;
    overflow: hidden !important;
}

/* Prevent Streamlit's rerun layout from introducing extra vertical gaps. */
div[data-testid="stChatInput"] + div,
div[data-testid="stChatInput"] ~ div {
    margin-top: 0 !important;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem 0.85rem 1rem;
    }
    .chat-row {
        width: 100%;
    }
    .user-message, .bot-message {
        max-width: calc(100% - 2.05rem);
    }
    .subtitle {
        font-size: 0.9rem;
        margin-bottom: 0.75rem;
    }
    .feature-grid {
        grid-template-columns: 1fr;
        gap: 0.55rem;
    }
}

/* Final alignment override: composer and conversation share one column. */
.chat-row {
    width: 1040px !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

div[data-testid="stChatInput"] {
    width: 1040px !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
    margin-left: auto !important;
    margin-right: auto !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}

div[data-testid="stChatInput"] > div {
    width: 100% !important;
    max-width: 100% !important;
    box-sizing: border-box !important;
}

@media (max-width: 768px) {
    .chat-row,
    div[data-testid="stChatInput"] {
        width: 100% !important;
        max-width: 100% !important;
    }
}


/* FINAL COMPOSER ALIGNMENT: match the 1040px conversation column exactly. */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] form > div {
    width: min(1040px, calc(100% - 2rem)) !important;
    max-width: 1040px !important;
    box-sizing: border-box !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

[data-testid="stChatInput"] {
    position: static !important;
    padding: 0 !important;
    margin-top: 0.55rem !important;
    margin-bottom: 0 !important;
}

[data-testid="stChatInput"] form {
    padding: 0 !important;
}

[data-testid="stChatInput"] textarea {
    width: 100% !important;
    box-sizing: border-box !important;
}

@media (max-width: 768px) {
    [data-testid="stChatInput"],
    [data-testid="stChatInput"] > div,
    [data-testid="stChatInput"] form,
    [data-testid="stChatInput"] form > div {
        width: 100% !important;
        max-width: 100% !important;
    }
}


/* FINAL STABILITY PATCH: prevent composer growth and browser scroll anchoring jumps. */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"], .block-container {
    scroll-behavior: auto !important;
    overflow-anchor: none !important;
}

/* Keep every chat row from changing width/height during a rerun. */
.chat-row {
    min-width: 0 !important;
    min-height: 0 !important;
    contain: layout style !important;
}

.chat-row .user-message,
.chat-row .bot-message {
    min-width: 0 !important;
    box-sizing: border-box !important;
}

/* One-line composer: Enter submits, it never turns into a growing textarea. */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] form,
[data-testid="stChatInput"] form > div {
    height: 3rem !important;
    min-height: 3rem !important;
    max-height: 3rem !important;
    overflow: hidden !important;
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] input {
    height: 2.35rem !important;
    min-height: 2.35rem !important;
    max-height: 2.35rem !important;
    line-height: 1.25 !important;
    padding-top: 0.55rem !important;
    padding-bottom: 0.55rem !important;
    resize: none !important;
    overflow: hidden !important;
    white-space: nowrap !important;
    field-sizing: fixed !important;
}

/* Do not animate layout changes when Streamlit reruns after Enter. */
[data-testid="stChatInput"],
[data-testid="stChatInput"] *,
.chat-row, .chat-row * {
    transition: none !important;
    animation: none !important;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# TITLE
# ==================================================

st.markdown(
    '<div class="title">📚 RAG PDF Chatbot</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions from your PDF using Retrieval-Augmented Generation'
    '</div>',
    unsafe_allow_html=True
)



# ==================================================
# GROQ API
# ==================================================

from groq import Groq
import streamlit as st

API_KEY = st.secrets["GROQ_API_KEY"]

client = Groq(api_key=API_KEY)

# ==================================================
# SESSION STATE
# ==================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

if "total_characters" not in st.session_state:
    st.session_state.total_characters = 0

if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0


# Keep a stable placeholder in the Streamlit element tree.
# Its content is decided AFTER the uploader has been evaluated, so the
# home cards disappear immediately when a file is selected.
features_placeholder = st.empty()

# ==================================================
# PDF UPLOAD
# ==================================================

if "uploader_version" not in st.session_state:
    st.session_state.uploader_version = 0

uploader_key = f"pdf_uploader_{st.session_state.uploader_version}"
upload_col, remove_col = st.columns([0.92, 0.08], gap="small")

with upload_col:
    uploaded_file = st.file_uploader(
        "📄 Upload your PDF",
        type=["pdf"],
        key=uploader_key
    )

# Render the home section using the CURRENT uploader value, not stale
# session-state data from the previous Streamlit run.
if uploaded_file is None and st.session_state.pdf_name is None and not st.session_state.messages:
    with features_placeholder.container():
        st.markdown(
            """
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">📄</div>
                    <div class="feature-title">One PDF workspace</div>
                    <div class="feature-copy">Upload one document and keep the conversation focused.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🔎</div>
                    <div class="feature-title">Grounded answers</div>
                    <div class="feature-copy">Retrieve relevant content before generating a response.</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">⚡</div>
                    <div class="feature-title">Simple chat flow</div>
                    <div class="feature-copy">Ask follow-up questions in a clean, familiar interface.</div>
                </div>
            </div>
            <div class="section-kicker">Your document workspace</div>
            """,
            unsafe_allow_html=True
        )
else:
    features_placeholder.empty()

with remove_col:
    if uploaded_file is not None:
        st.markdown('<div class="pdf-remove-button">', unsafe_allow_html=True)
        if st.button("✕", key="remove_pdf", help="Remove the current PDF"):
            # Rotate the uploader key. This is the reliable Streamlit way
            # to clear the visible file chip after a PDF is removed.
            st.session_state.uploader_version += 1
            st.session_state.pdf_name = None
            st.session_state.total_characters = 0
            st.session_state.total_chunks = 0
            st.session_state.messages = []
            st.session_state.vector_store = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ==================================================
# PROCESS UPLOADED PDF
# ==================================================

if uploaded_file is not None:

    # Check if a new PDF was uploaded
    if st.session_state.pdf_name != uploaded_file.name:

        with st.spinner("📄 Processing PDF..."):

            # Save uploaded PDF temporarily
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".pdf"
            ) as temp_file:

                temp_file.write(uploaded_file.getbuffer())

                pdf_path = temp_file.name

            try:

                # Extract text
                text = extract_text_from_pdf(pdf_path)

                # Check extracted text
                if not text.strip():
                    st.error(
                        "❌ Could not extract text from this PDF."
                    )
                    st.stop()

                # Create chunks
                chunks = get_chunks(text)

                # Create vector database
                vector_store = create_vector_store(chunks)

                # Save in session
                st.session_state.vector_store = vector_store
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.total_characters = len(text)
                st.session_state.total_chunks = len(chunks)

                # Clear previous chat
                st.session_state.messages = []

            finally:

                # Delete temporary PDF
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)

        # ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:
    st.header("📄 PDF Information")

    if st.session_state.pdf_name:
        st.markdown(
            f"""
            <div class="sidebar-file-card">
                <div class="sidebar-label">File</div>
                <div class="sidebar-file-name">{st.session_state.pdf_name}</div>
            </div>
            <div class="sidebar-metrics">
                <div class="sidebar-metric">Characters<strong>{st.session_state.total_characters:,}</strong></div>
                <div class="sidebar-metric">Chunks<strong>{st.session_state.total_chunks}</strong></div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="sidebar-file-card"><div class="sidebar-label">Status</div>'
            '<div class="sidebar-file-name">No PDF uploaded yet</div></div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.header("💡 How to use")
    st.markdown(
        """
        1. Upload a PDF.
        2. Wait for processing.
        3. Ask a question.
        4. Get an answer grounded in the PDF.
        """
    )

    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ==================================================
# CHECK PDF
# ==================================================

if st.session_state.vector_store is None:

    # Do not render a second-looking empty upload state while a file is
    # already selected and being processed. The uploader above is the only
    # upload control in the app.
    if uploaded_file is None:
        st.info("👆 Please upload a PDF to start chatting.")

else:

    # ==================================================
    # PDF STATUS
    # ==================================================

    st.markdown(
        f"""
        <div class="status-box">
            ✅ PDF Ready: {st.session_state.pdf_name}
        </div>
        """,
        unsafe_allow_html=True
    )


    # ==================================================
    # DISPLAY CHAT HISTORY
    # ==================================================

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="chat-row user-row">
                    <div class="user-message">{message["content"]}</div>
                    <div class="chat-avatar" aria-label="User message">👤</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="chat-row bot-row">
                    <div class="chat-avatar" aria-label="Assistant message">🤖</div>
                    <div class="bot-message">{message["content"]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


    # ==================================================
    # QUESTION INPUT
    # ==================================================

    question = st.chat_input(
        "Ask a question about your PDF..."
    )


    # ==================================================
    # PROCESS QUESTION
    # ==================================================

    if question:

        # Save user question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # Display user question
        st.markdown(
            f"""
            <div class="chat-row user-row">
                <div class="user-message">{question}</div>
                <div class="chat-avatar" aria-label="User message">👤</div>
            </div>
            """,
            unsafe_allow_html=True
        )


        # ==================================================
        # RETRIEVAL
        # ==================================================

        with st.spinner("🔎 Searching the PDF..."):

            results = (
                st.session_state.vector_store
                .similarity_search(
                    question,
                    k=2
                )
            )


        # ==================================================
        # CONTEXT
        # ==================================================

        context = "\n\n".join(
            result.page_content
            for result in results
        )


        # ==================================================
        # PROMPT
        # ==================================================

        prompt = f"""
You are a strict RAG PDF Assistant.

Answer the user's question ONLY using the PDF context
provided below.

IMPORTANT RULES:

1. Use only the PDF context.
2. Do not use outside knowledge.
3. Do not invent information.
4. Do not invent examples.
5. If the answer is not available in the PDF context,
   say exactly:

"Sorry, this information is not available in the PDF."

6. Keep the answer simple and clear.
7. Make the answer suitable for a viva.
8. For normal questions use:
   - Definition
   - Important points
   - Example only if present in the PDF.
9. For comparison questions, give clear differences.

PDF CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""


        # ==================================================
        # GROQ RESPONSE
        # ==================================================

        try:

            with st.spinner("🤖 Generating answer..."):

                response = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a strict PDF-based RAG assistant. "
                                "Answer only from the supplied context."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.1,

                    max_completion_tokens=400
                )


            # Get answer
            answer = response.choices[0].message.content


            # Save answer
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )


            # Display answer
            st.markdown(
                f"""
                <div class="chat-row bot-row">
                    <div class="chat-avatar" aria-label="Assistant message">🤖</div>
                    <div class="bot-message">{answer}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


        except Exception as e:

            st.error(
                "❌ Error while generating answer."
            )

            st.write(e)
>>>>>>> 0283c297be84baacc220c26ebe6b2159d1490d46
