from dotenv import load_dotenv
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings 
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma  # Updated import
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

loader = PyPDFLoader("data/document.pdf")
documents = loader.load()

# Split documents into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = text_splitter.split_documents(documents)


embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


chroma_db = Chroma.from_documents(
    documents=chunks, 
    embedding=embeddings, 
    persist_directory="data", 
    collection_name="just_demo"
)

# Create a custom prompt template for better responses
prompt_template = """Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.
If the question is not related to the context, politely respond that you are tuned to only answer questions that are related to the context.

Context: {context}

Question: {question}
Answer in the same language as the question:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

# Create the retrieval chain
chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=chroma_db.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True
)

# Example query
query = "What is this document about?"
response = chain.invoke({"query": query})

print("Answer : ", response["result"])
# print("\nSource documents:")
# for i, doc in enumerate(response["source_documents"]):
#     print(f"Document {i+1}: {doc.metadata['source']}, page {doc.metadata.get('page', 'N/A')}")