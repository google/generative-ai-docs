"""
Batched Embeddings Example for Gemini API

Demonstrates how to efficiently process multiple texts in a single API call.
"""

import os
import google.generativeai as genai

def batch_embed_example():
    # Configure the API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    genai.configure(api_key=api_key)

    # Sample texts to embed
    texts = [
        "The quick brown fox jumps over the lazy dog.",
        "Gemini's batch embeddings are more efficient than individual calls.",
        "Always prefer batch processing when possible.",
        "This example shows best practices for the Gemini Embeddings API.",
        "Batch processing reduces API calls and improves performance."
    ]

    print(f"Embedding {len(texts)} texts in a single batch...")

    try:
        response = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type="RETRIEVAL_DOCUMENT"
        )

        assert len(response["embedding"]) == len(texts)

        print(f"\nSuccess! Generated {len(texts)} embeddings:")
        for i, (text, emb) in enumerate(zip(texts, response["embedding"])):
            print(f"\nText {i+1}: {text[:50]}...")
            print(f"First 5 dimensions: {emb[:5]}")
            print(f"Total dimensions: {len(emb)}")

    except Exception as e:
        print(f"Error during batch embedding: {e}")

if __name__ == "__main__":
    batch_embed_example()
