import os
import random
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from pinecone import Pinecone

# --- 1. Load Environment Variables ---
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

if not GOOGLE_API_KEY:
    raise ValueError("Missing GOOGLE_API_KEY in .env")
if not PINECONE_API_KEY:
    raise ValueError("Missing PINECONE_API_KEY in .env")

genai.configure(api_key=GOOGLE_API_KEY)
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# --- 2. Define Tool Function ---
def create_support_ticket(email: str, issue_description: str) -> str:
    ticket_id = f"TICKET-{random.randint(1000, 9999)}"
    print(f"✅ TICKET CREATED: {ticket_id} for {email}")
    return f"Support ticket {ticket_id} has been created for {email}."

create_ticket_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="create_support_ticket",
            description="Create a support ticket when a user needs human help.",
            parameters={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User's email address"},
                    "issue_description": {"type": "string", "description": "Summary of the user's problem"}
                },
                "required": ["email", "issue_description"]
            }
        )
    ]
)

# --- 3. FastAPI Setup ---
app = FastAPI(title="Aven Support Agent - Voice & Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 4. Models & Config ---
INDEX_NAME = "aven-support-agent"
llm = genai.GenerativeModel('gemini-1.5-pro-latest', tools=[create_ticket_tool])
embedding_model = "models/text-embedding-004"
index = pinecone_client.Index(INDEX_NAME)

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

# --- 5. Endpoints ---

@app.post("/query", response_model=QueryResponse)
async def answer_query(request: QueryRequest):
    try:
        query_embedding = genai.embed_content(model=embedding_model, content=request.query)['embedding']
        query_results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        context = "\n\n".join([match['metadata'].get('text', '') for match in query_results['matches']])
        prompt = f"Context: {context}\n\nQuestion: {request.query}"

        chat = llm.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt)
        final_text = "".join(part.text for part in response.parts if part.text)

        return QueryResponse(answer=final_text or "Processed your request with tools. What else can I help with?")
    except Exception as e:
        print("❌ Error in /query:", e)
        raise HTTPException(status_code=500, detail="Internal error during query.")

@app.post("/create-ticket")
async def create_ticket_endpoint(request: TicketRequest):
    try:
        message = create_support_ticket(request.email, request.issue_description)
        return {"message": message}
    except Exception as e:
        print("❌ Error in /create-ticket:", e)
        raise HTTPException(status_code=500, detail="Failed to create ticket.")

@app.get("/api/vapi-config", response_model=VapiConfigResponse)
async def get_vapi_config():
    if not VAPI_PUBLIC_KEY or not VAPI_ASSISTANT_ID:
        raise HTTPException(status_code=500, detail="Missing Vapi config in .env")
    return VapiConfigResponse(publicKey=VAPI_PUBLIC_KEY, assistantId=VAPI_ASSISTANT_ID)

@app.post("/api/vapi")
async def handle_vapi_webhook(request: VapiWebhookRequest):
    if request.message.get("type") != "assistant-request":
        return {}

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
        print("❌ Vapi webhook error:", e)
        return {"message": {"role": "assistant", "content": "Sorry, something went wrong."}}
