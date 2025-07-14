# /backend/src/main.py

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from pinecone import Pinecone

# --- 1. Load API Keys from .env file ---
# This MUST be at the top, before using any keys.
load_dotenv()

# --- 2. Configure and Initialize Services ---
# This section ensures all services are ready before the app starts.

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Error: GOOGLE_API_KEY not found in your .env file.")
genai.configure(api_key=GOOGLE_API_KEY)

# Configure Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
if not PINECONE_API_KEY:
    raise ValueError("Error: PINECONE_API_KEY not found in your .env file.")
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# --- 3. Create FastAPI App and Global Clients ---
# These are created once when the server starts.

app = FastAPI(title="Aven Support Agent")

INDEX_NAME = "aven-support-agent"  # Your Pinecone index name
llm = genai.GenerativeModel('gemini-1.5-pro-latest')
embedding_model = "models/text-embedding-004"
index = pinecone_client.Index(INDEX_NAME)

# --- 4. Define API Data Models ---

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

# --- 5. Core Application Logic ---

def get_llm_response(query: str, context: str) -> str:
    prompt = f"""
    You are a helpful customer support agent for Aven.
    Use the following context to answer the user's question.
    If the context doesn't contain the answer, say "I'm sorry, I don't have enough information to answer that."

    Context:
    {context}

    User's Question:
    {query}
    """
    try:
        response = llm.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating LLM response: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate language model response.")

# --- 6. API Endpoint ---

@app.post("/query", response_model=QueryResponse)
async def answer_query(request: QueryRequest):
    """
    Receives a query, finds relevant context in Pinecone, and generates an answer.
    """
    try:
        # Create embedding for the incoming query
        query_embedding = genai.embed_content(
            model=embedding_model,
            content=request.query
        )['embedding']

        # Query Pinecone for context
        query_results = index.query(
            vector=query_embedding,
            top_k=5,
            include_metadata=True
        )
        context_chunks = [match['metadata'].get('text', '') for match in query_results['matches']]
        context = "\n\n".join(context_chunks)

        # Generate the final answer
        answer = get_llm_response(query=request.query, context=context)
        
        return QueryResponse(answer=answer)

    except Exception as e:
        print(f"An error occurred in the query endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")