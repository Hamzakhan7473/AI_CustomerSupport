import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec

def read_chunks(file_path: str) -> list[str]:
    """Reads the chunked data from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Split by double newline and filter out empty strings
    return [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]

def create_embeddings(chunks: list[str], model="models/text-embedding-004") -> list[list[float]]:
    """Creates embeddings for a list of text chunks using Gemini."""
    print(f"Creating embeddings for {len(chunks)} chunks...")
    embeddings_list = []
    for i, chunk in enumerate(chunks):
        try:
            response = genai.embed_content(model=model, content=chunk)
            embeddings_list.append(response['embedding'])
            # A small delay to respect API rate limits
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(chunks)} chunks...")
                time.sleep(1)
        except Exception as e:
            print(f"Could not create embedding for chunk {i}: {e}")
            embeddings_list.append([]) # Add empty list for failed chunks
    return embeddings_list

def setup_pinecone_index(pinecone_client, index_name: str, dimension: int):
    """Sets up a Pinecone index if it doesn't already exist."""
    print("Connecting to Pinecone...")
    if index_name not in pinecone_client.list_indexes().names():
        print(f"Index '{index_name}' not found. Creating a new one...")
        pinecone_client.create_index(
            name=index_name,
            dimension=dimension,
            metric='cosine',
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
    return pinecone_client.Index(index_name)

if __name__ == '__main__':
    # --- Load Environment & Initialize Clients ---
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    # AFTER (for debugging only)
    pinecone_client = Pinecone(api_key="")
    
    # --- Configuration ---
    index_name = "aven-support-agent"
    chunked_data_file = "chunked_aven_data.txt"
    # Dimension for Google's text-embedding-004 model is 768
    vector_dimension = 768

    # 1. Read the processed chunks
    text_chunks = read_chunks(chunked_data_file)
    print(f"📄 Read {len(text_chunks)} chunks from file.")
    
    # 2. Create embeddings
    embeddings = create_embeddings(text_chunks)
    
    # 3. Set up Pinecone index
    index = setup_pinecone_index(pinecone_client, index_name, vector_dimension)
    print(f"🌲 Pinecone index '{index_name}' is ready.")
    
    # 4. Prepare and upsert vectors to Pinecone
    vectors_to_upsert = []
    # Filter out any chunks that failed to embed
    for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
        if embedding: # Only add if embedding was successful
            vectors_to_upsert.append({
                "id": f"chunk_{i}",
                "values": embedding,
                "metadata": {"text": chunk}
            })
    
    if vectors_to_upsert:
        print(f"Uploading {len(vectors_to_upsert)} vectors to Pinecone...")
        index.upsert(vectors=vectors_to_upsert, batch_size=100)
        print("✅ All vectors have been uploaded successfully.")
        print("Final index stats:")
        print(index.describe_index_stats())
    else:
        print("No vectors to upload.")