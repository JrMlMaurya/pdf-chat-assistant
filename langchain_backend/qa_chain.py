# importing necessary libraries
import os 
from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain.chat_models import init_chat_model
from langchain.prompts import PromptTemplate

# set the groq API key
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Function to create a question-answering chain using a vector store
def create_qa_chain(vectorstore):
    
    # Initialize the LLM ("llama3-8b-8192") with Groq API key
    llm = init_chat_model("llama3-8b-8192", model_provider="groq") 

    # Create a RetrievalQA chain using the LLM and vector store retriever
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
        chain_type="stuff",
        return_source_documents=True,
    )

    # return the chain
    return chain

