from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Dict, Any, Tuple, Optional
from langchain_core.documents import Document
import re

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

def vector_store_exists(persist_directory="data/chroma_db"): # 
    """
    Check if a valid Chroma vector store exists at the given directory.
    
    Args:
        persist_directory (str): Path to the vector store directory
        
    Returns:
        bool: True if a valid vector store exists, False otherwise
    """
    if not os.path.exists(persist_directory):
        return False
    
    # Check if the directory is empty
    if not os.listdir(persist_directory):
        return False
    
    # Check if it's a valid ChromaDB
    try:
        embeddings = get_multilingual_embeddings()
        vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
        # Try a simple operation to validate the database
        _ = vector_store._collection.count()
        return True
    except Exception as e:
        print(f"Vector store validation failed: {e}")
        return False

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

def get_or_create_vector_store(documents, persist_directory="data/chroma_db"):
    persist_dir = Path(persist_directory)
    persist_dir.mkdir(parents=True, exist_ok=True)

    if vector_store_exists(str(persist_dir)):
        print("Loading existing vector store...")
        embeddings = get_multilingual_embeddings()
        vector_store = Chroma(
            persist_directory=str(persist_dir),
            embedding_function=embeddings
        )
        print("Vector store loaded successfully.")
    else:
        print("Creating new vector store...")
        vector_store = create_vector_store(documents, persist_directory=str(persist_dir))
        print("Vector store created successfully.")

    return vector_store

# Intent and Entity Recognition
class IntentEntityRecognizer:
    def __init__(self):
        # Define FAQ patterns based on your requirements
        self.faq_patterns = {
            # Mess and Dining
            "mess_timings": [
                r"(mess|dining|food).* (timing|schedule|hour|when|open|close)",
                r"(what|when).* (mess|dining).* (time|timing|hour|open)",
                r"(breakfast|lunch|dinner).* (time|served|available)"
            ],
            "mess_fees": [
                r"(mess|dining).* (fee|charge|cost|price|payment)",
                r"(how much|what).* (mess|dining).* (fee|charge|cost|price)"
            ],
            
            # Hostel
            "hostel_complaints": [
                r"(hostel|room|maintenance|issue|problem|complaint|report|fix)",
                r"(how|where).* (report|complain).* (hostel|maintenance|issue)"
            ],
            "hostel_fees": [
                r"(hostel|accommodation).* (fee|charge|cost|price|payment)",
                r"(how much|what).* (hostel).* (fee|charge|cost|price)"
            ],
            "hostel_rules": [
                r"(hostel).* (rule|regulation|policy|visitor|guest)",
                r"(are|is).* (visitor|guest).* (allow|permit)"
            ],
            
            # Library
            "library_hours": [
                r"(library).* (time|timing|hour|open|close|schedule)",
                r"(when|what time).* (library).* (open|close)"
            ],
            
            # ID Card
            "id_card_issue": [
                r"(id card|identity card|student id).* (duplicate|lost|missing|new|issue)",
                r"(how|where).* (get|obtain|apply).* (duplicate|new).* (id card)"
            ],
            
            # Transport
            "transport_service": [
                r"(bus|transport|shuttle).* (service|route|schedule|timing)",
                r"(is there|available).* (bus|transport).* (from|to)"
            ],
            
            # Medical
            "medical_facilities": [
                r"(medical|clinic|health|doctor|hospital).* (campus|available|facility)",
                r"(is there).* (medical|clinic|health).* (campus)"
            ],
            
            # Sports
            "sports_facilities": [
                r"(sports|game|basketball|court|field|ground).* (book|reserve|available|facility)",
                r"(how).* (book|reserve).* (sports|basketball|court|field)"
            ],
            
            # Office Hours
            "office_hours": [
                r"(admin|office).* (time|timing|hour|open|close|schedule)",
                r"(when).* (admin|office).* (open|close)"
            ],
            
            # Holidays
            "holiday_list": [
                r"(holiday|vacation|close|closed).* (diwali|festival|list|schedule)",
                r"(is).* (campus|college).* (close|closed).* (diwali|festival)"
            ],
            
            # Contacts and Helplines
            "helpline_numbers": [
                r"(helpline|number|contact|phone).* (exam|query|question|help)",
                r"(whom|who).* (call|contact).* (exam|query)"
            ],
            "department_contacts": [
                r"(contact|number|phone).* (department|cs|computer science)",
                r"(what).* (contact|number).* (department|cs)"
            ],
            "emergency_contact": [
                r"(emergency|urgent).* (number|contact|call|help)",
                r"(what).* (number|contact).* (emergency|urgent)"
            ],
            
            # Forms and Downloads
            "forms_download": [
                r"(form|download|find|get).* (exam|application|submission)",
                r"(where).* (find|download|get).* (form|application)"
            ],
            
            # Deadlines
            "important_deadlines": [
                r"(deadline|last date|due date|submit).* (form|application|fee)",
                r"(when).* (last date|deadline).* (submit|application|form)"
            ],
            
            # Admissions
            "admission_process": [
                r"(admission|apply|application).* (process|procedure|how)",
                r"(how).* (apply|application).* (admission)"
            ],
            
            # Fees and Payments
            "course_fees": [
                r"(fee|charge|cost|price).* (course|b.tech|program|structure)",
                r"(what).* (fee|charge|cost).* (course|b.tech|program)"
            ],
            "fee_payment_methods": [
                r"(fee|payment).* (method|online|cash|bank|transfer|pay)",
                r"(can i|how).* (pay|payment).* (fee|online)"
            ],
            "fee_due_dates": [
                r"(fee|payment).* (due date|last date|deadline|when)",
                r"(when).* (pay|due).* (fee|payment)"
            ],
            
            # Scholarships
            "scholarship_eligibility": [
                r"(scholarship|financial aid).* (eligible|eligibility|qualify)",
                r"(am i|are i).* (eligible|qualify).* (scholarship|financial aid)"
            ],
            "scholarship_application": [
                r"(scholarship|financial aid).* (apply|application|process|how)",
                r"(how).* (apply|application).* (scholarship|financial aid)"
            ],
            "scholarship_deadlines": [
                r"(scholarship|financial aid).* (deadline|last date|submit|when)",
                r"(when).* (last date|deadline).* (scholarship|financial aid)"
            ],
            
            # Academic Schedules
            "class_timetable": [
                r"(class|timetable|schedule).* (semester|subject|course)",
                r"(what).* (timetable|schedule).* (semester|class)"
            ],
            "exam_timetable": [
                r"(exam|test).* (timetable|schedule|date|when)",
                r"(when).* (exam|test).* (schedule|date)"
            ],
            "academic_calendar": [
                r"(academic|semester).* (calendar|schedule|start|begin|end)",
                r"(when).* (semester|academic).* (start|begin|end)"
            ],
            
            # Course Content
            "course_syllabus": [
                r"(syllabus|content|curriculum).* (course|subject|data structure)",
                r"(what).* (syllabus|content).* (course|subject|data structure)"
            ],
            
            # Exam Procedures
            "exam_registration": [
                r"(exam|test).* (register|registration|enroll|sign up)",
                r"(how).* (register|registration).* (exam|test)"
            ],
            "exam_halls": [
                r"(exam|test).* (hall|center|location|venue|where)",
                r"(where).* (exam|test).* (hall|center|location)"
            ],
            "hall_tickets": [
                r"(hall ticket|admit card|exam card).* (download|get|obtain)",
                r"(how).* (download|get).* (hall ticket|admit card)"
            ],
            
            # Grading and Results
            "grading_system": [
                r"(grading|grade|mark).* (system|calculate|method|how)",
                r"(how).* (grade|mark).* (calculate|compute)"
            ],
            "results_declaration": [
                r"(result|score|mark).* (declare|announce|publish|when)",
                r"(when).* (result|score).* (declare|announce|publish)"
            ],
            "result_revaluation": [
                r"(revaluation|rechecking|recheck|review).* (exam|result|apply)",
                r"(can i|how).* (apply|request).* (revaluation|rechecking)"
            ],
            
            # General query fallback
            "general_query": []
        }
        
        # Entity patterns
        self.entity_patterns = {
            "course_code": r"[A-Z]{2,4}\s?\d{3,4}",
            "date": r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s\d{1,2}(?:st|nd|rd|th)?,?\s\d{4}\b",
            "time": r"\b\d{1,2}:\d{2}\s?(?:AM|PM)?\b",
            "semester": r"\b(semester|sem)\s?[1-8]\b",
            "department": r"\b(CS|IT|ECE|EEE|MECH|CIVIL|chemical|physics|chemistry|maths|mathematics)\b",
            "amount": r"\$\d+(?:\.\d{2})?|\d+\s?(?:rupees|rs|USD|dollars)"
        }
    
    def add_custom_intent(self, intent_name: str, patterns: List[str]):
        """Add custom intent patterns"""
        self.faq_patterns[intent_name] = patterns
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        entities = {}
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        return entities
    
    def recognize_intent(self, text: str) -> Tuple[str, float]:
        text_lower = text.lower()
        best_intent = "general_query"
        highest_score = 0.0
        
        for intent, patterns in self.faq_patterns.items():
            # If no patterns, it's a catch-all intent
            if not patterns:
                continue
                
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                if matches:
                    # Score based on number and quality of matches
                    score = len(matches) * 0.5
                    
                    # If it's an exact match to a common phrase, boost score
                    if any(phrase in text_lower for phrase in pattern.split('|')):
                        score += 1.0
                    
                    if score > highest_score:
                        highest_score = score
                        best_intent = intent
        
        return best_intent, highest_score
    
    def process_query(self, query: str) -> Dict[str, Any]:
        intent, confidence = self.recognize_intent(query)
        entities = self.extract_entities(query)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "original_query": query
        }

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
    
    # Initialize intent recognizer
    intent_recognizer = IntentEntityRecognizer()
    
    # Create prompt template with conversation history and intent context
    prompt_template = """You are a helpful assistant for students. Use the following pieces of context, conversation history, and detected intent to answer the question at the end in the same language as the question. Maintain a semi-professional tone as we are conversing with students.

Detected Intent: {intent}
Detected Entities: {entities}

Conversation History:
{history}

Context from documents:
{context}

Question: {question}
Answer:"""
    
    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["intent", "entities", "history", "context", "question"]
    )
    
    # Create a custom function to handle the QA process
    def query_openrouter(query, context, history, intent_info):
        # Format entities for display
        entities_str = ", ".join([f"{k}: {v}" for k, v in intent_info['entities'].items()]) if intent_info['entities'] else "None"
        
        # Format the prompt with context, history, intent and question
        formatted_prompt = PROMPT.format(
            intent=intent_info['intent'],
            entities=entities_str,
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
        
        # Recognize intent and entities
        intent_info = intent_recognizer.process_query(query)
        print(f"Detected intent: {intent_info['intent']} (confidence: {intent_info['confidence']:.2f})")
        if intent_info['entities']:
            print(f"Detected entities: {intent_info['entities']}")
        
        # Retrieve relevant documents - adjust k based on intent confidence
        k_value = 5 if intent_info['confidence'] > 0.7 else 3
        retriever = vector_store.as_retriever(search_kwargs={"k": k_value})
        docs = retriever.get_relevant_documents(query)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Get conversation history
        history = memory.get_formatted_history()
        
        # Get answer from OpenRouter
        result = query_openrouter(query, context, history, intent_info)
        
        # Add to memory
        memory.add_message("User", query)
        memory.add_message("Assistant", result)
        
        return {
            "result": result,
            "source_documents": docs,
            "intent_info": intent_info
        }
    
    return qa_chain


# Interactive chat function
def interactive_chat(vector_store):
    memory = ConversationMemory(max_history=5)
    qa_chain = create_qa_chain(vector_store, memory)
    
    print("Welcome to the Student Query Chatbot!")
    print("Type 'quit' to exit, 'clear' to clear conversation history, or 'history' to view conversation history.")
    print("Type 'intent' to see available intent types.")
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
        elif query.lower() == 'intent':
            print("\nAvailable intents: course_schedule, exam_info, assignment_deadline, course_material, professor_office_hours, general_query")
            continue
        elif not query.strip():
            continue
            
        try:
            response = qa_chain({"query": query})
            print(f"\nAssistant: {response['result']}")
            
            # Show intent information for debugging
            if response['intent_info']['confidence'] > 0.7:
                print(f"\n[Detected intent: {response['intent_info']['intent']}]")
                
        except Exception as e:
            print(f"Error processing query: {e}")


# Main function
from pathlib import Path

def main():
    # Resolve script directory (where fun.py lives)
    script_dir = Path(__file__).resolve().parent

    # Always point to the data folder inside the script directory
    folderpath = script_dir / "data"

    # Debug prints so you can see what's being checked
    print("Script file:", Path(__file__).resolve())
    print("Current working dir:", Path.cwd())
    print("Looking for data folder at:", folderpath)

    # Check if folder exists
    if not folderpath.exists():
        print(f"Error: The folder '{folderpath}' does not exist.")
        print("Please create the 'data' folder inside the script directory or point folderpath elsewhere.")
        return

    # Check if folder is empty
    if not any(folderpath.iterdir()):
        print(f"Error: The folder '{folderpath}' is empty.")
        print("Please add PDF/DOCX files to the data folder.")
        return

    # Load documents (load_documents accepts a str path)
    documents = load_documents(str(folderpath))
    print(f"Loaded {len(documents)} documents from the folder.")

    # Use a chroma_db folder inside the data folder
    chroma_dir = script_dir / "data" / "chroma_db"
    vector_store = get_or_create_vector_store(documents, persist_directory=str(chroma_dir))

    # Start interactive chat
    interactive_chat(vector_store)


if __name__ == "__main__":
    main()