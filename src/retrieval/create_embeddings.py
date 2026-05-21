import os
import chromadb
from langchain_ollama import OllamaEmbeddings
from src.ingestion.load_docs import load_documents
from src.ingestion.chunk_docs import chunk_documents

CHROMA_PATH = "./embeddings/chroma_db"
COLLECTION_NAME = "legal_documents"

def main():
    print("Starting embeddings generation pipeline...")
    
    # 1. Load and chunk documents
    print("\n--- Step 1: Loading & Chunking ---")
    try:
        docs = load_documents()
        chunks = chunk_documents(docs)
    except Exception as e:
        print(f"Error during document ingestion: {e}")
        return

    if not chunks:
        print("No chunks found to embed.")
        return

    # 2. Setup Persistent ChromaDB Client
    print(f"\n--- Step 2: Connecting to ChromaDB ---")
    print(f"Using PersistentClient at {CHROMA_PATH}")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # 3. Prevent duplicate embeddings
    print("\n--- Step 3: Preparing Collection ---")
    existing_collections = [col.name for col in client.list_collections()]
    if COLLECTION_NAME in existing_collections:
        print(f"Collection '{COLLECTION_NAME}' already exists. Deleting to prevent duplicates...")
        client.delete_collection(name=COLLECTION_NAME)
    
    print(f"Creating clean collection '{COLLECTION_NAME}'...")
    collection = client.create_collection(name=COLLECTION_NAME)
    
    # 4. Initialize Embeddings Model
    print("\n--- Step 4: Initializing Embeddings Model ---")
    print("Using explicit 'nomic-embed-text' model...")
    embeddings_model = OllamaEmbeddings(model="nomic-embed-text")
    
    # 5. Process and insert chunks manually
    print("\n--- Step 5: Generating and Storing Embeddings ---")
    
    texts = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        chunk_id = f"chunk_{i}"
        
        # Ensure required metadata exists
        metadata = {
            "source": chunk.metadata.get("source", "unknown"),
            "page": chunk.metadata.get("page", 0),
            "chunk_id": chunk_id
        }
        
        texts.append(chunk.page_content)
        metadatas.append(metadata)
        ids.append(chunk_id)
    
    # Generate embeddings explicitly
    try:
        print(f"Generating explicit embeddings for {len(texts)} chunks. This may take a moment...")
        # Batch generation of embedding vectors
        embedding_vectors = embeddings_model.embed_documents(texts)
        
        print("Inserting manually into ChromaDB collection...")
        collection.add(
            documents=texts,
            embeddings=embedding_vectors,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully stored {len(texts)} vectors with metadata in ChromaDB.")
        
        count = collection.count()
        print(f"Verification: ChromaDB now contains {count} vectors.")
        
    except Exception as e:
        print(f"Error during embedding generation or insertion: {e}")

if __name__ == "__main__":
    main()
