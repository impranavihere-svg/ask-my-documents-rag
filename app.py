import os

import gradio as gr
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini"
)


# ---------------------------------------------------------
# GLOBAL VECTOR DATABASE
# ---------------------------------------------------------

vector_store = None


# ---------------------------------------------------------
# EMBEDDING MODEL
# ---------------------------------------------------------

embeddings = FastEmbedEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)



# ---------------------------------------------------------
# PROCESS DOCUMENTS
# ---------------------------------------------------------

def process_documents(files):

    global vector_store

    if not files:
        return "❌ Please upload at least one PDF document."

    try:

        all_documents = []

        # 1. Load PDF documents
        for file in files:

            loader = PyPDFLoader(file)

            documents = loader.load()

            all_documents.extend(documents)

        if not all_documents:
            return "❌ No text could be extracted from the uploaded documents."

        # 2. Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120
        )

        chunks = text_splitter.split_documents(all_documents)

        if not chunks:
            return "❌ No text chunks were created."

        # 3. Create embeddings and store in FAISS
        vector_store = FAISS.from_documents(
            chunks,
            embeddings
        )

        # Count pages
        page_count = len(all_documents)

        # Count documents
        document_count = len(files)

        return (
            "✅ Documents processed successfully!\n\n"
            f"📄 Documents: {document_count}\n"
            f"📑 Pages: {page_count}\n"
            f"🧩 Chunks created: {len(chunks)}"
        )

    except Exception as e:

        return f"❌ Error while processing documents:\n{str(e)}"


# ---------------------------------------------------------
# ASK QUESTION
# ---------------------------------------------------------

def ask_question(question):

    global vector_store

    if vector_store is None:

        return (
            "Please upload and process at least one document "
            "before asking a question.",
            ""
        )

    if not question or not question.strip():

        return (
            "Please enter a question.",
            ""
        )

    if not OPENROUTER_API_KEY:

        return (
            "❌ OpenRouter API key is missing. "
            "Please configure the .env file.",
            ""
        )

    try:

        # 1. Retrieve top 4 relevant chunks
        retrieved_documents = vector_store.similarity_search(
            question,
            k=4
        )

        if not retrieved_documents:

            return (
                "I could not find this information in the uploaded documents.",
                ""
            )

        # 2. Create context from retrieved chunks
        context_parts = []

        for i, document in enumerate(retrieved_documents):

            source = document.metadata.get(
                "source",
                "Unknown"
            )

            page = document.metadata.get(
                "page",
                0
            )

            context_parts.append(
                f"""
SOURCE {i + 1}
File: {os.path.basename(source)}
Page: {page + 1}

Content:
{document.page_content}
"""
            )

        context = "\n".join(context_parts)

        # 3. Create grounded prompt
        prompt = f"""
You are a document-based question answering assistant.

Answer the user's question using ONLY the information
provided in the retrieved document context below.

If the answer cannot be found in the context, say:

"I could not find this information in the uploaded documents."

Do not use your general knowledge.
Do not invent facts.
Do not make unsupported claims.

Give a concise and clear answer.

-------------------------
RETRIEVED DOCUMENT CONTEXT
-------------------------

{context}

-------------------------
USER QUESTION
-------------------------

{question}

-------------------------
ANSWER
-------------------------
"""

        # 4. Connect to OpenRouter
        llm = ChatOpenAI(
            model=OPENROUTER_MODEL,
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            temperature=0
        )

        # 5. Generate answer
        response = llm.invoke(prompt)

        answer = response.content

        # 6. Display retrieved sources
        sources = "### Retrieved Sources\n\n"

        for i, document in enumerate(retrieved_documents):

            source = document.metadata.get(
                "source",
                "Unknown"
            )

            page = document.metadata.get(
                "page",
                0
            )

            sources += (
                f"**Source {i + 1}**\n\n"
                f"**File:** {os.path.basename(source)}  \n"
                f"**Page:** {page + 1}  \n\n"
                f"**Relevant Content:**\n"
                f"{document.page_content}\n\n"
                f"---\n\n"
            )

        return answer, sources

    except Exception as e:

        return (
            f"❌ Error while generating the answer:\n{str(e)}",
            ""
        )


# ---------------------------------------------------------
# GRADIO USER INTERFACE
# ---------------------------------------------------------

with gr.Blocks(
    title="Ask My Documents – RAG Assistant"
) as demo:

    gr.Markdown(
        """
        # 📚 Ask My Documents
        ### Simple Retrieval-Augmented Generation (RAG) Assistant

        Upload your PDF documents, process them, and ask questions
        based only on the information contained in your documents.
        """
    )

    gr.Markdown("## 📄 1. Upload Documents")

    pdf_files = gr.File(
        label="Upload PDF Documents",
        file_count="multiple",
        file_types=[".pdf"],
        type="filepath"
    )

    process_button = gr.Button(
        "⚙️ Process Documents",
        variant="primary"
    )

    status_box = gr.Markdown(
        "Status: Waiting for documents..."
    )

    process_button.click(
        fn=process_documents,
        inputs=pdf_files,
        outputs=status_box
    )

    gr.Markdown("---")

    gr.Markdown("## 💬 2. Ask a Question")

    question_box = gr.Textbox(
        label="Ask a question about your documents",
        placeholder="Example: What are the course outcomes?",
        lines=2
    )

    ask_button = gr.Button(
        "🔍 ASK",
        variant="primary"
    )

    gr.Markdown("## 🧠 ANSWER")

    answer_box = gr.Markdown(
        "Your answer will appear here."
    )

    gr.Markdown("## 📚 SOURCES")

    sources_box = gr.Markdown(
        "Retrieved document sources will appear here."
    )

    ask_button.click(
        fn=ask_question,
        inputs=question_box,
        outputs=[answer_box, sources_box]
    )


# ---------------------------------------------------------
# START APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860
    )