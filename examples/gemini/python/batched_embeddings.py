"""
Batched Embeddings Example for Gemini API

Demonstrates how to efficiently process multiple texts in a single API call.
"""

import google.generativeai as genai

def batch_embed_example():
    # Configure the API (in production, use environment variables)
    genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your actual API key
    
    # Sample texts to embed
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Gemini's batch embeddings are more efficient than individual calls.",
        "Always prefer batch processing when possible.",
        "This example shows best practices for the Gemini Embeddings API.",
        "Batch processing reduces API calls and improves performance."
    ]
    
    print(f"Embedding {len(texts)} texts in a single batch...")
    
    # Make a single batch request
    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type="RETRIEVAL_DOCUMENT"
        )
        
        # Verify we got embeddings for all texts
        assert len(response["embedding"]) == len(texts)
        
        print("\nSuccess! Embeddings generated:")
        for i, (text, embedding) in enumerate(zip(texts, response["embedding"])):
            print(f"\nText {i+1}: {text[:50]}...")
            print(f"Embedding vector (first 5 dims): {embedding[:5]}")
            print(f"Vector length: {len(embedding)}")
            
    except Exception as e:
        print(f"Error during batch embedding: {e}")

if __name__ == "__main__":
    batch_embed_example()
