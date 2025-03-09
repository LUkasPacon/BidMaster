import os
from typing import List, Dict, Optional
import PyPDF2
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI()

def initialize_pinecone():
    """Initialize Pinecone with API key and environment"""
    global pc
    pc = Pinecone(
        api_key=os.getenv('PINECONE_API_KEY')
    )

# Initialize Pinecone client
initialize_pinecone()

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """Extract text from a PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return None

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        
        # If this is not the first chunk, include overlap
        if start > 0:
            start = start - overlap
            
        # If this is the last chunk, adjust end
        if end >= text_length:
            end = text_length
            
        chunk = text[start:end]
        chunks.append(chunk)
        
        # Move start position for next chunk
        start = end
        
        # If we've processed the entire text, break
        if end >= text_length:
            break
            
    return chunks

def create_embedding(text: str) -> List[float]:
    """Create embedding for a text using OpenAI API"""
    try:
        response = openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error creating embedding: {e}")
        return None

def create_embeddings_and_upload(chunks: List[str], source: str, index_name: str = "pdf-search") -> bool:
    """Create embeddings for chunks and upload to Pinecone"""
    try:
        # Check if index exists, if not create it
        if index_name not in [index.name for index in pc.list_indexes()]:
            pc.create_index(
                name=index_name,
                dimension=3072,  # dimension for text-embedding-3-large
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-west-2"
                )
            )
        
        # Connect to index
        index = pc.Index(index_name)
        
        # Create and upload embeddings in batches
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            vectors = []
            
            for j, chunk in enumerate(batch_chunks):
                embedding = create_embedding(chunk)
                if embedding:
                    vectors.append({
                        "id": f"{source}_{i+j}",
                        "values": embedding,
                        "metadata": {
                            "text": chunk,
                            "source": source
                        }
                    })
            
            if vectors:
                index.upsert(vectors=vectors)
                
        return True
    except Exception as e:
        print(f"Error uploading to Pinecone: {e}")
        return False

def generate_answer_with_context(query: str, relevant_chunks: List[Dict], client: OpenAI) -> str:
    """Generate an answer using GPT-4 based on the retrieved chunks"""
    try:
        # Prepare context from chunks
        context = "\n\n---\n\n".join([chunk['metadata']['text'] for chunk in relevant_chunks])
        
        # Create system message
        system_message = """You are a helpful assistant that answers questions based on the provided context. 
        Your answers should be:
        1. Accurate and based only on the provided context
        2. Well-structured and easy to understand
        3. Include relevant quotes or references when appropriate
        If the context doesn't contain enough information to answer the question, say so."""
        
        # Create messages for chat completion
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
        ]
        
        # Get response from GPT-4
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I couldn't generate an answer at this time."

def search_in_pdf(query: str, index_name: str = "pdf-search", top_k: int = 5,
                 similarity_threshold: float = 0.3, return_results: bool = False) -> Optional[Dict]:
    """Search for similar chunks in Pinecone and generate an answer"""
    try:
        # Create embedding for query
        query_embedding = create_embedding(query)
        
        # Connect to index
        index = pc.Index(index_name)
        
        # Search for similar vectors
        results = index.query(
            vector=query_embedding,
            top_k=top_k * 2,
            include_metadata=True
        )
        
        # Filter and sort results
        matches = []
        if results["matches"]:
            matches = [match for match in results["matches"] if match["score"] >= similarity_threshold]
            matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:top_k]
        
        # If no relevant results found, use GPT-4 for general knowledge
        if not matches:
            try:
                response = openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. When answering, start with 'While this isn't mentioned in the document, I can tell you that...' to indicate this is general knowledge."},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                answer = response.choices[0].message.content
                
                if return_results:
                    return {"matches": [], "ai_answer": answer}
                
                print("\n=== AI-Generated Answer (General Knowledge) ===")
                print(answer)
                return None
            except Exception as e:
                print(f"Error generating general knowledge answer: {e}")
                return None if not return_results else {"matches": [], "ai_answer": None}
        
        # Generate answer using document context
        answer = generate_answer_with_context(query, matches, openai_client)
        
        if return_results:
            return {
                "matches": matches,
                "ai_answer": answer
            }
        
        # Display results
        print(f"\nResults for query: '{query}'")
        for i, match in enumerate(matches, 1):
            print(f"\n--- Result {i} ---")
            print(f"Similarity score: {match['score']:.4f}")
            print(f"Source: {match['metadata'].get('source', 'Unknown')}")
            print(f"Text:\n{match['metadata']['text']}")
        
        print("\n=== AI-Generated Answer ===")
        print(answer)
        
        return results
    
    except Exception as e:
        print(f"Error during search: {e}")
        return None

# Export all necessary functions and variables
__all__ = [
    'initialize_pinecone',
    'pc',
    'extract_text_from_pdf',
    'chunk_text',
    'create_embedding',
    'create_embeddings_and_upload',
    'generate_answer_with_context',
    'search_in_pdf'
]