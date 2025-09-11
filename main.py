from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
from langchain_core.documents import Document

# Embeddings - Using Hugging Face multilingual model
from langchain_community.embeddings import HuggingFaceEmbeddings

from dotenv import load_dotenv
import os

# Vector store
from langchain_community.vectorstores import Chroma

# LLM for question answering
from openai import OpenAI
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
            loaded_docs = loader.load()
            # Add metadata: filename and page number
            for i, doc in enumerate(loaded_docs):
                doc.metadata["source"] = filename
                doc.metadata["page"] = i + 1  # Page numbers start at 1
            documents.extend(loaded_docs)
        elif filename.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
            loaded_docs = loader.load()
            # Add metadata: filename (no page info for docx)
            for doc in loaded_docs:
                doc.metadata["source"] = filename
            documents.extend(loaded_docs)
        else:
            print(f"Unsupported file type: {filename}")
            continue
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

# Conversation memory management
class ConversationMemory:
    def __init__(self, max_history=10):
        self.history = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        # Keep only the most recent messages
        if len(self.history) > self.max_history * 2:  # *2 because we have both user and assistant messages
            self.history = self.history[-self.max_history * 2:]
    
    def get_formatted_history(self):
        formatted_history = []
        for message in self.history:
            formatted_history.append(f"{message['role']}: {message['content']}")
        return "\n".join(formatted_history)
    
    def clear_history(self):
        self.history = []

# Create QA chain with memory
def create_qa_chain(vector_store, memory):
    # Initialize OpenRouter client
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )
    
    # Create prompt template with conversation history
    prompt_template = """You are a helpful assistant for students. Use the following pieces of context and conversation history to answer the question at the end in the same language as the question. Maintain a semi-professional tone as we are conversing with students.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Conversation History:
{history}

Context from documents:
{context}

Question: {question}
Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["history", "context", "question"]
    )
    
    # Create a custom function to handle the QA process
    def query_openrouter(query, context, history):
        # Format the prompt with context, history and question
        formatted_prompt = PROMPT.format(
            history=history,
            context=context, 
            question=query
        )
        
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
        
        # Get conversation history
        history = memory.get_formatted_history()
        
        # Get answer from OpenRouter
        result = query_openrouter(query, context, history)
        
        # Add to memory
        memory.add_message("User", query)
        memory.add_message("Assistant", result)
        
        return {
            "result": result,
            "source_documents": docs
        }
    
    return qa_chain


# Interactive chat function
def interactive_chat(vector_store):
    memory = ConversationMemory(max_history=5)
    qa_chain = create_qa_chain(vector_store, memory)
    
    print("Welcome to the Student Query Chatbot!")
    print("Type 'quit' to exit, 'clear' to clear conversation history, or 'history' to view conversation history.")
    print("You can ask questions in multiple languages.")
    print("-" * 50)
    
    while True:
        query = input("\nYou: ")
        
        if query.lower() == 'quit':
            print("Goodbye!")
            break
        elif query.lower() == 'clear':
            memory.clear_history()
            print("Conversation history cleared.")
            continue
        elif query.lower() == 'history':
            print("\nConversation History:")
            print(memory.get_formatted_history())
            continue
        elif not query.strip():
            continue
            
        try:
            response = qa_chain({"query": query})
            print(f"\nAssistant: {response['result']}")
            
            # Optionally show sources (can be toggled with a command if desired)
            # print("\nSources:")
            # for i, doc in enumerate(response['source_documents']):
            #     print(f"  {i+1}. {doc.metadata.get('source', 'Unknown')}, page {doc.metadata.get('page', 'N/A')}")
                
        except Exception as e:
            print(f"Error processing query: {e}")


# Main function
def main():
    # Load your document
    folderpath = 'data'
    documents = load_documents(folderpath)
    print(f"Loaded {len(documents)} documents from the folder.")

    # Create vector store
    vector_store = create_vector_store(documents)
    
    # Start interactive chat
    interactive_chat(vector_store)

if __name__ == "__main__":
    main()