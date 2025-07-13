import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from openai import OpenAI
from pinecone import Pinecone

# --- Load Environment & Initialize Clients ---

# Construct the path to the .env file in the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

# Initialize API clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pinecone_client = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


# --- FastAPI App & Pinecone Index ---

app = FastAPI()
INDEX_NAME = "aven-support-agent"

# Connect to the Pinecone index
print("Connecting to Pinecone index...")
index = pinecone_client.Index(INDEX_NAME)
print("✅ Connected to Pinecone index.")


# --- RAG Core Functions ---

def get_context(query: str, top_k: int = 3) -> str:
    """
    Creates a vector embedding for the user's query and retrieves the
    most relevant text chunks (context) from the Pinecone index.
    """
    try:
        query_embedding = openai_client.embeddings.create(
            input=[query],
            model="text-embedding-3-small"
        ).data[0].embedding

        query_results = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        context_chunks = [match['metadata']['text'] for match in query_results['matches']]
        return " ".join(context_chunks)
    except Exception as e:
        print(f"Error getting context from Pinecone: {e}")
        return "Error: Could not retrieve context."

def get_llm_response(query: str, context: str) -> str:
    """
    Generates a response from the LLM based on the user's query and
    the retrieved context from the knowledge base.
    """
    prompt = f"""
    You are a helpful and friendly customer support agent for Aven.
    Use the following context to answer the user's question accurately.
    Do not make up information. If the context doesn't contain the answer,
    say "I'm sorry, I don't have enough information to answer that."

    Context:
    {context}

    User's Question:
    {query}
    """
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful customer support agent for Aven."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting response from LLM: {e}")
        return "Error: Could not generate a response."


# --- API Endpoint for Vapi ---

@app.post("/api/v1")
async def handle_vapi_request(request: Request):
    """
    This is the main endpoint Vapi will call. It orchestrates the RAG pipeline.
    """
    body = await request.json()
    
    # Extract the last message from the user
    # Vapi sends a transcript of the conversation
    last_message = body.get('message', {}).get('content', [{}])[-1]
    
    if last_message.get('role') == 'user':
        user_query = last_message.get('content', '')
        print(f"Received query: {user_query}")
        
        # 1. Retrieve context from Pinecone
        context = get_context(user_query)
        
        # 2. Generate a response from the LLM
        ai_response = get_llm_response(user_query, context)
        
        print(f"Sending reply: {ai_response}")
        # 3. Send the response back to Vapi
        return {"reply": ai_response}
        
    return {"reply": "I'm listening. How can I help you with Aven today?"}