from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from langchain_core.documents import Document

# Embeddings - Using Hugging Face multilingual model
from langchain_community.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv
import os

# Vector store
from langchain_community.vectorstores import Chroma

# LLM for question answering (still using OpenAI for this part)
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()
# Check for missing API key
if not os.getenv("OPENAI_API_KEY"):
    print("Error: OPENAI_API_KEY environment variable not set. Please add it to your .env file.")
    exit(1)


def load_documents(folder_path: str) -> List[Document]:
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif filename.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            print(f"Unsupported file type: {filename}")
            continue
        documents.extend(loader.load())
    return documents

def get_multilingual_embeddings():
    # Using a popular multilingual model
    model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},  # Use 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True}
    )
    return embeddings

def create_vector_store(documents, persist_directory="data/chroma_db"):
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"Split the documents into {len(chunks)} chunks.")
    # Create embeddings
    embeddings = get_multilingual_embeddings()
    
    # Create vector store
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    return vector_store

def get_or_create_vector_store(documents, persist_directory="data/chroma_db"):
    # If the directory exists and is not empty, load the vector store
    if os.path.exists(persist_directory) and os.listdir(persist_directory):
        print("Loading existing vector store...")
        embeddings = get_multilingual_embeddings()
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    else:
        print("Creating new vector store...")
        vector_store = create_vector_store(documents, persist_directory)
    return vector_store

# Create QA chain
def create_qa_chain(vector_store):
    # Initialize LLM for answering (using OpenAI but you could use a local model too)
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",
        temperature=0.5,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Create prompt template
    prompt_template = """Use the following pieces of context to answer the question at the end in the same language as the question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}
Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"]
    )
    
    # Create retrieval chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    
    return qa_chain


# Main function
def main():
    # Load your document
    folderpath = 'data'
    documents = load_documents(folderpath)
    print(f"Loaded {len(documents)} documents from the folder.")

    # Create vector store
    vector_store = get_or_create_vector_store(documents)
    
    # Create QA chain
    qa_chain = create_qa_chain(vector_store)
    
    # Test with queries in different languages
    queries = [
        "When do all students have mid semester examination?",  # English
        "सभी छात्रों की मध्य सेमेस्टर परीक्षा कब होगी?",  # hindi
        "সকল শিক্ষার্থীর মিড সেমিস্টার পরীক্ষা কখন হয়?",     # bengali
        "అందరు విద్యార్థులకు మిడ్ సెమిస్టర్ పరీక్షలు ఎప్పుడు ఉంటాయి?",     # telugu
        "सगळा विद्यार्थियां री मिड सेमेस्टर री परीक्षा कद है?"   # marwari
    ]
    
    for query in queries:
        print(f"\nQuestion: {query}")
        try:
            response = qa_chain.invoke({"query": query})
            print(f"Answer: {response['result']}")
            
            # Show sources
            print("Sources:")
            for i, doc in enumerate(response['source_documents']):
                print(f"  {i+1}. {doc.metadata.get('source', 'Unknown')}, page {doc.metadata.get('page', 'N/A')}")
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()



