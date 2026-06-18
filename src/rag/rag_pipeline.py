import sys
import chromadb
from langchain_ollama import OllamaEmbeddings, OllamaLLM

CHROMA_PATH = "./embeddings/chroma_db"
COLLECTION_NAME = "legal_documents"

def generate_answer(query: str):
    print(f"Connecting to ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Rule: Fail loudly if collection does not exist
    existing_collections = [col.name for col in client.list_collections()]
    if COLLECTION_NAME not in existing_collections:
        raise ValueError(
            f"CRITICAL ERROR: Collection '{COLLECTION_NAME}' does not exist! "
            f"Please run Phase 3 to generate embeddings first."
        )
    
    collection = client.get_collection(name=COLLECTION_NAME)
    
    # Rule: Embed query using nomic-embed-text
    print(f"Initializing Embeddings Model (nomic-embed-text)...")
    embeddings_model = OllamaEmbeddings(model="nomic-embed-text")
    query_vector = embeddings_model.embed_query(query)
    
    # Retrieve top 3 chunks
    print(f"Querying ChromaDB for top 3 relevant chunks...")
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
        include=["metadatas", "documents", "distances"]
    )
    
    distances = results["distances"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    
    # Filter out chunks with distance score above 0.65
    filtered_context_chunks = []
    retrieved_chunks = []  # For UI display
    print("\n--- RETRIEVED CONTEXT ---")
    for i in range(len(documents)):
        distance = distances[i]
        if distance <= 0.65:
            text = documents[i]
            meta = metadatas[i]
            formatted_chunk = f"""
[Source: {meta.get('source')} | Page: {meta.get('page')}]

{text}
"""
            filtered_context_chunks.append(formatted_chunk)
            retrieved_chunks.append({"text": formatted_chunk, "distance": distance})
            print(f"[Distance: {distance:.4f}] Included: {text[:80].replace(chr(10), ' ')}...")
        else:
            print(f"[Distance: {distance:.4f}] Ignored (above 0.65 threshold)")
            
    if not filtered_context_chunks:
        print("No context found below the distance threshold of 0.65.")
        return (
            "I don't have sufficient information in the provided documents to answer this question.",
            []
        )

    context_str = "\n\n".join(filtered_context_chunks)
        
    # Construct the strictly grounded prompt
    prompt = f"""Answer the question using ONLY the provided context.

Do NOT use outside knowledge.

If the answer is not explicitly present in the context,
respond EXACTLY with:
"I don't have sufficient information in the provided documents to answer this question."

Do not infer.
Do not guess.
Do not partially answer from prior knowledge.

CONTEXT:
{context_str}

QUESTION:
{query}
"""

    print("\n--- SENDING TO LLAMA3.2 ---")
    llm = OllamaLLM(model="llama3.2")
    response = llm.invoke(prompt)
    
    print("\n--- FINAL GENERATED ANSWER ---")
    print(response)
    print("=" * 50)
    
    return response, retrieved_chunks

if __name__ == "__main__":
    # Test queries: one in-context, one out-of-context
    test_queries = [
        "What are the requirements for a valid contract in India?",
        "What is a reciprocal promise?",
        "What is the speed of light?"  # Should trigger the fallback response
    ]
    
    for q in test_queries:
        print(f"\n\n>>> USER QUERY: {q} <<<")
        try:
            generate_answer(q)
        except ValueError:
            raise
        except Exception as e:
            print(f"\nUnexpected execution error: {e}")
