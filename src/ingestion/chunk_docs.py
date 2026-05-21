from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.ingestion.load_docs import load_documents

def chunk_documents(documents, chunk_size=500, chunk_overlap=50):
    """
    Splits documents into smaller chunks for embeddings.
    """
    print(f"Splitting {len(documents)} pages into chunks of size {chunk_size} with overlap {chunk_overlap}...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"Successfully split into {len(chunks)} chunks.")
    
    return chunks

if __name__ == "__main__":
    docs = load_documents()
    chunks = chunk_documents(docs)
    
    if chunks:
        print(f"\nSample chunk #1:\n{chunks[0].page_content}")
        print(f"\nSample chunk metadata: {chunks[0].metadata}")
