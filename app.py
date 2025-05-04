# import necessary libraries
import streamlit as st
import os
import base64
import tempfile
import hashlib
from datetime import datetime
from streamlit.components.v1 import html
from langchain_backend.document_loader import process_pdf
from langchain_backend.qa_chain import create_qa_chain

# Function to display PDF in Streamlit
def display_pdf_from_bytes(file_bytes):
    base64_pdf = base64.b64encode(file_bytes).decode("utf-8")
    pdf_display = f"""
        <iframe 
            src="data:application/pdf;base64,{base64_pdf}" 
            width="100%" 
            height="100%" 
            type="application/pdf" 
            style="height:100vh; width:100%">
        </iframe>
    """
    st.sidebar.markdown(pdf_display, unsafe_allow_html=True)

# Set the page configuration
st.set_page_config(page_title="PDF Document Query Application", layout="wide")

# Initialize session state variables
if 'chat' not in st.session_state:
    st.session_state.chat = []

# if 'last_file_hash' not in st.session_state:
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None

# Set the title and icon
st.title("📄 Chat with your Document")

# Function to get the hash of the uploaded file
def get_file_hash(file_bytes):
    return hashlib.md5(file_bytes).hexdigest()

# upload the PDF file
uploaded_file = st.sidebar.file_uploader("Upload your PDF", type="pdf")

# Check if a file is uploaded
if uploaded_file:
    file_bytes = uploaded_file.read()
    file_hash = get_file_hash(file_bytes)
    st.sidebar.markdown("### 📄 PDF Preview")
    display_pdf_from_bytes(file_bytes)

    # Check if the file hash is different from the last uploaded file
    if st.session_state.get("last_file_hash") != file_hash:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # Process the PDF and create a vector database
        with st.spinner("Processing PDF..."):
            vectordb = process_pdf(tmp_path)
            st.session_state.qa_chain = create_qa_chain(vectordb)
            st.session_state.last_file_hash = file_hash
            st.sidebar.success("PDF uploaded and processed!")


st.subheader("Ask a question about your PDF")

# Check if the QA chain is available
if st.session_state.qa_chain:
    # Create a text input for the user to ask questions
    query = st.text_input("Your question", placeholder="Ask your question here...", label_visibility="hidden")

    left, middle, right = st.columns(3)
    if middle.button("Ask Question", icon="🤔", use_container_width=True) and query.strip():
        answer = st.session_state.qa_chain.invoke(query)
        sources = answer.get("source_documents", [])
        source_texts = "\n\n".join(
            f"🔹 {doc.page_content.strip()[:500]}..." for doc in sources
        )

        st.session_state.chat.append({"user": query,
                                       "ai": answer["result"],
                                       "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                       "sources": source_texts
                                        })
                        
    # Display the chat history
    for chat in reversed(st.session_state.chat[-5:]):
        with st.chat_message("user"):
            st.markdown(chat["user"])
            st.markdown(
                f"<div style='text-align: right; color: gray; font-size: 0.8em;'>{chat['timestamp']}</div>",
                unsafe_allow_html=True
            )
        with st.chat_message("assistant"):
            st.markdown(chat["ai"])
            if "sources" in chat:
                with st.expander("🧠 View sources"):
                    st.markdown(chat["sources"])
            st.markdown(
                f"<div style='text-align: right; color: gray; font-size: 0.8em;'>{chat['timestamp']}</div>",
                unsafe_allow_html=True
            )

else:
    st.info("Upload a PDF to get started.")
