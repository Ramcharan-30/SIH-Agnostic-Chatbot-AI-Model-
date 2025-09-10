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
# from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()
# Check for missing API key
if not os.getenv("OPENROUTER_API_KEY"):
    print("Error: OPENROUTER_API_KEY environment variable not set. Please add it to your .env file.")
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

def get_or_create_vector_store(documents, persist_directory="data"):
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
    # Initialize OpenRouter client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    
    # Create prompt template
    prompt_template = """Use the following pieces of context to answer the question at the end in the same language as the question. Mantain a semi professional tone of chat as we are conversing with students.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context: {context}

Question: {question}
Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"]
    )
    

    # Create a custom function to handle the QA process
    def query_openrouter(query, context):
        # Format the prompt with context and question
        formatted_prompt = PROMPT.format(context=context, question=query)
        
        # Make request to OpenRouter API
        try:
            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "http://localhost",  # Optional
                    "X-Title": "RAG Chatbot",  # Optional
                },
                model="deepseek/deepseek-chat-v3.1:free",  # Using DeepSeek V3.1
                messages=[
                    {
                        "role": "user",
                        "content": formatted_prompt
                    }
                ],
                temperature=0.5
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            return f"An error occurred: {str(e)}"
    
    # Create a simple chain-like function
    def qa_chain(inputs):
        query = inputs["query"]
        
        # Retrieve relevant documents
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Get answer from OpenRouter
        result = query_openrouter(query, context)
        
        return {
            "result": result,
            "source_documents": docs
        }
    
    return qa_chain
    # # Create retrieval chain
    # qa_chain = RetrievalQA.from_chain_type(
    #     llm=llm,
    #     chain_type="stuff",
    #     retriever=vector_store.as_retriever(search_kwargs={"k": 3}),
    #     chain_type_kwargs={"prompt": PROMPT},
    #     return_source_documents=True
    # )
    
    # return qa_chain


# Main function
def main():
    # Load your document
    folderpath = 'data'
    documents = load_documents(folderpath)
    print(f"Loaded {len(documents)} documents from the folder.")

    # Create vector store
    vector_store = create_vector_store(documents)
    
    # Create QA chain
    qa_chain = create_qa_chain(vector_store)
    
    # Test with queries in different languages
    queries = [
        "Why did IIT kharagpur adminstration decide to put mid sem exam on 20th and 21th of september?",  # English
        "सभी छात्रों की मध्य सेमेस्टर परीक्षा कब होगी?",  # hindi
        "সকল শিক্ষার্থীর মিড সেমিস্টার পরীক্ষা কখন হয়?",     # bengali
        "అందరు విద్యార్థులకు మిడ్ సెమిస్టర్ పరీక్షలు ఎప్పుడు ఉంటాయి?",     # telugu
        "सगळा विद्यार्थियां री मिड सेमेस्टर री परीक्षा कद है?"   # marwari
    ]
    
    for query in queries:
        print(f"\nQuestion: {query}")
        try:
            response = qa_chain({"query": query})
            print(f"Answer: {response['result']}")
            
            # Show sources
            print("Sources:")
            for i, doc in enumerate(response['source_documents']):
                print(f"  {i+1}. {doc.metadata.get('source', 'Unknown')}, page {doc.metadata.get('page', 'N/A')}")
        except Exception as e:
            print(f"Error processing query: {e}")

if __name__ == "__main__":
    main()



