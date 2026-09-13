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

.stApp {
    background: #0f172a;
    color: #f8fafc;
}

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

/* Title */

.title {
    text-align: center;
    font-size: 40px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 16px;
    margin-bottom: 30px;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: #111827;
}

section[data-testid="stSidebar"] * {
    color: #e5e7eb;
}

/* PDF status */

.status-box {
    padding: 12px;
    border-radius: 10px;
    background: #123c2a;
    text-align: center;
    color: #86efac;
    font-weight: 600;
    margin-bottom: 25px;
}

/* User message */

.user-message {
    background: #1e3a8a;
    color: #ffffff;
    padding: 14px 18px;
    border-radius: 15px;
    margin: 10px 0 10px 15%;
}

/* Bot message */

.bot-message {
    background: #1e293b;
    color: #e2e8f0;
    padding: 16px 20px;
    border-radius: 15px;
    margin: 10px 15% 10px 0;
    border: 1px solid #334155;
}

/* Chat labels */

.chat-label {
    font-weight: 700;
    margin-bottom: 7px;
    color: #ffffff;
}

/* Input */

div[data-testid="stChatInput"] {
    background: #1e293b;
}

div[data-testid="stChatInput"] textarea {
    background: #1e293b;
    color: #ffffff;
}

/* Buttons */

.stButton > button {
    background: #4f46e5;
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

.stButton > button:hover {
    background: #6366f1;
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


# ==================================================
# PDF UPLOAD
# ==================================================

uploaded_file = st.file_uploader(
    "📄 Upload your PDF",
    type=["pdf"]
)


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

        st.success("✅ PDF loaded successfully!")


# ==================================================
# CHECK PDF
# ==================================================

if st.session_state.vector_store is None:

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
    # SIDEBAR
    # ==================================================

    with st.sidebar:

        st.header("📄 PDF Information")

        st.write(
            f"**File:** {st.session_state.pdf_name}"
        )

        st.write(
            f"**Characters:** {st.session_state.total_characters}"
        )

        st.write(
            f"**Chunks:** {st.session_state.total_chunks}"
        )

        st.divider()

        st.header("💡 How to use")

        st.write(
            """
            1. Upload a PDF.
            2. Wait for processing.
            3. Enter your question.
            4. RAG searches relevant PDF content.
            5. Groq generates the answer.
            """
        )

        st.divider()

        if st.button(
            "🗑️ Clear Chat",
            use_container_width=True
        ):

            st.session_state.messages = []

            st.rerun()


    # ==================================================
    # DISPLAY CHAT HISTORY
    # ==================================================

    for message in st.session_state.messages:

        if message["role"] == "user":

            st.markdown(
                f"""
                <div class="user-message">
                    <div class="chat-label">👤 You</div>
                    {message["content"]}
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.markdown(
                f"""
                <div class="bot-message">
                    <div class="chat-label">🤖 RAG Assistant</div>
                    {message["content"]}
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
            <div class="user-message">
                <div class="chat-label">👤 You</div>
                {question}
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
                <div class="bot-message">
                    <div class="chat-label">🤖 RAG Assistant</div>
                    {answer}
                </div>
                """,
                unsafe_allow_html=True
            )


        except Exception as e:

            st.error(
                "❌ Error while generating answer."
            )

            st.write(e)
