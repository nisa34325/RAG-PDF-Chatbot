<<<<<<< HEAD
from rag import extract_text_from_pdf, get_chunks, create_vector_store
from groq import Groq


# ==========================================
# 1. PDF PATH
# ==========================================

pdf_path = r"C:\Users\Nisa\Downloads\DBMSRag.pdf"


# ==========================================
# 2. GROQ API KEY
# ==========================================

import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ==========================================
# 3. LOAD PDF
# ==========================================

print("Loading PDF...")

text = extract_text_from_pdf(pdf_path)

print("PDF loaded successfully!")
print("Total characters:", len(text))


# ==========================================
# 4. CREATE CHUNKS
# ==========================================

chunks = get_chunks(text)

print("Total chunks:", len(chunks))


# ==========================================
# 5. CREATE VECTOR DATABASE
# ==========================================

print("\nCreating vector database...")

vector_store = create_vector_store(chunks)

print("Vector database created successfully!")


# ==========================================
# 6. START CHATBOT
# ==========================================

print("\n===================================")
print("          DBMS RAG CHATBOT")
print("===================================")

print("Ask questions from your PDF.")
print("Type 'exit' to stop.")


# ==========================================
# 7. CHAT LOOP
# ==========================================

while True:

    question = input("\nYou: ").strip()


    # ======================================
    # EXIT
    # ======================================

    if question.lower() == "exit":

        print("Goodbye!")

        break


    # ======================================
    # EMPTY QUESTION
    # ======================================

    if not question:

        print("Please enter a question.")

        continue


    # ======================================
    # RETRIEVE RELEVANT CHUNKS
    # ======================================

    results = vector_store.similarity_search(
        question,
        k=2
    )


    # ======================================
    # CREATE CONTEXT
    # ======================================

    context = "\n\n".join(
        result.page_content
        for result in results
    )


    # ======================================
    # CREATE PROMPT
    # ======================================

    prompt = f"""
You are a DBMS Viva Assistant.

Answer the user's question ONLY using the information
provided in the PDF context.

IMPORTANT RULES:

1. Do NOT use outside knowledge.
2. Do NOT add information that is not present in the PDF.
3. Do NOT invent examples.
4. If the answer is not available in the PDF context,
   say exactly:

"Sorry, this information is not available in the PDF."

5. Keep the answer simple and suitable for a viva.
6. For normal questions, use:
   - Definition
   - Important points
   - Example only if available in the PDF.
7. For comparison questions, give clear differences.

PDF CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""


    # ======================================
    # SEND REQUEST TO GROQ
    # ======================================

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict DBMS viva assistant. "
                        "Use only the provided PDF context."
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


        # ==================================
        # GET ANSWER
        # ==================================

        answer = response.choices[0].message.content

        print("\nBot:")
        print(answer)


    # ======================================
    # ERROR HANDLING
    # ======================================

    except Exception as e:

        print("\nError while generating answer:")
        print(e)
=======
from rag import extract_text_from_pdf, get_chunks, create_vector_store
from groq import Groq


# ==========================================
# 1. PDF PATH
# ==========================================

pdf_path = r"C:\Users\Nisa\Downloads\DBMSRag.pdf"


# ==========================================
# 2. GROQ API KEY
# ==========================================

import os
from groq import Groq

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ==========================================
# 3. LOAD PDF
# ==========================================

print("Loading PDF...")

text = extract_text_from_pdf(pdf_path)

print("PDF loaded successfully!")
print("Total characters:", len(text))


# ==========================================
# 4. CREATE CHUNKS
# ==========================================

chunks = get_chunks(text)

print("Total chunks:", len(chunks))


# ==========================================
# 5. CREATE VECTOR DATABASE
# ==========================================

print("\nCreating vector database...")

vector_store = create_vector_store(chunks)

print("Vector database created successfully!")


# ==========================================
# 6. START CHATBOT
# ==========================================

print("\n===================================")
print("          DBMS RAG CHATBOT")
print("===================================")

print("Ask questions from your PDF.")
print("Type 'exit' to stop.")


# ==========================================
# 7. CHAT LOOP
# ==========================================

while True:

    question = input("\nYou: ").strip()


    # ======================================
    # EXIT
    # ======================================

    if question.lower() == "exit":

        print("Goodbye!")

        break


    # ======================================
    # EMPTY QUESTION
    # ======================================

    if not question:

        print("Please enter a question.")

        continue


    # ======================================
    # RETRIEVE RELEVANT CHUNKS
    # ======================================

    results = vector_store.similarity_search(
        question,
        k=2
    )


    # ======================================
    # CREATE CONTEXT
    # ======================================

    context = "\n\n".join(
        result.page_content
        for result in results
    )


    # ======================================
    # CREATE PROMPT
    # ======================================

    prompt = f"""
You are a DBMS Viva Assistant.

Answer the user's question ONLY using the information
provided in the PDF context.

IMPORTANT RULES:

1. Do NOT use outside knowledge.
2. Do NOT add information that is not present in the PDF.
3. Do NOT invent examples.
4. If the answer is not available in the PDF context,
   say exactly:

"Sorry, this information is not available in the PDF."

5. Keep the answer simple and suitable for a viva.
6. For normal questions, use:
   - Definition
   - Important points
   - Example only if available in the PDF.
7. For comparison questions, give clear differences.

PDF CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""


    # ======================================
    # SEND REQUEST TO GROQ
    # ======================================

    try:

        response = client.chat.completions.create(

            model="openai/gpt-oss-20b",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict DBMS viva assistant. "
                        "Use only the provided PDF context."
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


        # ==================================
        # GET ANSWER
        # ==================================

        answer = response.choices[0].message.content

        print("\nBot:")
        print(answer)


    # ======================================
    # ERROR HANDLING
    # ======================================

    except Exception as e:

        print("\nError while generating answer:")
        print(e)
>>>>>>> 0283c297be84baacc220c26ebe6b2159d1490d46
