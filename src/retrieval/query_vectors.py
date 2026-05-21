import chromadb
from langchain_ollama import OllamaEmbeddings

CHROMA_PATH = "./embeddings/chroma_db"
COLLECTION_NAME = "legal_documents"
TEST_QUERY = "What are the requirements for a valid contract in India?"

def main():
    print(f"Connecting to ChromaDB at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Rule: Fail loudly if collection does not exist
    existing_collections = [col.name for col in client.list_collections()]
    if COLLECTION_NAME not in existing_collections:
        raise ValueError(
            f"CRITICAL ERROR: Collection '{COLLECTION_NAME}' does not exist! "
            f"Please run Phase 3 to generate embeddings first. Do not query an empty DB."
        )
    
    print(f"Loading collection '{COLLECTION_NAME}'...")
    collection = client.get_collection(name=COLLECTION_NAME)
    
    # Rule: Embed query using identical model (nomic-embed-text)
    print(f"Initializing Embeddings Model (nomic-embed-text)...")
    embeddings_model = OllamaEmbeddings(model="nomic-embed-text")
    
    print(f"\nEmbedding test query: '{TEST_QUERY}'")
    query_vector = embeddings_model.embed_query(TEST_QUERY)
    
    # Query ChromaDB explicitly passing the embedding vector
    print(f"Querying ChromaDB for top 3 relevant chunks...")
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=3,
        include=["metadatas", "documents", "distances"]
    )
    
    # Rule: Print raw distance scores and metadata
    print("\n" + "="*50)
    print("--- RETRIEVAL RESULTS ---")
    print("="*50)
    
    distances = results["distances"][0]
    metadatas = results["metadatas"][0]
    documents = results["documents"][0]
    
    for i in range(len(documents)):
        rank = i + 1
        distance = distances[i]
        meta = metadatas[i]
        
        chunk_id = meta.get("chunk_id", "unknown")
        source = meta.get("source", "unknown")
        page = meta.get("page", "unknown")
        text = documents[i]
        
        print(f"\n[Rank {rank}] (Distance: {distance:.4f})")
        print(f"Metadata -> Chunk ID: {chunk_id} | Source: {source} | Page: {page}")
        print(f"Text:\n{text}")
        print("-" * 50)

if __name__ == "__main__":
    try:
        main()
    except ValueError:
        raise
    except Exception as e:
        print(f"\nUnexpected execution error: {e}")
