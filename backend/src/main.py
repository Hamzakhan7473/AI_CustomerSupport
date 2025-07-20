import os
import random
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool
from pinecone import Pinecone

# 1. Load .env vars
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

if not GOOGLE_API_KEY or not PINECONE_API_KEY:
    raise ValueError("❌ Missing GOOGLE_API_KEY or PINECONE_API_KEY in .env")

# 2. Initialize Google & Pinecone
genai.configure(api_key=GOOGLE_API_KEY)
pinecone = Pinecone(api_key=PINECONE_API_KEY)

# 3. FastAPI instance
app = FastAPI(title="Aven AI Support Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Models
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

# 5. LLM Tool: create_support_ticket
def create_support_ticket(email: str, issue_description: str) -> str:
    ticket_id = f"TICKET-{random.randint(1000, 9999)}"
    print(f"✅ TICKET CREATED: {ticket_id} for {email}")
    return f"Support ticket {ticket_id} created for {email}."

create_ticket_tool = Tool(
    function_declarations=[
        FunctionDeclaration(
            name="create_support_ticket",
            description="Create a support ticket when the user has an issue.",
            parameters={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User's email"},
                    "issue_description": {"type": "string", "description": "Details of the issue"},
                },
                "required": ["email", "issue_description"]
            }
        )
    ]
)

# 6. Initialize LLM + Pinecone index
INDEX_NAME = "aven-support-agent"
embedding_model = "models/text-embedding-004"
index = pinecone.Index(INDEX_NAME)
llm = genai.GenerativeModel("gemini-1.5-pro-latest", tools=[create_ticket_tool])

# 7. Query endpoint
@app.post("/query", response_model=QueryResponse)
async def answer_query(request: QueryRequest):
    try:
        print(f"📩 Query received: {request.query}")
        query_embedding = genai.embed_content(
            model=embedding_model,
            content=request.query
        )["embedding"]

        results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        context = "\n\n".join(match["metadata"].get("text", "") for match in results["matches"])

        chat = llm.start_chat(enable_automatic_function_calling=True)
        prompt = f"Context:\n{context}\n\nUser: {request.query}"
        response = chat.send_message(prompt)

        final_text = "".join(part.text for part in response.parts if part.text)
        return QueryResponse(answer=final_text or "🤖 No answer found.")
    except Exception as e:
        print("❌ Error in /query:", e)
        raise HTTPException(status_code=500, detail="Internal server error.")

# 8. Create ticket
@app.post("/create-ticket")
async def create_ticket(request: TicketRequest):
    try:
        msg = create_support_ticket(request.email, request.issue_description)
        return {"message": msg}
    except Exception as e:
        print("❌ Ticket creation failed:", e)
        raise HTTPException(status_code=500, detail="Could not create ticket.")

# 9. Vapi config for frontend
@app.get("/api/vapi-config", response_model=VapiConfigResponse)
async def get_vapi_config():
    if not VAPI_PUBLIC_KEY or not VAPI_ASSISTANT_ID:
        raise HTTPException(status_code=500, detail="Missing Vapi credentials.")
    return VapiConfigResponse(publicKey=VAPI_PUBLIC_KEY, assistantId=VAPI_ASSISTANT_ID)

# 10. Vapi webhook handler
@app.post("/api/vapi")
async def handle_vapi_webhook(request: VapiWebhookRequest):
    try:
        if request.message.get("type") != "assistant-request":
            return {}

        last_message = request.message["messages"][-1]["content"]
        print(f"🎤 Voice Query: {last_message}")

        query_embedding = genai.embed_content(model=embedding_model, content=last_message)["embedding"]
        results = index.query(vector=query_embedding, top_k=3, include_metadata=True)
        context = "\n\n".join(match["metadata"].get("text", "") for match in results["matches"])

        prompt = f"Context:\n{context}\n\nUser: {last_message}"
        chat = llm.start_chat(enable_automatic_function_calling=True)
        response = chat.send_message(prompt)

        final_text = "".join(part.text for part in response.parts if part.text)
        return {"message": {"role": "assistant", "content": final_text or "🤖 No response."}}
    except Exception as e:
        print("❌ Webhook error:", e)
        return {"message": {"role": "assistant", "content": "⚠️ Voice assistant failed."}}
