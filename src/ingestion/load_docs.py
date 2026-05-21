import os
from langchain_community.document_loaders import PyPDFDirectoryLoader

def load_documents(data_dir: str = "data/raw"):
    """
    Loads all PDF documents from the specified directory.
    """
    print(f"Loading documents from {data_dir}...")
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"Directory {data_dir} does not exist.")
    
    loader = PyPDFDirectoryLoader(data_dir)
    documents = loader.load()
    
    print(f"Successfully loaded {len(documents)} document pages.")
    return documents

if __name__ == "__main__":
    docs = load_documents()
    if docs:
        print(f"Sample content from first page: {docs[0].page_content[:200]}...")
