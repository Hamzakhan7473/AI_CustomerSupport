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

# Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Error: GOOGLE_API_KEY not found in your .env file.")
genai.configure(api_key=GOOGLE_API_KEY)

# Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("Error: PINECONE_API_KEY not found in your .env file.")
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# --- 2. Tool Definition and Schema ---
def create_support_ticket(email: str, issue_description: str) -> str:
    """Creates a new support ticket for a user."""
    ticket_id = f"TICKET-{random.randint(1000, 9999)}"
    print(f"--- TICKET CREATED: {ticket_id} for {email} ---")
    return f"Support ticket {ticket_id} has been successfully created for {email}."

# This is the full, correct definition that replaces the placeholder.
create_ticket_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="create_support_ticket",
            description="Creates a support ticket when a user has a problem that needs human intervention.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "email": {"type": "STRING", "description": "The user's email address."},
                    "issue_description": {"type": "STRING", "description": "A detailed summary of the user's problem."}
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

# --- 5. API Data Models ---
class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

class TicketRequest(BaseModel):
    email: str
    issue_description: str

class VapiConfigResponse(BaseModel):
    publicKey: str
    assistantId: str

class VapiWebhookRequest(BaseModel):
    message: dict

# --- 6. API Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def answer_query(request: QueryRequest):
    """Handles conversational text queries using RAG and tools."""
    try:
        query_embedding = genai.embed_content(model=embedding_model, content=request.query)['embedding']
        query_results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        context = "\n\n".join([match['metadata'].get('text', '') for match in query_results['matches']])
        
        prompt = f"Context: {context}\n\nQuestion: {request.query}"
        
        chat = llm.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt)

        final_text = "".join(part.text for part in response.parts if part.text)
        
        if not final_text:
            final_text = "I've processed your request with one of my tools. How else can I help?"

        return QueryResponse(answer=final_text)
    except Exception as e:
        print(f"Error in /query endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.post("/create-ticket", summary="Create a support ticket directly")
async def create_ticket_endpoint(request: TicketRequest):
    """Handles direct ticket creation from a form."""
    try:
        confirmation_message = create_support_ticket(
            email=request.email,
            issue_description=request.issue_description
        )
        return {"message": confirmation_message}
    except Exception as e:
        print(f"Error in /create-ticket endpoint: {e}")
        raise HTTPException(status_code=500, detail="Failed to create support ticket.")

@app.get("/api/vapi-config", response_model=VapiConfigResponse)
async def get_vapi_config():
    """Provides the frontend with the necessary Vapi keys."""
    vapi_public_key = os.getenv("VAPI_PUBLIC_KEY")
    vapi_assistant_id = os.getenv("VAPI_ASSISTANT_ID")
    if not vapi_public_key or not vapi_assistant_id:
        raise HTTPException(status_code=500, detail="Vapi configuration missing on server.")
    return VapiConfigResponse(publicKey=vapi_public_key, assistantId=vapi_assistant_id)

@app.post("/api/vapi")
async def handle_vapi_webhook(request: VapiWebhookRequest):
    """Handles all incoming webhooks from Vapi for voice calls."""
    if request.message.get("type") == "assistant-request":
        last_user_message = request.message['messages'][-1]['content']
        try:
            query_embedding = genai.embed_content(model=embedding_model, content=last_user_message)['embedding']
            query_results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
            context = "\n\n".join([match['metadata'].get('text', '') for match in query_results['matches']])
            
            prompt = f"Context: {context}\n\nQuestion: {last_user_message}"
            
            chat = llm.start_chat(enable_automatic_function_calling=True)
            response = chat.send_message(prompt)
            
            final_text = "".join(part.text for part in response.parts if part.text)
            return {"message": {"role": "assistant", "content": final_text}}
        except Exception as e:
            print(f"Error processing Vapi request: {e}")
            return {"message": {"role": "assistant", "content": "I'm sorry, an error occurred."}}
    return {}
