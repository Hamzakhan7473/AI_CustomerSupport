# /backend/src/main.py

import os
import random
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from pinecone import Pinecone
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai.types import FunctionDeclaration, Tool

# --- 1. Load Environment and Configure Services ---
load_dotenv()
# (Keep your existing Google and Pinecone configuration here)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)


# --- 2. Tool Definition and Schema ---
def create_support_ticket(email: str, issue_description: str) -> str:
    """Creates a new support ticket for a user."""
    ticket_id = f"TICKET-{random.randint(1000, 9999)}"
    return f"Support ticket {ticket_id} has been successfully created for {email}."

create_ticket_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="create_support_ticket",
            description="Creates a support ticket for a user.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "email": {"type": "STRING", "description": "The user's email address."},
                    "issue_description": {"type": "STRING", "description": "A summary of the user's problem."}
                },
                "required": ["email", "issue_description"]
            }
        )
    ]
)


# --- 3. FastAPI App and Middleware Setup ---
app = FastAPI(title="Aven Support Agent - Voice & Chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Initialize Global Clients ---
INDEX_NAME = "aven-support-agent"
llm = genai.GenerativeModel('gemini-1.5-pro-latest', tools=[create_ticket_tool])
embedding_model = "models/text-embedding-004"
index = pinecone_client.Index(INDEX_NAME)


# --- 5. VAPI-SPECIFIC DATA MODELS & ENDPOINT ---
# These models match the structure of the webhooks Vapi will send.
class VapiWebhookRequest(BaseModel):
    message: dict

@app.post("/api/vapi")
async def handle_vapi_webhook(request: VapiWebhookRequest):
    """
    Handles all incoming webhooks from Vapi and generates a response.
    """
    message_type = request.message.get("type")
    
    # This is the main request type where Vapi asks for the assistant's next turn.
    if message_type == "assistant-request":
        # The last message in the list is the user's most recent input.
        last_user_message = request.message['messages'][-1]['content']
        
        print(f"--- Vapi Request | User: '{last_user_message}' ---")
        
        try:
            # Reuse our RAG logic
            query_embedding = genai.embed_content(model=embedding_model, content=last_user_message)['embedding']
            query_results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
            context = "\n\n".join([match['metadata'].get('text', '') for match in query_results['matches']])
            
            prompt = f"Context: {context}\n\nQuestion: {last_user_message}"
            
            # Use the chat session for robust function calling
            chat = llm.start_chat(enable_automatic_function_calling=True)
            response = chat.send_message(prompt)
            
            # Send the text response back to Vapi
            return {"message": {"role": "assistant", "content": response.text}}

        except Exception as e:
            print(f"Error processing Vapi request: {e}")
            return {"message": {"role": "assistant", "content": "I'm sorry, I encountered an error."}}

    # You can add handlers for other Vapi message types here (e.g., 'hang-up').
    return {}


# --- 6. Existing Endpoints for Text-Based Chat ---
# (Your existing /query and /create-ticket endpoints remain here)
class QueryRequest(BaseModel):
    query: str
class QueryResponse(BaseModel):
    answer: str
class TicketRequest(BaseModel):
    email: str
    issue_description: str

@app.post("/query", response_model=QueryResponse)
async def answer_query(request: QueryRequest):
    # ... (existing implementation)
    pass

@app.post("/create-ticket")
async def create_ticket_endpoint(request: TicketRequest):
    # ... (existing implementation)
    pass
