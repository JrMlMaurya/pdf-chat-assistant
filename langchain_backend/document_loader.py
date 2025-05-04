# importing the necessary libraries
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# function to process the PDF file and create a vector database
def process_pdf(file_path: str):
    # Load the PDF file
    loader = PyPDFLoader(file_path)
    docs = loader.load()

    # Split the documents into smaller chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    # Create embeddings for the chunks
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(chunks, embeddings)

    # return the vector database
    return vectordb
